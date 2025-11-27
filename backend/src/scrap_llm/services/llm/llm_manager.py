from langchain_openai import ChatOpenAI
from ..langfuse.langfuseService import LangfuseConfig
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache
from langchain_ollama import ChatOllama
from .config import LLMAction
from langchain_core.messages import SystemMessage, HumanMessage
from .config import MODEL_TO_PROVIDER

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class LLMManager:
    def __init__(
        self,
        models,
        prompt_args,
        action: str,
        output_schema=None,
    ):
        self.action = LLMAction(action)
        self.models = models
        self.prompt_args = prompt_args
        self.output_schema = output_schema

        set_llm_cache(InMemoryCache())

    def format_prompt(self, system_content) -> List:
        """Return correctly typed list of LangChain messages."""
        return [
            SystemMessage(content=system_content),
            HumanMessage(content=self.prompt_args),
        ]

    def call_llm(
        self,
        trace_id=None,
    ) -> Dict[str, Any]:
        """
        Try each model in order until one succeeds. Returns the first successful response or None.
        """
        for model_name in self.models:
            provider = MODEL_TO_PROVIDER.get(model_name)
            if provider is None:
                raise ValueError(
                    f"Model {model_name} not supported. Available models: {list(MODEL_TO_PROVIDER.keys())}"
                )
            response = self.execute_llm(provider, model_name, trace_id)
            if response is not None:
                return response
            logger.warning(f"{model_name} failed, trying next model...")
        logger.critical("All models failed")
        return None

    def execute_llm(self, provider, model_name, trace_id=None):
        """
        Instantiate and run the model for the given provider and name. Optionally include trace_id in config.
        """
        if provider == "openai":
            model = ChatOpenAI(model_name=model_name, name=model_name)
        elif provider == "anthropic":
            model = ChatAnthropic(model=model_name, name=model_name)
        elif provider == "gemini":
            model = ChatGoogleGenerativeAI(
                api_key=os.getenv("GOOGLE_API_KEY"),
                model=model_name,
                name=model_name,
                temperature=0.0,
            )
        elif provider == "local":
            model = ChatOllama(model=model_name, name=model_name, temperature=0.0)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        langfuse = LangfuseConfig(
            self.action.value, trace_name=f"{self.action.value}_{model.name}"
        )
        prompt_obj = langfuse.get_prompt(self.action.value, label="production")
        system_content = prompt_obj.prompt[0]["content"]

        prompt = self.format_prompt(system_content)
        if self.output_schema:
            if isinstance(model, ChatOpenAI):
                model = model.with_structured_output(
                    self.output_schema, method="function_calling"
                )
            else:
                model = model.with_structured_output(self.output_schema)
        try:
            config = {
                "callbacks": [langfuse._initialize_with_langchain()],
                "metadata": {
                    "prompt_id": getattr(prompt_obj, "id", None),
                    "prompt_version": getattr(prompt_obj, "version", None),
                    "prompt_label": "production",
                },
            }

            if trace_id is not None:
                config["run_id"] = trace_id

            response = model.invoke(
                prompt,
                config=config,
            )
        except Exception as e:
            logger.error(f"💥 Error from {model.name}: {str(e)}")
            return None

        if response is None:
            return None
        return {"response": response}
