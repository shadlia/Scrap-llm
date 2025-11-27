from typing import Dict, Any
from fastapi import APIRouter

from app.request_schemas import (
    CrawlRequest,
    FilterRequest,
    ExtractionRequest,
    ScrapRequest,
    GetOneProductRequest,
    FullPipelineRequest,
)
from app.services import crawl, filter, extract, scrap
from app.exceptions import (
    StorageException,
    EmptyResultException,
    ValidationException,
)

router = APIRouter()


@router.post("/crawl", response_model=Dict[str, Any])
async def crawl_url(request: CrawlRequest):
    """Crawl a website to fetch all URLs"""
    if not request.url:
        raise ValidationException("URL is required")

    urls = await crawl.crawl_urls(request.url, request.use_agent, request.use_hakrawler)
    if not urls:
        raise EmptyResultException(f"No URLs found for {request.url}")

    return {
        "status": "success",
        "message": f"Found {len(urls)} URLs",
        "urls": urls,
    }


@router.post("/filter", response_model=Dict[str, Any])
async def filter_urls(request: FilterRequest):
    """Filter URLs to identify product URLs"""
    if not request.urls:
        raise ValidationException("URLs list cannot be empty")

    filtered = await filter.filter_urls(request.urls, request.model, request.method)
    if not filtered:
        raise EmptyResultException("No product URLs found in the provided URLs")

    return {
        "status": "success",
        "message": f"Found {len(filtered)} product URLs out of {len(request.urls)} URLs",
        "product_urls": filtered,
    }


@router.post("/extract", response_model=Dict[str, Any])
async def extract_products(request: ExtractionRequest):
    """Extract product details from product URLs"""
    if not request.product_urls:
        raise ValidationException("Product URLs list cannot be empty")
    if not request.domain:
        raise ValidationException("Domain is required")

    products = await extract.extract_products(
        request.product_urls, request.domain, request.models, request.client_id
    )
    if not products:
        raise EmptyResultException(
            f"No products extracted from {len(request.product_urls)} URLs"
        )

    return {
        "status": "success",
        "message": f"Successfully extracted product details from {len(request.product_urls)} URLs",
        "domain": request.domain,
        "products": products,
    }


@router.post("/api/send-scrap-request", response_model=Dict[str, Any])
async def send_scrap_request(request: ScrapRequest):
    """Send scraping request to task queue"""
    if (
        not request.url
        or not request.type
        or not request.dataSourceId
        or not request.dealId
    ):
        raise ValidationException("URL, type, dataSourceId, and dealId are required")

    result = scrap.send_scrap_request(
        request.url, request.type, request.dataSourceId, request.dealId
    )
    return result


@router.post("/request_one_product", response_model=Dict[str, Any])
async def request_one_product(request: GetOneProductRequest):
    """Process single product extraction"""
    if not request.product_url or not request.domain:
        raise ValidationException("Product URL and domain are required")

    result = await scrap.process_single_product(
        request.product_url, request.domain, request.dataSourceId, request.dealId
    )
    return result


@router.post("/request_full_website", response_model=Dict[str, Any])
async def request_full_website(request: FullPipelineRequest):
    """Process full website pipeline"""
    if not request.url or not request.dataSourceId or not request.dealID:
        raise ValidationException("URL, dataSourceId, and dealID are required")

    result = await scrap.process_full_website(
        request.url, request.dataSourceId, request.dealID, request.skip_sitemap
    )
    return result


@router.get("/api/get-scrap-result/{dataSourceId}", response_model=Dict[str, Any])
async def get_scrap_result(dataSourceId: str):
    """Get scraping results from Redis"""
    if not dataSourceId:
        raise ValidationException("dataSourceId is required")

    try:
        result = scrap.get_scrap_result(dataSourceId)
        return result
    except StorageException as e:
        if "No items found" in str(e.message):
            raise EmptyResultException(
                f"No results found for dataSourceId: {dataSourceId}"
            )
        raise
