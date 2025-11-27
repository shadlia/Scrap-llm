from enum import Enum


# --- Types/Enums ---
class LLMAction(str, Enum):
    EXTRACTION = "extraction"
    FILTERING = "filtering"
    EXTRACTING_CHAT = "extracting_chat"
    FILTERING_REGEX_CHAT = "filtering_regex_chat"
    FILTERING_LLM_CHAT = "filtering_llm_chat"
    CATALOG_FILTERING_CHAT = "catalog_filtering_chat"
    LLM_EVALUATION_EXTRACTION = "LLM_EVALUATION_EXTRACTION"
    TRIM_HTML = "trim_html"


# --- Config/Constants ---
PROVIDER_MODELS = {
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-3.5",
        "gpt-4.1",
        "gpt-4.1-mini",
        "ft:gpt-4.1-mini-2025-04-14:choose:10-samples:BXrWEC3a",
    ],
    "gemini": [
        "gemini-1.5-flash",
        "gemini-2.0-flash-001",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite-preview-06-17",
    ],
    "anthropic": [
        "claude-3-opus-20240229",
        "claude-3-5-sonnet-2024062",
        "claude-3-5-haiku-20241022",
    ],
    "local": ["deepseek-r1:14b", "qwen2.5:14b"],
}

MODEL_TO_PROVIDER = {
    model: provider for provider, models in PROVIDER_MODELS.items() for model in models
}
