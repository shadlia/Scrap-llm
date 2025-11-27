from scrap_llm.services.llm.llm_manager import LLMManager
from scrap_llm.services.llm.experiment_manager import ExperimentManager
from scrap_llm.config.schemas import Products


async def run_experiment(
    dataset_name: str,
    num_items: int,
    item_id: str,
    model: str,
):
    """
    Run the LLM experiment on the specified dataset.
    """
    llm_manager_extractor = LLMManager(
        models=[model],
        prompt_args="product_urls",
        action="extracting_chat",
        output_schema=Products,
    )

    llm_experiment = ExperimentManager(
        llm_manager_extractor,
    )

    results = llm_experiment.run_experiment(
        dataset_name,
        num_items,
        item_id,
    )
    print(results)

    # Calculate summary statistics
    total_items = len(results)
    successful_items = sum(1 for r in results if "error" not in r)
    total_manual_accuracy = 0
    valid_items = 0

    for result in results:
        if "error" not in result:
            valid_items += 1
            total_manual_accuracy += result["manual_evaluation"]["accuracy"]

    avg_manual_accuracy = (
        (total_manual_accuracy / valid_items * 100) if valid_items > 0 else 0
    )

    return {
        "summary": {
            "total_items": total_items,
            "successful_items": successful_items,
            "manual_accuracy": f"{avg_manual_accuracy:.2f}%",
            "extractor_model": llm_manager_extractor.models,
        },
        "detailed_results": results,
    }


async def add_to_dataset(dataset_name: str, url: str, variants_data_list: list[dict]):
    """
    Adds a single item with potentially multiple variants to the specified dataset.
    """
    if not variants_data_list:
        print("No variants data provided to add_to_dataset.")
        return False

    formatted_variants = []
    for product_details in variants_data_list:
        formatted_variants.append(
            {
                "product_name": product_details.get("name", ""),
                "product_sku": product_details.get("sku", ""),
                "product_gtin": product_details.get("gtin", ""),
                "product_public_price_ttc": product_details.get(
                    "product_public_price_ttc", ""
                ),
                "product_price_after_discount_ttc": product_details.get(
                    "product_price_after_discount_ttc", ""
                ),
                "product_option": product_details.get("option", ""),
                "product_color": product_details.get("color", ""),
                "product_size": product_details.get("size", ""),
                "product_stock": product_details.get("stock", ""),
                "product_country_of_manufacture": product_details.get("country", ""),
                "product_image_url": product_details.get("image_url", ""),
            }
        )

    expected_output = {"variants": formatted_variants}
    first_variant_name = (
        variants_data_list[0].get("name", "N/A") if variants_data_list else "N/A"
    )

    item = {
        "url": url,
        "expected_output": expected_output,
        "metadata": {
            "Domain": url.split("/")[2] if url else "",
            "Product name": first_variant_name,
            "Product url": url,
            "Number of variants": len(variants_data_list),
        },
    }

    llm_manager_extractor = LLMManager(
        models=["gpt-4.1-mini"],  # this is just a holder to use the ExperimentManager
        prompt_args="product_urls",  # this is just a holder to use the ExperimentManager
        action="extracting_chat",  # this is just a holder to use the ExperimentManager
        output_schema=Products,  # this is just a holder to use the ExperimentManager
    )

    llm_experiment = ExperimentManager(llm_manager_extractor)
    await llm_experiment.add_item_to_dataset(dataset_name, item)
    return True
