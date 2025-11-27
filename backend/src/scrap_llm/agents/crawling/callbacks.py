# --- Define your callback function ---
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional


def clean_output(callback_context: CallbackContext, output: dict):
    print(f"Callback running after model call for agent: {callback_context.agent_name}")
    print(f"llm_response: {output}")
    if output.content and output.content.parts:
        text_content = output.content.parts[0].text
        if text_content:
            cleaned_output = text_content.replace("```json", "").replace("```", "")
            print(f"cleaned_output: {cleaned_output}")
    return cleaned_output
