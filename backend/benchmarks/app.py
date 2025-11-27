import streamlit as st
from ui.history_view import render_history_view
from ui.dataset_form import render_add_to_dataset_form
from ui.experiment_form import render_run_experiment_form
from ui.model_comparison import render_model_comparison
from ui.navigation import sidebar_navigation
import subprocess
import sys
import os


def main():
    st.set_page_config(page_title="Benchmarks Dashboard", page_icon="📊", layout="wide")
    page = sidebar_navigation()

    if page == "Add to Dataset":
        render_add_to_dataset_form()
    elif page == "Run Experiment":
        render_run_experiment_form()
    elif page == "Runs History":
        render_history_view()
    elif page == "Model Comparison":
        render_model_comparison()


def launch():
    """Launch the Streamlit app using subprocess"""
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)


if __name__ == "__main__":
    main()
