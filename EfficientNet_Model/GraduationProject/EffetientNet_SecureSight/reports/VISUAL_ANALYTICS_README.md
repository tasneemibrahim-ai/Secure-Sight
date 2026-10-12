# SecureSight Full Visual Analytics System

## 📊 Overview

The SecureSight evaluation pipeline now includes **comprehensive visual analytics** at three levels:
- **Per-Run Level**: 10 detailed plots + full report
- **Batch Level**: 5 comparison plots + batch analysis
- **Global Level**: 8 global plots + comprehensive rankings + deployment recommendations

## 🏗️ Output Directory Structure

```
evaluation/
├── detailed_batches/
│   ├── batch_1/
│   │   ├── run_1/
│   │   │   ├── plots/                    # 10 PNG plots per run
│   │   │   │   ├── training_loss.png     # Train vs val loss
│   │   │   │   ├── val_loss.png          # Validation loss only
│   │   │   │   ├── accuracy.png          # Train vs val accuracy
│   │   │   │   ├── f1.png                # Train vs val F1
│   │   │   │   ├── roc_curve.png         # ROC curve (OVR)
│   │   │   │   ├── pr_curve.png          # Precision-Recall curve
│   │   │   │   ├── confusion_matrix.png  # Confusion matrix heatmap
│   │   │   │   ├── per_class_bar.png     # Per-class metrics bars
│   │   │   │   ├── radar_per_class.png   # Radar chart per-class
│   │   │   │   └── latency.png           # Latency distribution
│   │   │   ├── epoch_results.csv         # Detailed epoch data
│   │   │   ├── run_summary.json          # Run metadata & metrics
│   │   │   └── report.txt                # Detailed run report
│   │   ├── run_2/
│   │   │   └── ... (same structure)
│   │   ├── ...
│   │   └── run_5/
│   │
│   ├── batch_2/
│   │   └── ... (5 runs)
│   └── ...batch_5/
│
├── batches_comparison/
│   ├── batch_1/
│   │   ├── comparison_plots/             # 5 PNG plots per batch
│   │   │   ├── batch_runs_accuracy.png   # Accuracy comparison bar
│   │   │   ├── batch_runs_f1.png         # F1 comparison bar
│   │   │   ├── batch_runs_loss.png       # Loss comparison line
│   │   │   ├── batch_runs_latency.png    # Latency comparison bar
│   │   │   └── batch_radar_comparison.png # Overlay radar chart
│   │   └── batch_report.txt              # Batch statistics & analysis
│   └── ...batch_5/
│
└── global_analysis/
    ├── GLOBAL_PLOTS/                     # 8 PNG plots (global level)
    │   ├── all_batches_accuracy.png      # Mean accuracy per batch
    │   ├── all_batches_f1.png            # Mean F1 per batch
    │   ├── all_batches_loss.png          # Mean loss per batch
    │   ├── all_batches_latency.png       # Mean latency per batch
    │   ├── stability_score.png           # Stability ranking
    │   ├── performance_heatmap.png       # Performance matrix
    │   ├── best_vs_worst.png             # Best vs worst comparison
    │   └── hyperparameter_impact.png     # HP impact analysis
    ├── GLOBAL_REPORT.txt                 # Comprehensive global report
    └── GLOBAL_STATS.json                 # Structured statistics
```

## 📈 Plots Per Run (10 Total)

### 1. **training_loss.png**
- **What**: Training vs Validation Loss curves
- **Why**: Detect overfitting/underfitting patterns
- **Format**: Line plot with epochs on x-axis

### 2. **val_loss.png**
- **What**: Validation Loss only (zoomed in)
- **Why**: Focus on generalization performance
- **Format**: Single line plot

### 3. **accuracy.png**
- **What**: Training vs Validation Accuracy
- **Why**: Track overall classification improvement
- **Format**: Line plot with both curves

### 4. **f1.png**
- **What**: Training vs Validation F1 Score (macro)
- **Why**: Monitor balanced performance
- **Format**: Line plot

### 5. **roc_curve.png**
- **What**: ROC Curve (One-vs-Rest for multi-class)
- **Why**: Evaluate classification at different thresholds
- **Format**: Multi-class ROC with AUC scores

### 6. **pr_curve.png**
- **What**: Precision-Recall Curve (One-vs-Rest)
- **Why**: Assess precision/recall tradeoff
- **Format**: Multi-class PR with AP scores

### 7. **confusion_matrix.png**
- **What**: Heatmap of predictions vs truth
- **Why**: Identify misclassification patterns
- **Format**: Annotated heatmap

### 8. **per_class_bar.png**
- **What**: Per-class Precision, Recall, F1 (grouped bars)
- **Why**: Identify problematic classes
- **Format**: Grouped bar chart

### 9. **radar_per_class.png**
- **What**: Radar chart showing per-class recall
- **Why**: Visual comparison of class-wise performance
- **Format**: Polar/radar chart

### 10. **latency.png**
- **What**: Inference latency distribution histogram
- **Why**: Assess inference speed consistency
- **Format**: Histogram with bins

## 📊 Batch-Level Plots (5 Per Batch)

### 1. **batch_runs_accuracy.png**
- Compares accuracy across 5 runs in batch
- Bar chart with error bars showing stability

### 2. **batch_runs_f1.png**
- Compares F1 scores across runs
- Bar chart highlighting best/worst runs

### 3. **batch_runs_loss.png**
- Loss comparison as line plot
- Shows convergence consistency

### 4. **batch_runs_latency.png**
- Latency bar chart across runs
- Identifies latency outliers

### 5. **batch_radar_comparison.png**
- Overlay radar charts for all 5 runs
- Shows performance signature per run

**Batch Report Includes:**
- Mean/std statistics per metric
- Best & worst run identification
- Stability analysis
- Hyperparameters summary

## 🌍 Global Analysis Plots (8 Total)

### 1. **all_batches_accuracy.png**
- Mean accuracy per batch comparison
- Identifies most accurate batch

### 2. **all_batches_f1.png**
- Mean F1 per batch
- Key metric for balanced evaluation

### 3. **all_batches_loss.png**
- Mean loss per batch
- Convergence comparison

### 4. **all_batches_latency.png**
- Mean latency per batch
- Speed vs accuracy tradeoff

### 5. **stability_score.png**
- Custom stability metric (1.0 = perfect stability)
- Based on F1 and accuracy std deviation
- Ranks batches by consistency

### 6. **performance_heatmap.png**
- 3D performance matrix: accuracy, F1, latency (normalized)
- One row per batch
- Quick visual identification of sweet spots

### 7. **best_vs_worst.png**
- Side-by-side comparison of best and worst models
- Metrics: Accuracy, F1, Precision, Recall, AUC
- Deployment decision support

### 8. **hyperparameter_impact.png**
- Shows how hyperparameters affect F1 per batch
- Links batch composition to performance
- Helps understand hyperparameter sensitivity

## 📋 Global Report (GLOBAL_REPORT.txt)

Contains:
- **Top 10 Runs**: Ranked by F1 score with full metrics
- **Batch Ranking**: By mean F1 with stability (std dev)
- **Stability Ranking**: Which batches are most consistent
- **Best Model for Deployment**: Specific batch/run recommendation
- **Recommended Hyperparameters**: From best run
- **Performance Summary**: Global statistics
- **Accuracy-Latency Tradeoff Analysis**: Speed vs accuracy
- **Deployment Recommendation**: Actionable guidance

## 📊 Global Stats (GLOBAL_STATS.json)

Structured JSON containing:
```json
{
  "total_runs": 25,
  "total_batches": 5,
  "timestamp": "2026-05-03T...",
  "batch_statistics": {
    "batch_1": {
      "accuracy": {"mean": 0.9234, "std": 0.0045},
      "f1": {"mean": 0.9187, "std": 0.0052},
      "latency": {"mean": 12.34, "std": 0.89},
      "count": 5
    },
    ...
  },
  "overall": {
    "best_run": {
      "batch": "batch_1",
      "run": "run_1",
      "f1": 0.9345,
      "accuracy": 0.9456,
      "latency_ms": 11.23
    },
    "mean_accuracy": 0.9234,
    "mean_f1": 0.9187,
    "mean_latency_ms": 12.34
  }
}
```

## 🚀 Usage

### Basic Usage in Training Script

```python
from eval_tracker import RunTracker
import torch

# Initialize tracker for a run
tracker = RunTracker(
    batch_num=1,
    run_idx=1,
    hyperparams={
        'learning_rate': 1e-4,
        'batch_size': 32,
        'dropout': 0.3,
        'optimizer': 'adamw',
        'weight_decay': 1e-5,
        'class_names': ['Normal', 'Attack1', 'Attack2'],
    }
)

# Record epochs during training
for epoch in range(num_epochs):
    train_loss, train_acc, train_f1 = train_epoch()
    val_loss, val_acc, val_f1 = validate()
    
    tracker.record_epoch({
        'epoch': epoch + 1,
        'train_loss': train_loss,
        'val_loss': val_loss,
        'train_acc': train_acc,
        'val_acc': val_acc,
        'train_f1': train_f1,
        'val_f1': val_f1,
    })

# Finalize with final metrics
final_metrics = compute_final_metrics(model, val_loader)
latency_stats = measure_latency(model, val_loader)

tracker.finalize(
    final_metrics=final_metrics,
    latency=latency_stats,
    eval_labels=val_labels,
    eval_probs=val_probabilities,
)
```

### Generate Batch & Global Reports

```python
# After running all 5 runs in a batch:
RunTracker.generate_batch_report(batch_num=1)

# After all 25 runs complete:
RunTracker.generate_global_report()
```

### Directory Structure Customization

By default, output goes to `./evaluation/`. To change:

```python
# In path_setup.py, modify get_evaluation_base_dir()
def get_evaluation_base_dir() -> str:
    return "/path/to/custom/evaluation/dir"
```

## 📐 Metrics Computed

**Per Run:**
- Accuracy, Precision, Recall, F1, AUC
- Per-class Precision/Recall/F1
- Loss (training & validation)
- Latency (mean, std, p95, p99)
- Confusion matrix

**Per Batch:**
- Mean & Std of all metrics
- Stability scores
- Best & worst run
- Aggregate statistics

**Globally:**
- Top 10 runs ranking
- Batch ranking by F1
- Stability ranking
- Best model overall
- Hyperparameter analysis
- Performance heatmaps

## 🎯 Key Features

✅ **No Training Changes**: Pure evaluation layer  
✅ **No Runtime Slowdown**: Evaluation post-training  
✅ **Matplotlib Only**: No seaborn dependency  
✅ **Auto-Generated**: Folders created automatically  
✅ **Fully Reproducible**: Timestamps & seeds tracked  
✅ **Class Mapping**: Uses config.py CLASS_NAMES  
✅ **Professional**: Thesis-ready figures  
✅ **Interpretable**: Text reports + plots  
✅ **Deployment-Ready**: Explicit recommendations

## 📈 Typical Workflow

```
1. Run 5 batches × 5 runs (25 total)
   ↓
2. Each run generates:
   - 10 detailed plots
   - Run report
   - Epoch CSV
   - Summary JSON
   ↓
3. After each batch:
   - 5 batch comparison plots
   - Batch report
   ↓
4. After all complete:
   - 8 global plots
   - Global report
   - Stats JSON
   ↓
5. Use GLOBAL_REPORT.txt to choose deployment model
```

## 🔍 Interpreting Results

### High Stability, High Accuracy
- ✅ **Best scenario**: This batch/run is production-ready
- Action: Deploy with confidence

### High Accuracy, Low Stability
- ⚠️ **Caution**: Some runs are excellent, others mediocre
- Action: Use best run, but validate thoroughly
- Investigate: Why is stability low?

### Low Accuracy
- ❌ **Poor performance**: Model needs retaining
- Action: Adjust hyperparameters, try next batch
- Investigate: Check confusion matrix for problematic classes

### High Latency
- ⏱️ **Slow inference**: May not meet production SLAs
- Action: Optimize model size or batch processing
- Compare: Can accept small accuracy drop for speed?

### Overfitting Pattern
- 📈 **Training loss << Validation loss**
- Visible in: training_loss.png, accuracy.png
- Action: Increase dropout, add regularization

## 🛠️ Troubleshooting

**Q: Some plots are missing**
- A: Check that final_metrics and latency are provided to tracker.finalize()

**Q: Reports are empty**
- A: Ensure all runs completed successfully (status='completed' in JSON)

**Q: Latency histogram shows no data**
- A: Latency dict must have 'samples' key with list of millisecond values

**Q: Class names don't appear correctly**
- A: Pass class_names in hyperparams dict when initializing RunTracker

## 📚 File Reference

| File | Purpose | Auto-Generated |
|------|---------|---|
| training_loss.png | Loss curves | ✓ |
| accuracy.png | Accuracy tracking | ✓ |
| confusion_matrix.png | Misclassification analysis | ✓ |
| roc_curve.png | Threshold analysis | ✓ |
| batch_runs_accuracy.png | Batch comparison | ✓ |
| batch_report.txt | Batch analysis | ✓ |
| GLOBAL_REPORT.txt | Deployment guidance | ✓ |
| GLOBAL_STATS.json | Structured data | ✓ |
| epoch_results.csv | Epoch-by-epoch data | ✓ |
| run_summary.json | Run metadata | ✓ |

## ✨ Advanced Features

- **Stability Metric**: Custom calculation based on metric std dev
- **OVR ROC/PR**: Proper multi-class curve handling
- **Heatmaps**: Color-coded performance visualization
- **Radar Charts**: Multi-dimensional performance overview
- **Auto-Folders**: All directories created on-demand
- **Error Handling**: Graceful failures for missing data

---

**Generated by SecureSight Full Visual Analytics System**
