from pydantic import BaseModel, Field, ConfigDict


class Product(BaseModel):
    name: str = Field(description="The name of the product")
    price: str = Field(description="The price of the product")


class Productv2(BaseModel):
    product_name: str = Field(description="The name of the product")
    product_sku: str = Field(description="The sku of the product")
    product_gtin: str = Field(description="The gtin of the product")
    product_public_price_ttc: str = Field(
        description="The price before discount of the product"
    )
    product_price_after_discount_ttc: str = Field(
        description="The price after discount of the product"
    )
    product_option: str = Field(description="The options of the product")
    product_color: str = Field(description="The color of the product")
    product_size: str = Field(description="The size of the product")
    product_stock: str = Field(description="The stock of the product")
    product_country_of_manufacture: str = Field(
        description="The country of manufacture of the product"
    )

    product_image_url: str = Field(description="The image url of the product")
    model_config = ConfigDict(extra="allow")


class Products(BaseModel):
    variants: list[Productv2] = Field(description="The list of product's variants")
