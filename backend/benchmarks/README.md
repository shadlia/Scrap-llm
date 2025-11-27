# Benchmarks UI

A Streamlit-based interface for running and analyzing LLM experiments with Langfuse integration.

## Features

- **Run Experiments**: Execute LLM experiments on different datasets with various models
- **Add to Dataset**: Add new items to datasets for testing
- **History View**: View experiment history with detailed results
- **Model Comparison**: Compare accuracy, cost, and latency across different models
- **Langfuse Integration**: Load experiment data directly from Langfuse
- **Auto-Loading**: Automatically loads experiment data when pages are accessed

## Installation

Make sure you have the required dependencies installed:

```bash
cd backend
poetry install
```

## Usage

Run the benchmarks application:

```bash
cd backend/benchmarks
python app.py
```

Or use the poetry script:

```bash
cd backend
poetry run benchmarks
```

## Navigation

The application includes four main pages:

1. **Add to Dataset**: Add new test items to datasets
2. **Run Experiment**: Execute experiments with different models
3. **Runs History**: View experiment history and detailed results
4. **Model Comparison**: Comprehensive model analysis and comparison

## Model Comparison Features

The model comparison page provides comprehensive analysis capabilities:

### **Performance Overview**
- **Model Performance Summary Table**: Shows average accuracy, standard deviation, number of items, cost, and latency for each model
- **Accuracy Bar Chart**: Visual comparison of average accuracy across models
- **Cost vs Accuracy Trade-off**: Scatter plot showing the relationship between cost and performance

### **Detailed Model Analysis**
- **Key Metrics**: Average accuracy, number of items, best/worst performance
- **Performance Metrics**: Average latency, total cost, average cost per experiment
- **Relationship Curves**: 
  - **Accuracy vs Cost**: Shows how cost changes with accuracy for each model
  - **Accuracy vs Latency**: Shows how latency changes with accuracy for each model

### **Model Recommendations**
- **Best Overall Performance**: Model with highest accuracy
- **Most Cost-Effective**: Model with best accuracy/cost ratio
- **Detailed Rankings**: Top models by accuracy, cost, and efficiency

## Data Sources

The application can work with two types of experiment data:

1. **Local Experiments**: Run directly through the UI and stored in session state
2. **Langfuse Experiments**: Historical data loaded from Langfuse datasets

### **Auto-Loading**
- Data automatically loads when accessing History or Model Comparison pages
- Uses the current dataset from session state
- No manual button clicks required

## Metrics Explained

- **Avg Accuracy (%)**: Average performance across all items
- **Std Accuracy**: Consistency measure (±X% indicates variation range)
- **Number of Items**: How many individual items were tested
- **Avg Cost ($)**: Average cost per experiment (not per item)
- **Avg Latency**: Average response time per experiment

*Note: "N/A" in Std Accuracy means only one experiment was performed - need multiple experiments to measure consistency.*

## Key Visualizations

1. **Performance Summary Table**: Aggregated metrics for each model
2. **Accuracy Comparison**: Bar chart with color coding
3. **Cost vs Performance**: Scatter plot with size indicating number of items
4. **Relationship Curves**: Line charts showing accuracy-cost and accuracy-latency relationships
5. **Individual Model Analysis**: Detailed breakdown for selected models

## Data Structure

The application processes experiment data at the item level:
- Each experiment run contains multiple items
- Metrics are calculated per item for granular analysis
- Cost and latency are shown per experiment (not divided by items)
- Standard deviation measures consistency across experiments

## Troubleshooting

### **No Data Loading**
- Check your dataset name in Langfuse
- Ensure experiments have been run for the selected dataset
- Verify Langfuse connection and permissions

### **Incorrect Metrics**
- Cost shows total experiment cost (not per item)
- Latency shows total experiment latency (not per item)
- Standard deviation requires multiple experiments per model

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
