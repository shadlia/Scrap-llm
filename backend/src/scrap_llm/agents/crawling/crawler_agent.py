import asyncio
import json

from google.adk.agents import Agent

from dotenv import load_dotenv
from .schema import UrlInput
from .config import (
    MODEL_NAME,
    PROMPT_CRAWLING_AGENT,
    MCP_SERVER_CONFIG,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from .callbacks import clean_output
from .config import APP_NAME, USER_ID, SESSION_ID_TOOL_AGENT
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


class CrawlingAgent:
    def __init__(self, domain: str, agent, exit_stack):
        self.domain = domain
        self.agent = agent
        self.exit_stack = exit_stack

    @classmethod
    async def create(cls, domain: str):
        agent, exit_stack = await cls._create_agent()
        return cls(domain, agent, exit_stack)

    @staticmethod
    async def _create_agent():
        # get tools from mcp server
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=MCP_SERVER_CONFIG
        )
        print("PROMPT_CRAWLING_AGENT", PROMPT_CRAWLING_AGENT)
        crawling_agent_with_tool = Agent(
            model=MODEL_NAME,
            name="crawling_agent",
            description="Retrieves all the product urls from a e-commerce shop using the set of tools.",
            instruction=PROMPT_CRAWLING_AGENT,
            tools=tools,
            input_schema=UrlInput,
            output_key="product_urls_result",
        )
        return crawling_agent_with_tool, exit_stack

    async def _close(self):
        await self.exit_stack.aclose()

    async def run_crawling_agent(
        self,
    ) -> list[str]:

        session_service = InMemorySessionService()

        session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_TOOL_AGENT
        )

        crawling_runner = Runner(
            agent=self.agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        stored_output = await self.call_agent_and_print(
            crawling_runner,
            self.agent,
            SESSION_ID_TOOL_AGENT,
            f'{{"url": "{self.domain}"}}',
            session_service,
        )
        await self.exit_stack.aclose()
        print("stored_output: ", stored_output)
        return stored_output

    @staticmethod
    async def call_agent_and_print(
        runner_instance: Runner,
        agent_instance: LlmAgent,
        session_id: str,
        query_json: str,
        session_service: InMemorySessionService,
    ):
        """Sends a query to the specified agent/runner and prints results."""
        print("\n" + "=" * 50)
        print(f"🤖 Starting Agent: '{agent_instance.name}'")
        print(f"📝 Query: {query_json}")
        print("=" * 50)

        user_content = types.Content(role="user", parts=[types.Part(text=query_json)])

        final_response_content = "No final response received."
        print("\n🔄 Starting Agent Execution...")
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session_id, new_message=user_content
        ):
            # if event.content.parts[0].function_call:
            #     print(
            #         f"Function called: {event.content.parts[0].function_call.name}, with args: {event.content.parts[0].function_call.args}"
            #     )
            # elif event.content.parts[0].function_response:
            #     print(
            #         f"Function responded: {event.content.parts[0].function_response.name}, with response: {event.content.parts[0].function_response.response}"
            #     )
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

        current_session = session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        stored_output = current_session.state.get(agent_instance.output_key)

        # print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
        try:
            # Attempt to parse and pretty print if it's JSON
            parsed_output = json.loads(stored_output)
            print(json.dumps(parsed_output, indent=2))
        except (json.JSONDecodeError, TypeError):
            # Otherwise, print as string
            print(stored_output)
        print("-" * 30)
        return stored_output
