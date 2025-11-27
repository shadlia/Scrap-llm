import requests
import re
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from furl import furl
from bs4 import BeautifulSoup
import logging
# from ..agents.crawling.crawler_agent import CrawlingAgent
import os

logger = logging.getLogger(__name__)


class URLCrawler:
    def __init__(self, domain):
        self.domain = domain

    async def run(self):
        """Main entry point for URL discovery"""
        self.domain = self.clean_url(self.domain)

        # Discover sitemap URLs from both sitemap.xml and robots.txt
        sitemap_urls = await self.discover_sitemaps()

        if not sitemap_urls:
            logger.warning("No sitemaps found")
            logger.warning("No sitemaps found and AgentCrawler is disabled.")
            return []
            # return await AgentCrawler(self.domain).run()

        # Fetch and parse all discovered sitemaps
        all_urls = await self.fetch_and_parse_sitemaps(sitemap_urls)

        logger.info(f"Found {len(all_urls)} URLs.")
        return all_urls

    def clean_url(self, url):
        """Clean and normalize the domain URL"""
        f = furl(url)
        return f.origin + "/"

    async def discover_sitemaps(self):
        """Discover sitemap URLs from both sitemap.xml and robots.txt"""
        sitemap_urls = []

        # Try direct sitemap.xml first
        sitemap_url = self.domain + "sitemap.xml"
        try:
            request = requests.get(sitemap_url)
            if request.status_code == 200 and request.text.startswith("<?xml"):
                sitemap_urls.append(sitemap_url)
            else:
                # Try fallback method
                response = await self.fetch_fallback(sitemap_url)
                if response:
                    sitemap_urls.append(sitemap_url)
        except Exception as e:
            logger.warning(f"Failed to check sitemap.xml: {e}")

        # Try robots.txt if no direct sitemap found
        if not sitemap_urls:
            robot_url = self.domain + "robots.txt"
            try:
                response = requests.get(robot_url)
                if response.status_code != 200:
                    response = await self.fetch_fallback(robot_url)

                if response and hasattr(response, "text"):
                    newline_regex = r"\r\n|\r|\n"
                    lines = re.split(newline_regex, response.text)
                    for line in lines:
                        if line.startswith("Sitemap:"):
                            sitemap_url = line.split(" ")[1]
                            sitemap_urls.append(sitemap_url)

            except Exception as e:
                logger.warning(f"Failed to fetch robots.txt: {e}")

        return list(set(sitemap_urls))  # Remove duplicates

    async def fetch_and_parse_sitemaps(self, sitemap_urls):
        """Fetch and parse all sitemap URLs to extract page URLs"""
        all_urls = set()
        sitemap_queue = list(sitemap_urls)

        while sitemap_queue:
            current_sitemap = sitemap_queue.pop(0)

            # Fetch sitemap content
            try:
                response = requests.get(current_sitemap, timeout=30)
                if response.status_code == 200:
                    xml_content = response.content
                    logger.info(f"Sitemap fetched successfully: {current_sitemap}")
                else:
                    xml_content = await self.fetch_fallback(current_sitemap)

                if xml_content is None:
                    logger.warning(f"Failed to fetch sitemap: {current_sitemap}")
                    continue

            except Exception as e:
                logger.error(f"Failed to fetch sitemap {current_sitemap}: {e}")
                xml_content = await self.fetch_fallback(current_sitemap)
                if xml_content is None:
                    continue

            # Parse sitemap content
            try:
                soup = BeautifulSoup(xml_content, features="xml")

                # Check if it's a sitemap index by looking for <sitemap> tags
                sitemap_tags = soup.find_all("sitemap")
                if sitemap_tags:
                    # It's a sitemap index - add nested sitemaps to queue
                    for sitemap in sitemap_tags:
                        loc = sitemap.find("loc")
                        if loc is not None and loc.text:
                            sitemap_queue.append(loc.text.strip())
                else:
                    # It's a regular sitemap with URLs
                    url_tags = soup.find_all("url")
                    for url in url_tags:
                        loc = url.find("loc")
                        if loc is not None and loc.text:
                            all_urls.add(loc.text.strip())

            except Exception as e:
                logger.error(f"Failed to parse sitemap {current_sitemap}: {e}")
                continue

        return list(all_urls)

    async def fetch_fallback(self, url):
        """Fallback method using AsyncWebCrawler for blocked requests"""
        config = CrawlerRunConfig(
            magic=True,
            verbose=True,
        )
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=config)
                if not result.success:
                    logger.warning(f"Failed to fetch URL with fallback: {url}")
                    return None
                return result.html
        except Exception as e:
            logger.error(f"Fallback fetch failed for {url}: {e}")
            return None


""" class AgentCrawler:
    def __init__(self, domain):
        self.domain = domain

    async def run(self):
        print("Running agent crawler")
        agent = await CrawlingAgent.create(self.domain)
        urls = await agent.run_crawling_agent()
        await agent._close()
        urls_cleaned = self.extract_urls_dict(urls)
        print("URLS:", urls_cleaned)
        return urls_cleaned

    def extract_urls_dict(self, raw_response: str) -> list:
        # Remove code block markers and possible leading/trailing whitespace
        cleaned = raw_response.strip()
        cleaned = re.sub(r"^(```json|```|'''json|''')\s*", "", cleaned)
        cleaned = re.sub(r"(```|''')\s*$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            urls = data.get("urls", [])
            return urls
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
 """

class Hakrawler:
    """Client for the hakrawler Go service API"""

    def __init__(self, domain):
        self.domain = domain
        if os.getenv("LOCAL_DEV") == "docker":
            self.hakrawler_url = "http://host.docker.internal:8081/"
        elif os.getenv("LOCAL_DEV") == "local":
            self.hakrawler_url = "http://127.0.0.1:8081/"
        else:
            self.hakrawler_url = (
                "https://europe-west1-choose-vp-dev.cloudfunctions.net/hakrawler"
            )

        # File extensions to filter out (obvious non-product pages)
        self.excluded_extensions = {
            # Document files
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            # Image files
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".webp",
            ".ico",
            ".tiff",
            ".tif",
            # Video files
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".mkv",
            ".m4v",
            ".3gp",
            # Audio files
            ".mp3",
            ".wav",
            ".ogg",
            ".aac",
            ".flac",
            ".wma",
            ".m4a",
            # Archive files
            ".zip",
            ".rar",
            ".tar",
            ".gz",
            ".7z",
            ".bz2",
            ".xz",
            # Code/config files
            ".js",
            ".css",
            ".xml",
            ".json",
            ".yml",
            ".yaml",
            ".ini",
            ".cfg",
            # Application files
            ".exe",
            ".dmg",
            ".pkg",
            ".deb",
            ".rpm",
            ".msi",
            ".app",
            # Other files
            ".bin",
            ".iso",
            ".img",
            ".log",
            ".tmp",
            ".bak",
        }

    def filter_urls(self, urls):
        """
        Filter out URLs that are obviously not product pages based on file extensions

        Args:
            urls (list): List of URLs to filter

        Returns:
            list: Filtered list of URLs
        """
        if not urls:
            return []

        filtered_urls = []

        for url in urls:
            # Extract the path part of the URL and get the extension
            try:
                from urllib.parse import urlparse

                parsed_url = urlparse(url)
                path = parsed_url.path.lower()

                # Check if the path ends with any excluded extension
                has_excluded_extension = any(
                    path.endswith(ext) for ext in self.excluded_extensions
                )

                if not has_excluded_extension:
                    filtered_urls.append(url)

            except Exception as e:
                # If there's an error parsing the URL, include it to be safe
                logger.warning(f"Error parsing URL {url}: {e}")
                filtered_urls.append(url)

        return filtered_urls

    async def run(self):
        """
        Crawl a domain using the hakrawler service

        Returns:
            list: List of discovered URLs
        """
        payload = {
            "url": self.domain,
        }

        try:
            response = requests.post(
                f"{self.hakrawler_url}/crawl",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,  # Give enough time for the crawling to complete
            )

            if response.status_code == 200:
                data = response.json()
                urls = data.get("urls", [])
                # Handle case where hakrawler returns null urls
                if urls is None:
                    urls = []

                logger.info(f"Hakrawler found {len(urls)} raw URLs for {self.domain}")

                # Filter out non-product URLs
                filtered_urls = self.filter_urls(urls)

                logger.info(
                    f"After filtering: {len(filtered_urls)} URLs remaining for {self.domain}"
                )
                return filtered_urls
            else:
                logger.error(
                    f"Hakrawler API error {response.status_code}: {response.text}"
                )
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to hakrawler service: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from hakrawler: {e}")
            return []
