"""
SecureSight Enhanced Evaluation Tracker with Full Visual Analytics

Complete visual analytics at:
- Per-run level (10 plots + report)
- Per-batch level (5 comparison plots + report)
- Global level (8 global plots + comprehensive report + stats)
"""

import os
import json
import csv
import time
import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_curve

from path_setup import get_evaluation_base_dir


# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

def _safe_mkdir(path: str) -> None:
    """Create directory with parents, no error if exists."""
    os.makedirs(path, exist_ok=True)


def _format_duration(seconds: float) -> str:
    """Convert seconds to readable format."""
    return str(datetime.timedelta(seconds=int(seconds)))


# ================================================================================
# PLOTTING UTILITIES
# ================================================================================

def _plot_line_curves(
    x,
    series: List[Tuple[List[float], str, str]],
    title: str,
    xlabel: str,
    ylabel: str,
    out_path: str,
) -> None:
    """Generic line plot for multiple series."""
    fig, ax = plt.subplots(figsize=(11, 7))
    for values, label, style in series:
        ax.plot(x, values, style, label=label, linewidth=2.5, markersize=6)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10)
    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_histogram(
    values: List[float],
    title: str,
    xlabel: str,
    out_path: str,
) -> None:
    """Histogram plot for distribution."""
    fig, ax = plt.subplots(figsize=(10, 6))
    bins = min(25, max(5, len(values) // 2))
    ax.hist(values, bins=bins, color='#2a9d8f', alpha=0.8, edgecolor='black', linewidth=1.2)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_confusion_matrix(
    cm: List[List[int]],
    class_names: List[str],
    out_path: str,
) -> None:
    """Plot confusion matrix heatmap."""
    cm_arr = np.asarray(cm, dtype=int)
    if cm_arr.size == 0:
        return

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(cm_arr, cmap='Blues', aspect='auto')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Count')

    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('True', fontsize=12)
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha='right')
    ax.set_yticklabels(class_names)

    thresh = cm_arr.max() / 2.0 if cm_arr.size else 0
    for i in range(cm_arr.shape[0]):
        for j in range(cm_arr.shape[1]):
            ax.text(
                j, i, str(int(cm_arr[i, j])),
                ha='center', va='center',
                color='white' if cm_arr[i, j] > thresh else 'black',
                fontsize=9, fontweight='bold'
            )

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_bar(
    x_labels: List[str],
    y_values: List[float],
    title: str,
    ylabel: str,
    out_path: str,
    color: str = '#264653',
) -> None:
    """Bar chart plot."""
    fig, ax = plt.subplots(figsize=(12, 6))
    positions = np.arange(len(x_labels))
    bars = ax.bar(positions, y_values, color=color, alpha=0.85, edgecolor='black', linewidth=1.2)

    ax.set_xticks(positions)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}', ha='center', va='bottom', fontsize=9)

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_radar(
    values: List[float],
    labels: List[str],
    title: str,
    out_path: str,
) -> None:
    """Radar/polar chart plot."""
    if len(values) != len(labels) or len(values) < 3:
        return

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_closed = list(values) + [values[0]]
    angles_closed = angles + [angles[0]]

    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles_closed, values_closed, color='#e76f51', linewidth=2.5, marker='o', markersize=8)
    ax.fill(angles_closed, values_closed, alpha=0.25, color='#e76f51')
    ax.set_thetagrids(np.degrees(angles), labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True)

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_heatmap(
    matrix: np.ndarray,
    x_labels: List[str],
    y_labels: List[str],
    title: str,
    out_path: str,
    cmap: str = 'viridis',
) -> None:
    """Heatmap plot."""
    if matrix.size == 0:
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_yticklabels(y_labels)
    ax.set_title(title, fontsize=14, fontweight='bold')

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Value', fontsize=11)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = float(matrix[i, j])
            ax.text(j, i, f'{val:.3f}', ha='center', va='center',
                   color='white' if val > matrix.max() * 0.5 else 'black',
                   fontsize=9)

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_roc_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    class_names: List[str],
    out_path: str,
) -> None:
    """Plot ROC curve for multi-class (OVR)."""
    if y_prob.size == 0 or y_true.size == 0:
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    if y_prob.ndim == 1 or y_prob.shape[1] == 1:
        fpr, tpr, _ = roc_curve(y_true, y_prob.ravel(), pos_label=1)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color='#e76f51', lw=2.5, label=f'ROC (AUC={roc_auc:.3f})')
    else:
        num_classes = y_prob.shape[1]
        aucs = []
        for cls in range(num_classes):
            y_truth = (y_true == cls).astype(int)
            if y_truth.sum() == 0:
                continue
            fpr, tpr, _ = roc_curve(y_truth, y_prob[:, cls])
            roc_auc = auc(fpr, tpr)
            aucs.append(roc_auc)
            ax.plot(fpr, tpr, lw=2, alpha=0.8, label=f'{class_names[cls]} (AUC={roc_auc:.3f})')

        if aucs:
            mean_auc = np.mean(aucs)
            ax.plot([], [], lw=2.5, color='black', label=f'Mean AUC={mean_auc:.3f}')

    ax.plot([0, 1], [0, 1], 'k--', lw=2, alpha=0.4, label='Random')
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curve (One-vs-Rest)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_pr_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    class_names: List[str],
    out_path: str,
) -> None:
    """Plot Precision-Recall curve for multi-class (OVR)."""
    if y_prob.size == 0 or y_true.size == 0:
        return

    fig, ax = plt.subplots(figsize=(10, 8))

    if y_prob.ndim == 1 or y_prob.shape[1] == 1:
        precision, recall, _ = precision_recall_curve(y_true, y_prob.ravel(), pos_label=1)
        ap = auc(recall, precision)
        ax.plot(recall, precision, color='#e76f51', lw=2.5, label=f'PR (AP={ap:.3f})')
    else:
        num_classes = y_prob.shape[1]
        aps = []
        for cls in range(num_classes):
            y_truth = (y_true == cls).astype(int)
            if y_truth.sum() == 0:
                continue
            precision, recall, _ = precision_recall_curve(y_truth, y_prob[:, cls])
            ap = auc(recall, precision)
            aps.append(ap)
            ax.plot(recall, precision, lw=2, alpha=0.8, label=f'{class_names[cls]} (AP={ap:.3f})')

        if aps:
            mean_ap = np.mean(aps)
            ax.plot([], [], lw=2.5, color='black', label=f'Mean AP={mean_ap:.3f}')

    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.set_xlabel('Recall', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title('Precision-Recall Curve (One-vs-Rest)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def _plot_per_class_metrics(
    per_class: Dict[str, Dict[str, float]],
    out_path: str,
) -> None:
    """Plot per-class precision, recall, F1 as grouped bars."""
    if not per_class:
        return

    class_names = list(per_class.keys())
    precisions = [per_class[c].get('precision', 0.0) for c in class_names]
    recalls = [per_class[c].get('recall', 0.0) for c in class_names]
    f1_scores = [per_class[c].get('f1', 0.0) for c in class_names]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(class_names))
    width = 0.25

    bars1 = ax.bar(x - width, precisions, width, label='Precision', color='#264653', alpha=0.85)
    bars2 = ax.bar(x, recalls, width, label='Recall', color='#2a9d8f', alpha=0.85)
    bars3 = ax.bar(x + width, f1_scores, width, label='F1', color='#e76f51', alpha=0.85)

    ax.set_xlabel('Class', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Per-Class Metrics (Precision, Recall, F1)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(class_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1.1])

    fig.tight_layout()
    _safe_mkdir(os.path.dirname(out_path))
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


# ================================================================================
# RUN TRACKER
# ================================================================================

class RunTracker:
    """Track individual run metrics, generate per-run plots and reports."""

    BASE_OUTPUT_DIR = './evaluation'
    DETAILED_RESULTS_DIR = './evaluation/detailed_batches'
    COMPARISONS_DIR = './evaluation/batches_comparison'
    GLOBAL_DIR = './evaluation/global_analysis'

    @staticmethod
    def refresh_output_paths() -> None:
        """Refresh paths based on environment."""
        base = get_evaluation_base_dir()
        RunTracker.BASE_OUTPUT_DIR = base
        RunTracker.DETAILED_RESULTS_DIR = os.path.join(base, 'detailed_batches')
        RunTracker.COMPARISONS_DIR = os.path.join(base, 'batches_comparison')
        RunTracker.GLOBAL_DIR = os.path.join(base, 'global_analysis')

    def __init__(
        self,
        run_name: Optional[str] = None,
        batch_num: Optional[int] = None,
        run_idx: Optional[int] = None,
        hyperparams: Optional[Dict[str, Any]] = None,
    ):
        RunTracker.refresh_output_paths()

        self.batch_num = batch_num if batch_num is not None else self._get_next_batch_num()
        self.batch_name = f"batch_{self.batch_num}"
        self.batch_dir = os.path.join(self.DETAILED_RESULTS_DIR, self.batch_name)
        _safe_mkdir(self.batch_dir)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if run_idx is not None:
            candidate = f"run_{run_idx}"
            if os.path.exists(os.path.join(self.batch_dir, candidate)):
                candidate = f"run_{run_idx}_{timestamp}"
            self.run_name = f"{candidate}" if not run_name else f"{candidate}_{run_name}"
        else:
            self.run_name = run_name or f"run_{timestamp}"

        self.run_dir = os.path.join(self.batch_dir, self.run_name)
        _safe_mkdir(self.run_dir)

        self.plots_dir = os.path.join(self.run_dir, 'plots')
        _safe_mkdir(self.plots_dir)

        self.csv_path = os.path.join(self.run_dir, 'epoch_results.csv')
        self.report_path = os.path.join(self.run_dir, 'report.txt')
        self.summary_path = os.path.join(self.run_dir, 'run_summary.json')

        self.hyperparams = hyperparams or {}
        self.epoch_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.timestamp = timestamp

        self._save_metadata()
        print(f"\n{'='*70}")
        print(f"  ▶ Run Tracker Initialized")
        print(f"    Batch: {self.batch_name}")
        print(f"    Run:   {self.run_name}")
        print(f"    Path:  {self.run_dir}")
        print(f"{'='*70}\n")

    def _get_next_batch_num(self) -> int:
        """Get next batch number."""
        if not os.path.exists(self.DETAILED_RESULTS_DIR):
            return 1
        batches = []
        for d in os.listdir(self.DETAILED_RESULTS_DIR):
            if d.startswith('batch_'):
                try:
                    batches.append(int(d.replace('batch_', '')))
                except ValueError:
                    continue
        return max(batches) + 1 if batches else 1

    def _save_metadata(self) -> None:
        """Save initial metadata."""
        metadata = {
            'run_name': self.run_name,
            'batch': self.batch_num,
            'start_time': datetime.datetime.now().isoformat(),
            'hyperparams': self.hyperparams,
            'status': 'running',
        }
        with open(self.summary_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def record_epoch(self, epoch_data: Dict[str, Any]) -> None:
        """Record epoch metrics."""
        epoch_data = epoch_data.copy()
        self.epoch_results.append(epoch_data)
        if self.epoch_results:
            fieldnames = list(self.epoch_results[0].keys())
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.epoch_results)

        epoch = epoch_data.get('epoch', '?')
        print(f"  [RunTracker] Epoch {epoch} recorded")

    def finalize(
        self,
        final_metrics: Optional[Dict[str, Any]] = None,
        latency: Optional[Dict[str, float]] = None,
        eval_labels: Optional[np.ndarray] = None,
        eval_probs: Optional[np.ndarray] = None,
    ) -> None:
        """Finalize run: generate all plots and reports."""
        elapsed = time.time() - self.start_time
        elapsed_str = _format_duration(elapsed)

        summary: Dict[str, Any] = {
            'run_name': self.run_name,
            'batch': self.batch_num,
            'start_time': datetime.datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.datetime.now().isoformat(),
            'duration': elapsed_str,
            'total_epochs': len(self.epoch_results),
            'hyperparams': self.hyperparams,
            'status': 'completed',
        }

        if final_metrics:
            summary['final_metrics'] = final_metrics
        if latency:
            summary['latency'] = latency

        with open(self.summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"\n  [RunTracker] Generating plots...")
        self._generate_run_plots(final_metrics, latency, eval_labels, eval_probs)
        
        print(f"  [RunTracker] Generating report...")
        self._generate_run_report(summary, final_metrics, latency)

        print(f"\n{'='*70}")
        print(f"  ✓ Run Finalized: {self.run_name}")
        print(f"    Duration: {elapsed_str}")
        print(f"    Plots:    {self.plots_dir}")
        print(f"    Report:   {self.report_path}")
        print(f"{'='*70}\n")

        self.generate_batch_report(self.batch_num)
        RunTracker.generate_global_report()

    def _generate_run_plots(
        self,
        final_metrics: Optional[Dict[str, Any]],
        latency: Optional[Dict[str, float]],
        eval_labels: Optional[np.ndarray],
        eval_probs: Optional[np.ndarray],
    ) -> None:
        """Generate all 10 required plots per run."""
        if not self.epoch_results:
            return

        epochs = [r.get('epoch', i + 1) for i, r in enumerate(self.epoch_results)]
        train_loss = [r.get('train_loss', 0.0) for r in self.epoch_results]
        val_loss = [r.get('val_loss', 0.0) for r in self.epoch_results]
        train_acc = [r.get('train_acc', 0.0) for r in self.epoch_results]
        val_acc = [r.get('val_acc', 0.0) for r in self.epoch_results]
        train_f1 = [r.get('train_f1', 0.0) for r in self.epoch_results]
        val_f1 = [r.get('val_f1', 0.0) for r in self.epoch_results]

        # 1. Training Loss (train vs val)
        _plot_line_curves(
            epochs,
            [(train_loss, 'Training', 'b-o'), (val_loss, 'Validation', 'r-s')],
            'Training vs Validation Loss',
            'Epoch',
            'Loss',
            os.path.join(self.plots_dir, 'training_loss.png'),
        )

        # 2. Validation Loss (val only)
        _plot_line_curves(
            epochs,
            [(val_loss, 'Validation', 'r-s')],
            'Validation Loss Curve',
            'Epoch',
            'Loss',
            os.path.join(self.plots_dir, 'val_loss.png'),
        )

        # 3. Accuracy (train vs val)
        _plot_line_curves(
            epochs,
            [(train_acc, 'Training', 'b-o'), (val_acc, 'Validation', 'r-s')],
            'Training vs Validation Accuracy',
            'Epoch',
            'Accuracy',
            os.path.join(self.plots_dir, 'accuracy.png'),
        )

        # 4. F1 Score (train vs val)
        _plot_line_curves(
            epochs,
            [(train_f1, 'Training', 'b-o'), (val_f1, 'Validation', 'r-s')],
            'Training vs Validation F1 Score',
            'Epoch',
            'Macro F1',
            os.path.join(self.plots_dir, 'f1.png'),
        )

        # 5. ROC Curve
        if eval_labels is not None and eval_probs is not None and eval_labels.size and eval_probs.size:
            _plot_roc_curve(
                eval_labels,
                eval_probs,
                self.hyperparams.get('class_names', []),
                os.path.join(self.plots_dir, 'roc_curve.png'),
            )

            # 6. Precision-Recall Curve
            _plot_pr_curve(
                eval_labels,
                eval_probs,
                self.hyperparams.get('class_names', []),
                os.path.join(self.plots_dir, 'pr_curve.png'),
            )

        # 7. Confusion Matrix
        if final_metrics:
            cm = final_metrics.get('confusion_matrix', [])
            _plot_confusion_matrix(
                cm,
                self.hyperparams.get('class_names', []),
                os.path.join(self.plots_dir, 'confusion_matrix.png'),
            )

            # 8. Per-Class Bar Chart (Precision, Recall, F1)
            per_class_metrics = final_metrics.get('per_class', {})
            if per_class_metrics:
                _plot_per_class_metrics(
                    per_class_metrics,
                    os.path.join(self.plots_dir, 'per_class_bar.png'),
                )

                # 9. Radar Chart (per-class metrics)
                class_names = list(per_class_metrics.keys())
                recalls = [per_class_metrics[c].get('recall', 0.0) for c in class_names]
                if len(recalls) >= 3:
                    _plot_radar(
                        recalls,
                        class_names,
                        'Per-Class Recall Radar',
                        os.path.join(self.plots_dir, 'radar_per_class.png'),
                    )

        # 10. Latency Distribution
        if latency and latency.get('samples'):
            _plot_histogram(
                latency['samples'],
                'Inference Latency Distribution',
                'Latency (ms)',
                os.path.join(self.plots_dir, 'latency.png'),
            )

    def _generate_run_report(
        self,
        summary: Dict[str, Any],
        final_metrics: Optional[Dict[str, Any]],
        latency: Optional[Dict[str, float]],
    ) -> None:
        """Generate detailed text report for run."""
        lines: List[str] = []
        lines.append('=' * 90)
        lines.append(f"SecureSight Detailed Run Report — {self.run_name}")
        lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
        lines.append('=' * 90)
        lines.append('')

        lines.append(f"Batch ID: {self.batch_name}")
        lines.append(f"Run ID: {self.run_name}")
        lines.append(f"Start time: {summary.get('start_time')}")
        lines.append(f"End time:   {summary.get('end_time')}")
        lines.append(f"Duration:   {summary.get('duration')}")
        lines.append(f"Total epochs: {summary.get('total_epochs')}")
        lines.append('')

        lines.append('HYPERPARAMETERS:')
        for k, v in self.hyperparams.items():
            if k not in ['class_names', 'traceability_lines', 'observations', 'final_conclusion']:
                if isinstance(v, list):
                    lines.append(f"  {k}: {', '.join(map(str, v))}")
                else:
                    lines.append(f"  {k}: {v}")
        lines.append('')

        if final_metrics:
            lines.append('FINAL METRICS:')
            lines.append(f"  Accuracy:  {final_metrics.get('accuracy', 0.0):.4f}")
            lines.append(f"  Precision: {final_metrics.get('precision', 0.0):.4f}")
            lines.append(f"  Recall:    {final_metrics.get('recall', 0.0):.4f}")
            lines.append(f"  F1 Score:  {final_metrics.get('f1', 0.0):.4f}")
            lines.append(f"  AUC:       {final_metrics.get('auc', 0.0):.4f}")
            lines.append('')

        if latency:
            lines.append('LATENCY STATISTICS (milliseconds):')
            lines.append(f"  Mean:   {latency.get('mean_ms', 0.0):.2f} ms")
            lines.append(f"  Std:    {latency.get('std_ms', 0.0):.2f} ms")
            lines.append(f"  P95:    {latency.get('p95_ms', 0.0):.2f} ms")
            lines.append(f"  P99:    {latency.get('p99_ms', 0.0):.2f} ms")
            lines.append('')

        if final_metrics and final_metrics.get('per_class'):
            lines.append('PER-CLASS PERFORMANCE:')
            for class_name, metrics in final_metrics['per_class'].items():
                lines.append(f"  {class_name}:")
                lines.append(f"    Precision: {metrics.get('precision', 0.0):.4f}")
                lines.append(f"    Recall:    {metrics.get('recall', 0.0):.4f}")
                lines.append(f"    F1:        {metrics.get('f1', 0.0):.4f}")
                lines.append(f"    Support:   {metrics.get('support', 0)}")
            lines.append('')

        lines.append('EPOCH-BY-EPOCH PERFORMANCE:')
        lines.append('  Epoch | Train Loss | Train Acc | Train F1 | Val Loss | Val Acc | Val F1')
        lines.append('  ' + '-' * 75)
        for ed in self.epoch_results:
            lines.append(
                f"  {ed.get('epoch', '?'):>5} | "
                f"{ed.get('train_loss', 0):>10.4f} | "
                f"{ed.get('train_acc', 0):>9.4f} | "
                f"{ed.get('train_f1', 0):>8.4f} | "
                f"{ed.get('val_loss', 0):>8.4f} | "
                f"{ed.get('val_acc', 0):>7.4f} | "
                f"{ed.get('val_f1', 0):>6.4f}"
            )
        lines.append('')

        lines.append('PLOTS GENERATED:')
        lines.append('  ✓ training_loss.png - Training vs Validation Loss')
        lines.append('  ✓ val_loss.png - Validation Loss Curve')
        lines.append('  ✓ accuracy.png - Training vs Validation Accuracy')
        lines.append('  ✓ f1.png - Training vs Validation F1 Score')
        lines.append('  ✓ roc_curve.png - ROC Curve (One-vs-Rest)')
        lines.append('  ✓ pr_curve.png - Precision-Recall Curve')
        lines.append('  ✓ confusion_matrix.png - Confusion Matrix Heatmap')
        lines.append('  ✓ per_class_bar.png - Per-Class Metrics (Precision, Recall, F1)')
        lines.append('  ✓ radar_per_class.png - Per-Class Recall Radar Chart')
        lines.append('  ✓ latency.png - Inference Latency Distribution')
        lines.append('')

        lines.append('=' * 90)
        lines.append('End of Report')
        lines.append('=' * 90)

        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    @classmethod
    def generate_batch_report(cls, batch_num: int) -> None:
        """Generate batch-level comparison report and plots."""
        cls.refresh_output_paths()
        batch_name = f"batch_{batch_num}"
        batch_dir = os.path.join(cls.DETAILED_RESULTS_DIR, batch_name)
        
        if not os.path.exists(batch_dir):
            return

        print(f"\n  [BatchReport] Generating {batch_name} comparison plots...")

        _safe_mkdir(cls.COMPARISONS_DIR)
        batch_report_dir = os.path.join(cls.COMPARISONS_DIR, batch_name)
        comparison_plots_dir = os.path.join(batch_report_dir, 'comparison_plots')
        _safe_mkdir(comparison_plots_dir)

        summaries: List[Dict[str, Any]] = []
        for run_folder in sorted(os.listdir(batch_dir)):
            run_dir = os.path.join(batch_dir, run_folder)
            summary_path = os.path.join(run_dir, 'run_summary.json')
            if os.path.exists(summary_path):
                with open(summary_path, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                summary['run_folder'] = run_folder
                summary['run_dir'] = run_dir
                summaries.append(summary)

        if not summaries:
            return

        summaries.sort(key=lambda x: x.get('run_folder', ''))

        metrics = []
        for run in summaries:
            final = run.get('final_metrics', {})
            metrics.append({
                'run': run.get('run_folder'),
                'accuracy': float(final.get('accuracy', 0.0)),
                'f1': float(final.get('f1', 0.0)),
                'precision': float(final.get('precision', 0.0)),
                'recall': float(final.get('recall', 0.0)),
                'auc': float(final.get('auc', 0.0)),
                'loss': float(final.get('loss', 0.0)),
                'latency': float(run.get('latency', {}).get('mean_ms', 0.0)),
            })

        run_names = [m['run'] for m in metrics]
        accuracies = [m['accuracy'] for m in metrics]
        f1s = [m['f1'] for m in metrics]
        losses = [m['loss'] for m in metrics]
        latencies = [m['latency'] for m in metrics]

        stats = {
            'accuracy': {'mean': float(np.mean(accuracies)), 'std': float(np.std(accuracies, ddof=1)) if len(accuracies) > 1 else 0.0},
            'f1': {'mean': float(np.mean(f1s)), 'std': float(np.std(f1s, ddof=1)) if len(f1s) > 1 else 0.0},
            'loss': {'mean': float(np.mean(losses)), 'std': float(np.std(losses, ddof=1)) if len(losses) > 1 else 0.0},
            'latency': {'mean': float(np.mean(latencies)), 'std': float(np.std(latencies, ddof=1)) if len(latencies) > 1 else 0.0},
        }

        best_run = max(metrics, key=lambda x: (x['f1'], x['accuracy']))
        worst_run = min(metrics, key=lambda x: (x['f1'], x['accuracy']))

        print(f"    ✓ batch_runs_accuracy.png")
        _plot_bar(
            run_names,
            accuracies,
            f'Batch {batch_num} - Accuracy Comparison',
            'Accuracy',
            os.path.join(comparison_plots_dir, 'batch_runs_accuracy.png'),
        )

        print(f"    ✓ batch_runs_f1.png")
        _plot_bar(
            run_names,
            f1s,
            f'Batch {batch_num} - F1 Comparison',
            'Macro F1',
            os.path.join(comparison_plots_dir, 'batch_runs_f1.png'),
        )

        print(f"    ✓ batch_runs_loss.png")
        _plot_line_curves(
            list(range(1, len(run_names) + 1)),
            [(losses, 'Loss', 'r-o')],
            f'Batch {batch_num} - Loss Comparison',
            'Run #',
            'Loss',
            os.path.join(comparison_plots_dir, 'batch_runs_loss.png'),
        )

        print(f"    ✓ batch_runs_latency.png")
        _plot_bar(
            run_names,
            latencies,
            f'Batch {batch_num} - Latency Comparison',
            'Latency (ms)',
            os.path.join(comparison_plots_dir, 'batch_runs_latency.png'),
        )

        print(f"    ✓ batch_radar_comparison.png")
        if len(run_names) >= 3:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            metric_labels = ['Accuracy', 'F1', 'Precision', 'Recall', 'AUC']
            angles = np.linspace(0, 2 * np.pi, len(metric_labels), endpoint=False).tolist()
            angles += angles[:1]

            colors = plt.cm.Set3(np.linspace(0, 1, len(metrics)))
            for idx, m in enumerate(metrics):
                values = [m['accuracy'], m['f1'], m['precision'], m['recall'], m['auc']]
                values += [values[0]]
                ax.plot(angles, values, 'o-', linewidth=2, label=m['run'], color=colors[idx])
                ax.fill(angles, values, alpha=0.15, color=colors[idx])

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metric_labels, fontsize=11)
            ax.set_ylim(0, 1)
            ax.set_title(f'Batch {batch_num} - Radar Comparison', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True)
            ax.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1.3, 1.1))
            fig.tight_layout()
            fig.savefig(os.path.join(comparison_plots_dir, 'batch_radar_comparison.png'), dpi=200, bbox_inches='tight')
            plt.close(fig)

        report_lines: List[str] = []
        report_lines.append('=' * 90)
        report_lines.append(f"SecureSight Batch Comparison Report — {batch_name}")
        report_lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
        report_lines.append('=' * 90)
        report_lines.append(f"\nTotal runs: {len(metrics)}")
        report_lines.append('')

        report_lines.append('RUN SUMMARY:')
        for m in metrics:
            report_lines.append(
                f"  {m['run']:>10} | Acc: {m['accuracy']:.4f} | F1: {m['f1']:.4f} | "
                f"Loss: {m['loss']:.4f} | Latency: {m['latency']:.2f}ms"
            )
        report_lines.append('')

        report_lines.append('STABILITY METRICS:')
        report_lines.append(f"  Accuracy: mean={stats['accuracy']['mean']:.4f} ± {stats['accuracy']['std']:.4f}")
        report_lines.append(f"  F1:       mean={stats['f1']['mean']:.4f} ± {stats['f1']['std']:.4f}")
        report_lines.append(f"  Loss:     mean={stats['loss']['mean']:.4f} ± {stats['loss']['std']:.4f}")
        report_lines.append(f"  Latency:  mean={stats['latency']['mean']:.2f} ± {stats['latency']['std']:.2f}ms")
        report_lines.append('')

        report_lines.append(f"Best run:  {best_run['run']} (F1={best_run['f1']:.4f}, Acc={best_run['accuracy']:.4f})")
        report_lines.append(f"Worst run: {worst_run['run']} (F1={worst_run['f1']:.4f}, Acc={worst_run['accuracy']:.4f})")
        report_lines.append('')

        report_lines.append('HYPERPARAMETERS:')
        if summaries:
            hp = summaries[0].get('hyperparams', {})
            for k, v in hp.items():
                if k not in ['class_names', 'traceability_lines', 'observations', 'final_conclusion']:
                    report_lines.append(f"  {k}: {v}")
        report_lines.append('')

        report_lines.append('COMPARISON PLOTS:')
        report_lines.append('  ✓ batch_runs_accuracy.png')
        report_lines.append('  ✓ batch_runs_f1.png')
        report_lines.append('  ✓ batch_runs_loss.png')
        report_lines.append('  ✓ batch_runs_latency.png')
        report_lines.append('  ✓ batch_radar_comparison.png')
        report_lines.append('')

        report_lines.append('=' * 90)

        with open(os.path.join(batch_report_dir, 'batch_report.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"  [BatchReport] {batch_name} complete ✓")

    @classmethod
    def generate_global_report(cls) -> None:
        """Generate comprehensive global analysis report and plots."""
        cls.refresh_output_paths()

        if not os.path.exists(cls.DETAILED_RESULTS_DIR):
            return

        print(f"\n  [GlobalReport] Generating global analysis...")

        _safe_mkdir(cls.GLOBAL_DIR)
        global_plots_dir = os.path.join(cls.GLOBAL_DIR, 'GLOBAL_PLOTS')
        _safe_mkdir(global_plots_dir)

        all_runs: List[Dict[str, Any]] = []
        batch_data: Dict[str, List[Dict[str, Any]]] = {}

        for batch_folder in sorted(os.listdir(cls.DETAILED_RESULTS_DIR)):
            batch_path = os.path.join(cls.DETAILED_RESULTS_DIR, batch_folder)
            if not os.path.isdir(batch_path):
                continue

            batch_num = int(batch_folder.replace('batch_', '')) if batch_folder.startswith('batch_') else 0
            batch_data[batch_folder] = []

            for run_folder in sorted(os.listdir(batch_path)):
                run_dir = os.path.join(batch_path, run_folder)
                summary_path = os.path.join(run_dir, 'run_summary.json')
                if os.path.exists(summary_path):
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data['batch_folder'] = batch_folder
                    data['batch_num'] = batch_num
                    data['run_folder'] = run_folder
                    all_runs.append(data)
                    batch_data[batch_folder].append(data)

        if not all_runs:
            return

        valid_runs = [r for r in all_runs if r.get('final_metrics')]
        valid_runs.sort(key=lambda x: (x['final_metrics'].get('f1', 0.0), x['final_metrics'].get('accuracy', 0.0)), reverse=True)

        all_metrics = []
        for r in valid_runs:
            m = r['final_metrics']
            all_metrics.append({
                'batch': r.get('batch_folder'),
                'batch_num': r.get('batch_num'),
                'run': r.get('run_folder'),
                'accuracy': float(m.get('accuracy', 0.0)),
                'f1': float(m.get('f1', 0.0)),
                'precision': float(m.get('precision', 0.0)),
                'recall': float(m.get('recall', 0.0)),
                'auc': float(m.get('auc', 0.0)),
                'loss': float(m.get('loss', 0.0)),
                'latency': float(r.get('latency', {}).get('mean_ms', 0.0)),
                'hyperparams': r.get('hyperparams', {}),
            })

        batch_stats = {}
        for batch_key, runs in batch_data.items():
            batch_metrics = [m for m in all_metrics if m['batch'] == batch_key]
            if batch_metrics:
                accs = [m['accuracy'] for m in batch_metrics]
                f1s = [m['f1'] for m in batch_metrics]
                lats = [m['latency'] for m in batch_metrics]
                batch_stats[batch_key] = {
                    'accuracy': {'mean': float(np.mean(accs)), 'std': float(np.std(accs, ddof=1)) if len(accs) > 1 else 0.0},
                    'f1': {'mean': float(np.mean(f1s)), 'std': float(np.std(f1s, ddof=1)) if len(f1s) > 1 else 0.0},
                    'latency': {'mean': float(np.mean(lats)), 'std': float(np.std(lats, ddof=1)) if len(lats) > 1 else 0.0},
                    'count': len(batch_metrics),
                }

        batch_names = sorted(batch_stats.keys())

        # GLOBAL PLOTS

        print(f"    ✓ all_batches_accuracy.png")
        batch_accs = [np.mean([m['accuracy'] for m in all_metrics if m['batch'] == b]) for b in batch_names]
        _plot_bar(
            [f"Batch {b.replace('batch_', '')}" for b in batch_names],
            batch_accs,
            'Global Accuracy Comparison (All Batches)',
            'Mean Accuracy',
            os.path.join(global_plots_dir, 'all_batches_accuracy.png'),
        )

        print(f"    ✓ all_batches_f1.png")
        batch_f1s = [np.mean([m['f1'] for m in all_metrics if m['batch'] == b]) for b in batch_names]
        _plot_bar(
            [f"Batch {b.replace('batch_', '')}" for b in batch_names],
            batch_f1s,
            'Global F1 Comparison (All Batches)',
            'Mean F1',
            os.path.join(global_plots_dir, 'all_batches_f1.png'),
        )

        print(f"    ✓ all_batches_loss.png")
        batch_loss = [np.mean([m['loss'] for m in all_metrics if m['batch'] == b]) for b in batch_names]
        _plot_bar(
            [f"Batch {b.replace('batch_', '')}" for b in batch_names],
            batch_loss,
            'Global Loss Comparison (All Batches)',
            'Mean Loss',
            os.path.join(global_plots_dir, 'all_batches_loss.png'),
        )

        print(f"    ✓ all_batches_latency.png")
        batch_lat = [np.mean([m['latency'] for m in all_metrics if m['batch'] == b]) for b in batch_names]
        _plot_bar(
            [f"Batch {b.replace('batch_', '')}" for b in batch_names],
            batch_lat,
            'Global Latency Comparison (All Batches)',
            'Mean Latency (ms)',
            os.path.join(global_plots_dir, 'all_batches_latency.png'),
        )

        print(f"    ✓ stability_score.png")
        stability_scores = []
        for b in batch_names:
            f1_std = batch_stats[b]['f1']['std']
            acc_std = batch_stats[b]['accuracy']['std']
            stability = 1.0 - np.clip((f1_std + acc_std) / 2.0, 0, 1)
            stability_scores.append(float(stability))

        _plot_bar(
            [f"Batch {b.replace('batch_', '')}" for b in batch_names],
            stability_scores,
            'Stability Score per Batch (1.0=Most Stable)',
            'Stability Score',
            os.path.join(global_plots_dir, 'stability_score.png'),
            color='#2a9d8f',
        )

        print(f"    ✓ performance_heatmap.png")
        perf_matrix = []
        for b in batch_names:
            batch_metrics = [m for m in all_metrics if m['batch'] == b]
            if batch_metrics:
                mean_acc = np.mean([m['accuracy'] for m in batch_metrics])
                mean_f1 = np.mean([m['f1'] for m in batch_metrics])
                mean_lat = np.mean([m['latency'] for m in batch_metrics])
                lat_norm = 1.0 - np.clip(mean_lat / max(1.0, max(batch_lat)), 0, 1)
                perf_matrix.append([mean_acc, mean_f1, lat_norm])

        if perf_matrix:
            _plot_heatmap(
                np.array(perf_matrix),
                [f"Batch {b.replace('batch_', '')}" for b in batch_names],
                ['Accuracy', 'F1', 'Latency (normalized)'],
                'Performance Heatmap (All Batches)',
                os.path.join(global_plots_dir, 'performance_heatmap.png'),
            )

        print(f"    ✓ best_vs_worst.png")
        if valid_runs:
            best_run = all_metrics[0]
            worst_run = min(all_metrics, key=lambda x: (x['f1'], x['accuracy']))

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            best_metrics = [best_run['accuracy'], best_run['f1'], best_run['precision'], best_run['recall'], best_run['auc']]
            worst_metrics = [worst_run['accuracy'], worst_run['f1'], worst_run['precision'], worst_run['recall'], worst_run['auc']]
            metric_names = ['Accuracy', 'F1', 'Precision', 'Recall', 'AUC']

            x_pos = np.arange(len(metric_names))
            ax1.bar(x_pos, best_metrics, color='#2a9d8f', alpha=0.85, edgecolor='black')
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(metric_names, rotation=45, ha='right')
            ax1.set_ylim([0, 1.1])
            ax1.set_title(f'Best Run: {best_run["batch"]}/{best_run["run"]}', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Score')
            ax1.grid(True, alpha=0.3, axis='y')

            ax2.bar(x_pos, worst_metrics, color='#e76f51', alpha=0.85, edgecolor='black')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(metric_names, rotation=45, ha='right')
            ax2.set_ylim([0, 1.1])
            ax2.set_title(f'Worst Run: {worst_run["batch"]}/{worst_run["run"]}', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Score')
            ax2.grid(True, alpha=0.3, axis='y')

            fig.suptitle('Best vs Worst Run Comparison', fontsize=14, fontweight='bold')
            fig.tight_layout()
            fig.savefig(os.path.join(global_plots_dir, 'best_vs_worst.png'), dpi=200, bbox_inches='tight')
            plt.close(fig)

        print(f"    ✓ hyperparameter_impact.png")
        if valid_runs and valid_runs[0].get('hyperparams'):
            hp_keys = [k for k in valid_runs[0]['hyperparams'].keys()
                      if k not in ['class_names', 'traceability_lines', 'observations', 'final_conclusion']]

            if hp_keys and batch_names:
                try:
                    hp_matrix = []
                    for b in batch_names:
                        batch_runs = [r for r in valid_runs if r.get('batch_folder') == b]
                        if batch_runs:
                            avg_f1 = np.mean([r['final_metrics'].get('f1', 0.0) for r in batch_runs])
                            hp_matrix.append([avg_f1])

                    if hp_matrix:
                        _plot_heatmap(
                            np.array(hp_matrix),
                            ['Avg F1'],
                            [f"Batch {i+1}" for i in range(len(batch_names))],
                            'Hyperparameter Impact: F1 per Batch',
                            os.path.join(global_plots_dir, 'hyperparameter_impact.png'),
                        )
                except Exception:
                    pass

        print(f"    ✓ GLOBAL_STATS.json")
        global_stats = {
            'total_runs': len(all_runs),
            'total_batches': len(batch_names),
            'timestamp': datetime.datetime.now().isoformat(),
            'batch_statistics': batch_stats,
            'overall': {
                'best_run': {
                    'batch': valid_runs[0]['batch_folder'] if valid_runs else None,
                    'run': valid_runs[0]['run_folder'] if valid_runs else None,
                    'f1': float(valid_runs[0]['final_metrics'].get('f1', 0.0)) if valid_runs else 0.0,
                    'accuracy': float(valid_runs[0]['final_metrics'].get('accuracy', 0.0)) if valid_runs else 0.0,
                    'latency_ms': float(valid_runs[0].get('latency', {}).get('mean_ms', 0.0)) if valid_runs else 0.0,
                },
                'mean_accuracy': float(np.mean([m['accuracy'] for m in all_metrics])) if all_metrics else 0.0,
                'mean_f1': float(np.mean([m['f1'] for m in all_metrics])) if all_metrics else 0.0,
                'mean_latency_ms': float(np.mean([m['latency'] for m in all_metrics])) if all_metrics else 0.0,
            },
        }

        with open(os.path.join(cls.GLOBAL_DIR, 'GLOBAL_STATS.json'), 'w', encoding='utf-8') as f:
            json.dump(global_stats, f, indent=2)

        print(f"    ✓ GLOBAL_REPORT.txt")
        report_lines: List[str] = []
        report_lines.append('=' * 100)
        report_lines.append('SECURESIGHT GLOBAL EVALUATION REPORT')
        report_lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
        report_lines.append('=' * 100)
        report_lines.append('')

        report_lines.append(f"Total Runs Analyzed: {len(all_runs)}")
        report_lines.append(f"Total Batches: {len(batch_names)}")
        report_lines.append(f"Runs per Batch: {len(all_runs) // max(1, len(batch_names))}")
        report_lines.append('')

        report_lines.append('TOP 10 RUNS BY F1 SCORE:')
        for idx, m in enumerate(all_metrics[:10], 1):
            report_lines.append(
                f"  {idx:2}. {m['batch']}/{m['run']:>10} | F1={m['f1']:.4f} | Acc={m['accuracy']:.4f} | "
                f"Prec={m['precision']:.4f} | Rec={m['recall']:.4f} | Lat={m['latency']:.2f}ms"
            )
        report_lines.append('')

        report_lines.append('BATCH RANKING (by mean F1):')
        batch_ranking = [(b, batch_stats[b]) for b in batch_names]
        batch_ranking.sort(key=lambda x: x[1]['f1']['mean'], reverse=True)
        for idx, (batch_key, stats) in enumerate(batch_ranking, 1):
            report_lines.append(
                f"  {idx}. {batch_key}: F1={stats['f1']['mean']:.4f}±{stats['f1']['std']:.4f} | "
                f"Acc={stats['accuracy']['mean']:.4f}±{stats['accuracy']['std']:.4f} | "
                f"Lat={stats['latency']['mean']:.2f}±{stats['latency']['std']:.2f}ms"
            )
        report_lines.append('')

        report_lines.append('STABILITY RANKING:')
        stability_ranking = [(i, s) for i, s in enumerate(stability_scores)]
        stability_ranking.sort(key=lambda x: x[1], reverse=True)
        for idx, (batch_idx, score) in enumerate(stability_ranking, 1):
            report_lines.append(f"  {idx}. Batch {batch_idx + 1}: Stability={score:.4f}")
        report_lines.append('')

        if valid_runs:
            best = all_metrics[0]
            report_lines.append('BEST MODEL FOR DEPLOYMENT:')
            report_lines.append(f"  Batch: {best['batch']}")
            report_lines.append(f"  Run:   {best['run']}")
            report_lines.append(f"  F1:    {best['f1']:.4f}")
            report_lines.append(f"  Accuracy: {best['accuracy']:.4f}")
            report_lines.append(f"  Latency:  {best['latency']:.2f}ms")
            report_lines.append('')

            report_lines.append('RECOMMENDED HYPERPARAMETERS:')
            for k, v in best['hyperparams'].items():
                if k not in ['class_names', 'traceability_lines', 'observations', 'final_conclusion']:
                    report_lines.append(f"  {k}: {v}")
            report_lines.append('')

        report_lines.append('PERFORMANCE SUMMARY:')
        report_lines.append(f"  Global Mean Accuracy: {global_stats['overall']['mean_accuracy']:.4f}")
        report_lines.append(f"  Global Mean F1:       {global_stats['overall']['mean_f1']:.4f}")
        report_lines.append(f"  Global Mean Latency:  {global_stats['overall']['mean_latency_ms']:.2f}ms")
        report_lines.append('')

        report_lines.append('ACCURACY-LATENCY TRADEOFF:')
        report_lines.append('  Fastest batch:    ' + (f"{batch_ranking[-1][0]} ({batch_ranking[-1][1]['latency']['mean']:.2f}ms avg)"
                                                       if batch_ranking else "N/A"))
        report_lines.append('  Most accurate:    ' + (f"{batch_ranking[0][0]} ({batch_ranking[0][1]['accuracy']['mean']:.4f} acc avg)"
                                                      if batch_ranking else "N/A"))
        report_lines.append('')

        report_lines.append('GLOBAL PLOTS GENERATED:')
        report_lines.append('  ✓ all_batches_accuracy.png - Mean accuracy per batch')
        report_lines.append('  ✓ all_batches_f1.png - Mean F1 per batch')
        report_lines.append('  ✓ all_batches_loss.png - Mean loss per batch')
        report_lines.append('  ✓ all_batches_latency.png - Mean latency per batch')
        report_lines.append('  ✓ stability_score.png - Stability ranking')
        report_lines.append('  ✓ performance_heatmap.png - Performance matrix')
        report_lines.append('  ✓ best_vs_worst.png - Best vs worst model comparison')
        report_lines.append('  ✓ hyperparameter_impact.png - Hyperparameter impact analysis')
        report_lines.append('')

        report_lines.append('DEPLOYMENT RECOMMENDATION:')
        if valid_runs:
            report_lines.append(f"  ✓ Use {best['batch']}/{best['run']} as production model")
            report_lines.append(f"  ✓ Expected F1 score in production: {best['f1']:.4f}")
            report_lines.append(f"  ✓ Expected inference latency: {best['latency']:.2f}ms per batch")
            report_lines.append(f"  ✓ Validate on production dataset before full deployment")
        else:
            report_lines.append('  No valid runs found for deployment recommendation')
        report_lines.append('')

        report_lines.append('=' * 100)
        report_lines.append('End of Global Report')
        report_lines.append('=' * 100)

        with open(os.path.join(cls.GLOBAL_DIR, 'GLOBAL_REPORT.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"  [GlobalReport] Complete ✓")
        print(f"    Location: {cls.GLOBAL_DIR}")


# Alias for backward compatibility
RunTracker.generate_new_runs_report = RunTracker.generate_global_report


if __name__ == '__main__':
    for i in range(1, 6):
        RunTracker.generate_batch_report(i)
    RunTracker.generate_global_report()
