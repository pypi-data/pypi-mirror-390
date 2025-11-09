#!/usr/bin/env bash

set -ex

export PYTHONNOUSERSITE=True

python_version="$1"
requirements_path="$2"
pip_index_url="$3"
output_path="$4"
channel="$5"
model_env_name=mlflow_backend-env

if [[ -z "$pip_index_url" ]]; then
  pip_index_url="https://pypi.org/simple"
fi

if [ "$(uname)" != "Darwin" ]; then
  extra_reqs="libstdcxx-ng=13"
else
  extra_reqs=""
fi

# only install build-essential on linux and if gcc does not exist
if [ "$(uname)" != "Darwin" ] && ! command -v gcc &> /dev/null; then
  apt-get update
  apt-get install -y build-essential
fi

set +x; eval "$(conda shell.bash hook)"; set -x

conda env remove -y -n $model_env_name || true
conda create -y -q -c $channel -n $model_env_name "python=$python_version" conda-pack "$extra_reqs"
set +x; conda activate $model_env_name; set -x

pip install uv --index-url "$pip_index_url"
uv pip install -r "$requirements_path" --index-url "$pip_index_url" "numpy<2"

conda-pack --name $model_env_name --output "$output_path" --ignore-missing-files --exclude lib/python3.1
chmod 666 "$output_path"
