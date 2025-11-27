import logging
from src.scrap_llm.crawling.urls_crawler import URLCrawler, Hakrawler

logger = logging.getLogger(__name__)


async def crawl_urls(
    url: str, use_agent: bool = False, use_hakrawler: bool = False
) -> list[str]:
    """Crawl a website to fetch all URLs"""
    try:
        if use_agent:
            crawler = AgentCrawler(url)
        elif use_hakrawler:
            crawler = Hakrawler(url)
        else:
            crawler = URLCrawler(url)

        urls = await crawler.run()
        logger.info(f"Found {len(urls)} URLs from {url}")
        return urls
    except Exception as e:
        logger.error(f"Failed to crawl {url}: {str(e)}")
        raise
