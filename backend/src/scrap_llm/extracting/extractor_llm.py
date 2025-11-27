import time
from dotenv import load_dotenv
import asyncio

from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    LXMLWebScrapingStrategy,
    RateLimiter,
)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.async_crawler_strategy import (
    AsyncHTTPCrawlerStrategy,
)
from ..services.llm.llm_manager import LLMManager
from ..config import prompts as prompts
from ..utils.utils import (
    clean_html,
    format_prices,
)
from ..config.schemas import Productv2, Products
from ..config.crawl import http_crawler_config
from ..services.langfuse.langfuseService import LangfuseConfig
from .retry_strategies.rate_limiter import RateLimiterRetry
from .retry_strategies.playwright import PlaywrightRetry
from .retry_strategies.external_api import ExternalAPIRetry
import logging
from ..services.notifications.service import NotificationService

logger = logging.getLogger(__name__)
load_dotenv()


class ExtractorLLM:
    def __init__(
        self,
        models: dict[str] | str,
        domain,
        product_urls: list[str],
        client_id: str = None,
    ):
        self.models = models
        self.domain = domain
        self.product_urls = product_urls
        self.langfuse = LangfuseConfig("extraction")
        self.products = []
        self.failed_urls = []
        self.index = 0
        self.prompt = self.langfuse.get_prompt(
            "extraction", label="latest"
        ).get_langchain_prompt()
        self.client_id = client_id
        self.notification_service = (
            NotificationService(client_id) if client_id else None
        )

    async def extract(self):
        total_urls = len(self.product_urls)
        self.failed_urls = []
        start_time = time.time()
        logger.info(f"Starting product extraction for {total_urls} URLs")

        try:
            run_config = CrawlerRunConfig(
                scraping_strategy=LXMLWebScrapingStrategy(),
                verbose=True,
            )
            dispatcher = MemoryAdaptiveDispatcher(
                memory_threshold_percent=70.0,
                check_interval=5,
                max_session_permit=30,
                rate_limiter=RateLimiter(
                    base_delay=(0.4, 0.8), max_delay=5.0, max_retries=2
                ),
            )

            async with AsyncWebCrawler(
                crawler_strategy=AsyncHTTPCrawlerStrategy(
                    browser_config=http_crawler_config
                )
            ) as crawler:
                products_set = set(self.product_urls)

                results = await crawler.arun_many(
                    urls=products_set,
                    config=run_config,
                    dispatcher=dispatcher,
                )

                sem = asyncio.Semaphore(5)
                tasks = []

                for result in results:
                    tasks.append(asyncio.create_task(self.process_product(result, sem)))

                await asyncio.gather(*tasks)

            if self.failed_urls:
                logger.warning(
                    f"Found {len(self.failed_urls)} failed URLs, starting retry process"
                )
                logger.info(f"Failed URLs: {self.failed_urls}")
                retry_strategies = [
                    RateLimiterRetry(self.domain, self.models),
                    PlaywrightRetry(self.domain, self.models),
                    ExternalAPIRetry(self.domain, self.models),
                ]

                for strategy in retry_strategies:
                    if len(self.failed_urls) == 0:
                        break

                    logger.info(f"Attempting retry with {strategy.__class__.__name__}")
                    successful_urls, self.failed_urls, products = await strategy.retry(
                        self.failed_urls
                    )
                    products = [self.format_product(product) for product in products]
                    self.products.extend(products)
                    logger.info(
                        f"Retry completed. Success: {len(successful_urls)}, Still failed: {len(self.failed_urls)}"
                    )

            logger.info("Product extraction completed successfully")
            if self.notification_service:
                await self.notification_service.send_completion_notification(
                    time.time() - start_time
                )

            end_time = time.time()
            logger.info(f"Total time taken: {end_time - start_time} seconds")
            return self.products

        except Exception as e:
            logger.critical(
                f"Critical error during product extraction: {str(e)}", exc_info=True
            )
            raise

    async def extract_product_data(self, cleaned_html):
        try:
            llm_manager = LLMManager(
                self.models,
                cleaned_html,
                "extracting_chat",
                Products,
            )
            logger.info("Starting product information extraction with LLM")

            # Run LLM extraction in a separate thread since call_llm() is synchronous
            llm_response = await asyncio.to_thread(llm_manager.call_llm)
            if not llm_response:
                logger.error("No response from LLM")
                return None
            response = llm_response.get("response")
            logger.info("Successfully extracted product information")
            return response
        except Exception as e:
            logger.error(
                f"Failed to extract product information: {str(e)}", exc_info=True
            )

    async def process_product(self, result, sem):
        if not result.success:
            self.failed_urls.append(result.url)
            logger.warning(f"Failed to process URL: {result.url}")
            return
        async with sem:
            try:
                current_url = result.url

                progress = int((self.index) / len(self.product_urls) * 100)
                await self.send_progress_update(progress, current_url)

                logger.info(f"Processing product from URL: {current_url}")
                print(f"Processing product from URL: {current_url}")

                cleaned_html = clean_html(result.html)
                logger.debug(f"Cleaned HTML length: {len(cleaned_html)}")

                products = await self.extract_product_data(cleaned_html)

                if not products:
                    self.failed_urls.append(current_url)
                    logger.error(f"No products found for URL: {current_url}")
                    return None

                for product in products.variants:
                    # Check if product name is None or empty string
                    product_name = getattr(product, "product_name", None)
                    if product_name is None or product_name == "":
                        self.failed_urls.append(current_url)
                        logger.error(f"Product name is missing for URL: {current_url}")
                        return None

                    product.url = current_url

                    if self.notification_service:
                        await self.send_progress_product_done(product)

                    self.products.append(self.format_product(product))
                    logger.info(
                        f"Successfully processed product: {product.product_name}"
                    )
                self.index += 1

                return current_url

            except Exception as e:
                logger.error(f"Error processing product: {str(e)}", exc_info=True)
                return None

    def format_product(self, product: Productv2):
        if hasattr(product, "product_currency") and product.product_currency:
            currency = product.product_currency
        else:
            currency = "EUR"

        if (
            hasattr(product, "product_public_price_ttc")
            and product.product_public_price_ttc
        ):
            product.product_public_price_ttc = format_prices(
                product.product_public_price_ttc, currency
            )
        if (
            hasattr(product, "product_price_after_discount_ttc")
            and product.product_price_after_discount_ttc
        ):
            product.product_price_after_discount_ttc = format_prices(
                product.product_price_after_discount_ttc, currency
            )

        return product

    async def send_progress_update(
        self,
        progress: int,
        current_url: str,
    ):
        """Send progress update through Fastly"""
        if self.notification_service:
            await self.notification_service.send_progress_update(progress, current_url)

    async def send_progress_product_done(self, product: Productv2):
        """Send product completion through Fastly"""
        if self.notification_service:
            await self.notification_service.send_product_done(product.model_dump())

    async def extract_single_product(self, url: str) -> Products | None:
        """Crawl a single product page and extract information using LLM."""
        print(f"Starting extraction for single product: {url}")
        run_config = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy(),
        )
        async with AsyncWebCrawler(
            crawler_strategy=AsyncHTTPCrawlerStrategy(
                browser_config=http_crawler_config
            )
        ) as crawler:
            try:
                result = await crawler.arun(url=url, config=run_config)
                if not result.success:
                    print(f"Failed to crawl URL: {url}")
                    return await self.extract_single_product_playwright(url)

                print(f"Successfully crawled: {url}")
                cleaned_html = clean_html(result.html)
                print(f"Cleaned HTML length: {len(cleaned_html)}")

                products = await self.extract_product_data(cleaned_html)
                print(f"Products: {products}")

                # Optionally format prices and add URL if needed for downstream use
                # This part might depend on how you intend to use the output
                for product in products.variants:
                    product.url = url  # Add the URL to the product data
                    product = self.format_product(product)
                print(f"Extraction successful for: {url}")
                return products

            except Exception as e:
                print(f"Error extracting single product from {url}: {e}")
                self.failed_urls.append(url)
                return None

    async def extract_single_product_playwright(self, url: str) -> Products | None:
        print(f"Starting extraction with playwright for single product: {url}")
        run_config = CrawlerRunConfig(
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=self.verbose,
        )
        async with AsyncWebCrawler() as crawler:
            try:
                result = await crawler.arun(url=url, config=run_config)
                if not result.success:
                    print(f"Failed to crawl URL: {url}")
                    return await self.extract_single_product_external(url)

                print(f"Successfully crawled: {url}")
                cleaned_html = clean_html(result.html)
                print(f"Cleaned HTML length: {len(cleaned_html)}")

                products = await self.extract_product_infos(cleaned_html)

                # Optionally format prices and add URL if needed for downstream use
                # This part might depend on how you intend to use the output
                for product in products.variants:
                    product = self.format_product(product)
                print(f"Extraction successful for: {url}")
                return products

            except Exception as e:
                print(f"Error extracting single product from {url}: {e}")
                self.failed_urls.append(url)
                return None

    async def extract_single_product_external(self, url: str) -> Products | None:
        return None

    async def process_result(self, result, save_path, total_urls):
        try:
            if not result.success:
                logger.error(f"Failed to process URL: {result.url}")
                raise

            current_url = await asyncio.to_thread(
                self.process_product_sync, result, save_path
            )
            if current_url:
                if self.notification_service:
                    progress = int((self.index) / total_urls * 100)
                    await self.send_progress_update(progress, current_url)
            else:
                self.failed_urls.append(result.url)
            self.index += 1
        except Exception as e:
            print(e)
            self.failed_urls.append(result.url)
