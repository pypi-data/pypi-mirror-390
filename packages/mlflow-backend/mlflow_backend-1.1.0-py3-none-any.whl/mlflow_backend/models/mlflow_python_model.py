import json
import os
from typing import List

import mlflow
import numpy as np
import pandas as pd
import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    """Your Python model must use the same class name. Every Python model
    that is created must have "TritonPythonModel" as the class name.
    """

    def initialize(self, args):
        """`initialize` is called only once when the model is being loaded.
        Implementing `initialize` function is optional. This function allows
        the model to initialize any state associated with this model.

        Parameters
        ----------
        args : dict
          Both keys and values are strings. The dictionary keys and values are:
          * model_config: A JSON string containing the model configuration
          * model_instance_kind: A string containing model instance kind
          * model_instance_device_id: A string containing model instance device
            ID
          * model_repository: Model repository path
          * model_version: Model version
          * model_name: Model name
        """
        self.model_path = os.path.join(args["model_repository"], args["model_version"])

        # open model config yaml to determine loader type
        # with open(os.path.join(args["model_repository"], args["model_version"], "MLmodel"), "r") as f:
        #    model_config = yaml.safe_load(f)

        self.model = mlflow.pyfunc.load_model(self.model_path)
        self.model_config = json.loads(args["model_config"])

    def execute(self, requests: List["pb_utils.InferenceRequest"]):
        """`execute` must be implemented in every Python model. `execute`
        function receives a list of pb_utils.InferenceRequest as the only
        argument. This function is called when an inference is requested
        for this model.

        Parameters
        ----------
        requests : list
          A list of pb_utils.InferenceRequest

        Returns
        -------
        list
          A list of pb_utils.InferenceResponse. The length of this list must
          be the same as `requests`
        """

        responses = []

        for request in requests:
            inputs = dict()
            for input_config in self.model_config["input"]:
                input_tensor = pb_utils.get_input_tensor_by_name(request, input_config["name"])
                input_tensor = input_tensor.as_numpy()
                if input_config["data_type"] == "TYPE_STRING":
                    input_tensor = np.vectorize(lambda x: x.decode())(input_tensor).astype(object)
                inputs[input_config["name"]] = input_tensor

            try:
                output = self.model.predict(inputs)
            except (ValueError, mlflow.exceptions.MlflowException, KeyError) as e1:
                try:
                    output = self.model.predict(*list(inputs.values()))
                except mlflow.exceptions.MlflowException as e2:
                    try:
                        output = self.model.predict(*[v.tolist() for v in inputs.values()])
                    except Exception as e3:
                        raise pb_utils.TritonModelException(
                            f"MLFlow model prediction failed with errors: \n{e1}, \n{e2}, \n{e3}"
                        )

            output_tensors = list()
            if isinstance(output, np.ndarray):
                if len(self.model_config["output"]) > 1:
                    raise pb_utils.TritonModelException(
                        f"Model output is a numpy array but model config specifies multiple outputs"
                    )
                output_name = self.model_config["output"][0]["name"]
                output_type = pb_utils.TRITON_STRING_TO_NUMPY[self.model_config["output"][0]["data_type"]]
                output_tensors.append(pb_utils.Tensor(output_name, output.astype(output_type)))
            elif isinstance(output, pd.Series):
                if len(self.model_config["output"]) > 1:
                    raise pb_utils.TritonModelException(
                        f"Model output is a pandas series but model config specifies multiple outputs"
                    )
                output_name = self.model_config["output"][0]["name"]
                output_type = pb_utils.TRITON_STRING_TO_NUMPY[self.model_config["output"][0]["data_type"]]
                output_tensors.append(pb_utils.Tensor(output_name, output.values.astype(output_type)))
            elif isinstance(output, pd.DataFrame):
                for output_config in self.model_config["output"]:
                    output_type = pb_utils.TRITON_STRING_TO_NUMPY[output_config["data_type"]]
                    output_tensors.append(
                        pb_utils.Tensor(output_config["name"], output[output_config["name"]].values.astype(output_type))
                    )
            elif isinstance(output, list):
                if len(self.model_config["output"]) > 1:
                    raise pb_utils.TritonModelException(
                        f"Model output is a list but model config specifies multiple outputs"
                    )
                output_name = self.model_config["output"][0]["name"]
                output_type = pb_utils.TRITON_STRING_TO_NUMPY[self.model_config["output"][0]["data_type"]]
                output_tensors.append(pb_utils.Tensor(output_name, np.array(output).astype(output_type)))
            elif isinstance(output, dict):
                for output_config in self.model_config["output"]:
                    output_name = output_config["name"]
                    output_type = pb_utils.TRITON_STRING_TO_NUMPY[output_config["data_type"]]
                    output_tensors.append(
                        pb_utils.Tensor(output_name, np.array(output[output_name]).astype(output_type))
                    )
            # enable handling of torch tensors without needing to include torch as dependency for all python models
            else:
                try:
                    import torch

                    if isinstance(output, torch.Tensor):
                        if len(self.model_config["output"]) > 1:
                            raise pb_utils.TritonModelException(
                                f"Model output is a tensor but model config specifies multiple outputs"
                            )
                        output_name = self.model_config["output"][0]["name"]
                        output_type = pb_utils.TRITON_STRING_TO_NUMPY[self.model_config["output"][0]["data_type"]]
                        output_tensors.append(pb_utils.Tensor(output_name, output.numpy().astype(output_type)))
                    else:
                        raise pb_utils.TritonModelException(
                            f"Unsupported MLFlow output type: {type(output)}. Please use numpy arrays or pandas dataframes."
                        )
                except:
                    raise pb_utils.TritonModelException(
                        f"Unsupported MLFlow output type: {type(output)}. Please use numpy arrays or pandas dataframes. If you are using torch tensors, please include torch as a dependency"
                    )

            inference_response = pb_utils.InferenceResponse(output_tensors=output_tensors)
            responses.append(inference_response)

        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is optional. This function allows
        the model to perform any necessary clean-ups before exit.
        """
        print("Cleaning up...")
        del self.model
