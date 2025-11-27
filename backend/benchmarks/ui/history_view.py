import streamlit as st
import pandas as pd
from logic.result_saver import load_langfuse_history_to_session


def render_history_view():
    st.title("Runs History 📊")
    st.markdown("View your experiment history and results")

    # Auto-load data from Langfuse
    if "experiment_history" not in st.session_state:
        st.session_state.experiment_history = []

    # Get the current dataset from session state or use default
    current_dataset = st.session_state.get("current_dataset", "extraction_dataset")

    # Auto-load data if no experiments are loaded
    if not st.session_state.experiment_history:
        with st.spinner("🔄 Loading experiment data from Langfuse..."):
            try:
                load_langfuse_history_to_session(current_dataset)
                st.success(
                    f"✅ Loaded experiment data from '{current_dataset}' dataset"
                )
            except Exception as e:
                st.error(f"❌ Failed to load data: {str(e)}")
                st.info(
                    "No experiments found. Run some experiments first or check your dataset name."
                )

    # Dataset selector for switching datasets
    col1, col2 = st.columns([2, 1])
    with col1:
        dataset_name = st.selectbox(
            "Select Dataset",
            [
                "extraction_dataset",
                "extraction_test_dataset",
                "extraction_train_dataset",
            ],
            key="dataset_name_key_history",
            index=(
                0
                if current_dataset == "extraction_dataset"
                else 1 if current_dataset == "extraction_test_dataset" else 2
            ),
        )
    with col2:
        if st.button("🔄 Reload Data"):
            with st.spinner("Loading experiment history from Langfuse..."):
                load_langfuse_history_to_session(dataset_name)
                st.success("Experiment history loaded from Langfuse!")

    if (
        "experiment_history" not in st.session_state
        or not st.session_state.experiment_history
    ):
        st.info(
            "No experiments have been loaded yet. Run experiments or check your dataset configuration."
        )
        return

    # Create a DataFrame for better display
    history_data = []
    for exp in st.session_state.experiment_history:
        # Ensure model is always a string for display
        model = exp["model"]
        if isinstance(model, list):
            model = ", ".join(str(m) for m in model)

        # Extract additional metrics
        summary = exp["results"]["summary"]
        total_cost = summary.get("total_cost", 0)
        avg_latency = summary.get("avg_latency", 0)

        history_data.append(
            {
                "Timestamp": exp["timestamp"],
                "Dataset": exp["dataset_name"],
                "Items": exp["num_items"],
                "Extractor Model": model,
                "Accuracy (%)": exp["results"]["summary"]["manual_accuracy"],
                "Total Cost ($)": f"${total_cost:.4f}" if total_cost > 0 else "N/A",
                "Avg Latency (s)": f"{avg_latency:.3f}s" if avg_latency > 0 else "N/A",
            }
        )

    df = pd.DataFrame(history_data)

    # Convert percentage strings to float for plotting
    df["Accuracy (%)"] = df["Accuracy (%)"].str.rstrip("%").astype(float)

    # Display the summary table
    st.dataframe(df, use_container_width=True)

    # Add some visualizations for overall trends
    if len(df) > 1:
        st.subheader("Performance Trends")

        col1, col2 = st.columns(2)

        with col1:
            st.line_chart(df.set_index("Timestamp")["Accuracy (%)"])
            st.caption("Accuracy Over Time")

        with col2:
            # Only show cost chart if we have cost data
            cost_data = df[df["Total Cost ($)"] != "N/A"]
            if len(cost_data) > 0:
                # Convert cost strings to float
                cost_values = (
                    cost_data["Total Cost ($)"].str.replace("$", "").astype(float)
                )
                st.line_chart(cost_data.set_index("Timestamp")["Total Cost ($)"])
                st.caption("Cost Over Time")

    # Allow viewing detailed results
    st.subheader("View Detailed Results")
    selected_run = st.selectbox(
        "Select Run",
        options=range(len(st.session_state.experiment_history)),
        format_func=lambda x: f"Run {x + 1} - {st.session_state.experiment_history[x]['timestamp']}",
    )

    if selected_run is not None:
        exp = st.session_state.experiment_history[selected_run]
        st.markdown("### Run Details")
        tab1, tab2, tab3 = st.tabs(
            ["Summary", "Manual Evaluation", "Cost & Performance"]
        )

        with tab1:
            st.json(exp["results"]["summary"])

        with tab2:
            for i, result in enumerate(exp["results"]["detailed_results"], 1):
                with st.expander(f"Item {i} - Manual Evaluation"):
                    st.markdown("#### Accuracy Metrics")

                    # Handle both local experiment format and Langfuse format
                    if "manual_evaluation" in result:
                        # Local experiment format
                        st.json(result["manual_evaluation"])
                    elif "accuracy" in result:
                        # Langfuse format
                        accuracy_data = {
                            "accuracy": result["accuracy"],
                            "accuracy_percentage": f"{result['accuracy'] * 100:.2f}%",
                        }
                        st.json(accuracy_data)
                    else:
                        st.info("No accuracy data available for this item")

                    # Show the raw LLM output
                    if "output" in result and result["output"]:
                        st.markdown("#### Raw LLM Output")
                        st.code(str(result["output"]), language="json")

                    # Show cost and latency if available
                    if "cost" in result or "latency" in result:
                        st.markdown("#### Performance Metrics")
                        metrics_col1, metrics_col2 = st.columns(2)
                        with metrics_col1:
                            if "cost" in result:
                                st.metric("Cost", f"${result['cost']:.4f}")
                        with metrics_col2:
                            if "latency" in result:
                                st.metric("Latency", f"{result['latency']:.3f}s")

        with tab3:
            summary = exp["results"]["summary"]
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Cost", f"${summary.get('total_cost', 0):.4f}")

            with col2:
                st.metric("Average Latency", f"{summary.get('avg_latency', 0):.3f}s")

            with col3:
                st.metric("Success Rate", summary["manual_accuracy"])
