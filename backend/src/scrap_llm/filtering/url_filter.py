from typing import List
from .filters.regex_filter import RegexURLFilter
from .filters.llm_filter import FullLLMURLFilter
import logging

logger = logging.getLogger(__name__)


class URLFilterManager:
    """
    Main class that orchestrates URL filtering using different strategies
    """

    def __init__(self, model: str, verbose: bool = False):
        self.model = model
        self.verbose = verbose

        # Initialize filters
        self.regex_filter = RegexURLFilter(model)
        self.llm_filter = FullLLMURLFilter(model)

    async def filter_urls(self, urls: List[str]) -> List[str]:
        """
        Send urls to llm filter
        """
        try:
            filtered_urls = await self.regex_filter.filter_urls(
                urls=urls,
            )

            return filtered_urls

        except Exception as error:
            logger.error(f"URL filtering failed: {error}")
            return []
