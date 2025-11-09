import json
import os
from typing import List

import mlflow
import numpy as np
import triton_python_backend_utils as pb_utils
import yaml


class NumpyFloatValuesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


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
        from transformers import AutoTokenizer, pipeline

        def get_automodel_class(model_config):
            model_type = model_config["flavors"]["transformers"]["instance_type"]
            if "SequenceClassification" in model_type:
                from transformers import (
                    AutoModelForSequenceClassification as AutoModelClass,
                )
            elif "TokenClassification" in model_type:
                from transformers import (
                    AutoModelForTokenClassification as AutoModelClass,
                )
            elif "QuestionAnswering" in model_type:
                from transformers import AutoModelForQuestionAnswering as AutoModelClass
            elif "TextGeneration" in model_type:
                from transformers import AutoModelForCausalLM as AutoModelClass
            elif "Summarization" in model_type:
                from transformers import AutoModelForSeq2SeqLM as AutoModelClass
            elif "Translation" in model_type:
                from transformers import AutoModelForSeq2SeqLM as AutoModelClass
            elif "Text2TextGeneration" in model_type:
                from transformers import AutoModelForSeq2SeqLM as AutoModelClass
            elif "TextClassification" in model_type:
                from transformers import (
                    AutoModelForSequenceClassification as AutoModelClass,
                )
            return AutoModelClass

        self.model_path = os.path.join(args["model_repository"], args["model_version"])

        # open model config yaml to determine loader type
        with open(os.path.join(args["model_repository"], args["model_version"], "MLmodel"), "r") as f:
            model_config = yaml.safe_load(f)

        gpu = mlflow.transformers.is_gpu_available()
        device = 0 if gpu else "cpu"
        tokenizer_path = os.path.join(self.model_path, "components/tokenizer")
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        AutoModelClass = get_automodel_class(model_config)
        model = AutoModelClass.from_pretrained(f"{self.model_path}/model/")
        # read task from model config
        task = model_config["flavors"]["transformers"]["task"]
        self.pipeline = pipeline(task, model=model, tokenizer=tokenizer, device=device)

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

            hf_input = list(inputs.values())[0].flatten().tolist()
            output = self.pipeline(hf_input)

            # transformer pipelines return a list of objects of variable structure, depending on the task (i.e. list of dicts, list of lists, etc.)
            # To support dynamic batch sizes, we can only support a single output tensor which will be called "output0"
            output_name = "output0"
            output_list = list()
            for member in output:
                output_list.append(json.dumps(member, cls=NumpyFloatValuesEncoder))

            output_tensors = [pb_utils.Tensor(output_name, np.array(output_list, dtype=object))]
            inference_response = pb_utils.InferenceResponse(output_tensors=output_tensors)
            responses.append(inference_response)

        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is optional. This function allows
        the model to perform any necessary clean-ups before exit.
        """
        print("Cleaning up...")
        del self.pipeline
