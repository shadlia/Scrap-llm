import json
import streamlit as st
from scrap_llm.services.llm.llm_manager import LLMManager
from scrap_llm.services.llm.experiment_manager import ExperimentManager
from scrap_llm.config.schemas import Products


def fill_form_from_json(json_data):
    try:
        data = json.loads(json_data)
        if "variants" in data:
            variants = []
            for variant in data["variants"]:
                variants.append(
                    {
                        "name": variant.get("product_name", ""),
                        "product_public_price_ttc": variant.get(
                            "product_public_price_ttc", ""
                        ),
                        "product_price_after_discount_ttc": variant.get(
                            "product_price_after_discount_ttc", ""
                        ),
                        "country": variant.get("product_country_of_manufacture", ""),
                        "image_url": variant.get("product_image_url", ""),
                        "sku": variant.get("product_sku", ""),
                        "gtin": variant.get("product_gtin", ""),
                        "option": variant.get("product_option", ""),
                        "color": variant.get("product_color", ""),
                        "size": variant.get("product_size", ""),
                        "stock": variant.get("product_stock", ""),
                    }
                )
            return variants
    except json.JSONDecodeError:
        st.error("Invalid JSON format")
    except Exception as e:
        st.error(f"Error parsing JSON: {str(e)}")
    return None


async def generate_json_from_url(url: str) -> str:
    """
    Generate a JSON string for the JSON input area based on the provided product URL.
    """
    llm_manager_extractor = LLMManager(
        models=["gpt-4.1-mini"],  # TODO: Make model configurable if needed
        prompt_args="product_urls",
        action="extracting_chat",
        output_schema=Products,
    )
    llm_manager_judge = LLMManager(
        models=["gpt-4.1-mini"],
        prompt_args="product_urls",
        action="LLM_EVALUATION_EXTRACTION",
    )
    exp_manager = ExperimentManager(llm_manager_extractor, llm_manager_judge)
    product_data = await exp_manager.extract_product_infos(url)
    product_data_json = product_data.model_dump_json(indent=4)
    return product_data_json
