from .base import BaseRetryStrategyImpl
from typing import List, Tuple, Any
from ...utils.utils import trim_domain
import logging

logger = logging.getLogger(__name__)


class ExternalAPIRetry(BaseRetryStrategyImpl):
    async def retry_failed_urls(
        self, failed_urls: List[str], save_path: str
    ) -> List[str]:
        logger.warning("External API retry not implemented yet")
        return failed_urls

    async def retry(
        self, failed_urls: List[str]
    ) -> Tuple[List[str], List[str], List[Any]]:
        """
        Retry failed URLs using external API strategy.
        """
        save_path = "./result/" + trim_domain(self.domain)
        still_failed_urls = await self.retry_failed_urls(failed_urls, save_path)
        successful_urls = [url for url in failed_urls if url not in still_failed_urls]
        return successful_urls, still_failed_urls, []
