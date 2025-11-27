import re
from bs4 import BeautifulSoup
from mcp.server.fastmcp import Context
from furl import furl

# Import the mcp instance from server.py in the same directory
from server import mcp


def clean_url(url):
    f = furl(url)
    return f.origin + "/"


# @mcp.tool()
# async def get_html(ctx: Context, url: str) -> str:
#     """Get the HTML content of a website"""
#     crawler = ctx.request_context.lifespan_context.crawler
#     config = ctx.request_context.lifespan_context.config
#     result = await crawler.arun(url, config)
#     if not result.success:
#         return f"Error fetching {url}"
#     return result.html


@mcp.tool()
async def get_all_links(ctx: Context, url: str) -> list[str]:
    """Get all links from a website"""
    urls = []
    crawler = ctx.request_context.lifespan_context.crawler
    config = ctx.request_context.lifespan_context.config
    result = await crawler.arun(url, config)
    if not result.success:
        return [f"Error fetching {url}"]

    for link in result.links["internal"]:
        urls.append(link["href"])
    return urls


@mcp.tool()
async def get_sitemap_urls(ctx: Context, url: str) -> list[str]:
    """Get all origin sitemap urls from the homepage of a website"""
    sitemap_urls = set()
    crawler = ctx.request_context.lifespan_context.crawler
    config = ctx.request_context.lifespan_context.config
    result = await crawler.arun(clean_url(url) + "robots.txt", config)
    if not result.success:
        return [f"Error fetching {url}"]
    html = result.html
    newline_regex = r"\r\n|\r|\n"
    lines = re.split(newline_regex, html)
    for line in lines:
        if line.startswith("Sitemap:"):
            sitemap_url = line.split(" ")[1]
            sitemap_urls.add(sitemap_url)
    if len(sitemap_urls) == 0:
        result = await crawler.arun(clean_url(url) + "sitemap.xml", config)
        if not result.success:
            return [f"No sitemap urls found for {url}"]
        return [clean_url(url) + "sitemap.xml"]

    return list(sitemap_urls)


@mcp.tool()
async def parse_sitemap(ctx: Context, url: str) -> list[str]:
    """Parse a sitemap url and return all urls in the sitemap"""
    crawler = ctx.request_context.lifespan_context.crawler
    config = ctx.request_context.lifespan_context.config
    result = await crawler.arun(url, config)
    if not result.success:
        return [f"Error fetching {url}"]
    xml_content = result.html
    soup = BeautifulSoup(xml_content, features="xml")

    urls = []

    # Check if it's a sitemap index by looking for <sitemap> tags
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags:
        # It's a sitemap index
        for sitemap in sitemap_tags:
            loc = sitemap.find("loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
    else:
        # It's a regular sitemap with URLs
        url_tags = soup.find_all("url")
        for (
            url_tag
        ) in url_tags:  # Renamed variable to avoid conflict with outer scope 'url'
            loc = url_tag.find("loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())

    return urls
