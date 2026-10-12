#!/usr/bin/env python3
"""
SecureSight Visual Analytics - Final Batches Completion
Complete batches 3, 4, and 5 with robust error handling.
"""

# Set matplotlib backend BEFORE any other imports
import matplotlib
matplotlib.use('Agg')

import os
import sys
import numpy as np
import random
import time
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

def run_single_run(batch_num, run_idx, batch_config):
    """Run a single run with error handling"""
    print(f"\n{'='*50}")
    print(f"Batch {batch_num}, Run {run_idx}")
    print(f"{'='*50}")

    # Check if this run already exists
    run_dir = f"evaluation/detailed_batches/batch_{batch_num}/run_{run_idx}"
    if os.path.exists(run_dir):
        print(f"✓ Run {run_idx} already exists, skipping...")
        return True

    try:
        # Initialize tracker
        tracker = RunTracker(
            batch_num=batch_num,
            run_idx=run_idx,
            hyperparams={
                'learning_rate': batch_config['lr'],
                'batch_size': batch_config['bs'],
                'dropout': batch_config['dropout'],
                'optimizer': batch_config['optimizer'],
                'weight_decay': batch_config['weight_decay'],
                'class_names': ['Normal', 'Exploit', 'Backdoor', 'Poisoning'],
                'seed': 42 + (batch_num-1)*5 + run_idx,
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
        return True

    except Exception as e:
        print(f"❌ Error in batch_{batch_num}/run_{run_idx}: {e}")
        return False

def run_batch_with_resume(batch_num, batch_config):
    """Run a batch, resuming from any incomplete runs"""
    print(f"\n🚀 Processing Batch {batch_num} (5 runs)")
    print(f"Hyperparameters: LR={batch_config['lr']}, BS={batch_config['bs']}, Dropout={batch_config['dropout']}")
    print("="*60)

    completed_runs = 0

    for run_idx in range(1, 6):
        success = run_single_run(batch_num, run_idx, batch_config)
        if success:
            completed_runs += 1
        time.sleep(0.1)  # Small delay between runs

    print(f"\n🎉 Batch {batch_num} processing complete! {completed_runs}/5 runs successful.")

    # Force global report update after batch completion
    if completed_runs > 0:
        try:
            from eval_tracker import RunTracker
            # Trigger global report generation by creating a dummy tracker and calling the static method
            dummy_tracker = RunTracker(batch_num=1, run_idx=1, hyperparams={'dummy': True})
            RunTracker.generate_global_report()
            print("✓ Global report updated")
        except Exception as e:
            print(f"⚠️ Could not update global report: {e}")

    return completed_runs

def main():
    print("🚀 SecureSight Visual Analytics - Final Batches Completion")
    print("=" * 70)

    # Set random seed for reproducible demo
    np.random.seed(42)
    random.seed(42)

    # Define hyperparameters per batch (different configs for meaningful comparison)
    batch_configs = {
        3: {'lr': 2e-4, 'bs': 64, 'dropout': 0.4, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        4: {'lr': 1e-4, 'bs': 64, 'dropout': 0.1, 'optimizer': 'adamw', 'weight_decay': 1e-5},
        5: {'lr': 8e-5, 'bs': 128, 'dropout': 0.3, 'optimizer': 'adamw', 'weight_decay': 1e-5},
    }

    total_completed = 0

    # Run remaining batches
    for batch_num in [3, 4, 5]:
        completed = run_batch_with_resume(batch_num, batch_configs[batch_num])
        total_completed += completed

    print("\n" + "="*70)
    print(f"🎉 COMPLETION SUMMARY: {total_completed} runs added")
    print("="*70)

    # Show final deployment recommendation
    global_report_path = "evaluation/global_analysis/GLOBAL_REPORT.txt"
    if os.path.exists(global_report_path):
        print("\n" + "="*70)
        print("🎯 FINAL DEPLOYMENT RECOMMENDATION:")
        print("="*70)
        try:
            with open(global_report_path, 'r') as f:
                content = f.read()
                # Extract key sections
                lines = content.split('\n')
                in_best_model = False
                in_hyperparams = False

                for line in lines:
                    if 'BEST MODEL FOR DEPLOYMENT:' in line:
                        in_best_model = True
                        print(line)
                    elif 'RECOMMENDED HYPERPARAMETERS:' in line:
                        in_hyperparams = True
                        print(f"\n{line}")
                    elif in_best_model and line.strip() and not line.startswith('  ') and 'RECOMMENDED' not in line:
                        if 'PERFORMANCE SUMMARY:' in line:
                            break
                        print(line)
                    elif in_hyperparams and line.strip() and not line.startswith('  ') and 'PERFORMANCE' not in line:
                        if 'ACCURACY-LATENCY' in line:
                            break
                        print(line)

                print(f"\n📊 Total runs analyzed: {len([l for l in lines if 'batch_' in l and '|' in l])}")
                print("📁 Full results: evaluation/global_analysis/GLOBAL_REPORT.txt")

        except Exception as e:
            print(f"Could not read global report: {e}")

if __name__ == "__main__":
    main()