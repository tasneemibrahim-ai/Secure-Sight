# 🚀 SecureSight Visual Analytics - Quick Start Guide

## Installation Check

```bash
# Verify the system is ready
cd tasnim/
python -c "from eval_tracker import RunTracker; print('✓ Ready to go!')"
```

## Basic Example

```python
from eval_tracker import RunTracker
import numpy as np

# ===== STEP 1: Initialize =====
tracker = RunTracker(
    batch_num=1,
    run_idx=1,
    hyperparams={
        'learning_rate': 1e-4,
        'batch_size': 32,
        'dropout': 0.3,
        'optimizer': 'adamw',
        'weight_decay': 1e-5,
        'class_names': ['Normal', 'Exploit', 'Backdoor', 'Poisoning'],
    }
)

# ===== STEP 2: Record Training Progress =====
num_epochs = 20
for epoch in range(num_epochs):
    # Your training code...
    train_loss = 0.234 + np.random.randn() * 0.01
    train_acc = 0.85 + epoch * 0.01 + np.random.randn() * 0.01
    train_f1 = 0.82 + epoch * 0.01
    
    val_loss = 0.267 + np.random.randn() * 0.02
    val_acc = 0.83 + epoch * 0.005
    val_f1 = 0.80 + epoch * 0.005
    
    tracker.record_epoch({
        'epoch': epoch + 1,
        'train_loss': train_loss,
        'val_loss': val_loss,
        'train_acc': train_acc,
        'val_acc': val_acc,
        'train_f1': train_f1,
        'val_f1': val_f1,
    })

# ===== STEP 3: Collect Final Metrics =====
final_metrics = {
    'accuracy': 0.92,
    'precision': 0.90,
    'recall': 0.91,
    'f1': 0.905,
    'auc': 0.94,
    'loss': 0.25,
    'confusion_matrix': [
        [100, 5, 2, 1],
        [4, 98, 3, 2],
        [1, 2, 99, 3],
        [2, 1, 2, 98]
    ],
    'per_class': {
        'Normal': {'precision': 0.91, 'recall': 0.91, 'f1': 0.91, 'support': 108},
        'Exploit': {'precision': 0.89, 'recall': 0.89, 'f1': 0.89, 'support': 107},
        'Backdoor': {'precision': 0.92, 'recall': 0.90, 'f1': 0.91, 'support': 105},
        'Poisoning': {'precision': 0.90, 'recall': 0.89, 'f1': 0.90, 'support': 103},
    }
}

# ===== STEP 4: Measure Latency =====
latency_samples = np.random.gamma(shape=2, scale=5, size=1000)  # in milliseconds
latency_stats = {
    'mean_ms': float(np.mean(latency_samples)),
    'std_ms': float(np.std(latency_samples)),
    'p95_ms': float(np.percentile(latency_samples, 95)),
    'p99_ms': float(np.percentile(latency_samples, 99)),
    'samples': latency_samples.tolist(),
}

# ===== STEP 5: Finalize & Generate All Plots =====
val_labels = np.array([0, 0, 1, 2, ...])  # true labels
val_probs = np.random.rand(1000, 4)      # predicted probabilities
val_probs /= val_probs.sum(axis=1, keepdims=True)  # normalize

tracker.finalize(
    final_metrics=final_metrics,
    latency=latency_stats,
    eval_labels=val_labels,
    eval_probs=val_probs,
)
# ✓ Automatically generates:
#   - 10 per-run plots in ./evaluation/detailed_batches/batch_1/run_1/plots/
#   - Per-run report
#   - Batch comparisons (if all runs in batch complete)
#   - Global analysis (if all batches complete)
```

## Output Structure After First Run

```
evaluation/
└── detailed_batches/
    └── batch_1/
        └── run_1/
            ├── plots/                    (10 PNG files)
            │   ├── training_loss.png
            │   ├── val_loss.png
            │   ├── accuracy.png
            │   ├── f1.png
            │   ├── roc_curve.png
            │   ├── pr_curve.png
            │   ├── confusion_matrix.png
            │   ├── per_class_bar.png
            │   ├── radar_per_class.png
            │   └── latency.png
            ├── epoch_results.csv         (training progression)
            ├── run_summary.json          (metadata + metrics)
            └── report.txt                (detailed analysis)
```

## Full Output After 25 Runs (5 Batches × 5 Runs)

```
evaluation/
├── detailed_batches/                     (Per-run analysis)
│   ├── batch_1/
│   │   ├── run_1/  ✓ 10 plots + report
│   │   ├── run_2/  ✓ 10 plots + report
│   │   ├── run_3/  ✓ 10 plots + report
│   │   ├── run_4/  ✓ 10 plots + report
│   │   └── run_5/  ✓ 10 plots + report
│   ├── batch_2/    (same structure)
│   ├── batch_3/    (same structure)
│   ├── batch_4/    (same structure)
│   └── batch_5/    (same structure)
│
├── batches_comparison/                   (Batch-level analysis)
│   ├── batch_1/
│   │   ├── comparison_plots/
│   │   │   ├── batch_runs_accuracy.png
│   │   │   ├── batch_runs_f1.png
│   │   │   ├── batch_runs_loss.png
│   │   │   ├── batch_runs_latency.png
│   │   │   └── batch_radar_comparison.png
│   │   └── batch_report.txt
│   ├── batch_2/    (same structure)
│   └── ...batch_5/
│
└── global_analysis/                      (Global level analysis)
    ├── GLOBAL_PLOTS/
    │   ├── all_batches_accuracy.png
    │   ├── all_batches_f1.png
    │   ├── all_batches_loss.png
    │   ├── all_batches_latency.png
    │   ├── stability_score.png
    │   ├── performance_heatmap.png
    │   ├── best_vs_worst.png
    │   └── hyperparameter_impact.png
    ├── GLOBAL_REPORT.txt               (DEPLOYMENT GUIDE)
    └── GLOBAL_STATS.json               (Structured metrics)

Total: 25 runs × 10 plots + 5 batches × 5 plots + 8 global plots
     = 250 + 25 + 8 = 283 PNG files + reports
```

## Running 5 Batches Complete Example

```python
from eval_tracker import RunTracker

BATCHES = 5
RUNS_PER_BATCH = 5

# Define hyperparameters per batch
batch_configs = {
    1: {'lr': 1e-4, 'bs': 32, 'dropout': 0.3},
    2: {'lr': 5e-5, 'bs': 32, 'dropout': 0.2},
    3: {'lr': 2e-4, 'bs': 64, 'dropout': 0.4},
    4: {'lr': 1e-4, 'bs': 64, 'dropout': 0.1},
    5: {'lr': 8e-5, 'bs': 128, 'dropout': 0.3},
}

for batch_num in range(1, BATCHES + 1):
    config = batch_configs[batch_num]
    
    for run_idx in range(1, RUNS_PER_BATCH + 1):
        print(f"\n{'='*60}")
        print(f"Running Batch {batch_num}, Run {run_idx}")
        print(f"{'='*60}")
        
        # Initialize tracker (note: batch_num must match!)
        tracker = RunTracker(
            batch_num=batch_num,
            run_idx=run_idx,
            hyperparams={
                'learning_rate': config['lr'],
                'batch_size': config['bs'],
                'dropout': config['dropout'],
                'optimizer': 'adamw',
                'weight_decay': 1e-5,
                'class_names': ['Normal', 'Exploit', 'Backdoor', 'Poisoning'],
            }
        )
        
        # Train model...
        model = build_model()
        for epoch in range(20):
            train_loss, train_acc = train_epoch(model)
            val_loss, val_acc = validate(model)
            tracker.record_epoch({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'train_acc': train_acc,
                'val_acc': val_acc,
                'train_f1': train_acc,  # simplified
                'val_f1': val_acc,
            })
        
        # Evaluate...
        final_metrics = evaluate(model)
        latency_stats = measure_latency(model)
        
        # Finalize (automatically generates batch & global reports)
        tracker.finalize(
            final_metrics=final_metrics,
            latency=latency_stats,
            eval_labels=val_labels,
            eval_probs=val_probs,
        )

print("\n" + "="*60)
print("✓ ALL 25 RUNS COMPLETE!")
print("="*60)
print("\nView results:")
print("  • Per-run plots: evaluation/detailed_batches/batch_*/run_*/plots/")
print("  • Batch comparison: evaluation/batches_comparison/batch_*/comparison_plots/")
print("  • Global analysis: evaluation/global_analysis/GLOBAL_PLOTS/")
print("  • Deployment guide: evaluation/global_analysis/GLOBAL_REPORT.txt")
```

## Key Files Generated

| File Type | Count | Location | Purpose |
|-----------|-------|----------|---------|
| Per-run plots | 250 | `detailed_batches/batch_*/run_*/plots/*.png` | Individual run analysis |
| Per-run reports | 25 | `detailed_batches/batch_*/run_*/report.txt` | Detailed metrics per run |
| Batch comparison plots | 25 | `batches_comparison/batch_*/comparison_plots/*.png` | 5 plots × 5 batches |
| Batch reports | 5 | `batches_comparison/batch_*/batch_report.txt` | Batch statistics |
| Global plots | 8 | `global_analysis/GLOBAL_PLOTS/*.png` | System-wide analysis |
| Global report | 1 | `global_analysis/GLOBAL_REPORT.txt` | **DEPLOYMENT DECISION** |
| Stats JSON | 1 | `global_analysis/GLOBAL_STATS.json` | Structured metrics |

## Key Metrics in Reports

### Per-Run Report Includes:
✓ Hyperparameters  
✓ Final metrics (Acc, Prec, Rec, F1, AUC)  
✓ Latency statistics (mean, std, p95, p99)  
✓ Per-class performance  
✓ Epoch-by-epoch progression  

### Batch Report Includes:
✓ Summary of 5 runs  
✓ Stability analysis (std deviation)  
✓ Best & worst run  
✓ Batch hyperparameters  

### Global Report Includes:
✓ Top 10 runs ranked  
✓ Batch ranking by F1  
✓ Stability ranking  
✓ **BEST MODEL RECOMMENDED** (batch/run)  
✓ Recommended hyperparameters  
✓ Accuracy-latency tradeoff analysis  
✓ **DEPLOYMENT RECOMMENDATION**  

## Reading the Global Report

The GLOBAL_REPORT.txt is your deployment decision guide. Look for:

```
BEST MODEL FOR DEPLOYMENT:
  Batch: batch_1
  Run:   run_3
  F1:    0.9234
  Accuracy: 0.9345
  Latency: 12.34ms

RECOMMENDED HYPERPARAMETERS:
  learning_rate: 0.0001
  batch_size: 32
  dropout: 0.3
  optimizer: adamw
  weight_decay: 0.00001

DEPLOYMENT RECOMMENDATION:
  ✓ Use batch_1/run_3 as production model
  ✓ Expected F1 score in production: 0.9234
  ✓ Expected inference latency: 12.34ms per batch
  ✓ Validate on production dataset before full deployment
```

## Tips & Tricks

### 1. Understanding Stability Scores
- **1.0**: All runs in batch have identical performance (perfect stability)
- **0.8+**: Very stable (recommended for production)
- **0.5-0.8**: Moderate variance (acceptable)
- **<0.5**: High variance (consider retraining)

### 2. Interpreting Confusion Matrix
- Diagonal elements = correct predictions
- Off-diagonal = misclassifications
- Large off-diagonal values = model confuses these classes

### 3. ROC/PR Curves
- Closer to top-left = better performance
- Vertical distance = precision at given recall
- Area Under Curve (AUC) = single-number score

### 4. Latency Distribution
- Bell curve shape = consistent latency (good)
- Long tail = occasional slow inferences (bad)
- Mean < 50ms = suitable for real-time (typical)

### 5. Heatmaps
- Bright colors = high performance
- Dark colors = low performance
- Scan for patterns across batches

## Common Scenarios

### Scenario 1: Great Accuracy, Variable Latency
```
→ Check latency.png for each run
→ Use run with good accuracy AND low latency
→ Consider batch size / model optimization
```

### Scenario 2: One Batch Much Better Than Others
```
→ Use that batch's best run for deployment
→ Investigate why: Is it the hyperparameters?
→ Consider ensemble approach if similar

```

### Scenario 3: Overfitting Detected
```
Training Loss keeps decreasing
Validation Loss starts increasing
→ Use run with best validation metrics
→ Consider higher dropout in next batch
→ Check per_class_bar.png for class-wise issues
```

---

**Generated for SecureSight Full Visual Analytics System**
