from decimal import Decimal
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class DealItem(BaseModel):
    """Format pour Smart Offer"""

    name: str
    sku: Optional[str] = None
    url: Optional[HttpUrl] = None
    gtin: Optional[str] = None
    discountedPrice: Optional[Decimal] = Field(
        None, description="Prix remisé en centimes"
    )
    listPrice: Optional[Decimal] = Field(None, description="Prix normal en centimes")
    madeIn: Optional[str] = None
    images: Optional[list[str]] = None


def product_to_dealitem(product: any) -> dict:
    # Prepare the images field
    image_url = product.get("product_image_url")
    if isinstance(image_url, str) and image_url.strip():
        images = [image_url]
    elif isinstance(image_url, list) and image_url:
        images = image_url
    else:
        images = None

    # Mapping product to dealitem
    fields = {
        "name": product.get("product_name"),
        "sku": product.get("product_sku"),
        "url": product.get("url"),
        "gtin": product.get("product_gtin"),
        "discountedPrice": (
            float(
                product.get("product_public_price_ttc")
                .replace("€", "")
                .replace("£", "")
                .replace(",", ".")
                .strip()
            )
            * 100
            if product.get("product_public_price_ttc")
            and product.get("product_public_price_ttc").strip()
            else None
        ),
        "listPrice": (
            float(
                product.get("product_price_after_discount_ttc")
                .replace("€", "")
                .replace("£", "")
                .replace(",", ".")
                .strip()
            )
            * 100
            if product.get("product_price_after_discount_ttc")
            and product.get("product_price_after_discount_ttc").strip()
            else None
        ),
        "madeIn": product.get("product_country_of_manufacture"),
        "images": images,
    }

    clean_fields = {k: v for k, v in fields.items() if v not in [None, "", []]}
    return clean_fields
