import logging
from src.scrap_llm.extracting.extractor_llm import ExtractorLLM

logger = logging.getLogger(__name__)


async def extract_products(
    product_urls: list[str], domain: str, models: list[str], client_id: str = None
):
    """Extract product details from URLs"""
    try:
        if not product_urls:
            raise ValueError("No product URLs provided")

        extractor = ExtractorLLM(models, domain, product_urls, client_id)
        products = await extractor.extract()

        logger.info(
            f"Extracted {len(products or [])} products from {len(product_urls)} URLs"
        )
        return products or []
    except Exception as e:
        logger.error(f"Failed to extract products: {str(e)}")
        raise


async def extract_single_product(
    product_url: str, domain: str, models: list[str], verbose: bool = False
):
    """Extract single product details"""
    try:
        extractor = ExtractorLLM(
            product_urls=[product_url], domain=domain, models=models
        )
        product = await extractor.extract_single_product(url=product_url)

        logger.info(f"Extracted product from {product_url}")
        return product
    except Exception as e:
        logger.error(f"Failed to extract product from {product_url}: {str(e)}")
        raise
