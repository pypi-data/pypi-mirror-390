import functools
import json
import shutil
import subprocess

import numpy as np


def parse_mlflow_signature(mlflow_config: dict) -> tuple[int, dict, dict]:
    """Parses an MLFlow model signature into Triton input and output schemas

    Args:
        mlflow_config: the MLModel information for this model

    Returns:
        Tuple of max batch size, input schema, and output schema
    """

    mlflow_signature = mlflow_config["signature"]
    mlflow_inputs = json.loads(mlflow_signature["inputs"])
    mlflow_outputs = json.loads(mlflow_signature["outputs"])

    batch_sizes = set()
    inputs = dict()
    for i, model_input in enumerate(mlflow_inputs):
        name, dtype, dims, batch_size = parse_mlflow_signature_value(model_input)
        if name is None:
            name = f"input{i}"
        inputs[name] = dtype, dims, batch_size
        batch_sizes.add(batch_size)

    outputs = dict()
    for i, model_output in enumerate(mlflow_outputs):
        name, dtype, dims, batch_size = parse_mlflow_signature_value(model_output)
        if name is None:
            name = f"output{i}"
        outputs[name] = dtype, dims, batch_size
        batch_sizes.add(batch_size)

    if batch_sizes == {-1, 0}:
        for name, (dtype, dims, batch_size) in inputs.items():
            if batch_size == -1:
                inputs[name] = dtype, [-1] + dims, 0
        for name, (dtype, dims, batch_size) in outputs.items():
            if batch_size == -1:
                outputs[name] = dtype, [-1] + dims, 0
        batch_sizes.remove(-1)

    if len(batch_sizes) > 1:
        if 0 in batch_sizes:
            raise ValueError(f"Inconsistent batch sizes: {batch_sizes}")
        if -1 in batch_sizes:
            batch_sizes.remove(-1)
        batch_size = min(batch_sizes)
        for name, (dtype, dims, _) in inputs.items():
            inputs[name] = dtype, dims, batch_size
        for name, (dtype, dims, _) in outputs.items():
            outputs[name] = dtype, dims, batch_size
        batch_sizes = {batch_size}

    return batch_sizes.pop(), inputs, outputs


def parse_mlflow_signature_value(value: dict) -> tuple[str | None, str, list[int], int]:
    """Parses a MLFlow signature value into a tuple of (name, type, shape, batch size)

    Args:
        value: MLFlow signature value

    Returns:
        Tuple of (name, type, shape, batch size)
    """
    if value["type"] == "tensor":
        dtype = np_to_triton_dtype(np.dtype(value["tensor-spec"]["dtype"]))
        dtype = "STRING" if dtype == "BYTES" else dtype
        shape = value["tensor-spec"]["shape"]
        if len(shape) > 1:
            dims = shape[1:]
            batch_size = shape[0]
        else:
            dims = shape
            batch_size = 0
    elif value["type"] == "array":
        dtype = "STRING"
        dims = [-1]
        batch_size = 0
    else:
        value_type_mapping = {
            "string": "STRING",
            "integer": "INT32",
            "float": "FP32",
        }
        if value["type"] in value_type_mapping:
            dtype = value_type_mapping[value["type"]]
        else:
            dtype = np_to_triton_dtype(np.dtype(value["type"]))
        dims = [-1]
        batch_size = 0

    return value.get("name"), f"{dtype}", dims, batch_size


def np_to_triton_dtype(np_dtype):
    if np_dtype == bool:
        return "BOOL"
    elif np_dtype == np.int8:
        return "INT8"
    elif np_dtype == np.int16:
        return "INT16"
    elif np_dtype == np.int32:
        return "INT32"
    elif np_dtype == np.int64:
        return "INT64"
    elif np_dtype == np.uint8:
        return "UINT8"
    elif np_dtype == np.uint16:
        return "UINT16"
    elif np_dtype == np.uint32:
        return "UINT32"
    elif np_dtype == np.uint64:
        return "UINT64"
    elif np_dtype == np.float16:
        return "FP16"
    elif np_dtype == np.float32:
        return "FP32"
    elif np_dtype == np.float64:
        return "FP64"
    elif np_dtype == np.object_ or np_dtype.type == np.bytes_:
        return "BYTES"
    return None


@functools.lru_cache(maxsize=None)
def is_docker_available(**_) -> tuple[bool, str]:
    """Check if the Docker environment can build conda pack.
    This function checks if the Docker command is available on the system and can run docker commands.
    Returns:
        bool: True if Docker is available, False otherwise.
        str: A message indicating the result of the check.
    """
    if shutil.which("docker") is None:
        return False, "Docker command not found. Please install Docker to build conda pack in a Docker environment."
    try:
        subprocess.run(["docker", "ps"], capture_output=True, text=True, check=True)
        return True, "Docker is available and can run commands."
    except subprocess.CalledProcessError as e:
        return False, f"Docker is not running or not accessible. Error: {e.stderr.strip()}"
