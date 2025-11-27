import streamlit as st
from datetime import datetime
from scrap_llm.services.llm.experiment_manager import ExperimentManager
from scrap_llm.services.llm.llm_manager import LLMManager


def save_experiment_result(experiment_results, dataset_name, model, num_items):
    """Save experiment results to session state."""
    if "experiment_history" not in st.session_state:
        st.session_state.experiment_history = []

    experiment_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_name": dataset_name,
        "model": model,
        "num_items": num_items,
        "results": experiment_results,
    }

    st.session_state.experiment_history.append(experiment_data)


def get_langfuse_experiment_history(dataset_name: str):
    """
    Fetch experiment history from Langfuse and format it for the UI.

    Args:
        dataset_name: Name of the dataset to fetch experiments for

    Returns:
        List of formatted experiment data for the UI
    """
    try:
        # Create a minimal LLM manager for the experiment manager
        llm_manager = LLMManager(
            models=["gpt-4"],  # Dummy model for initialization
            prompt_args="product_urls",
            action="extracting_chat",
            output_schema=None,
        )

        experiment_manager = ExperimentManager(llm_manager)

        # Get all runs for the dataset
        runs = experiment_manager.langfuse.langfuse.get_dataset_runs(dataset_name)

        formatted_experiments = []

        for run in runs.data:
            run_items = experiment_manager.langfuse.langfuse.get_dataset_run(
                dataset_name, run.name
            ).dataset_run_items

            # Group items by run
            run_results = []
            total_accuracy = 0
            valid_items = 0

            for item in run_items:
                trace = experiment_manager.langfuse.langfuse.get_trace(item.trace_id)

                # Extract accuracy score if available
                accuracy_score = 0
                if trace.scores:
                    for score in trace.scores:
                        if score.name == "Fields_accuracy":
                            accuracy_score = score.value
                            break

                if accuracy_score > 0:
                    total_accuracy += accuracy_score
                    valid_items += 1

                run_results.append(
                    {
                        "item_id": item.id,
                        "trace_id": item.trace_id,
                        "accuracy": accuracy_score,
                        "cost": trace.total_cost,
                        "latency": trace.latency,
                        "output": trace.output,
                        "metadata": trace.metadata,
                        # Add manual_evaluation object to match local experiment format
                        "manual_evaluation": {
                            "accuracy": accuracy_score,
                            "accuracy_percentage": f"{accuracy_score * 100:.2f}%",
                            "source": "langfuse",
                        },
                    }
                )

            # Calculate average accuracy for the run
            avg_accuracy = (
                (total_accuracy / valid_items * 100) if valid_items > 0 else 0
            )

            # Format the experiment data
            experiment_data = {
                "timestamp": (
                    run.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(run, "created_at")
                    else "Unknown"
                ),
                "dataset_name": dataset_name,
                "model": run.name,
                "num_items": len(run_results),
                "results": {
                    "summary": {
                        "total_items": len(run_results),
                        "successful_items": valid_items,
                        "manual_accuracy": f"{avg_accuracy:.2f}%",
                        "extractor_model": [run.name],
                        "total_cost": sum(r.get("cost", 0) for r in run_results),
                        "avg_latency": (
                            sum(r.get("latency", 0) for r in run_results)
                            / len(run_results)
                            if run_results
                            else 0
                        ),
                    },
                    "detailed_results": run_results,
                },
            }

            formatted_experiments.append(experiment_data)

        return formatted_experiments

    except Exception as e:
        st.error(f"Error fetching experiment history from Langfuse: {str(e)}")
        return []


def load_langfuse_history_to_session(dataset_name: str):
    """
    Load Langfuse experiment history into Streamlit session state.

    Args:
        dataset_name: Name of the dataset to load history for
    """
    if "experiment_history" not in st.session_state:
        st.session_state.experiment_history = []

    # Fetch experiments from Langfuse
    langfuse_experiments = get_langfuse_experiment_history(dataset_name)

    # Merge with existing session state (avoid duplicates)
    existing_timestamps = {
        exp["timestamp"] for exp in st.session_state.experiment_history
    }

    for exp in langfuse_experiments:
        if exp["timestamp"] not in existing_timestamps:
            st.session_state.experiment_history.append(exp)

    # Sort by timestamp (newest first)
    st.session_state.experiment_history.sort(key=lambda x: x["timestamp"], reverse=True)
