from abc import ABC, abstractmethod
from typing import List, Dict, Union


class URLFilterStrategy(ABC):
    """
    Abstract base class defining the interface for URL filtering strategies.
    """

    @abstractmethod
    async def filter_urls(
        self,
        urls: List[str],
    ) -> List[str]:
        """
        Filter a list of URLs using a specific strategy.

        Args:
            urls: List of URLs to filter
            total_usage_metrics: Dictionary to track usage metrics
            prompt_name: Name of the prompt to use
            langfuse_config: LangfuseConfig instance
            model: The LLM model to use
            verbose: Whether to print verbose output
            batch_size: Size of batches for filtering

        Returns:
            List of filtered URLs
        """
        pass

    @abstractmethod
    def format_response(self, response: str) -> Union[str, List[str]]:
        """
        Format the raw response from the filter.

        Args:
            response: Raw response string

        Returns:
            Formatted response
        """
        pass

    def clean_response(self, response: str) -> str:
        """
        Utility method to clean responses.

        Args:
            response: Response string that might contain code blocks

        Returns:
            Cleaned response string
        """
        if not response:
            return ""

        # Remove code block markers if present
        if response.startswith("```"):
            response = response.replace("```json", "", 1)
            response = response.replace("```regex", "", 1)
            if response.endswith("```"):
                response = response.rsplit("```", 1)[0]

        return response.strip().strip("`")
