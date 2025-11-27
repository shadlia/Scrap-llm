import json
from typing import List
from ..interfaces.url_filter_strategy import URLFilterStrategy
from ...services.llm.llm_manager import LLMManager
from ...config.prompts import FILTERING_LLM_CHAT_PROMPT
import logging

logger = logging.getLogger(__name__)


class FullLLMURLFilter(URLFilterStrategy):
    """
    Filter URLs using full LLM capabilities
    """

    def __init__(self, model: str):
        self.model = model

    async def filter_urls(
        self,
        urls: List[str],
    ) -> List[str]:
        llm_manager = LLMManager([self.model], urls, FILTERING_LLM_CHAT_PROMPT)
        response = llm_manager.call_llm()

        filtered_urls = self.format_response(response.get("response").content)

        logger.info(
            f"Filtered {len(filtered_urls)} URLs from {len(urls)} total using llm"
        )

        return filtered_urls

    def format_response(self, response: str) -> List[str]:
        """Format the LLM response into a list of URLs"""
        try:
            cleaned_response = self.clean_response(response)
            parsed = json.loads(cleaned_response)

            if isinstance(parsed, list):
                if parsed and isinstance(parsed[0], dict) and "url" in parsed[0]:
                    return [item["url"] for item in parsed]
                return parsed

            return []

        except Exception as e:
            logger.error(f"Error in format_response: {str(e)}")
            logger.error(f"Raw response: {response}")
            return []
