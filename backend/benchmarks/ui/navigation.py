import streamlit as st


def sidebar_navigation():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Add to Dataset"

    st.sidebar.title("Scrap LLM Benchmarks ")

    if st.sidebar.button(
        "Add to Dataset",
        type=(
            "primary"
            if st.session_state.current_page == "Add to Dataset"
            else "secondary"
        ),
        use_container_width=True,
    ):
        st.session_state.current_page = "Add to Dataset"
        st.rerun()

    if st.sidebar.button(
        "Run Experiment",
        type=(
            "primary"
            if st.session_state.current_page == "Run Experiment"
            else "secondary"
        ),
        use_container_width=True,
    ):
        st.session_state.current_page = "Run Experiment"
        st.rerun()

    if st.sidebar.button(
        "Runs History",
        type=(
            "primary"
            if st.session_state.current_page == "Runs History"
            else "secondary"
        ),
        use_container_width=True,
    ):
        st.session_state.current_page = "Runs History"
        st.rerun()

    if st.sidebar.button(
        "Model Comparison",
        type=(
            "primary"
            if st.session_state.current_page == "Model Comparison"
            else "secondary"
        ),
        use_container_width=True,
    ):
        st.session_state.current_page = "Model Comparison"
        st.rerun()

    return st.session_state.current_page
