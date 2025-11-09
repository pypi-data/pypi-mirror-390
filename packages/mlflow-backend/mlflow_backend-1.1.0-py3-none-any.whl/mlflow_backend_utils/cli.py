import click

from mlflow_backend_utils.sdk import build_conda_pack, build_config, build_triton_stub


@click.group()
def cli():
    pass


@cli.command("build-env")
@click.option("--python-version", "-p", type=str, default="3.10")
@click.option("--requirements", "-r", type=click.Path(exists=True), required=False)
@click.option("--platform", type=click.types.Choice(["x86", "arm"], case_sensitive=False), required=False)
@click.option("--output-path", "-o", type=click.Path(), default="conda-pack.tar.gz")
@click.option("--conda-channel", type=str, default="conda-forge")
@click.option("--pip-index-url", type=str, default="https://pypi.org/simple")
@click.option(
    "--preferred-methods",
    type=click.Choice(["docker", "local"], case_sensitive=False),
    multiple=True,
    default=["docker", "local"],
)
def cli_build_conda_pack(
    requirements, python_version, platform, output_path, conda_channel, pip_index_url, preferred_methods
):
    try:
        build_conda_pack(
            python_version=python_version,
            requirements=requirements,
            platform=platform,
            output_path=output_path,
            pip_index_url=pip_index_url,
            conda_channel=conda_channel,
            preferred_methods=preferred_methods,
        )
    except RuntimeError as e:
        click.secho(f"Error building conda pack: {e}", fg="red")
        raise click.Abort()


@cli.command("build-stub")
@click.option("--python-version", "-p", type=str, required=True)
@click.option("--triton-version", "-t", type=str, required=True)
@click.option("--platform", type=click.types.Choice(["x86", "arm"], case_sensitive=False), required=False)
@click.option("--output-path", "-o", type=click.Path(), default="triton_python_backend_stub")
@click.option("--conda-channel", type=str, default="conda-forge")
@click.option(
    "--preferred-methods",
    type=click.Choice(["docker", "kubernetes"], case_sensitive=False),
    multiple=True,
    default=["docker", "kubernetes"],
)
@click.option("--k8s_shared_s3_path", type=str, required=False)
@click.option("--k8s_service_account", type=str, default="default")
def cli_build_triton_python_stub(
    python_version,
    triton_version,
    platform,
    output_path,
    conda_channel,
    preferred_methods,
    k8s_shared_s3_path,
    k8s_service_account,
):
    try:
        build_triton_stub(
            python_version=python_version,
            triton_version=triton_version,
            platform=platform,
            output_path=output_path,
            conda_channel=conda_channel,
            k8s_shared_s3_path=k8s_shared_s3_path,
            k8s_service_account=k8s_service_account,
            preferred_methods=preferred_methods,
        )
    except RuntimeError as e:
        click.secho(f"Error building Triton Python stub: {e}", fg="red")
        raise click.Abort()


@cli.command("build-config")
@click.option("--model-path", "-m", type=click.Path(exists=True), required=True)
@click.option("--conda-pack-path", "-c", type=click.Path(exists=True), required=False)
@click.option("--default-max-batch-size", "-b", type=int, default=1000)
def cli_build_config(model_path, conda_pack_path, default_max_batch_size):
    config = build_config(model_path, conda_pack_path, default_max_batch_size=default_max_batch_size)
    print(config)


if __name__ == "__main__":
    cli()
