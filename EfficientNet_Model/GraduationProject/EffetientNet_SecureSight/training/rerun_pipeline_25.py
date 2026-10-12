"""
SecureSight: rigorous 25-run rerun pipeline (5 batches x 5 runs).

Key safety:
- Never writes to dataset directories.
- Writes all outputs under an experiment root (default: ~/Code/securesight_rerun_experiments/).

Per run outputs:
- model checkpoint (best_model.pth copied to run root)
- logs.txt (full training stdout/stderr)
- metrics.json (accuracy, macro + per-class precision/recall/f1, confusion matrix, meta)
- plots/ (loss/acc/f1 + combined)
- confusion_matrix.png
- radar_chart.png

Per batch outputs:
- batch_summary.txt (comparison of 5 runs, best run selection)

Final outputs:
- final_report/final_report.txt
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass(frozen=True)
class BatchHP:
    name: str
    epochs: int
    batch_size: int
    lr: float
    dropout: float
    optimizer: str
    weight_decay: float
    early_stopping_patience: int


def _now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _ensure_empty_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def _write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def _save_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def _run_cmd(cmd: List[str], *, cwd: Path, env: Dict[str, str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        f.write("COMMAND:\n")
        f.write(" ".join(cmd) + "\n\n")
        f.write("ENV OVERRIDES:\n")
        for k in sorted(env.keys()):
            if k.endswith("PASSWORD"):
                continue
            f.write(f"{k}={env[k]}\n")
        f.write("\n" + ("=" * 80) + "\n\n")
        f.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return proc.wait()


def _load_training_csv(csv_path: Path) -> Dict[str, List[float]]:
    import csv

    curves: Dict[str, List[float]] = {}
    if not csv_path.is_file():
        return curves
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                if k is None:
                    continue
                if k not in curves:
                    curves[k] = []
                try:
                    curves[k].append(float(v))
                except Exception:
                    # keep placeholder NaN to preserve alignment
                    curves[k].append(float("nan"))
    return curves


def _plot_curves(curves: Dict[str, List[float]], out_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    epochs = curves.get("epoch") or list(range(1, len(next(iter(curves.values()), [])) + 1))

    def save_one(keys: Tuple[str, ...], title: str, ylabel: str, filename: str):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1, 1, 1)
        for k in keys:
            if k in curves:
                ax.plot(epochs, curves[k], marker="o", linewidth=2, label=k)
        ax.set_title(title)
        ax.set_xlabel("Epoch")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / filename, dpi=180)
        plt.close(fig)

    save_one(("train_loss", "val_loss"), "Loss vs Epochs", "Loss", "loss_vs_epochs.png")
    save_one(("train_acc", "val_acc"), "Accuracy vs Epochs", "Accuracy", "accuracy_vs_epochs.png")
    save_one(("train_f1", "val_f1"), "F1 vs Epochs (macro)", "F1", "f1_vs_epochs.png")

    # combined
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1)
    if "val_loss" in curves:
        ax.plot(epochs, curves["val_loss"], label="val_loss", linewidth=2)
    if "val_acc" in curves:
        ax.plot(epochs, curves["val_acc"], label="val_acc", linewidth=2)
    if "val_f1" in curves:
        ax.plot(epochs, curves["val_f1"], label="val_f1", linewidth=2)
    ax.set_title("Combined Validation Metrics vs Epochs")
    ax.set_xlabel("Epoch")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "combined_metrics.png", dpi=180)
    plt.close(fig)


def _plot_confusion_matrix(cm: np.ndarray, class_names: List[str], out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cm = np.asarray(cm)
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)

    # annotate
    thresh = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                str(int(cm[i, j])),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=8,
            )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def _plot_radar(per_class_f1: List[float], class_names: List[str], out_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    values = np.asarray(per_class_f1, dtype=float)
    values = np.clip(values, 0.0, 1.0)
    labels = list(class_names)

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = np.concatenate([values, [values[0]]])
    angles = angles + [angles[0]]
    labels_closed = labels + [labels[0]]

    fig = plt.figure(figsize=(9, 9))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 1)
    ax.set_title("Radar Chart — Per-class F1", y=1.08)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def _classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, class_names: List[str]) -> Dict[str, Any]:
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    acc = float(accuracy_score(y_true, y_pred))
    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    macro = report.get("macro avg", {})
    per_class = {k: v for k, v in report.items() if k in class_names}
    return {
        "accuracy": acc,
        "macro": {
            "precision": float(macro.get("precision", 0.0)),
            "recall": float(macro.get("recall", 0.0)),
            "f1": float(macro.get("f1-score", 0.0)),
            "support": int(macro.get("support", 0)),
        },
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
    }


def _leakage_check(train_dirs: List[str], val_dirs: List[str]) -> Dict[str, Any]:
    """
    Strict but metadata-only check: intersection of relative file paths between train and val.
    This can be large; we keep it class-wise and count-only (and sample a few overlaps).
    """
    def list_files(root: Path) -> List[str]:
        out: List[str] = []
        for dp, _, fnames in os.walk(root):
            for f in fnames:
                if f.startswith("."):
                    continue
                p = Path(dp) / f
                out.append(str(p.relative_to(root)))
        return out

    results: Dict[str, Any] = {"by_class": [], "total_overlap": 0, "samples": []}
    samples: List[str] = []
    total_overlap = 0

    for tr, vr in zip(train_dirs, val_dirs):
        tr_p = Path(tr)
        vr_p = Path(vr)
        if not tr_p.exists() or not vr_p.exists():
            results["by_class"].append(
                {"train_dir": str(tr_p), "val_dir": str(vr_p), "status": "missing_dir"}
            )
            continue
        tr_files = set(list_files(tr_p))
        vr_files = set(list_files(vr_p))
        inter = tr_files.intersection(vr_files)
        total_overlap += len(inter)
        if len(samples) < 25 and inter:
            for s in list(sorted(inter))[: max(0, 25 - len(samples))]:
                samples.append(f"{tr_p.name}:{s}")
        results["by_class"].append(
            {
                "train_dir": str(tr_p),
                "val_dir": str(vr_p),
                "train_files": len(tr_files),
                "val_files": len(vr_files),
                "overlap": len(inter),
            }
        )

    results["total_overlap"] = total_overlap
    results["samples"] = samples
    return results


def run_one(
    *,
    tasnim_dir: Path,
    experiment_root: Path,
    batch_idx: int,
    run_idx: int,
    hp: BatchHP,
    seed: int,
    code_root: Path,
) -> Dict[str, Any]:
    run_dir = experiment_root / "runs" / f"batch_{batch_idx}" / f"run_{run_idx}"
    plots_dir = run_dir / "plots"
    _ensure_empty_dir(run_dir)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Training will write into SECURESIGHT_OUTPUT_ROOT (= run_dir)
    env = os.environ.copy()
    env["SECURESIGHT_CODE_ROOT"] = str(code_root)
    env["SECURESIGHT_OUTPUT_ROOT"] = str(run_dir)
    env["SECURESIGHT_EVAL_BASE"] = str(run_dir / "evaluation")
    # Prefer the server-provided clean split to avoid empty/invalid validation sets.
    # This keeps the dataset folders untouched while ensuring strict train/val separation.
    env["SECURESIGHT_TRAIN_ROOT"] = str(code_root / "clean_split" / "train")
    env["SECURESIGHT_VAL_ROOT"] = str(code_root / "clean_split" / "val")
    # clean_split is a precomputed feature dataset; force feature mode (no image backbone)
    env["SECURESIGHT_PRECOMPUTED_FEATURES"] = "1"
    env["SECURESIGHT_FEATURE_DIM"] = env.get("SECURESIGHT_FEATURE_DIM", "2560")
    env.setdefault("CUDA_VISIBLE_DEVICES", env.get("CUDA_VISIBLE_DEVICES", "0"))

    # Train
    train_cmd = [
        sys.executable,
        "-u",
        "train.py",
        "--epochs",
        str(hp.epochs),
        "--batch_size",
        str(hp.batch_size),
        "--lr",
        str(hp.lr),
        "--dropout",
        str(hp.dropout),
        "--optimizer",
        hp.optimizer,
        "--weight_decay",
        str(hp.weight_decay),
        "--seed",
        str(seed),
        "--early_stopping_patience",
        str(hp.early_stopping_patience),
        "--batch",
        str(batch_idx),
        "--run_name",
        f"batch{batch_idx}_run{run_idx}",
        "--no_aug",
    ]

    logs_path = run_dir / "logs.txt"
    rc = _run_cmd(train_cmd, cwd=tasnim_dir, env=env, log_path=logs_path)
    if rc != 0:
        return {
            "status": "failed",
            "return_code": rc,
            "run_dir": str(run_dir),
            "batch": batch_idx,
            "run": run_idx,
            "seed": seed,
            "hyperparams": dataclasses.asdict(hp),
        }

    def _pick_checkpoint() -> Path | None:
        """
        Training (train.py) writes checkpoints into the RunTracker run_dir
        (under SECURESIGHT_EVAL_BASE/detailed_results/batch_X/<run_timestamp>/),
        not necessarily under SECURESIGHT_OUTPUT_ROOT/checkpoints.

        We pick, in order:
        - run_dir/checkpoints/best_model.pth (if present)
        - newest evaluation/detailed_results/batch_X/*/best_model.pth
        - newest evaluation/detailed_results/batch_X/*/checkpoint_epoch_*.pth
        """
        cand = run_dir / "checkpoints" / "best_model.pth"
        if cand.is_file():
            return cand

        batch_dir = run_dir / "evaluation" / "detailed_results" / f"batch_{batch_idx}"
        if batch_dir.is_dir():
            subdirs = [p for p in batch_dir.iterdir() if p.is_dir()]
            subdirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            for sd in subdirs[:10]:
                best = sd / "best_model.pth"
                if best.is_file():
                    return best
                ckpts = sorted(
                    sd.glob("checkpoint_epoch_*.pth"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if ckpts:
                    return ckpts[0]
        return None

    ckpt = _pick_checkpoint()
    if ckpt is None:
        return {
            "status": "failed",
            "return_code": 0,
            "error": "training_completed_but_no_checkpoint_found",
            "run_dir": str(run_dir),
            "batch": batch_idx,
            "run": run_idx,
            "seed": seed,
            "hyperparams": dataclasses.asdict(hp),
        }

    # Copy checkpoint to run root to match required structure
    shutil.copy2(ckpt, run_dir / "best_model.pth")

    # Evaluate best checkpoint (fresh eval to produce deterministic metrics.json + cm/radar)
    # IMPORTANT: make the in-process evaluation use the same environment flags as training
    # (feature-only model, same feature dim, same split roots).
    for k in (
        "SECURESIGHT_CODE_ROOT",
        "SECURESIGHT_OUTPUT_ROOT",
        "SECURESIGHT_EVAL_BASE",
        "SECURESIGHT_TRAIN_ROOT",
        "SECURESIGHT_VAL_ROOT",
        "SECURESIGHT_PRECOMPUTED_FEATURES",
        "SECURESIGHT_FEATURE_DIM",
        "SECURESIGHT_USE_MERGED_NPZ_LAYOUT",
    ):
        if k in env:
            os.environ[k] = env[k]

    tasnim_dir_str = str(tasnim_dir)
    if tasnim_dir_str not in sys.path:
        sys.path.insert(0, tasnim_dir_str)

    import torch
    import torch.nn as nn
    from sklearn.metrics import confusion_matrix

    import config as cfg
    from dataset import create_dataloaders
    from model import create_model
    from utils import evaluate_model, get_device, load_checkpoint, set_seed

    set_seed(seed)
    device = get_device()
    train_loader, val_loader, class_info = create_dataloaders(
        train_dirs=cfg.TRAIN_DIRS,
        val_dirs=cfg.VAL_DIRS,
        batch_size=hp.batch_size,
        num_workers=cfg.NUM_WORKERS,
        max_frames=cfg.MAX_FRAMES_PER_VIDEO,
        use_augmentation=False,
        oversample_minority=False,
        sampling_strategy=cfg.SAMPLING_STRATEGY,
    )

    model = create_model(
        model_name=cfg.MODEL_NAME,
        num_classes=cfg.NUM_CLASSES,
        pretrained=cfg.PRETRAINED,
        dropout=hp.dropout,
        feature_dim=cfg.FEATURE_DIM,
        use_image_backbone=cfg.USE_IMAGE_BACKBONE,
    ).to(device)

    load_checkpoint(model, None, str(run_dir / "best_model.pth"), device)
    model.eval()
    criterion = nn.CrossEntropyLoss(weight=class_info["weights"].to(device))

    val_metrics, val_loss, y_true, y_prob = evaluate_model(model, val_loader, device, criterion)
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    y_pred = np.argmax(y_prob, axis=1)

    # Full metrics (macro + per-class) and confusion matrix
    class_names = list(cfg.CLASS_DISPLAY_NAMES)
    detailed = _classification_metrics(y_true, y_pred, class_names)
    cm = np.array(detailed["confusion_matrix"], dtype=int)

    # Curves
    curves = _load_training_csv(run_dir / "logs" / "training_results.csv")
    _plot_curves(curves, plots_dir)

    # Confusion matrix and radar chart
    _plot_confusion_matrix(cm, class_names, run_dir / "confusion_matrix.png")
    per_class_f1 = [float(detailed["per_class"][c]["f1-score"]) for c in class_names]
    _plot_radar(per_class_f1, class_names, run_dir / "radar_chart.png")

    # Leakage check (metadata-only)
    leakage = _leakage_check(cfg.TRAIN_DIRS, cfg.VAL_DIRS)

    metrics_obj = {
        "status": "ok",
        "batch": batch_idx,
        "run": run_idx,
        "seed": seed,
        "hyperparams": dataclasses.asdict(hp),
        "val_loss": float(val_loss),
        "val_metrics_macro_only": {k: float(v) for k, v in val_metrics.items()},
        "metrics": detailed,
        "dataset_distribution": {
            "train": class_info.get("train_distribution", {}),
            "val": class_info.get("val_distribution", {}),
            "class_names": class_names,
        },
        "leakage_check": leakage,
        "artifacts": {
            "checkpoint": str((run_dir / "best_model.pth").resolve()),
            "logs": str(logs_path.resolve()),
            "plots_dir": str(plots_dir.resolve()),
            "confusion_matrix_png": str((run_dir / "confusion_matrix.png").resolve()),
            "radar_chart_png": str((run_dir / "radar_chart.png").resolve()),
        },
    }
    _save_json(run_dir / "metrics.json", metrics_obj)
    return metrics_obj


def summarize_batch(experiment_root: Path, batch_idx: int) -> Dict[str, Any]:
    batch_dir = experiment_root / "runs" / f"batch_{batch_idx}"
    runs: List[Dict[str, Any]] = []
    for run_idx in range(1, 6):
        p = batch_dir / f"run_{run_idx}" / "metrics.json"
        if p.is_file():
            runs.append(json.loads(p.read_text(encoding="utf-8")))
        else:
            runs.append({"status": "missing", "run": run_idx})

    scored = []
    for r in runs:
        if r.get("status") == "ok":
            f1 = float(r["metrics"]["macro"]["f1"])
            acc = float(r["metrics"]["accuracy"])
            scored.append((f1, acc, r))

    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    best = scored[0][2] if scored else None

    # Comparison table
    lines = []
    lines.append(f"Batch {batch_idx} summary")
    lines.append("=" * 80)
    lines.append("run\tseed\tacc\tmacro_f1\tval_loss\tstatus")
    for r in runs:
        if r.get("status") == "ok":
            lines.append(
                f"{r['run']}\t{r['seed']}\t{r['metrics']['accuracy']:.6f}\t{r['metrics']['macro']['f1']:.6f}\t{r['val_loss']:.6f}\tOK"
            )
        else:
            lines.append(f"{r.get('run','?')}\t-\t-\t-\t-\t{r.get('status','?')}")

    lines.append("")
    if best:
        lines.append("Best run (by macro F1, tie-breaker accuracy):")
        lines.append(f"- run: {best['run']}")
        lines.append(f"- seed: {best['seed']}")
        lines.append(f"- acc: {best['metrics']['accuracy']:.6f}")
        lines.append(f"- macro_f1: {best['metrics']['macro']['f1']:.6f}")
        lines.append(f"- checkpoint: {best['artifacts']['checkpoint']}")
        lines.append(f"- leakage_total_overlap: {best['leakage_check']['total_overlap']}")
    else:
        lines.append("No successful runs in this batch.")

    _write_text(batch_dir / "batch_summary.txt", "\n".join(lines) + "\n")
    return {"batch": batch_idx, "runs": runs, "best": best}


def final_report(experiment_root: Path, batch_summaries: List[Dict[str, Any]]) -> None:
    out_dir = experiment_root / "final_report"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_ok = []
    for b in batch_summaries:
        for r in b["runs"]:
            if r.get("status") == "ok":
                all_ok.append(r)

    best_overall = None
    if all_ok:
        best_overall = sorted(
            all_ok,
            key=lambda r: (float(r["metrics"]["macro"]["f1"]), float(r["metrics"]["accuracy"])),
            reverse=True,
        )[0]

    accs = [float(r["metrics"]["accuracy"]) for r in all_ok]
    f1s = [float(r["metrics"]["macro"]["f1"]) for r in all_ok]
    mean_acc = float(np.mean(accs)) if accs else 0.0
    mean_f1 = float(np.mean(f1s)) if f1s else 0.0

    # Aggregate confusion matrix
    agg_cm = None
    class_names = None
    for r in all_ok:
        cm = np.array(r["metrics"]["confusion_matrix"], dtype=int)
        if agg_cm is None:
            agg_cm = cm.copy()
            class_names = r["dataset_distribution"]["class_names"]
        else:
            agg_cm += cm

    report_lines = []
    report_lines.append("SecureSight — Full Clean Re-run Experiment (25 runs)")
    report_lines.append("=" * 80)
    report_lines.append(f"Experiment root: {experiment_root}")
    report_lines.append(f"Generated at: {_now_ts()}")
    report_lines.append("")

    report_lines.append("Summary (all successful runs)")
    report_lines.append("-" * 80)
    report_lines.append(f"successful_runs: {len(all_ok)}/25")
    report_lines.append(f"mean_accuracy: {mean_acc:.6f}")
    report_lines.append(f"mean_macro_f1: {mean_f1:.6f}")
    report_lines.append("")

    report_lines.append("Best run per batch")
    report_lines.append("-" * 80)
    for b in batch_summaries:
        best = b.get("best")
        if not best:
            report_lines.append(f"batch_{b['batch']}: (no successful runs)")
            continue
        report_lines.append(
            f"batch_{b['batch']}: run_{best['run']} | acc={best['metrics']['accuracy']:.6f} | macro_f1={best['metrics']['macro']['f1']:.6f} | seed={best['seed']}"
        )
    report_lines.append("")

    report_lines.append("Best overall run")
    report_lines.append("-" * 80)
    if best_overall:
        report_lines.append(
            f"batch_{best_overall['batch']} run_{best_overall['run']} | acc={best_overall['metrics']['accuracy']:.6f} | macro_f1={best_overall['metrics']['macro']['f1']:.6f} | seed={best_overall['seed']}"
        )
        report_lines.append(f"checkpoint: {best_overall['artifacts']['checkpoint']}")
        report_lines.append(f"leakage_total_overlap: {best_overall['leakage_check']['total_overlap']}")
    else:
        report_lines.append("(none)")
    report_lines.append("")

    report_lines.append("Dataset distribution recap (from last successful run)")
    report_lines.append("-" * 80)
    if all_ok:
        last = all_ok[-1]
        report_lines.append(json.dumps(last["dataset_distribution"], indent=2))
    else:
        report_lines.append("(no data)")
    report_lines.append("")

    report_lines.append("Confusion matrix analysis (aggregated across successful runs)")
    report_lines.append("-" * 80)
    if agg_cm is not None and class_names:
        report_lines.append("class_names: " + ", ".join(class_names))
        report_lines.append("aggregate_confusion_matrix (rows=true, cols=pred):")
        report_lines.append(np.array2string(agg_cm, separator=", "))
        # simple per-class recall/precision from agg cm
        tp = np.diag(agg_cm).astype(float)
        support = agg_cm.sum(axis=1).astype(float)
        pred_sum = agg_cm.sum(axis=0).astype(float)
        with np.errstate(divide="ignore", invalid="ignore"):
            recall = np.where(support > 0, tp / support, 0.0)
            precision = np.where(pred_sum > 0, tp / pred_sum, 0.0)
        report_lines.append("")
        report_lines.append("per-class recall/precision from aggregated CM:")
        for i, cn in enumerate(class_names):
            report_lines.append(f"- {cn}: recall={recall[i]:.4f}, precision={precision[i]:.4f}, support={int(support[i])}")
    else:
        report_lines.append("(no successful runs)")
    report_lines.append("")

    report_lines.append("Stability / overfitting discussion (heuristic)")
    report_lines.append("-" * 80)
    if all_ok:
        report_lines.append(
            "We flag instability if macro F1 varies widely across seeds within the same batch."
        )
        for b in batch_summaries:
            ok = [r for r in b["runs"] if r.get("status") == "ok"]
            if not ok:
                continue
            f1 = np.array([float(r["metrics"]["macro"]["f1"]) for r in ok], dtype=float)
            report_lines.append(
                f"batch_{b['batch']}: macro_f1 mean={float(f1.mean()):.6f}, std={float(f1.std()):.6f}, min={float(f1.min()):.6f}, max={float(f1.max()):.6f}"
            )
        report_lines.append("")
        report_lines.append(
            "Overfitting check: consult each run’s plots (train vs val curves) under runs/batch_i/run_j/plots/."
        )
    else:
        report_lines.append("(no successful runs)")
    report_lines.append("")

    report_lines.append("Leakage / bias detection")
    report_lines.append("-" * 80)
    if all_ok:
        overlaps = [int(r["leakage_check"]["total_overlap"]) for r in all_ok]
        report_lines.append(f"leakage_check_total_overlap min/mean/max: {min(overlaps)}/{float(np.mean(overlaps)):.2f}/{max(overlaps)}")
        report_lines.append(
            "If total_overlap > 0, the train/val split is likely contaminated (same relative files present in both)."
        )
    else:
        report_lines.append("(no data)")
    report_lines.append("")

    _write_text(out_dir / "final_report.txt", "\n".join(report_lines) + "\n")

    # Also write aggregated CM figure if available
    if agg_cm is not None and class_names:
        _plot_confusion_matrix(agg_cm, class_names, out_dir / "aggregate_confusion_matrix.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code-root", default=os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code"))
    ap.add_argument("--tasnim-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--experiment-root", default=os.path.join(os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code"), "securesight_rerun_experiments"))
    ap.add_argument("--start-batch", type=int, default=1)
    ap.add_argument("--end-batch", type=int, default=5)
    ap.add_argument("--runs-per-batch", type=int, default=5)
    ap.add_argument("--seed-base", type=int, default=1000)
    args = ap.parse_args()

    tasnim_dir = Path(args.tasnim_dir).resolve()
    experiment_root = Path(args.experiment_root).resolve()
    code_root = Path(args.code_root).resolve()

    experiment_root.mkdir(parents=True, exist_ok=True)

    # 5 batch hyperparameter configs (change ONLY per batch)
    batch_hps: List[BatchHP] = [
        BatchHP("b1", epochs=50, batch_size=32, lr=1e-4, dropout=0.30, optimizer="adamw", weight_decay=1e-5, early_stopping_patience=10),
        BatchHP("b2", epochs=50, batch_size=32, lr=5e-5, dropout=0.20, optimizer="adamw", weight_decay=1e-4, early_stopping_patience=10),
        BatchHP("b3", epochs=50, batch_size=64, lr=2e-4, dropout=0.40, optimizer="adamw", weight_decay=1e-5, early_stopping_patience=10),
        BatchHP("b4", epochs=50, batch_size=64, lr=1e-4, dropout=0.10, optimizer="adam",  weight_decay=1e-4, early_stopping_patience=10),
        BatchHP("b5", epochs=50, batch_size=128, lr=8e-5, dropout=0.30, optimizer="adamw", weight_decay=5e-5, early_stopping_patience=10),
    ]

    batch_summaries: List[Dict[str, Any]] = []

    for batch_idx in range(args.start_batch, args.end_batch + 1):
        hp = batch_hps[batch_idx - 1]
        for run_idx in range(1, args.runs_per_batch + 1):
            seed = args.seed_base + (batch_idx - 1) * args.runs_per_batch + (run_idx - 1)
            print(f"\n=== BATCH {batch_idx} RUN {run_idx} seed={seed} ===", flush=True)
            _ = run_one(
                tasnim_dir=tasnim_dir,
                experiment_root=experiment_root,
                batch_idx=batch_idx,
                run_idx=run_idx,
                hp=hp,
                seed=seed,
                code_root=code_root,
            )
        batch_summaries.append(summarize_batch(experiment_root, batch_idx))

    final_report(experiment_root, batch_summaries)
    print(f"\nDONE. Final report at: {experiment_root / 'final_report' / 'final_report.txt'}")


if __name__ == "__main__":
    main()

