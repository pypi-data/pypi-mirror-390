import os
import platform as _platform
import shutil
import subprocess
from pathlib import Path

from mlflow_backend_utils.constants import ARM_PLATFORMS, X86_PLATFORMS


def can_build_conda_pack_local(requested_platform: str | None, **_) -> tuple[bool, str]:
    """Check if the local environment can build conda pack.
    This function performs the following checks:
    - Ensures that the conda command is available
    - Checks if the local platform matches the requested platform
    - Verifies that the operating system is Linux

    Args:
        requested_platform: The platform for which to check compatibility (e.g., "x86", "arm").

    Returns:
        bool: True if the local environment can build conda pack, False otherwise.
        str: A message indicating the result of the check.
    """
    if shutil.which("conda") is None:
        return False, "Conda command not found. Please install conda to build conda pack in local environment."

    if requested_platform and requested_platform not in X86_PLATFORMS and requested_platform not in ARM_PLATFORMS:
        raise ValueError(f"Unknown platform: {requested_platform}")

    if _platform.system() != "Linux":
        return False, "Conda pack can only be built on Linux operating systems."

    if requested_platform:
        local_platform = _platform.machine()
        if (requested_platform in X86_PLATFORMS and local_platform in X86_PLATFORMS) or (
            requested_platform in ARM_PLATFORMS and local_platform in ARM_PLATFORMS
        ):
            return True, "Local platform matches requested platform."
        else:
            return False, f"Local platform {local_platform} does not match requested platform {requested_platform}."
    else:
        return True, "Local environment can build conda pack without platform restrictions."


def build_conda_pack_local(
    *,
    python_version: str,
    requirements: str | Path,
    output_path: str | Path = "conda-pack.tar.gz",
    pip_index_url: str = "https://pypi.org/simple",
    conda_channel: str = "conda-forge",
    **_,
):
    requirements = Path(requirements)
    output_path = Path(output_path)

    if output_path.exists():
        output_path.unlink()

    result = subprocess.run(
        args=[
            Path(__file__).parent.joinpath("build_conda_env.sh").as_posix(),
            python_version,
            requirements.as_posix(),
            pip_index_url,
            output_path.as_posix(),
            conda_channel,
        ],
    )

    if result.returncode != 0:
        raise RuntimeError("Conda environment build failed")


def build_conda_pack_docker(
    *,
    python_version: str,
    requirements: str | Path,
    platform: str = None,
    output_path: str | Path = "conda-pack.tar.gz",
    pip_index_url: str = "https://pypi.org/simple",
    conda_channel: str = "conda-forge",
    **_,
):
    requirements = Path(requirements)
    output_path = Path(output_path)

    if output_path.exists():
        output_path.unlink()

    build_script_path = Path(__file__).parent.joinpath("build_conda_env.sh")
    volumes = [
        "-v",
        f"{build_script_path.parent.absolute().as_posix()}:/tmp/build_script",
        "-v",
        f"{os.path.curdir}:/workdir",
    ]

    env = []

    if "REQUESTS_CA_BUNDLE" in os.environ:
        volumes.extend(["-v", f"{os.environ['REQUESTS_CA_BUNDLE']}:/tmp/requests_ca_bundle.pem"])
        env.extend(["-e", "REQUESTS_CA_BUNDLE=/tmp/requests_ca_bundle.pem"])

    platform_args = list()
    if platform:
        if platform == "x86":
            platform_args = ["--platform", "linux/amd64"]
        elif platform == "arm":
            platform_args = ["--platform", "linux/arm64"]
        else:
            raise ValueError(f"Unknown platform: {platform}")

    volumes.extend(["-v", f"{requirements.absolute().as_posix()}:/tmp/requirements.txt"])

    result = subprocess.run(
        args=[
            "docker",
            "run",
            "--rm",
            *volumes,
            *platform_args,
            *env,
            "condaforge/miniforge3:25.3.1-0",
            "bash",
            "/tmp/build_script/build_conda_env.sh",
            python_version,
            "/tmp/requirements.txt",
            pip_index_url,
            f"/workdir/{output_path.name}",
            conda_channel,
        ],
    )
    if result.returncode != 0:
        raise RuntimeError("Conda environment build failed")

    shutil.move(output_path.name, output_path)
