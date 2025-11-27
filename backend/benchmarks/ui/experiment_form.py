import streamlit as st
import asyncio
from logic.experiment_runner import run_experiment
from logic.result_saver import save_experiment_result

# Model options with user-friendly labels and original values
MODEL_OPTIONS = [
    # {"label": "Gemini 1.5 Flash", "value": "gemini-1.5-flash"},
    {"label": "Gemini 2.0 Flash", "value": "gemini-2.0-flash-001"},
    {"label": "Gemini 2.5 Flash", "value": "gemini-2.5-flash"},
    {"label": "Gemini 2.5 Flash Lite", "value": "gemini-2.5-flash-lite-preview-06-17"},
    {"label": "Gemini 2.5 Pro", "value": "gemini-2.5-pro"},
    {"label": "GPT-4o", "value": "gpt-4o"},
    {"label": "GPT-4o-mini", "value": "gpt-4o-mini"},
    {"label": "GPT-4.1", "value": "gpt-4.1"},
    {"label": "GPT-4.1-mini", "value": "gpt-4.1-mini"},
    {
        "label": "FT: GPT-4.1-mini (10 samples)",
        "value": "ft:gpt-4.1-mini-2025-04-14:choose:10-samples:BXrWEC3a",
    },
    # {"label": "GPT-3.5", "value": "gpt-3.5"},
    # {"label": "Claude 3 Opus", "value": "claude-3-opus-20240229"},
    {"label": "Claude 3.5 Sonnet", "value": "claude-3-5-sonnet-2024062"},
    {"label": "Claude 3.5 Haiku", "value": "claude-3-5-haiku-20241022"},
]


def render_run_experiment_form():
    st.title("Run Experiment🧪")
    st.markdown("Run the LLM experiment on your dataset")

    if "use_llm_as_judge_key" not in st.session_state:
        st.session_state.use_llm_as_judge_key = False

    # Model selection with user-friendly names only
    model_display = [m["label"] for m in MODEL_OPTIONS]
    model_value_map = {m["label"]: m["value"] for m in MODEL_OPTIONS}
    selected_label = st.selectbox(
        "Select Extractor Model",
        model_display,
        index=0,
    )
    model = model_value_map[selected_label]

    # Dataset, Item ID, Number of Items
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        dataset_name = st.selectbox(
            "Dataset Name",
            [
                "extraction_dataset",
                "extraction_test_dataset",
                "extraction_train_dataset",
            ],
            key="dataset_name_key_run",
        )
        # Store current dataset in session state for history view
        st.session_state.current_dataset = dataset_name
    with col2:
        item_id = st.text_input(
            "Item ID (optional, disables Number of Items)",
            value=st.session_state.get("item_id_key", ""),
            key="item_id_key",
        )
    with col3:
        num_items_disabled = bool(item_id.strip())
        num_items_value = 0 if num_items_disabled else 1
        num_items = st.number_input(
            "Number of Items to Process",
            min_value=0 if num_items_disabled else 1,
            value=num_items_value,
            key="num_items_key",
            disabled=num_items_disabled,
        )
    st.caption(
        "Fill EITHER 'Number of Items to Process' OR 'Item ID'. If 'Item ID' is provided, only that item will be processed."
    )

    with st.form("run_experiment_form"):
        submitted = st.form_submit_button("Run Experiment")

        if submitted:
            try:
                with st.spinner("Running experiment..."):
                    experiment_results = asyncio.run(
                        run_experiment(
                            dataset_name,
                            num_items,
                            item_id,
                            model,
                        )
                    )
                    save_experiment_result(
                        experiment_results,
                        dataset_name,
                        model,
                        num_items,
                    )

                    st.subheader("Experiment Results")
                    tab1, tab2 = st.tabs(["Summary", "Detailed Results"])
                    with tab1:
                        st.markdown("### Summary Statistics")
                        st.json(experiment_results["summary"])
                    with tab2:
                        st.markdown("### Detailed Results")
                        for i, result in enumerate(
                            experiment_results["detailed_results"], 1
                        ):
                            with st.expander(f"Item {i}"):
                                st.json(result)
            except Exception as e:
                st.error(f"Error running experiment: {str(e)}")
