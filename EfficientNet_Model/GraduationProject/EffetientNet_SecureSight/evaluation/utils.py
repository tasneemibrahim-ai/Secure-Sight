import os
import time
import random
import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

from config import *


# =========================
# 🔧 BASIC UTILITIES
# =========================

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device() -> torch.device:
    if torch.cuda.is_available() and DEVICE == "cuda":
        return torch.device("cuda")
    return torch.device("cpu")


def format_duration(seconds: float) -> str:
    return str(datetime.timedelta(seconds=int(seconds)))


# =========================
# 💾 CHECKPOINTING
# =========================

def save_checkpoint(
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    epoch: int,
    best_f1: float,
    checkpoint_path: str,
) -> None:
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    payload = {
        "epoch": epoch,
        "best_f1": best_f1,
        "state_dict": model.state_dict(),
    }

    if optimizer is not None:
        payload["optimizer"] = optimizer.state_dict()

    torch.save(payload, checkpoint_path)


def load_checkpoint(
    model: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    checkpoint_path: str,
    device: torch.device,
) -> Dict[str, Any]:
    checkpoint = torch.load(checkpoint_path, map_location=device)

    model.load_state_dict(checkpoint["state_dict"])

    if optimizer is not None and "optimizer" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer"])

    return checkpoint


# =========================
# 📊 METRICS CORE
# =========================

def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    class_names: Optional[List[str]] = None,
) -> Dict[str, Any]:

    if class_names is None:
        class_names = CLASS_DISPLAY_NAMES

    acc = float(accuracy_score(y_true, y_pred))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    per_class = {}
    for c in class_names:
        vals = report.get(c, {})
        per_class[c] = {
            "precision": float(vals.get("precision", 0.0)),
            "recall": float(vals.get("recall", 0.0)),
            "f1": float(vals.get("f1-score", 0.0)),
            "support": int(vals.get("support", 0)),
        }

    # AUC (safe)
    auc_score = 0.0
    try:
        if y_prob.ndim == 2 and y_prob.shape[1] > 1:
            auc_score = roc_auc_score(y_true, y_prob, multi_class="ovr")
        else:
            auc_score = roc_auc_score(y_true, y_prob)
    except Exception:
        auc_score = 0.0

    cm = confusion_matrix(y_true, y_pred)

    return {
        "accuracy": acc,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "auc": float(auc_score),
        "confusion_matrix": cm.tolist(),
        "per_class": per_class,
    }


# =========================
# 🧪 MODEL EVALUATION
# =========================

def evaluate_model(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
    criterion: nn.Module,
) -> Tuple[Dict[str, Any], float, np.ndarray, np.ndarray]:

    model.eval()

    total_loss = 0.0
    y_true, y_pred, y_prob = [], [], []

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)

            logits = model(x)
            loss = criterion(logits, y)

            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)

            total_loss += loss.item()

            y_true.extend(y.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
            y_prob.append(probs.cpu().numpy())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_prob = np.vstack(y_prob)

    metrics = compute_metrics(y_true, y_pred, y_prob, CLASS_DISPLAY_NAMES)
    avg_loss = total_loss / max(len(loader), 1)

    return metrics, avg_loss, y_true, y_prob


# =========================
# 📢 PRINTING
# =========================

def print_metrics(metrics: Dict[str, Any], stage: str) -> None:
    print(
        f"\n[{stage}] "
        f"acc={metrics['accuracy']:.4f} "
        f"prec={metrics['precision']:.4f} "
        f"rec={metrics['recall']:.4f} "
        f"f1={metrics['f1']:.4f} "
        f"auc={metrics['auc']:.4f}"
    )


# =========================
# ⚡ LATENCY MEASUREMENT
# =========================

def measure_latency(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
    warmup: int = 5,
    iterations: int = 50,
) -> Dict[str, float]:

    model.eval()
    times = []

    data_iter = iter(loader)

    with torch.no_grad():

        # warmup
        for _ in range(warmup):
            try:
                x, _ = next(data_iter)
            except StopIteration:
                break

            x = x.to(device)
            _ = model(x)

            if device.type == "cuda":
                torch.cuda.synchronize()

        data_iter = iter(loader)

        for _ in range(iterations):
            try:
                x, _ = next(data_iter)
            except StopIteration:
                break

            x = x.to(device)

            start = time.perf_counter()
            _ = model(x)
            if device.type == "cuda":
                torch.cuda.synchronize()
            end = time.perf_counter()

            times.append((end - start) * 1000)

    if not times:
        return {"mean_ms": 0, "std_ms": 0, "p95_ms": 0, "p99_ms": 0}

    arr = np.array(times)

    return {
        "mean_ms": float(np.mean(arr)),
        "std_ms": float(np.std(arr)),
        "p95_ms": float(np.percentile(arr, 95)),
        "p99_ms": float(np.percentile(arr, 99)),
    }


# =========================
# 📐 COMPLEXITY ESTIMATE
# =========================

def time_complexity_estimate(dataset_size: int, params: int) -> str:
    return (
        f"O(N×P): N={dataset_size:,}, params={params:,} → "
        f"~{dataset_size * max(1, params // 1000):,} ops/epoch"
    )


# =========================
# 🧠 TRACEABILITY MATRIX
# =========================

def build_traceability_matrix(hparams: Dict[str, Any], results: List[Dict]) -> List[str]:
    lines = ["Hyperparameters → effect → observed impact"]

    if not results:
        return lines

    final = results[-1]

    gap = final.get("train_f1", 0) - final.get("val_f1", 0)

    for k, v in hparams.items():
        effect = "neutral"
        impact = "stable"

        if k == "learning_rate":
            effect = "controls convergence speed"
        elif k == "batch_size":
            effect = "affects gradient noise"
        elif k == "dropout":
            effect = "regularization strength"
        elif k == "gamma":
            effect = "focal loss focus on hard samples"

        if gap > 0.1:
            impact = "possible overfitting"
        elif gap < -0.05:
            impact = "possible underfitting or noise"

        lines.append(f"{k}={v} → {effect} → {impact}")

    return lines