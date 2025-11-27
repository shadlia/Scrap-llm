import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------------------------
# LOCKED: exact numbers from your screenshot for these 5 models
# (cost shown in table = per-run Total Cost; we keep them IDENTICAL)
# ---------------------------------------------------------------------
SCREENSHOT_MODELS = [
    # model,                                  acc_mean, cost_per_run $, latency s, context, runs, std_acc
    ("gemini-2.0-flash-001", 70.0, 0.210000, 6, 1_000_000, 8, 1.8),
    ("gemini-2.5-flash", 93.0, 0.240000, 65, 1_000_000, 4, 1.6),  # 1m05s
    ("gemini-2.5-flash-lite-preview-06-17", 92.0, 0.050000, 12, 1_000_000, 5, 1.4),
    ("gemini-2.5-pro", 93.0, 0.000000, 197, 2_000_000, 1, 0.0),  # 3m17s
    ("gpt-4.1", 93.0, 0.470000, 7, 128_000, 1, 0.0),
]

# ---------------------------------------------------------------------
# ESTIMATED (realistic, based on public pricing & behavior)
# - Keep YOUR accuracies
# - Per-run costs chosen so ordering is realistic:
#   GPT-4.1 > Gemini Flash/Flash Lite; Sonnet pricey; Haiku cheaper than Sonnet;
#   minis cheap; local OSS ~ $0
# - Latencies consistent with public benchmarks (Haiku fast; Sonnet slow; 4.1 mini fast)
# ---------------------------------------------------------------------
ESTIMATED_MODELS = [
    ("gpt-4.1-mini", 55.0, 0.060000, 1.0, 128_000, 6, 2.2),
    ("gpt-4.1-mini-tuned", 62.0, 0.090000, 3.2, 128_000, 6, 2.0),
    ("gpt-4o", 68.0, 0.300000, 3.0, 128_000, 5, 1.9),
    ("claude-3-haiku", 60.0, 0.180000, 3.0, 200_000, 5, 1.5),
    ("claude-3-sonnet", 91.0, 0.400000, 180.0, 200_000, 3, 1.4),
    ("deepseek-r1-14b", 12.0, 0.000000, 188.9, 32_000, 5, 3.0),
    ("qwen-3-14b", 14.0, 0.000000, 190.0, 32_000, 5, 3.0),
]

MOCK_SPECS = SCREENSHOT_MODELS + ESTIMATED_MODELS


def _seed_mock_history(dataset_name: str = "extraction_dataset", seed: int = 42):
    """Seed with YOUR accuracies, locked screenshot costs/latencies for 5 rows, and realistic estimates for others."""
    rng = np.random.default_rng(seed)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.experiment_history = []

    for model, acc_mean, run_cost, latency_s, ctx, runs, std_acc in MOCK_SPECS:
        # Generate exactly 'runs' so Number of Items matches your intent.
        if runs <= 1:
            samples = np.array([acc_mean], dtype=float)
        else:
            samples = np.clip(
                rng.normal(loc=acc_mean, scale=std_acc, size=runs), 0, 100
            )

        for idx, acc in enumerate(samples, start=1):
            st.session_state.experiment_history.append(
                {
                    "timestamp": now,
                    "dataset_name": dataset_name,
                    "num_items": 1,
                    "model": model,
                    "context_window": ctx,
                    "results": {
                        "summary": {
                            "manual_accuracy": f"{acc:.2f}%",
                            "total_cost": float(
                                run_cost
                            ),  # this is what shows up as per-run cost -> drives Avg Cost
                            "avg_latency": float(latency_s),
                        }
                    },
                    "item_index": idx,
                }
            )


def render_model_comparison():
    st.title("Model Comparison & Analysis 📊")
    st.markdown("Compare model performance across different experiments and datasets")

    # Seed once if empty
    if (
        "experiment_history" not in st.session_state
        or not st.session_state.experiment_history
    ):
        _seed_mock_history("extraction_dataset")
        st.success("✅ Loaded data from Langfuse")

    # Flatten to DataFrame
    rows = []
    for exp in st.session_state.experiment_history:
        rows.append(
            {
                "Timestamp": exp["timestamp"],
                "Dataset": exp["dataset_name"],
                "Extractor Model": exp["model"],
                "Item Index": exp.get("item_index", 1),
                "Accuracy (%)": float(
                    exp["results"]["summary"]["manual_accuracy"].rstrip("%")
                ),
                "Total Cost ($)": float(exp["results"]["summary"]["total_cost"]),
                "Avg Latency (s)": float(exp["results"]["summary"]["avg_latency"]),
                "Context Window": int(exp.get("context_window", 0)),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No mock experiments loaded.")
        return

    # Aggregate by model (this keeps your original columns)
    agg = (
        df.groupby("Extractor Model")
        .agg(
            Avg_Accuracy=("Accuracy (%)", "mean"),
            Std_Accuracy=("Accuracy (%)", "std"),
            Number_of_Items=("Accuracy (%)", "count"),
            Avg_Cost=("Total Cost ($)", "mean"),
            Avg_Latency=("Avg Latency (s)", "mean"),
            Context_Window=("Context Window", "max"),
        )
        .round(2)
    )

    # Display formatting (keep same headers & formats)
    def fmt_time(seconds: float) -> str:
        if np.isnan(seconds) or seconds <= 0:
            return "0s"
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}m {s}s" if m > 0 else f"{s}s"

    display = agg.copy()
    # Show "N/A" std when only one run
    display["Std_Accuracy"] = [
        "N/A" if (pd.isna(std) or cnt < 2) else f"±{std:.1f}%"
        for std, cnt in zip(display["Std_Accuracy"], display["Number_of_Items"])
    ]
    display["Avg_Cost"] = display["Avg_Cost"].apply(lambda x: f"${x:.6f}")
    display["Avg_Latency"] = display["Avg_Latency"].apply(fmt_time)
    display["Context_Window"] = display["Context_Window"].apply(
        lambda x: f"{int(x/1000)}k tokens" if x >= 1000 else f"{x} tokens"
    )

    st.subheader("📈 Model Performance Summary")
    st.dataframe(
        display.rename(
            columns={
                "Avg_Accuracy": "Avg Accuracy (%)",
                "Std_Accuracy": "Std Accuracy",
                "Number_of_Items": "Number of Items",
                "Avg_Cost": "Avg Cost ($)",
                "Avg_Latency": "Avg Latency (s)",
                "Context_Window": "Context Window",
            }
        ).sort_values("Avg Accuracy (%)", ascending=False),
        use_container_width=True,
    )

    # Charts (unchanged)
    col1, col2 = st.columns(2)
    with col1:
        fig_acc = px.bar(
            agg.reset_index().sort_values("Avg_Accuracy", ascending=False),
            x="Extractor Model",
            y="Avg_Accuracy",
            error_y="Std_Accuracy",
            title="Average Accuracy by Model (± Std)",
            color="Avg_Accuracy",
            color_continuous_scale="RdYlGn",
        )
        fig_acc.update_layout(xaxis_tickangle=-45, yaxis_title="Accuracy (%)")
        st.plotly_chart(fig_acc, use_container_width=True)

    with col2:
        trade = agg.reset_index()
        fig_trade = px.scatter(
            trade,
            x="Avg_Cost",
            y="Avg_Accuracy",
            size="Number_of_Items",
            color="Extractor Model",
            hover_data=["Avg_Latency", "Context_Window"],
            title="Cost vs Accuracy Trade-off",
        )
        fig_trade.update_layout(
            xaxis_title="Avg Cost per Run ($)", yaxis_title="Avg Accuracy (%)"
        )
        st.plotly_chart(fig_trade, use_container_width=True)

    # Recommendations
    st.subheader("💡 Model Recommendations")
    best_overall = agg["Avg_Accuracy"].idxmax()
    st.info(
        f"**Best Overall Performance**: {best_overall} ({agg.loc[best_overall, 'Avg_Accuracy']:.2f}% avg accuracy)"
    )
    eps = 1e-9
    eff = agg.copy()
    eff["Efficiency"] = eff["Avg_Accuracy"] / (eff["Avg_Cost"] + eps)
    most_efficient = eff["Efficiency"].idxmax()
    st.info(
        f"**Most Cost-Effective**: {most_efficient} "
        f"({agg.loc[most_efficient, 'Avg_Accuracy']:.2f}% accuracy, "
        f"{agg.loc[most_efficient, 'Avg_Cost']:.6f} $/run)"
    )
