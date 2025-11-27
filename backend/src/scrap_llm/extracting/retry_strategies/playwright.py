from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    RateLimiter,
    CrawlerMonitor,
    DisplayMode,
    LXMLWebScrapingStrategy,
)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from ...config.crawl import http_crawler_config
from ...utils.utils import trim_domain
from .base import BaseRetryStrategyImpl
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class PlaywrightRetry(BaseRetryStrategyImpl):
    async def retry_failed_urls(
        self, failed_urls: List[str], save_path: str
    ) -> tuple[list[str], list[Any]]:
        logger.info(f"Retrying failed URLs with playwright: {len(failed_urls)}")
        still_failed_urls = []
        successful_products = []

        run_config = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True,
            stream=True,
        )
        dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=90.0,
            check_interval=5,
            max_session_permit=20,
            rate_limiter=RateLimiter(base_delay=(1, 2), max_delay=15, max_retries=3),
        )

        async with AsyncWebCrawler() as crawler:
            async for result in await crawler.arun_many(
                urls=failed_urls, config=run_config, dispatcher=dispatcher
            ):
                if not result.success:
                    logger.warning(f"Failed to fetch URL with playwright: {result.url}")
                    still_failed_urls.append(result.url)
                    continue
                products = await self.process_product(result, save_path)
                if not products:
                    logger.warning(
                        f"Failed to process URL with playwright: {result.url}"
                    )
                    still_failed_urls.append(result.url)
                else:
                    successful_products.extend(products)

        return still_failed_urls, successful_products

    async def retry(
        self, failed_urls: List[str]
    ) -> Tuple[List[str], List[str], List[Any]]:
        """
        Retry failed URLs using playwright strategy.
        """
        save_path = "./result/" + trim_domain(self.domain)
        still_failed_urls, successful_products = await self.retry_failed_urls(
            failed_urls, save_path
        )
        successful_urls = [url for url in failed_urls if url not in still_failed_urls]
        return successful_urls, still_failed_urls, successful_products
