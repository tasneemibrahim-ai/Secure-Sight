"""
Regenerate global metrics with variance, median, and count.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

EVAL_DIR = Path('evaluation')
STAT_DIR = EVAL_DIR / 'statistical_analysis'
DETAILED_DIR = EVAL_DIR / 'detailed_batches'

# Load all run summaries
all_metrics = {
    'accuracy': [],
    'precision': [],
    'recall': [],
    'f1_score': [],
    'auc': [],
    'latency': []
}

for batch_dir in sorted(DETAILED_DIR.glob('batch_*')):
    for run_dir in sorted(batch_dir.glob('run_*')):
        summary_path = run_dir / 'run_summary.json'
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                metrics = summary.get('final_metrics', {})
                all_metrics['accuracy'].append(metrics.get('accuracy'))
                all_metrics['precision'].append(metrics.get('precision'))
                all_metrics['recall'].append(metrics.get('recall'))
                all_metrics['f1_score'].append(metrics.get('f1'))
                all_metrics['auc'].append(metrics.get('auc'))
                latency_mean = summary.get('latency', {}).get('mean_ms')
                all_metrics['latency'].append(latency_mean)

# Calculate statistics for each metric
global_metrics = {}
for metric_name, values in all_metrics.items():
    clean_values = [v for v in values if v is not None]
    if clean_values:
        global_metrics[metric_name] = {
            'mean': float(np.mean(clean_values)),
            'std': float(np.std(clean_values)),
            'variance': float(np.var(clean_values)),
            'min': float(np.min(clean_values)),
            'max': float(np.max(clean_values)),
            'median': float(np.median(clean_values)),
            'count': int(len(clean_values))
        }

# Save global metrics
metrics_file = STAT_DIR / 'summary' / 'global_metrics.json'
metrics_file.parent.mkdir(parents=True, exist_ok=True)

with open(metrics_file, 'w') as f:
    json.dump(global_metrics, f, indent=2)

print(f"✓ Regenerated global metrics with variance, median, count")
print(f"Metrics: {list(global_metrics.keys())}")
for metric, stats in list(global_metrics.items())[:2]:
    print(f"  {metric}: count={stats['count']}, mean={stats['mean']:.6f}, variance={stats['variance']:.6f}, median={stats['median']:.6f}")

# Also regenerate per-batch metrics
per_batch_metrics = {}
for batch_dir in sorted(DETAILED_DIR.glob('batch_*')):
    batch_id = batch_dir.name.replace('batch_', '')
    batch_metrics = {
        'accuracy': [],
        'precision': [],
        'recall': [],
        'f1_score': [],
        'auc': [],
        'latency': []
    }
    
    for run_dir in sorted(batch_dir.glob('run_*')):
        summary_path = run_dir / 'run_summary.json'
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                metrics = summary.get('final_metrics', {})
                batch_metrics['accuracy'].append(metrics.get('accuracy'))
                batch_metrics['precision'].append(metrics.get('precision'))
                batch_metrics['recall'].append(metrics.get('recall'))
                batch_metrics['f1_score'].append(metrics.get('f1'))
                batch_metrics['auc'].append(metrics.get('auc'))
                latency_mean = summary.get('latency', {}).get('mean_ms')
                batch_metrics['latency'].append(latency_mean)
    
    # Calculate stats for this batch
    batch_stats = {}
    for metric_name, values in batch_metrics.items():
        clean_values = [v for v in values if v is not None]
        if clean_values:
            batch_stats[metric_name] = {
                'mean': float(np.mean(clean_values)),
                'std': float(np.std(clean_values)),
                'variance': float(np.var(clean_values)),
                'min': float(np.min(clean_values)),
                'max': float(np.max(clean_values)),
                'median': float(np.median(clean_values)),
                'count': int(len(clean_values))
            }
    
    per_batch_metrics[batch_id] = batch_stats

# Save per-batch metrics
per_batch_file = STAT_DIR / 'summary' / 'per_batch_metrics.json'
with open(per_batch_file, 'w') as f:
    json.dump(per_batch_metrics, f, indent=2)

print(f"\n✓ Regenerated per-batch metrics")
print(f"Batches: {list(per_batch_metrics.keys())}")
