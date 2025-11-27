from crawl4ai import (
    RateLimiter,
    CrawlerMonitor,
    DisplayMode,
)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import HTTPCrawlerConfig


memory_dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=90.0,  # Pause if memory exceeds this
    check_interval=5.0,  # How often to check memory
    max_session_permit=30,  # Maximum concurrent tasks
    rate_limiter=RateLimiter(  # Optional rate limiting
        base_delay=(1, 3), max_delay=15, max_retries=6
    ),
    monitor=CrawlerMonitor(),  # Optional monitoring
)


http_crawler_config = HTTPCrawlerConfig(
    method="GET",
    headers={"User-Agent": "ScrapLLM/1.0"},
    follow_redirects=True,
    verify_ssl=False,
)
