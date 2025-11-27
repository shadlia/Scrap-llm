import os
import aiofiles
from bs4 import BeautifulSoup
import re
import csv
from furl import furl
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LXMLWebScrapingStrategy
from ..config.crawl import http_crawler_config


def format_prices(prices, currency):
    """
    Traite une liste ou une valeur unique de prix.
    - Si un seul prix est présent, il est formaté comme un montant.
    - Si plusieurs prix sont présents, un range est formaté.
    - Retourne une chaîne vide si la liste est vide ou une erreur survient.

    :param prices: Liste ou valeur unique de prix à formater.
    :param currency_symbol: Symbole monétaire à utiliser.
    :return: Chaîne formatée avec les prix ou un range.
    """
    if not prices:
        return ""
    if not isinstance(prices, list):
        prices = [prices]  # Convertir une valeur unique en liste
    currencies = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
    }
    try:
        cleaned_prices = []
        for price in prices:
            # Nettoyer les caractères non numériques et les espaces insécables
            price = str(price).replace("\xa0", "").replace(" ", "").strip()

            # Supprimer le symbole monétaire s'il est présent
            for symbol in ["$", "€", "£"]:
                price = price.replace(symbol, "")
            # Supprimer les symboles de devises
            for curr in ["EUR", "USD", "GBP"]:
                price = price.replace(curr, "")

            # Supprimer les signes "-" en début de chaîne
            if price.startswith("-"):
                price = price[1:].strip()

            # Gérer les formats de prix "49.-" en ajoutant les centimes manquants
            if price.endswith(".-"):
                price = price.replace(".-", ".00")

            if "," in price and "." in price:
                price = (
                    price.replace(",", "", 1)
                    if price.index(",") < price.index(".")
                    else price.replace(".", "", 1)
                )  # Supprime la 1ere virgule ou le 1er point dans 1,119.23 ou 1.119,23
            price = price.replace(
                ",", "."
            )  # Convertir les virgules restantes en points
            cleaned_prices.append(float(price))
        if len(cleaned_prices) == 1:
            return (
                f"{cleaned_prices[0]:,.2f}".replace(",", " ").replace(".", ",")
                + f" {currencies[currency]}"
            )
        return (
            f"{cleaned_prices[0]:,.2f}".replace(",", " ").replace(".", ",")
            + f" - {cleaned_prices[-1]:,.2f}".replace(",", " ").replace(".", ",")
            + f" {currencies[currency]}"
        )
    except ValueError as e:
        print(f"Erreur de formatage des prix {prices}: {e}")
        return ""


async def save_to_file(folder: str, file_name: str, content):
    if isinstance(content, list):
        content = "\n".join(map(str, content))

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file_name)
    async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
        await file.write(content)
    print(f"File saved: {file_path}")


def clean_product_page(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove <script> tags except those with type="application/ld+json" (b4 doesnt support removing script tags)
    for script in soup.find_all("script"):
        if script.get("type") != "application/ld+json":
            script.decompose()

    # Remove other unwanted elements
    for selector in [
        "style",
        "link[rel=stylesheet]",
        "[aria-label='Gallery thumbnails']",
        ".gallery-lightbox-outer-wrapper",
        ".ProductItem-relatedProducts",
        ".header-menu",
        "#header",
        "#footer-sections",
        ".ProductItem-nav",
        ".ProductItem-gallery-scroll",
        ".ProductItem-gallery-carousel-controls",
        ".ProductItem-gallery-current-slide-indicator",
        ".product-image-zoom-duplicate",
        ".product-quantity-input",
        ".sqs-add-to-cart-button-wrapper",
        ".variant-select-wrapper",
        ".variant-radiobtn-wrapper",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # only keep the esstential meta tags
    for meta in soup.find_all("meta"):
        # Skip meta tags with no attributes
        if meta.attrs is None:
            meta.decompose()
            continue

        if (
            not (
                meta.has_attr("property")
                and (
                    meta["property"].startswith("og:")
                    or meta["property"].startswith("product:")
                )
            )
            and not (meta.has_attr("name") and meta["name"] == "description")
            and not meta.has_attr("itemprop")
        ):
            meta.decompose()
    for details in soup.select("#product-details"):
        title = details.find("h1").get_text(strip=True) if details.find("h1") else ""
        price = (
            details.select_one(".price").get_text(strip=True)
            if details.select_one(".price")
            else ""
        )
        description = (
            details.select_one(".product-description").get_text(strip=True)
            if details.select_one(".product-description")
            else ""
        )

    details.clear()
    details.append(
        BeautifulSoup(
            f'<h2>{title}</h2><p>Price: {price}</p><p>{description}</p><script type="application/json"></script>',
            "html.parser",
        )
    )

    # remove unwanted attributes
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            tag.attrs.pop(attr, None)
    return str(soup)


def trim_domain(domain: str):
    file_name = furl(domain).netloc
    splitted_file_name = file_name.split(".")
    if len(splitted_file_name) == 2:
        return splitted_file_name[0]
    if len(splitted_file_name) > 2:
        return splitted_file_name[1]
    return file_name


def save_to_csv(data, file_name: str):
    if not data:
        return
    header = data[0].keys()
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

    return


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted attributes
    for tag in soup.find_all(True):
        for attr in [
            "style",
            "x-transition:enter",
            "x-transition:enter-start",
            "x-transition:enter-end",
        ]:
            tag.attrs.pop(attr, None)

    for tag in soup.find_all("script"):
        if tag.get("type") != "application/ld+json":
            tag.decompose()

    for selector in [
        "iframe",
        "noscript",
        ".wpforms-container",
        ".cmplz-consent-status",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # Convert back to string for regex cleaning
    html = str(soup)

    # Apply regex-based cleaning
    html = re.sub(r"&quot;", '"', html)
    html = re.sub(r"&apos;", "'", html)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<figure.*?</figure>", "", html, flags=re.DOTALL)
    html = re.sub(r"<svg.*?</svg>", "", html, flags=re.DOTALL)
    html = re.sub(r"<img[^>]*>", "", html)
    html = re.sub(r"<video.*?</video>", "", html, flags=re.DOTALL)
    html = re.sub(r"<iframe.*?</iframe>", "", html, flags=re.DOTALL)

    # Keep data attributes and meta tags
    html = re.sub(r'\sclass="[^"]*"', "", html)
    html = re.sub(r'\shref="[^"]*"', "", html)
    html = re.sub(r'\salt="[^"]*"', "", html)
    html = re.sub(r"<link[^>]*>", "", html)
    # Keep all data attributes
    html = re.sub(r'\sdata-srcset="[^"]*"', "", html)
    html = re.sub(r'\sid="[^"]*"', "", html)
    html = re.sub(r"<noscript.*?</noscript>", "", html, flags=re.DOTALL)
    html = re.sub(
        r'<div[^>]*id="cookie-information-template-wrapper"[^>]*>.*?</div>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(r'<div[^>]*id="coiOverlay"[^>]*>.*?</div>', "", html, flags=re.DOTALL)
    html = re.sub(r"<div", "<", html)
    html = re.sub(r"</div>", "</>", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = re.sub(
        r'<script.*?src="[^"]*\.js\?ver=\d+[^"]*".*?</script>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(
        r'<script\s+type="rocketlazyloadscript".*?</script>', "", html, flags=re.DOTALL
    )
    html = re.sub(r'https://[^\s\'"]*?\.js', "", html)
    html = re.sub(r'"use strict".*?</script>', "", html, flags=re.DOTALL)
    html = re.sub(r"<([a-z]+)[^>]*>(\s*)</\1>", "", html)
    html = re.sub(r"<>", "", html)
    html = re.sub(
        r"<script.*?const rocket_pairs = \[{.*?</script>", "", html, flags=re.DOTALL
    )
    html = re.sub(
        r'<script[^>]*id="asp-[^"]*-js-before".*?</script>', "", html, flags=re.DOTALL
    )
    html = re.sub(r"<span>", "<>", html)
    html = re.sub(r"</span>", "</>", html)
    html = re.sub(r"<strong>", "<b>", html)
    html = re.sub(r"</strong>", "</b>", html)
    html = re.sub(r"<em>", "<i>", html)
    html = re.sub(r"</em>", "</i>", html)
    html = re.sub(r"</?div[^>]*>", "", html)
    html = re.sub(r"</?nav[^>]*>", "", html)
    html = re.sub(r"</?header[^>]*>", "", html)
    html = re.sub(r"</?footer[^>]*>", "", html)
    html = re.sub(r'\sstyle=["\'"][^\'"]*["\']', "", html)
    html = re.sub(r"[\r\n\t]+", "", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = re.sub(r'target="_blank"', "", html)
    html = re.sub(r"document\.[\w\.]*=", "", html)
    html = re.sub(r"window\.[\w\.]*=", "", html)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r">\s+<", "><", html).strip()

    # Reload cleaned HTML into BeautifulSoup for final clean-up
    soup = BeautifulSoup(html, "html.parser")

    # Remove extra elements but preserve meta tags and data attributes
    for selector in [
        "iframe",
        "noscript",
        ".wpforms-container",
        ".cmplz-consent-status",
        "#cookie-banner",
        "#cookie-popup",
        "#cookie-policy",
        ".cookie-consent",
        ".cookie-notice",
        ".cookie-overlay",
        ".cookie-container",
        ".CybotCookiebotScrollArea",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # Manually remove script tags except those with type="application/ld+json"
    for tag in soup.find_all("script"):
        if tag.get("type") != "application/ld+json":
            tag.decompose()

    # Remove empty elements except meta tags and elements with data attributes
    for tag in soup.find_all():
        if (
            not tag.contents
            and not tag.get_text(strip=True)
            and not (tag.name == "meta")
            and not any(attr.startswith("data-") for attr in tag.attrs)
        ):
            tag.decompose()

    return str(soup)


def clean_html_product(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted attributes except product-related classes and data attributes
    for tag in soup.find_all(True):
        for attr in [
            "style",
            "x-transition:enter",
            "x-transition:enter-start",
            "x-transition:enter-end",
        ]:
            tag.attrs.pop(attr, None)
        # Keep class attribute if it contains 'product'
        if "class" in tag.attrs:
            classes = tag["class"]
            if not any("product" in c.lower() for c in classes):
                tag.attrs.pop("class")
        # Keep data-variants and other product-related data attributes
        for attr in list(tag.attrs.keys()):
            if attr.startswith("data-") and any(
                keyword in attr.lower() for keyword in ["variant", "product", "sku"]
            ):
                continue
            if attr not in ["class", "type"]:  # Keep class and type attributes
                tag.attrs.pop(attr, None)

    for tag in soup.find_all("script"):
        if tag.get("type") != "application/ld+json":
            tag.decompose()

    for selector in [
        "iframe",
        "noscript",
        ".wpforms-container",
        ".cmplz-consent-status",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # Convert back to string for regex cleaning
    html = str(soup)

    # Apply regex-based cleaning
    html = re.sub(r"&quot;", '"', html)
    html = re.sub(r"&apos;", "'", html)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<figure.*?</figure>", "", html, flags=re.DOTALL)
    html = re.sub(r"<svg.*?</svg>", "", html, flags=re.DOTALL)
    html = re.sub(r"<img[^>]*>", "", html)
    html = re.sub(r"<video.*?</video>", "", html, flags=re.DOTALL)
    html = re.sub(r"<iframe.*?</iframe>", "", html, flags=re.DOTALL)

    # Keep data attributes and meta tags
    html = re.sub(r'\shref="[^"]*"', "", html)
    html = re.sub(r'\salt="[^"]*"', "", html)
    html = re.sub(r"<link[^>]*>", "", html)
    # Keep all data attributes
    html = re.sub(r'\sdata-srcset="[^"]*"', "", html)
    html = re.sub(r'\sid="[^"]*"', "", html)
    html = re.sub(r"<noscript.*?</noscript>", "", html, flags=re.DOTALL)
    html = re.sub(
        r'<div[^>]*id="cookie-information-template-wrapper"[^>]*>.*?</div>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(r'<div[^>]*id="coiOverlay"[^>]*>.*?</div>', "", html, flags=re.DOTALL)

    # Preserve divs with product-related classes and data attributes
    html = re.sub(r"<div", "<", html)
    html = re.sub(r"</div>", "</>", html)
    # Restore divs with product-related classes or data attributes
    html = re.sub(
        r'<([^>]*(?:class="[^"]*product[^"]*"|data-variants="[^"]*"|data-item-id="[^"]*")[^>]*)>',
        r"<\1>",
        html,
    )

    html = re.sub(r"\s{2,}", " ", html)
    html = re.sub(
        r'<script.*?src="[^"]*\.js\?ver=\d+[^"]*".*?</script>',
        "",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(
        r'<script\s+type="rocketlazyloadscript".*?</script>', "", html, flags=re.DOTALL
    )
    html = re.sub(r'https://[^\s\'"]*?\.js', "", html)
    html = re.sub(r'"use strict".*?</script>', "", html, flags=re.DOTALL)
    html = re.sub(r"<([a-z]+)[^>]*>(\s*)</\1>", "", html)
    html = re.sub(r"<>", "", html)
    html = re.sub(
        r"<script.*?const rocket_pairs = \[{.*?</script>", "", html, flags=re.DOTALL
    )
    html = re.sub(
        r'<script[^>]*id="asp-[^"]*-js-before".*?</script>', "", html, flags=re.DOTALL
    )
    html = re.sub(r"<span>", "<>", html)
    html = re.sub(r"</span>", "</>", html)
    html = re.sub(r"<strong>", "<b>", html)
    html = re.sub(r"</strong>", "</b>", html)
    html = re.sub(r"<em>", "<i>", html)
    html = re.sub(r"</em>", "</i>", html)
    html = re.sub(r"</?div[^>]*>", "", html)
    html = re.sub(r"</?nav[^>]*>", "", html)
    html = re.sub(r"</?header[^>]*>", "", html)
    html = re.sub(r"</?footer[^>]*>", "", html)
    html = re.sub(r'\sstyle=["\'"][^\'"]*["\']', "", html)
    html = re.sub(r"[\r\n\t]+", "", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = re.sub(r'target="_blank"', "", html)
    html = re.sub(r"document\.[\w\.]*=", "", html)
    html = re.sub(r"window\.[\w\.]*=", "", html)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r">\s+<", "><", html).strip()

    # Reload cleaned HTML into BeautifulSoup for final clean-up
    soup = BeautifulSoup(html, "html.parser")

    # Remove extra elements but preserve product-related elements
    for selector in [
        "iframe",
        "noscript",
        ".wpforms-container",
        ".cmplz-consent-status",
        "#cookie-banner",
        "#cookie-popup",
        "#cookie-policy",
        ".cookie-consent",
        ".cookie-notice",
        ".cookie-overlay",
        ".cookie-container",
        ".CybotCookiebotScrollArea",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # Manually remove script tags except those with type="application/ld+json"
    for tag in soup.find_all("script"):
        if tag.get("type") != "application/ld+json":
            tag.decompose()

    # Remove empty elements except meta tags, elements with data attributes, and product-related elements
    for tag in soup.find_all():
        if (
            not tag.contents
            and not tag.get_text(strip=True)
            and not (tag.name == "meta")
            and not any(attr.startswith("data-") for attr in tag.attrs)
            and not (
                tag.get("class") and any("product" in c.lower() for c in tag["class"])
            )
            and not any(
                attr.startswith("data-")
                and any(
                    keyword in attr.lower() for keyword in ["variant", "product", "sku"]
                )
                for attr in tag.attrs
            )
        ):
            tag.decompose()

    return str(soup)


def clean_html_page_simple(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove common page elements
    unwanted_elements = [
        "header",
        "footer",
        "nav",
        "aside",
        "noscript",
        "iframe",
        "style",
        "link[rel=stylesheet]",
        "#cookie-banner",
        "#cookie-popup",
        "#cookie-policy",
        ".cookie-consent",
        ".cookie-notice",
        ".cookie-overlay",
        ".cookie-container",
        ".CybotCookiebotScrollArea",
        ".wpforms-container",
        ".cmplz-consent-status",
    ]

    for selector in unwanted_elements:
        for element in soup.select(selector):
            element.decompose()

    # Remove empty elements except scripts
    for element in soup.find_all():
        if (
            element.name != "script"
            and not element.contents
            and not element.get_text(strip=True)
        ):
            element.decompose()

    # Clean up whitespace
    html = str(soup)
    html = re.sub(r"[\r\n\t]+", "", html)
    html = re.sub(r"\s{2,}", " ", html)
    html = re.sub(r">\s+<", "><", html).strip()

    return html


async def get_html(url: str) -> str | None:
    """Crawl a single product page."""
    print(f"Starting extraction for single product: {url}")
    run_config = CrawlerRunConfig(
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )
    async with AsyncWebCrawler(
        crawler_strategy=AsyncHTTPCrawlerStrategy(browser_config=http_crawler_config)
    ) as crawler:
        try:
            result = await crawler.arun(url=url, config=run_config)
            if not result.success:
                print(f"Failed to crawl URL: {url}")
                # TODO add retries
                return None

            print(f"Successfully crawled: {url}")
            # cleaned_html = clean_html_page_simple(result.html)

            return result.html

        except Exception as e:
            print(f"Error extracting single product from {url}: {e}")
            return None
