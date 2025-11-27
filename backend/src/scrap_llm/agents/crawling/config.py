from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters
from src.scrap_llm.services.langfuse.langfuseService import LangfuseConfig

APP_NAME = "crawling_agent"
USER_ID = "choose"
SESSION_ID_TOOL_AGENT = "choose_000"
MODEL_NAME = "gemini-2.5-flash"

try:
    PROMPT_CRAWLING_AGENT = (
        LangfuseConfig(session_id=SESSION_ID_TOOL_AGENT, trace_name="crawling_agent")
        .get_prompt("extraction_agent", label="production")
        .prompt[0]["content"]
    )
except Exception as e:
    print(f"Warning: Failed to fetch prompt from Langfuse: {e}. Using default prompt.")
    PROMPT_CRAWLING_AGENT = "You are an expert web scraper. Extract the product information from the following html page."

MCP_SERVER_CONFIG = StdioServerParameters(
    command="python3",
    args=[
        "src/mcp/crawling/server.py",
    ],
)
