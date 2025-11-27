from typing import Dict, Any
from ...utils.utils import get_html

from ..langfuse.langfuseService import LangfuseConfig
from .llm_manager import LLMManager
from scrap_llm.config.schemas import Products


class ExperimentManager:
    """Manages LLM experiments with Langfuse integration for tracking and scoring."""

    def __init__(
        self,
        llm_manager_extractor: LLMManager,
    ):
        """Initialize the experiment manager with an LLM manager instance."""
        self.llm_manager_extractor = llm_manager_extractor
        self.model_name_extractor = llm_manager_extractor.models[0]
        self.langfuse = LangfuseConfig("langfuse-benchmarks")

    def run_experiment(
        self,
        dataset_name: str,
        number_of_items: int = 1,
        item_id: str = None,
    ):
        dataset = self.langfuse.langfuse.get_dataset(dataset_name)
        results = []
        if item_id:
            item = next(
                (item for item in list(dataset.items) if item.id == item_id), None
            )
            items_to_process = [item]
        else:
            items_to_process = list(dataset.items)[:number_of_items]

        for item in items_to_process:
            with item.observe(
                run_name=self.model_name_extractor
            ) as observation_trace_id:
                try:
                    # provider = MODEL_TO_PROVIDER[self.model_name_extractor]
                    llm = LLMManager(
                        models=self.llm_manager_extractor.models,
                        prompt_args=item.input,
                        action="extracting_chat",
                        output_schema=Products,
                    )
                    output = llm.call_llm(trace_id=observation_trace_id)

                    # Calculate manual scores
                    manual_scores = self.calculate_score_products(
                        item.expected_output, output["response"]
                    )

                    print(f"Manual scores: {manual_scores}")

                    # Record scores in Langfuse using self.langfuse
                    self.langfuse.langfuse.score(
                        trace_id=observation_trace_id,
                        name="Fields_accuracy",
                        value=manual_scores["accuracy"],
                        comment=f"Field-level accuracy: {manual_scores['correct_fields']}/{manual_scores['total_fields']}",
                    )

                    # Add results for this item
                    results.append(
                        {
                            "item_id": item.id,
                            "trace_id": observation_trace_id,
                            "output": output,
                            "manual_evaluation": {
                                "accuracy": manual_scores["accuracy"],
                                "correct_fields": manual_scores["correct_fields"],
                                "total_fields": manual_scores["total_fields"],
                                "field_scores": manual_scores["field_scores"],
                            },
                            "extractor_model": self.model_name_extractor[0],
                        }
                    )

                except Exception as e:
                    results.append(
                        {
                            "item_id": item.id,
                            "error": str(e),
                            "trace_id": observation_trace_id,
                        }
                    )

        return results

    def calculate_score_products(
        self,
        expected_output: Dict,
        actual_output: Any,
    ) -> Dict[str, Any]:
        """
        Calculate scores between expected and actual product outputs using best-match pairing.

        Args:
            expected_output: Expected product output
            actual_output: Actual product output from LLM

        Returns:
            Dictionary containing accuracy scores and field-level comparisons
        """
        try:
            print("Starting calculate_score_products")

            # Normalize actual products
            actual_products = []
            for product in actual_output.variants:
                actual_products.append(
                    product if isinstance(product, dict) else product.__dict__
                )

            expected_products = expected_output.get("variants", [])
            if not expected_products or not actual_products:
                print("No products found in one or both outputs")
                return {
                    "accuracy": 0,
                    "correct_fields": 0,
                    "total_fields": 0,
                    "field_scores": {},
                    "error": "No products found in one or both outputs",
                }

            # Get all unique fields
            all_fields = set()
            for product in expected_products + actual_products:
                all_fields.update(
                    field for field in product.keys() if not field.startswith("_")
                )

            total_fields = len(all_fields) * len(expected_products)
            correct_fields = 0
            field_scores = {}

            unmatched_actual = actual_products.copy()

            for i, expected_product in enumerate(expected_products):
                best_match = None
                best_match_score = -1
                best_match_index = -1

                # Find best matching actual product
                for j, actual_product in enumerate(unmatched_actual):
                    match_score = sum(
                        1
                        for field in all_fields
                        if expected_product.get(field, "")
                        == actual_product.get(field, "")
                    )
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_match = actual_product
                        best_match_index = j

                if best_match is None:
                    continue  # No match found

                # Remove the matched product from the pool
                unmatched_actual.pop(best_match_index)

                # Compare fields
                for field in all_fields:
                    expected_value = expected_product.get(field, "")
                    actual_value = best_match.get(field, "")
                    is_correct = expected_value == actual_value
                    if is_correct:
                        correct_fields += 1

                    field_key = f"product_{i + 1}_{field}"
                    field_scores[field_key] = {
                        "field": field,
                        "correct": is_correct,
                        "expected": expected_value,
                        "actual": actual_value,
                        "product_index": i + 1,
                    }

            overall_accuracy = correct_fields / total_fields if total_fields > 0 else 0

            return {
                "accuracy": overall_accuracy,
                "correct_fields": correct_fields,
                "total_fields": total_fields,
                "field_scores": field_scores,
            }

        except Exception as e:
            return {
                "accuracy": 0,
                "correct_fields": 0,
                "total_fields": 0,
                "field_scores": {},
                "error": str(e),
            }

    async def add_item_to_dataset(self, dataset_name: str, item: Dict):
        """
        Add an item to a dataset.

        Args:
            dataset_name: Name of the dataset to add to
        """
        print(f"Adding item to dataset: {item}")
        html = await get_html(item["url"])  # original html without cleaning

        if not html:
            print(f"Failed to get HTML for {item['url']}")
            raise Exception(f"Failed to get HTML for {item['url']}")
        else:
            print(f"HTML for {item['url']} retrieved successfully")

        self.langfuse.langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input=html,
            expected_output=item["expected_output"],
            metadata=item["metadata"],
        )
        return print("Item added to dataset successfully")

    async def get_experiments(self, dataset_name: str):
        runs = self.langfuse.langfuse.get_dataset_runs(
            dataset_name
        )  # --> run names (all run : for loop )

        # print(runs.data[0].name)

        for run in runs.data:
            print(run.name)
            run_items = self.langfuse.langfuse.get_dataset_run(
                dataset_name, run.name
            ).dataset_run_items

            for item in run_items:
                print(item.trace_id)
                trace = self.langfuse.langfuse.get_trace(item.trace_id)
                print(
                    f"Trace attributes: {[attr for attr in dir(trace) if not attr.startswith('_')]}"
                )
                print(trace.total_cost)
                print(trace.metadata["prompt_version"])
                print(trace.latency)
                print(trace.scores[0].name)
                print(trace.scores[0].value)
                print(trace.scores[0].comment)
                print(trace.output)

                print(
                    f"Trace attributes: {[attr for attr in dir(trace.output) if not attr.startswith('_')]}"
                )

        # one_run = self.langfuse.langfuse.get_dataset_run(
        #     dataset_name, "gemini-2.0-flash-001"
        # )  # --> trace id  ( get trace id for each run per name )
        # trace = self.langfuse.langfuse.get_trace("61069897-58a1-4d2f-9c14-b10381fdd554")
        # print(
        #     trace
        # )  # --> for each trace : we can get prompt version ,  ouput ,  score ,  etc.
        return runs
