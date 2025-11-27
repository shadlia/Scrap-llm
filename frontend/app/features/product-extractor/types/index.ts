export type Products = {
  variants: Product[];
};

export type Product = {
  id: string;
  url: string;
  product_name: string;
  product_subname: string;
  product_sku: string;
  product_gtin: string;
  product_public_price_ttc: string;
  product_price_after_discount_ttc: string;
  product_inci_composition: string;
  product_option: string;
  product_color: string;
  product_size: string;
  product_stock: string;
  product_country_of_manufacture: string;
  product_image_url: string;
  edited?: boolean;
};

export type ExtractionMode = "llm";

export type ExtractionResponse = {
  products: Product[];
  status: "success" | "error";
  message?: string;
};
