import logging
from redis import Redis
from google.cloud.tasks_v2 import CloudTasksClient

from app.clients.chooseBackend import ChooseBackend
from src.scrap_llm.services.invokers.invoker import TaskInvoker
from app.repositories.product_repository import ProductRepository
from app.models.DealItem import product_to_dealitem
from . import crawl, filter, extract
from app.exceptions import (
    TaskQueueException,
    ExtractionException,
    StorageException,
    BackendNotificationException,
)

logger = logging.getLogger(__name__)

# Global clients - will be set by main.py
redis_client: Redis
cloud_tasks_client: CloudTasksClient


def init_clients(redis: Redis, cloud_tasks: CloudTasksClient):
    """Initialize service clients"""
    global redis_client, cloud_tasks_client
    redis_client = redis
    cloud_tasks_client = cloud_tasks


def send_scrap_request(url: str, scrap_type: str, data_source_id: str, deal_id: str):
    """Send scraping request to task queue"""
    from app.request_schemas import GetOneProductRequest, FullPipelineRequest

    try:
        if scrap_type == "product":
            domain = url.split("/")[2]
            request = GetOneProductRequest(
                product_url=url,
                dataSourceId=data_source_id,
                domain=domain,
                dealId=deal_id,
            )
            TaskInvoker(
                cloud_tasks_client, request, "request_one_product"
            ).invoke_task()
        elif scrap_type == "website":
            request = FullPipelineRequest(
                url=url,
                skip_sitemap=False,
                filter_model="gemini-2.0-flash-001",
                filter_method="regex",
                dataSourceId=data_source_id,
                dealID=deal_id,
            )
            TaskInvoker(
                cloud_tasks_client, request, "request_full_website"
            ).invoke_task()

        logger.info(f"Queued {scrap_type} task for {url}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to send scrap request: {str(e)}")
        raise TaskQueueException(scrap_type, str(e))


async def process_single_product(
    product_url: str, domain: str, data_source_id: str, deal_id: str
):
    """Process single product and save to Redis"""
    try:
        product_data = await extract.extract_single_product(
            product_url, domain, ["gemini-2.0-flash-001", "gpt-4o-mini"]
        )

        # Save to Redis
        products_to_save = []
        if product_data.variants:
            products_to_save = [
                variant.model_dump() for variant in product_data.variants
            ]
        _save_and_notify(products_to_save, data_source_id, deal_id)
        return {"status": "success", "message": product_data}
    except Exception as e:
        logger.error(f"Failed to process product {product_url}: {str(e)}")
        raise ExtractionException(product_url, str(e))


async def process_full_website(
    url: str, data_source_id: str, deal_id: str, skip_sitemap: bool = False
):
    """Process full website pipeline"""
    try:
        # Crawl -> Filter -> Extract
        urls = await crawl.crawl_urls(url)
        filtered_urls = await filter.filter_urls(urls, method="regex")
        products = await extract.extract_products(
            filtered_urls, url, ["gemini-2.0-flash-001", "gpt-4o-mini"]
        )

        # Save to Redis
        products_to_save = [p.model_dump() for p in products]
        _save_and_notify(products_to_save, data_source_id, deal_id)

        return {"status": "success", "message": products}
    except Exception as e:
        logger.error(f"Pipeline failed for {url}: {str(e)}")
        raise ExtractionException(url, str(e))


def get_scrap_result(data_source_id: str):
    """Get results from Redis"""
    try:
        products = ProductRepository(
            data_source_id, redis_client
        ).get_products_by_datasourceid()
        deal_items = [product_to_dealitem(product) for product in products]
        return {
            "status": "success",
            "data": {"dealItems": deal_items, "dataSourceId": data_source_id},
        }
    except Exception as e:
        logger.error(f"Failed to get results: {str(e)}")
        raise StorageException("get_products_by_datasourceid", str(e))


def _save_and_notify(products: list, data_source_id: str, deal_id: str):
    """Save to Redis and notify backend"""
    try:
        print(f"Products in save and notify: {products}")
        ProductRepository(data_source_id, redis_client).set_products_by_datasourceid(
            products
        )
        ChooseBackend().deal_scrap_ready(deal_id, data_source_id)
        logger.info(f"Saved {len(products)} products and notified backend")
    except Exception as e:
        logger.error(f"Failed to save/notify: {str(e)}")
        # Try to distinguish between storage and notification errors
        if "redis" in str(e).lower():
            raise StorageException("set_products_by_datasourceid", str(e))
        else:
            raise BackendNotificationException(deal_id, str(e))
