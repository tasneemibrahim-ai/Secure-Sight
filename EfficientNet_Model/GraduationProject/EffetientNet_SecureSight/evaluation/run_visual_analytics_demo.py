#!/usr/bin/env python3
"""
SecureSight Visual Analytics - Full 25-Run Pipeline Demo
Generates complete evaluation output for testing the visual analytics system.
"""

# Set matplotlib backend BEFORE any other imports
import matplotlib
matplotlib.use('Agg')

import os
import sys
import numpy as np
import random
from eval_tracker import RunTracker

def simulate_training_metrics(epoch, base_acc=0.8, base_loss=0.4):
    """Simulate realistic training progression"""
    progress = epoch / 20.0  # 20 epochs total

    # Training improves over time with some noise
    train_loss = base_loss * (1 - progress * 0.7) + np.random.randn() * 0.02
    train_acc = base_acc + progress * 0.15 + np.random.randn() * 0.01
    train_f1 = train_acc - 0.02 + np.random.randn() * 0.01

    # Validation slightly worse than training
    val_loss = train_loss + 0.03 + np.random.randn() * 0.02
    val_acc = train_acc - 0.02 + np.random.randn() * 0.01
    val_f1 = train_f1 - 0.02 + np.random.randn() * 0.01

    return {
        'train_loss': max(0.1, train_loss),
        'val_loss': max(0.1, val_loss),
        'train_acc': min(0.98, max(0.5, train_acc)),
        'val_acc': min(0.98, max(0.5, val_acc)),
        'train_f1': min(0.98, max(0.5, train_f1)),
        'val_f1': min(0.98, max(0.5, val_f1)),
    }

def simulate_final_metrics(batch_num, run_idx):
    """Simulate final evaluation metrics with batch/run variation"""
    # Base performance varies by batch (different hyperparameters)
    batch_base = {
        1: 0.88,  # lr=1e-4, bs=32, dropout=0.3
        2: 0.86,  # lr=5e-5, bs=32, dropout=0.2
        3: 0.90,  # lr=2e-4, bs=64, dropout=0.4
        4: 0.87,  # lr=1e-4, bs=64, dropout=0.1
        5: 0.89,  # lr=8e-5, bs=128, dropout=0.3
    }

    base_acc = batch_base[batch_num]
    # Add run variation (stability test)
    run_variation = np.random.randn() * 0.02
    final_acc = base_acc + run_variation

    # Generate confusion matrix (4 classes)
    cm = np.random.randint(90, 110, (4, 4))
    # Make diagonal dominant
    for i in range(4):
        cm[i,i] = np.random.randint(95, 105)
        for j in range(4):
            if i != j:
                cm[i,j] = np.random.randint(1, 8)

    return {
        'accuracy': final_acc,
        'precision': final_acc - 0.01 + np.random.randn() * 0.01,
        'recall': final_acc - 0.005 + np.random.randn() * 0.01,
        'f1': final_acc - 0.007 + np.random.randn() * 0.01,
        'auc': final_acc + 0.02 + np.random.randn() * 0.01,
        'loss': 0.25 - (final_acc - 0.8) * 0.5 + np.random.randn() * 0.02,
        'confusion_matrix': cm.tolist(),
        'per_class': {
            'Normal': {
                'precision': final_acc + np.random.randn() * 0.02,
                'recall': final_acc + np.random.randn() * 0.02,
                'f1': final_acc + np.random.randn() * 0.02,
                'support': np.random.randint(95, 110)
            },
            'Exploit': {
                'precision': final_acc - 0.01 + np.random.randn() * 0.02,
                'recall': final_acc - 0.01 + np.random.randn() * 0.02,
                'f1': final_acc - 0.01 + np.random.randn() * 0.02,
                'support': np.random.randint(95, 110)
            },
            'Backdoor': {
                'precision': final_acc + 0.005 + np.random.randn() * 0.02,
                'recall': final_acc + 0.005 + np.random.randn() * 0.02,
                'f1': final_acc + 0.005 + np.random.randn() * 0.02,
                'support': np.random.randint(95, 110)
            },
            'Poisoning': {
                'precision': final_acc - 0.005 + np.random.randn() * 0.02,
                'recall': final_acc - 0.005 + np.random.randn() * 0.02,
                'f1': final_acc - 0.005 + np.random.randn() * 0.02,
                'support': np.random.randint(95, 110)
            },
        }
    }

def simulate_latency(batch_num):
    """Simulate latency measurements (varies by batch size)"""
    # Larger batch sizes generally have higher latency
    batch_size_multipliers = {1: 1.0, 2: 1.0, 3: 1.2, 4: 1.2, 5: 1.5}

    base_latency = 8.0 * batch_size_multipliers[batch_num]
    samples = np.random.gamma(shape=2, scale=base_latency/2, size=1000)

    return {
        'mean_ms': float(np.mean(samples)),
        'std_ms': float(np.std(samples)),
        'p95_ms': float(np.percentile(samples, 95)),
        'p99_ms': float(np.percentile(samples, 99)),
        'samples': samples.tolist(),
    }

def main():
    print("🚀 SecureSight Visual Analytics - Full Pipeline Demo")
    print("=" * 60)

    # Set random seed for reproducible demo
    np.random.seed(42)
    random.seed(42)

    BATCHES = 5
    RUNS_PER_BATCH = 5

    # Define hyperparameters per batch (different configs for meaningful comparison)
    batch_configs = {
        1: {'lr': 1e-4, 'bs': 32, 'dropout': 0.3, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        2: {'lr': 5e-5, 'bs': 32, 'dropout': 0.2, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        3: {'lr': 2e-4, 'bs': 64, 'dropout': 0.4, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        4: {'lr': 1e-4, 'bs': 64, 'dropout': 0.1, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        5: {'lr': 8e-5, 'bs': 128, 'dropout': 0.3, 'optimizer': 'adamw', 'weight_decay': 1e-5},
    }

    total_runs = 0

    for batch_num in range(1, BATCHES + 1):
        config = batch_configs[batch_num]

        for run_idx in range(1, RUNS_PER_BATCH + 1):
            total_runs += 1
            print(f"\n{'='*60}")
            print(f"Running Batch {batch_num}, Run {run_idx} (Total: {total_runs}/25)")
            print(f"Hyperparams: LR={config['lr']}, BS={config['bs']}, Dropout={config['dropout']}")
            print(f"{'='*60}")

            # Initialize tracker
            tracker = RunTracker(
                batch_num=batch_num,
                run_idx=run_idx,
                hyperparams={
                    'learning_rate': config['lr'],
                    'batch_size': config['bs'],
                    'dropout': config['dropout'],
                    'optimizer': config['optimizer'],
                    'weight_decay': config['weight_decay'],
                    'class_names': ['Normal', 'Exploit', 'Backdoor', 'Poisoning'],
                    'seed': 42 + total_runs,  # Different seed per run for stability testing
                }
            )

            # Simulate training epochs
            num_epochs = 20
            for epoch in range(num_epochs):
                metrics = simulate_training_metrics(epoch, base_acc=0.75 + batch_num * 0.02)
                tracker.record_epoch({
                    'epoch': epoch + 1,
                    **metrics
                })

                if epoch % 5 == 0:  # Progress indicator
                    print(f"  Epoch {epoch+1:2d}: Train Loss={metrics['train_loss']:.3f}, "
                          f"Val Acc={metrics['val_acc']:.3f}")

            # Simulate final evaluation
            final_metrics = simulate_final_metrics(batch_num, run_idx)
            latency_stats = simulate_latency(batch_num)

            # Generate fake eval data for ROC/PR curves
            num_samples = 1000
            val_labels = np.random.randint(0, 4, num_samples)
            val_probs = np.random.rand(num_samples, 4)
            val_probs /= val_probs.sum(axis=1, keepdims=True)  # Normalize to probabilities

            # Finalize (generates ALL plots and reports automatically)
            tracker.finalize(
                final_metrics=final_metrics,
                latency=latency_stats,
                eval_labels=val_labels,
                eval_probs=val_probs,
            )

            print(f"✓ Run {run_idx} complete - F1: {final_metrics['f1']:.3f}, "
                  f"Latency: {latency_stats['mean_ms']:.1f}ms")

    print("\n" + "="*60)
    print("🎉 ALL 25 RUNS COMPLETE!")
    print("="*60)
    print("\n📊 Generated outputs:")
    print("  • Per-run plots: evaluation/detailed_batches/batch_*/run_*/plots/")
    print("  • Batch comparisons: evaluation/batches_comparison/batch_*/comparison_plots/")
    print("  • Global analysis: evaluation/global_analysis/GLOBAL_PLOTS/")
    print("  • Deployment guide: evaluation/global_analysis/GLOBAL_REPORT.txt")
    print("\n📈 Total files generated: 365+ (283 plots + 82 reports/data files)")

if __name__ == "__main__":
    main()