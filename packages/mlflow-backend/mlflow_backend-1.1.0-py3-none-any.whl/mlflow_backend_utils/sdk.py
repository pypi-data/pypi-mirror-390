from pathlib import Path
from typing import Iterable, Literal

import click
import yaml

import mlflow_backend_utils.conda_pack_utils as _conda_pack_utils
import mlflow_backend_utils.triton_stub_utils as _triton_stub_utils
import mlflow_backend_utils.utils as _utils


def build_config(model_path: str | Path, conda_pack_path: Path | None = None, default_max_batch_size: int = 1000) -> str:
    """Builds a Triton config file from an MLflow model

    Args:
        model_path: Path to the MLflow model directory
        conda_pack_path: Path to the conda pack file
        default_max_batch_size: Default max batch size for the model

    Returns:
        str: The Triton config file
    """
    with open(Path(model_path).joinpath("MLmodel")) as f:
        mlflow_config = yaml.safe_load(f)

    editable_triton_config = f'backend: "mlflow"\n'

    batch_size, inputs, outputs = _utils.parse_mlflow_signature(mlflow_config)

    batch_size = default_max_batch_size if batch_size == -1 else batch_size
    editable_triton_config += f"\nmax_batch_size: {batch_size}"

    if "transformers" in mlflow_config["flavors"].keys():
        # we don't use MLflow signatures for transformers models due to the variable input/output schemas they have
        editable_triton_config += (
            f'\ninput [\n\t{{\n\t\tname: "input0"\n\t\tdata_type: TYPE_STRING\n\t\tdims: [-1]\n\t}}\n]'
        )
        editable_triton_config += (
            f'\noutput [\n\t{{\n\t\tname: "output0"\n\t\tdata_type: TYPE_STRING\n\t\tdims: [-1]\n\t}}\n]'
        )
    else:
        for name, (dtype, dims, _) in inputs.items():
            editable_triton_config += (
                f'\ninput [\n\t{{\n\t\tname: "{name}"\n\t\tdata_type: TYPE_{dtype}\n\t\tdims: {dims}\n\t}}\n]'
            )

        for name, (dtype, dims, _) in outputs.items():
            editable_triton_config += (
                f'\noutput [\n\t{{\n\t\tname: "{name}"\n\t\tdata_type: TYPE_{dtype}\n\t\tdims: {dims}\n\t}}\n]'
            )

    if conda_pack_path:
        conda_pack_path = Path(conda_pack_path)
        editable_triton_config += f'\nparameters: {{key: "EXECUTION_ENV_PATH" value: {{string_value: "$$TRITON_MODEL_DIRECTORY/{conda_pack_path.name}"}}}}\n'

    return editable_triton_config


def build_conda_pack(
    *,
    python_version: str,
    requirements: str | Path,
    platform: str = None,
    output_path: str | Path = "conda-pack.tar.gz",
    pip_index_url: str = "https://pypi.org/simple",
    conda_channel: str = "conda-forge",
    preferred_methods: Iterable[Literal["docker", "local"]] = ("docker", "local"),
):
    method_maps = {
        "docker": (_utils.is_docker_available, _conda_pack_utils.build_conda_pack_docker),  # noqa
        "local": (_conda_pack_utils.can_build_conda_pack_local, _conda_pack_utils.build_conda_pack_local),  # noqa
    }
    for method in preferred_methods:
        if method not in method_maps:
            raise ValueError(f"Unknown method: {method}. Supported methods are: {list(method_maps.keys())}")
        can_build_fn, build_fn = method_maps[method]
        can_build_w_method, reason = can_build_fn(requested_platform=platform)
        if can_build_w_method:
            return build_fn(
                python_version=python_version,
                requirements=requirements,
                platform=platform,
                output_path=output_path,
                pip_index_url=pip_index_url,
                conda_channel=conda_channel,
            )
        else:
            click.secho(f"Cannot build conda pack with {method} for reason: {reason}", fg="yellow")
    raise RuntimeError(
        f"Cannot build conda pack in current environment with methods: {preferred_methods}. "
        f"Supported methods are: {list(method_maps.keys())}"
    )


def build_triton_stub(
    *,
    python_version: str,
    triton_version: str,
    platform: str = None,
    output_path: str | Path = "triton_python_backend_stub",
    conda_channel: str = "conda-forge",
    k8s_shared_s3_path: str | None = None,
    k8s_service_account: str = "default",
    preferred_methods: Iterable[Literal["docker", "kubernetes"]] = ("docker", "kubernetes"),
):
    method_maps = {
        "docker": (_utils.is_docker_available, _triton_stub_utils.build_triton_stub_docker),
        "kubernetes": (
            _triton_stub_utils.can_build_triton_stub_kubernetes,
            _triton_stub_utils.build_triton_stub_kubernetes,
        ),
    }
    for method in preferred_methods:
        if method not in method_maps:
            raise ValueError(f"Unknown method: {method}. Supported methods are: {list(method_maps.keys())}")
        can_build_fn, build_fn = method_maps[method]
        can_build_w_method, reason = can_build_fn(requested_platform=platform, shared_s3_path=k8s_shared_s3_path)
        if can_build_w_method:
            return build_fn(
                python_version=python_version,
                triton_version=triton_version,
                platform=platform,
                output_path=output_path,
                conda_channel=conda_channel,
                k8s_shared_s3_path=k8s_shared_s3_path,
                k8s_service_account=k8s_service_account,
            )
        else:
            click.secho(f"Cannot build triton python stub with {method} for reason: {reason}", fg="yellow")
    raise RuntimeError(
        f"Cannot build triton python stub in current environment with methods: {preferred_methods}. "
        f"Supported methods are: {list(method_maps.keys())}"
    )
