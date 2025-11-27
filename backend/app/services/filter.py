import logging
from src.scrap_llm.filtering.url_filter import URLFilterManager

logger = logging.getLogger(__name__)


async def filter_urls(
    urls: list[str],
    model: str = "gemini-2.5-flash",
    method: str = "regex",
) -> list[str]:
    """Filter URLs to identify product URLs"""
    try:
        url_filter = URLFilterManager(model)

        if method.lower() == "regex":
            filtered = await url_filter.regex_filter.filter_urls(urls=urls)
            # Fallback to LLM if regex returns no results
            if not filtered:
                filtered = await url_filter.llm_filter.filter_urls(urls)
        else:
            filtered = await url_filter.llm_filter.filter_urls(urls)

        logger.info(f"Filtered {len(filtered)} URLs from {len(urls)}")
        return filtered
    except Exception as e:
        logger.error(f"Failed to filter URLs: {str(e)}")
        raise
