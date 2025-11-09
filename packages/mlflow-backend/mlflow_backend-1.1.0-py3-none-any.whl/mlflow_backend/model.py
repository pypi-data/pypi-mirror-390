import os
from typing import List

import triton_python_backend_utils as pb_utils
import yaml
from models import (
    MLFlowPythonModel,
    SentenceTransformersPythonModel,
    TransformersPythonModel,
)


class TritonPythonModel:
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
        with open(os.path.join(args["model_repository"], args["model_version"], "MLmodel"), "r") as f:
            mlflow_config = yaml.safe_load(f)

        flavors = tuple(mlflow_config["flavors"].keys())
        if "sentence_transformers" in flavors:
            model_class = SentenceTransformersPythonModel
        elif "transformers" in flavors:
            model_class = TransformersPythonModel
        else:
            model_class = MLFlowPythonModel

        self.model = model_class()
        self.model.initialize(args)

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
        return self.model.execute(requests)

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is optional. This function allows
        the model to perform any necessary clean-ups before exit.
        """
        self.model.finalize()
        del self.model
