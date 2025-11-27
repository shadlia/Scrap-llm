from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from ...config.schemas import Products


class RetryStrategyInterface(ABC):
    """
    Abstract base class defining the interface for retry strategies.
    """

    @abstractmethod
    async def retry(
        self, failed_urls: List[str]
    ) -> Tuple[List[str], List[str], List[Any]]:
        """
        Retry failed URLs using a specific strategy.

        Args:
            failed_urls: List of URLs that failed in previous attempts

        Returns:
            Tuple containing:
            - List of successfully processed URLs
            - List of URLs that still failed
            - List of successfully extracted products
        """
        pass

    @abstractmethod
    async def extract_product_infos(self, cleaned_html: str) -> Products:
        """
        Extract product information from cleaned HTML.

        Args:
            cleaned_html: Cleaned HTML content

        Returns:
            Products object containing extracted information
        """
        pass

    @abstractmethod
    async def process_product(self, result: Any, save_path: str) -> List[Any]:
        """
        Process a single product result.

        Args:
            result: Crawler result containing HTML and URL
            save_path: Path to save the results

        Returns:
            List of processed products
        """
        pass
