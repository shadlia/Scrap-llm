from pydantic import BaseModel
from typing import List, Optional


class CrawlRequest(BaseModel):
    url: str
    skip_sitemap: bool = False
    skip_trim: bool = False
    use_agent: bool = False
    use_hakrawler: bool = False


class FilterRequest(BaseModel):
    urls: List[str]
    model: str = "gemini-2.5-flash"
    method: str = "regex"  # "regex" or "llm"


class ExtractionRequest(BaseModel):
    product_urls: List[str]
    domain: str
    models: List[str] = [
        "gemini-2.0-flash-001",
        "gpt-4o-mini",
        "gemini-2.5-flash",
    ]
    client_id: Optional[str] = None


class FullPipelineRequest(BaseModel):
    url: str
    skip_sitemap: bool = False
    filter_method: str = "regex"
    filter_model: str = "gemini-2.5-pro"
    dataSourceId: str
    dealID: str


class GetOneProductRequest(BaseModel):
    product_url: str
    domain: str
    models: List[str] = ["gemini-2.0-flash-001", "gpt-4o-mini"]
    verbose: bool = False
    dataSourceId: str
    dealId: str


class ScrapRequest(BaseModel):
    dealId: str
    dataSourceId: str
    url: str
    type: str
