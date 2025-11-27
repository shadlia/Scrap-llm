from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    LXMLWebScrapingStrategy,
)
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP


@dataclass
class Crawl4AIContext:
    """Context for the Crawl4AI MCP server."""

    crawler: AsyncWebCrawler
    config: CrawlerRunConfig


@asynccontextmanager
async def crawl4ai_lifespan(server: FastMCP) -> AsyncIterator[Crawl4AIContext]:
    """
    Manages the Crawl4AI client lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        Crawl4AIContext: The context containing the Crawl4AI crawler
    """
    browser_config = BrowserConfig(headless=True, verbose=False)
    config = CrawlerRunConfig(
        verbose=False,
        scraping_strategy=LXMLWebScrapingStrategy(),
    )
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.__aenter__()

    try:
        yield Crawl4AIContext(
            crawler=crawler,
            config=config,
        )
    finally:
        await crawler.__aexit__(None, None, None)


mcp = FastMCP(
    "mcp-scrap-llm-crawling",
    description="MCP server for web crawling designed to extract product urls from a website",
    lifespan=crawl4ai_lifespan,
)


if __name__ == "__main__":
    mcp.run()
