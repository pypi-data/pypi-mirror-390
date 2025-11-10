# DConfusion
A Python package for working with confusion matrices - now with a web UI!

## Overview
`dconfusion` is a comprehensive Python package for working with confusion matrices, supporting both binary and multi-class classification. It now includes a beautiful Streamlit web interface for comparing multiple models side-by-side.

## ✨ New: Web Interface!

Launch the interactive web app to compare confusion matrices visually:

```bash
./run_app.sh
# or
streamlit run app/streamlit_app.py
```

**Features:**
- 📊 Compare multiple models side-by-side
- 📈 Interactive visualizations and metrics
- 📥 Export comparisons as CSV
- 🎯 Identify best-performing models instantly

[See QUICKSTART.md for detailed instructions](QUICKSTART.md)

## Features
* **Binary & Multi-class Support** - Works with 2+ classes
* **Comprehensive Metrics** - Accuracy, Precision, Recall, F1, MCC, Cohen's Kappa, and more
* **Flexible Input** - From values, matrix, or prediction lists
* **Visualization** - Beautiful matplotlib plots with metrics panels
* **Import/Export** - CSV, JSON, dict formats
* **Web UI** - Streamlit app for easy comparison
* **⚠️ NEW: Warning System** - Research-based warnings for common pitfalls (sample size, class imbalance, metric reliability)
* **Modular Design** - Clean separation: core, metrics, visualization, I/O

## Installation
You can install `dconfusion` using pip:

```bash
pip install dconfusion
```

Usage
Here's an example of how to use dconfusion:

# Binary classification (existing usage)
``` python
binary_cm = DConfusion(80, 70, 10, 20)
```

# Multi-class from matrix
``` python
multiclass_cm = DConfusion(
    confusion_matrix=[[50, 3, 2], [8, 45, 1], [4, 2, 48]], 
    labels=['Cat', 'Dog', 'Bird']
)
```

# Multi-class from predictions
``` python
y_true = ['Cat', 'Dog', 'Bird', 'Cat', 'Dog']
y_pred = ['Cat', 'Dog', 'Cat', 'Cat', 'Dog']  
cm = DConfusion.from_predictions(y_true, y_pred)
```

# Get class-specific metrics
``` python
# Get metrics for a specific class
cat_metrics = multiclass_cm.get_class_metrics(class_label='Cat')
# Returns: {'precision': 0.91, 'recall': 0.83, 'f1_score': 0.87, 'specificity': 0.95}
```

# Get overall metrics
```
overall_metrics = multiclass_cm.get_all_metrics()
```

# Plot confusion matrix
```python
cm = DConfusion(80, 70, 10, 20)
fig = cm.plot()

# Normalized with custom styling
fig2 = cm.plot(normalize=True, cmap='Blues', figsize=(10, 8))

# With metrics panel (binary only)
fig3 = cm.plot(show_metrics=True)

multiclass_cm = DConfusion(
    confusion_matrix=[[50, 3, 2], [8, 45, 1], [4, 2, 48]],
    labels=['Cat', 'Dog', 'Bird']
)

fig4 = multiclass_cm.plot(normalize=True, cmap='cool') # If we show metrics, only accuracy is displayed
fig4.show()
```

## ⚠️ Warning System (NEW!)

DConfusion now includes a comprehensive warning system based on peer-reviewed research on binary classification metrics. It automatically detects common pitfalls like:

- **Small sample sizes** that lead to high metric uncertainty
- **Class imbalance** with insufficient samples per class
- **Misleading accuracy** when it's close to majority class proportion
- **Perfect classification** that might indicate data leakage
- **Zero cells** (TP, TN, FP, or FN = 0) that make metrics undefined
- **Poor basic rates** hidden by high accuracy or ROC AUC
- **Unreliable comparisons** due to sample size or uncertainty issues

### Quick Start

```python
from dconfusion import DConfusion

# Create a confusion matrix
cm = DConfusion(true_positive=10, false_negative=5,
                false_positive=3, true_negative=12)

# Print warnings
cm.print_warnings()

# Or access warnings programmatically
warnings = cm.check_warnings()
for warning in warnings:
    print(warning.severity, warning.category, warning.message)

# Compare two models with warnings
model_a = DConfusion(tp=48, fn=7, fp=5, tn=40)
model_b = DConfusion(tp=50, fn=5, fp=8, tn=37)
result = model_a.compare_with(model_b, metric='accuracy')

if result['has_warnings']:
    print("Comparison may not be reliable:")
    for w in result['warnings']:
        print(f"  - {w}")
```

### Example Output

```
================================================================================
CONFUSION MATRIX ANALYSIS WARNINGS
================================================================================

WARNING (2):
--------------------------------------------------------------------------------
[WARNING] Sample Size: Total sample size (30) is small. Metric uncertainty
is approximately 1.8x higher than with 100 samples.
  → Recommendation: Collect 70 more samples to reduce uncertainty, or report
    confidence intervals with all metrics.

[WARNING] High Metric Uncertainty: Metric uncertainty is high (±9.1% for
accuracy). With n=30, differences smaller than ~18.2% may not be meaningful.
  → Recommendation: Need 120 samples to halve the uncertainty, or always
    report confidence intervals when comparing models.
================================================================================
```

**📖 For comprehensive documentation, see [WARNINGS_GUIDE.md](WARNINGS_GUIDE.md)**

### Research Foundation

The warning system is based on:
- **Chicco et al.** - Studies on MCC advantages and metric limitations
- **Lovell et al.** - Research showing uncertainty scales as 1/√N
- **Fazekas & Kovács** - Work on numerical consistency in ML evaluation

See `examples/warnings_demo.py` for detailed examples.

# Roadmap
This is the initial release (v0.2.1) of dconfusion, and we plan to add more features in future releases. Some potential features include:
- Backtracing statistical metrics based on partial data
- Integration with popular machine learning libraries

# Contributing
We welcome contributions to dconfusion! If you'd like to contribute, please fork the repository and submit a pull request.

# License
dconfusion is released under the MIT License. See LICENSE for details.

# Changelog
- v0.1: Initial release with basic confusion matrix representation and frequency calculation
- v0.2: Added support for multi-class confusion matrices
- v0.2.1: Added support for plotting confusion matrices
- v0.2.2: Added more metrics and CSV functionality. QOL improvements. Began adding validation functionality.
- Planned: 
  - Added support for multi-class confusion matrices with class level metrics 
  - Break the file into multiple modules