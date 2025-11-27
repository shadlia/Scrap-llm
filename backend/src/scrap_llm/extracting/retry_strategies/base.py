from ...utils.utils import (
    clean_html_page_simple,
    trim_domain,
    format_prices,
)
from ...services.langfuse.langfuseService import LangfuseConfig
from ...services.llm.llm_manager import LLMManager
from ...config.schemas import Products
from ..interfaces.retry_strategy import RetryStrategyInterface

from typing import List, Tuple, Any

from ...config import prompts as prompts
import logging

logger = logging.getLogger(__name__)


class BaseRetryStrategyImpl(RetryStrategyInterface):
    def __init__(self, domain: str, models: str, format_product=None):
        self.domain = domain
        self.models = models
        self.langfuse = LangfuseConfig("extraction")
        self.verbose = True
        self.format_product = format_product

    async def retry(
        self, failed_urls: List[str]
    ) -> Tuple[List[str], List[str], List[Any]]:
        """
        Base retry implementation that should be overridden by concrete strategies.
        """
        save_path = "./result/" + trim_domain(self.domain)
        still_failed_urls = await self.retry_failed_urls(failed_urls, save_path)
        return [], still_failed_urls, []

    async def extract_product_infos(self, cleaned_html: str) -> Products:
        llm_manager = LLMManager(
            self.models,
            cleaned_html,
            prompts.EXTRACT_PRODUCT_INFO_CHAT_PROMPT,
            Products,
        )

        llm_response = llm_manager.call_llm()
        llm_response = llm_manager.call_llm()
        response = llm_response.get("response")
        return response

    async def process_product(self, result: Any, save_path: str) -> List[Any]:
        """Process a single product result"""
        try:
            if not result.success:
                logger.error(
                    f"Error processing product in retry strategy: {result.error}"
                )
                # print("Error: ", result.error)
                return None

            current_url = result.url
            # print(
            #     "---------------------------processing products for --------------:"
            #     + trim_domain(current_url)
            # )

            cleaned_html = clean_html_page_simple(result.html)
            # print("Length of cleaned HTML", len(cleaned_html))
            # print("Length of HTML", len(result.html))

            # Extract product details using the LLM
            products_response = await self.extract_product_infos(cleaned_html)

            # Save the result into the file
            products_list = []
            for product in products_response.variants:
                # Check if product name is None or empty string
                product_name = getattr(product, "product_name", None)
                if product_name is None or product_name == "":
                    logger.error(f"Product name is missing for URL: {current_url}")
                    return None
                product.url = current_url
                if self.format_product:
                    product = self.format_product(product)
                products_list.append(product)

            # print(
            #     "------------------------------------------------------------------------"
            # )
            return products_list

        except Exception as e:
            logger.error(f"Error processing product: {e}")
            return None

    async def retry_failed_urls(
        self, failed_urls: List[str], save_path: str
    ) -> List[str]:
        """
        Abstract method that should be implemented by concrete strategies.
        """
        raise NotImplementedError("Subclasses must implement retry_failed_urls")
