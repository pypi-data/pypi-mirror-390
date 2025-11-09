import base64
import os
import random
import shutil
import subprocess
from pathlib import Path

import boto3
import yaml

from mlflow_backend_utils.constants import ARM_PLATFORMS, X86_PLATFORMS


def can_build_triton_stub_kubernetes(
    requested_platform: str | None = None,
    shared_s3_path: str | None = None,
    **_,
) -> tuple[bool, str]:
    # Check if kubectl is available
    if shutil.which("kubectl") is None:
        return False, "kubectl command not found. Please install kubectl to build Triton stub on Kubernetes."

    # Check if kubernetes is available
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            return False, "Unable to connect to a Kubernetes cluster with `kubectl get pods`."
    except subprocess.CalledProcessError as e:
        return False, f"Failed to get kubernetes pods: {e}"

    if requested_platform and requested_platform not in X86_PLATFORMS:
        # TODO: Support ARM platforms in the future
        return False, "Building Triton stub on Kubernetes is only supported for x86 platforms."

    if shared_s3_path is None:
        return False, "shared_s3_path is required to build Triton stub on Kubernetes."

    return True, "Local environment can build Triton stub on Kubernetes."


def build_triton_stub_docker(
    *,
    python_version: str,
    triton_version: str,
    platform: str = None,
    output_path: str | Path = "triton_python_backend_stub",
    conda_channel: str = "conda-forge",
    **_,
):
    output_path = Path(output_path)
    build_script_path = Path(__file__).parent.joinpath("build_triton_python_stub.sh")
    volumes = [
        "-v",
        f"{build_script_path.parent.absolute().as_posix()}:/tmp/build_script",
        "-v",
        f"{os.path.curdir}:/workdir",
    ]
    env = []
    container_cert_path = ""
    if "REQUESTS_CA_BUNDLE" in os.environ:
        container_cert_path = "/tmp/requests_ca_bundle.pem"
        volumes.extend(["-v", f"{os.environ['REQUESTS_CA_BUNDLE']}:{container_cert_path}"])
        env.extend(["-e", f"REQUESTS_CA_BUNDLE={container_cert_path}"])

    platform_args = list()
    if platform:
        if platform in X86_PLATFORMS:
            platform_args = ["--platform", "linux/amd64"]
        elif platform in ARM_PLATFORMS:
            platform_args = ["--platform", "linux/arm64"]
        else:
            raise ValueError(f"Unknown platform: {platform}")

    result = subprocess.run(
        args=[
            "docker",
            "run",
            "--rm",
            *volumes,
            *env,
            *platform_args,
            f"nvcr.io/nvidia/tritonserver:{triton_version.strip('r')}-py3",
            "bash",
            "/tmp/build_script/build_triton_python_stub.sh",
            triton_version,
            python_version,
            f"/workdir/{output_path.name}",
            conda_channel,
            "",  # no s3 path
            container_cert_path,
        ],
    )
    if result.returncode != 0:
        raise RuntimeError("Triton stub build failed")

    shutil.move(output_path.name, output_path)


def build_triton_stub_kubernetes(
    *,
    python_version: str,
    triton_version: str,
    output_path: str | Path = "triton_python_backend_stub",
    conda_channel: str = "conda-forge",
    k8s_shared_s3_path: str,
    k8s_job_name: str | None = None,
    k8s_service_account: str = "default",
    k8s_s3_endpoint_url: str | None = None,
    k8s_aws_access_key_id: str | None = None,
    k8s_aws_secret_access_key: str | None = None,
    k8s_aws_session_token: str | None = None,
    k8s_aws_region: str | None = None,
    **_,
):
    output_path = Path(output_path)
    if not k8s_job_name:
        k8s_job_name = (
            f"build-triton-python-stub-{triton_version.strip('r')}-{python_version}-{random.randint(0, 10000)}".replace(
                ".", "-"
            )
        )

    aws_secret_name = None
    if k8s_aws_access_key_id and k8s_aws_secret_access_key:
        aws_secret_name = f"aws-creds-{k8s_job_name}"
        setup_aws_credentials_secret(
            name=aws_secret_name,
            aws_access_key_id=k8s_aws_access_key_id,
            aws_secret_access_key=k8s_aws_secret_access_key,
            aws_session_token=k8s_aws_session_token,
        )

    remove_job_if_exists(k8s_job_name)
    job_manifest = create_job_manifest(
        job_name=k8s_job_name,
        python_version=python_version,
        triton_version=triton_version,
        s3_output_path=k8s_shared_s3_path,
        service_account=k8s_service_account,
        conda_channel=conda_channel,
        s3_endpoint_url=k8s_s3_endpoint_url,
        aws_region=k8s_aws_region,
        aws_secret=aws_secret_name,
    )
    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=yaml.dump(job_manifest),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create Kubernetes job: {result.stderr}")

    # wait for job to start running
    result = subprocess.run(
        [
            "kubectl",
            "wait",
            "--for=jsonpath={.status.ready}=1",
            "--timeout=600s",
            f"job/{job_manifest['metadata']['name']}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to wait for Kubernetes job to start: {result.stderr}")

    result = subprocess.run(
        [
            "kubectl",
            "logs",
            "-f",
            f'job/{job_manifest["metadata"]["name"]}',
        ]
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to get logs from Kubernetes job: {result.stderr}")

    # wait for job to complete
    for i in range(60 * 10 // 10):
        result = subprocess.run(
            ["kubectl", "wait", "--for=condition=complete", "--timeout=10s", f"job/{job_manifest['metadata']['name']}"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            break

        # raise error if job has failed
        job_status = subprocess.run(
            ["kubectl", "get", "job", k8s_job_name, "-o", "jsonpath={.status.failed}"],
            capture_output=True,
            text=True,
            check=True,
        )
        if job_status.stdout.strip() != "0":
            raise RuntimeError(f"Kubernetes job {k8s_job_name} has failed. Check the logs for more details.")
    else:
        raise RuntimeError(f"Failed to wait for Kubernetes job to complete: {result.stderr}")

    # cleanup secret if it was created
    if aws_secret_name:
        subprocess.run(["kubectl", "delete", "secret", aws_secret_name], check=True, capture_output=True, text=True)

    s3 = boto3.client("s3")
    bucket_name, key = k8s_shared_s3_path.replace("s3://", "").split("/", 1)
    try:
        s3.download_file(bucket_name, key, str(output_path))
    except Exception as e:
        raise RuntimeError(
            f"Failed to download Triton stub from S3: {e}. Ensure the job completed successfully and the file exists in S3."
        )


def create_job_manifest(
    job_name: str,
    python_version: str,
    triton_version: str,
    s3_output_path: str,
    conda_channel: str,
    cpu: str = "1",
    memory: str = "4Gi",
    service_account: str = "default",
    s3_endpoint_url: str | None = None,
    aws_region: str | None = None,
    aws_secret: str | None = None,
) -> dict:
    build_script = Path(__file__).parent.joinpath("build_triton_python_stub.sh").read_text()
    build_script = build_script.replace("$1", triton_version)
    build_script = build_script.replace("$2", python_version)
    build_script = build_script.replace("$3", "./tpbs")
    build_script = build_script.replace("$4", conda_channel)
    build_script = build_script.replace("$5", s3_output_path)

    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": job_name,
            "annotations": {"karpenter.sh/do-not-disrupt": "true"},
        },
        "spec": {
            "ttlSecondsAfterFinished": 60 * 60,
            "backoffLimit": 0,
            "template": {
                "metadata": {
                    "labels": {
                        "mlflow-backend-id": job_name,
                    }
                },
                "spec": {
                    "serviceAccountName": service_account,
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "compiler",
                            "image": f"nvcr.io/nvidia/tritonserver:{triton_version.strip('r')}-py3",
                            "imagePullPolicy": "Always",
                            "command": ["/bin/sh", "-c", build_script],
                            "resources": {
                                "requests": {"cpu": cpu, "memory": memory},
                                "limits": {"memory": memory},
                            },
                            "volumeMounts": [],
                            "env": [],
                            "envFrom": [],
                        }
                    ],
                    "volumes": [],
                },
            },
        },
    }

    if s3_endpoint_url:
        job_manifest["spec"]["template"]["spec"]["containers"][0]["env"].append(
            {"name": "AWS_ENDPOINT_URL_S3", "value": s3_endpoint_url}
        )

    if aws_region:
        job_manifest["spec"]["template"]["spec"]["containers"][0]["env"].append(
            {"name": "AWS_REGION", "value": aws_region}
        )
        job_manifest["spec"]["template"]["spec"]["containers"][0]["env"].append(
            {"name": "AWS_DEFAULT_REGION", "value": aws_region}
        )

    if aws_secret:
        job_manifest["spec"]["template"]["spec"]["containers"][0]["envFrom"].append({"secretRef": {"name": aws_secret}})

    """
    if False:
        job_manifest["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
            {"name": "efs-volume", "mountPath": "/efs"}
        )
        job_manifest["spec"]["template"]["spec"]["volumes"].append(
            {
                "name": "efs-volume",
                "persistentVolumeClaim": {"claimName": f"{namespace}-efs-team-default"},
            }
        )
    """

    return job_manifest


def setup_aws_credentials_secret(
    name: str, aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str | None = None
):
    """Creates a Kubernetes secret for AWS credentials."""
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "type": "Opaque",
        "metadata": {
            "name": name,
        },
        "data": {
            "AWS_ACCESS_KEY_ID": base64.b64encode(aws_access_key_id.encode()).decode(),
            "AWS_SECRET_ACCESS_KEY": base64.b64encode(aws_secret_access_key.encode()).decode(),
        },
    }
    if aws_session_token:
        secret["data"]["AWS_SESSION_TOKEN"] = base64.b64encode(aws_session_token.encode()).decode()

    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=yaml.dump(secret),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create Kubernetes secret: {result.stderr}")


def remove_job_if_exists(job_name: str):
    """Removes a Kubernetes job if it exists."""
    subprocess.run(
        ["kubectl", "delete", "job", job_name],
        capture_output=True,
        text=True,
        check=False,
    )
