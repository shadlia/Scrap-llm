from langfuse.callback import CallbackHandler
from langfuse import Langfuse
import os
from dotenv import load_dotenv
import json


class LangfuseClientSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            load_dotenv()
            cls._instance = Langfuse(
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                host=os.getenv("LANGFUSE_HOST"),
                environment="dev",
            )
        return cls._instance


class LangfuseConfig:
    def __init__(self, session_id, trace_name=None):
        self.session_id = session_id
        self.trace_name = trace_name
        self.langfuse = LangfuseClientSingleton.get_instance()

    def _initialize_with_langchain(self):
        return CustomCallbackHandler(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
            session_id=self.session_id,
            environment="dev",
            trace_name=self.trace_name,
        )

    def get_prompt(self, prompt_id, label=None):
        if label:
            return self.langfuse.get_prompt(
                prompt_id,
                label=label,
            )
        return self.langfuse.get_prompt(prompt_id)


class CustomCallbackHandler(CallbackHandler):
    def _parse_model_and_log_errors(self, *, serialized, metadata, kwargs):
        """Override the main function that parses the model name and logs errors."""

        model_name = super()._parse_model_and_log_errors(
            serialized=serialized, metadata=metadata, kwargs=kwargs
        )

        if model_name and isinstance(model_name, str):
            return model_name.replace("models/", "")


class DatasetExporter:
    """
    Export dataset items to a JSONL file to fine-tune a model
    """

    def __init__(self, session_id="123"):
        self.langfuse = LangfuseConfig(session_id=session_id)

    def get_dataset_items(self, name):
        dataset = self.langfuse.langfuse.get_dataset(name)
        prompt = "Extract the product information from the following html page "
        with open(f"{name}.jsonl", "w") as f:
            for item in dataset.items:
                if len(item.input) < 50000:
                    message_obj = {
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": item.input},
                            {
                                "role": "assistant",
                                "content": json.dumps(
                                    item.expected_output, ensure_ascii=False
                                ),
                            },
                        ]
                    }
                    f.write(json.dumps(message_obj, ensure_ascii=False) + "\n")
