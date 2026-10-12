import os
import hashlib
import numpy as np
import datetime
import random
from typing import List
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from path_setup import get_evaluation_report_dir

def compute_file_hash(filepath: str) -> str:
    """Compute MD5 hash of a file to detect duplicates."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return "UNKNOWN"

def generate_diagnostic_report(
    train_loader,
    val_loader,
    y_true: np.ndarray,
    y_prob: np.ndarray,
    class_names: List[str],
    val_loss: float = None,
    add_timestamp: bool = True,
    filename: str = "diagnostic_report",
    exact_path: str = None,
):
    """Generates a detailed diagnostic report mapping out data health and model performance."""
    # Retrieve datasets
    train_ds = train_loader.dataset
    val_ds = val_loader.dataset
    
    # 1. DATASET OVERVIEW
    total_train = len(train_ds)
    total_val = len(val_ds)
    total_samples = total_train + total_val
    num_classes = len(class_names)
    
    lines = []
    lines.append("==============================")
    lines.append("1. DATASET OVERVIEW")
    lines.append("==============================")
    lines.append(f"* Total number of samples: {total_samples}")
    lines.append(f"* Number of classes: {num_classes}")
    lines.append(f"* List all class names: {', '.join(class_names)}")
    
    class_counts = {i: 0 for i in range(num_classes)}
    for _, lbl in train_ds.samples:
        class_counts[lbl] += 1
    for _, lbl in val_ds.samples:
        class_counts[lbl] += 1
        
    for i in range(num_classes):
        cnt = class_counts[i]
        pct = (cnt / total_samples) * 100 if total_samples > 0 else 0
        lines.append(f"  - {class_names[i]}: {cnt} samples ({pct:.2f}%)")
        
    lines.append("")
    lines.append("==============================")
    lines.append("2. TRAIN / VALIDATION SPLIT CHECK")
    lines.append("=================================")
    lines.append(f"* Number of samples in train: {total_train}")
    lines.append(f"* Number of samples in validation: {total_val}")
    
    train_paths = [p for p, _ in train_ds.samples]
    val_paths = [p for p, _ in val_ds.samples]
    
    train_names = [os.path.basename(p) for p in train_paths]
    val_names = [os.path.basename(p) for p in val_paths]
    
    dup_names = set(train_names).intersection(set(val_names))
    dup_paths = set(train_paths).intersection(set(val_paths))
    
    lines.append(f"* Duplicate file names between train/val: {len(dup_names)}")
    if len(dup_names) > 0 and len(dup_names) <= 10:
        lines.append(f"  -> {list(dup_names)}")
    elif len(dup_names) > 10:
        lines.append(f"  -> (Showing first 10): {list(dup_names)[:10]}")
        
    lines.append(f"* Duplicate file paths between train/val: {len(dup_paths)}")
    
    identical_hashes = 0
    if len(dup_names) > 0:
        lines.append("* Hash check for files with duplicate names (checking up to 100)...")
        train_name_to_path = {os.path.basename(p): p for p in train_paths}
        val_name_to_path = {os.path.basename(p): p for p in val_paths}
        
        for name in list(dup_names)[:100]:
            thash = compute_file_hash(train_name_to_path[name])
            vhash = compute_file_hash(val_name_to_path[name])
            if thash != "UNKNOWN" and thash == vhash:
                identical_hashes += 1
        lines.append(f"  -> Found {identical_hashes} identical file hashes.")
    else:
        lines.append("* No duplicate names, skipping hash check.")
        
    lines.append("")
    lines.append("==============================")
    lines.append("3. PREDICTION DISTRIBUTION")
    lines.append("==========================")
    
    y_pred = np.argmax(y_prob, axis=1)
    
    pred_counts = {i: 0 for i in range(num_classes)}
    true_counts = {i: 0 for i in range(num_classes)}
    
    for p, t in zip(y_pred, y_true):
        pred_counts[p] += 1
        true_counts[t] += 1
        
    lines.append(f"{'Class':<20} | {'Predicted':<10} | {'Actual':<10}")
    lines.append("-" * 47)
    for i in range(num_classes):
        lines.append(f"{class_names[i]:<20} | {pred_counts[i]:<10} | {true_counts[i]:<10}")
        
    lines.append("")
    lines.append("==============================")
    lines.append("4. CONFUSION MATRIX")
    lines.append("===================")
    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
    
    lines.append("Raw Confusion Matrix:")
    header = f"{'True / Pred':<15} | " + " | ".join([f"{c[:8]:<8}" for c in class_names])
    lines.append(header)
    lines.append("-" * len(header))
    for i in range(num_classes):
        row = f"{class_names[i][:15]:<15} | " + " | ".join([f"{cm[i, j]:<8}" for j in range(num_classes)])
        lines.append(row)
        
    lines.append("\nNormalized Confusion Matrix (%):")
    cm_norm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)), normalize='true')
    header2 = f"{'True / Pred':<15} | " + " | ".join([f"{c[:8]:<8}" for c in class_names])
    lines.append(header2)
    lines.append("-" * len(header2))
    for i in range(num_classes):
        row = f"{class_names[i][:15]:<15} | " + " | ".join([f"{cm_norm[i, j]*100:>7.1f}%" for j in range(num_classes)])
        lines.append(row)
        
    lines.append("")
    lines.append("==============================")
    lines.append("5. PER-CLASS METRICS")
    lines.append("====================")
    
    prec, rec, f1, sup = precision_recall_fscore_support(y_true, y_pred, labels=list(range(num_classes)), zero_division=0)
    lines.append(f"{'Class':<20} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<10}")
    lines.append("-" * 73)
    for i in range(num_classes):
        lines.append(f"{class_names[i]:<20} | {prec[i]:<10.4f} | {rec[i]:<10.4f} | {f1[i]:<10.4f} | {sup[i]:<10}")
        
    lines.append("")
    lines.append("==============================")
    lines.append("6. ERROR ANALYSIS")
    lines.append("=================")
    
    wrong_idx = np.where(y_pred != y_true)[0]
    total_wrong = len(wrong_idx)
    pct_wrong = (total_wrong / len(y_true)) * 100 if len(y_true) > 0 else 0
    
    lines.append(f"* Total number of wrong predictions: {total_wrong}")
    lines.append(f"* Percentage of wrong predictions: {pct_wrong:.2f}%")
    
    confusions = {}
    for t, p in zip(y_true[wrong_idx], y_pred[wrong_idx]):
        pair = (t, p)
        confusions[pair] = confusions.get(pair, 0) + 1
        
    sorted_confusions = sorted(confusions.items(), key=lambda x: x[1], reverse=True)
    lines.append("\n* Most frequent misclassification pairs:")
    for (t, p), count in sorted_confusions[:5]:
        lines.append(f"  - {class_names[t]} -> predicted as -> {class_names[p]}: {count} times")
        
    lines.append("\n* Sample WRONG predictions (showing up to 20):")
    
    for idx in wrong_idx[:20]:
        t = y_true[idx]
        p = y_pred[idx]
        conf = y_prob[idx, p]
        
        if idx < len(val_ds.samples):
            fpath = val_ds.samples[idx][0]
        else:
            fpath = f"UNKNOWN_INDEX_{idx}"
            
        fname = os.path.basename(fpath)
        
        lines.append(f"  - File Name: {fname}")
        lines.append(f"    Full Path: {fpath}")
        lines.append(f"    True Label: {class_names[t]} | Pred Label: {class_names[p]} | Confidence: {conf:.4f}")
        lines.append("")
    lines.append("")
    lines.append("==============================")
    lines.append("7. CONFIDENCE ANALYSIS (IMPORTANT)")
    lines.append("==================================")
    
    correct_idx = np.where(y_pred == y_true)[0]
    
    avg_conf_correct = np.mean(y_prob[correct_idx, y_pred[correct_idx]]) if len(correct_idx) > 0 else 0
    avg_conf_wrong = np.mean(y_prob[wrong_idx, y_pred[wrong_idx]]) if len(wrong_idx) > 0 else 0
    
    lines.append(f"* Average confidence for correct predictions: {avg_conf_correct:.4f}")
    lines.append(f"* Average confidence for wrong predictions:   {avg_conf_wrong:.4f}")
    
    if avg_conf_wrong > 0.8:
        lines.append("\n[WARNING] Wrong predictions have very high confidence! Model might be overconfident and learning wrong patterns.")
        
    lines.append("")
    lines.append("==============================")
    lines.append("8. LEAKAGE / OVERFITTING INDICATORS")
    lines.append("===================================")
    
    warnings = []
    val_acc = len(correct_idx) / len(y_true) if len(y_true) > 0 else 0
    
    if val_acc > 0.97:
        if val_loss is not None and val_loss < 0.1:
            warnings.append(f"WARNING: Validation accuracy is extremely high (>97%) with very low loss ({val_loss:.4f}). Check for data leakage.")
        else:
            warnings.append("WARNING: Validation accuracy is extremely high (>97%). Check for data leakage.")
        
    if total_wrong < len(y_true) * 0.01 and len(y_true) > 0:
        warnings.append("WARNING: Very few misclassifications (<1%). Too good to be true?")
        
    diag_sum = np.trace(cm)
    if diag_sum == np.sum(cm) and np.sum(cm) > 0:
        warnings.append("WARNING: Perfect confusion matrix diagonal. Extreme risk of data leakage.")
        
    if len(dup_paths) > 0 or identical_hashes > 0:
        warnings.append(f"WARNING: Found {len(dup_paths)} identical paths and {identical_hashes} identical hashes between Train and Validation sets. Data is leaking!")
        
    if not warnings:
        lines.append("No obvious leakage indicators found.")
    else:
        for w in warnings:
            lines.append(w)
            
    lines.append("")
    lines.append("==============================")
    lines.append("9. FINAL SUMMARY")
    lines.append("================")
    
    lines.append("* Is the dataset balanced?")
    if total_samples > 0:
        min_class_pct = min([class_counts[i] for i in range(num_classes)]) / total_samples
        max_class_pct = max([class_counts[i] for i in range(num_classes)]) / total_samples
        if max_class_pct / max(min_class_pct, 1e-5) > 3:
            lines.append(f"  -> NO. High imbalance detected (Min class: {min_class_pct*100:.1f}%, Max class: {max_class_pct*100:.1f}%).")
        else:
            lines.append(f"  -> YES. Classes are relatively balanced.")
    else:
        lines.append("  -> UNKNOWN. Dataset is empty.")
        
    lines.append("* Any suspicious patterns?")
    if avg_conf_wrong > 0.85:
        lines.append("  -> High confidence errors. The model is confidently wrong. Check labels for misclassified samples.")
    else:
        lines.append("  -> Errors seem to have reasonable uncertainty.")
        
    lines.append("* Possible data leakage?")
    if len(warnings) > 0:
        lines.append(f"  -> YES! Found {len(warnings)} leakage indicators (see Section 8).")
    else:
        lines.append("  -> Unlikely based on automated checks.")
        
    lines.append("* Model generalization quality:")
    if val_acc > 0.95 and len(warnings) == 0:
        lines.append(f"  -> Excellent (Val Acc: {val_acc:.4f}).")
    elif val_acc > 0.80:
        lines.append(f"  -> Good (Val Acc: {val_acc:.4f}).")
    else:
        lines.append(f"  -> Poor (Val Acc: {val_acc:.4f}).")
        
    # ==============================
    # 10. DATASET VERIFICATION (CRITICAL)
    # ==============================
    lines.append("")
    lines.append("==============================")
    lines.append("10. DATASET VERIFICATION (CRITICAL)")
    lines.append("===================================")
    
    # Extract paths
    train_paths = [p for p, _ in train_ds.samples]
    val_paths = [p for p, _ in val_ds.samples]
    
    all_paths = train_paths + val_paths
    if all_paths:
        try:
            dataset_root = os.path.commonpath(all_paths)
            train_root = os.path.commonpath(train_paths) if train_paths else "N/A"
            val_root = os.path.commonpath(val_paths) if val_paths else "N/A"
        except:
            dataset_root = "Multiple roots/drives detected"
            train_root = "N/A"
            val_root = "N/A"
    else:
        dataset_root = "N/A"
        train_root = "N/A"
        val_root = "N/A"
        
    lines.append(f"* Dataset root directory: {dataset_root}")
    lines.append(f"* Train directory path:  {train_root}")
    lines.append(f"* Val directory path:    {val_root}")
    
    # Actual classes detected
    detected_classes = sorted(list(train_ds.class_counts.keys()))
    num_detected = len(detected_classes)
    lines.append(f"* Actual number of classes detected: {num_detected}")
    lines.append(f"* Class names loaded: {', '.join(class_names)}")
    
    lines.append("\n* Samples per class:")
    lines.append(f"{'Class':<20} | {'Train Samples':<15} | {'Val Samples':<15}")
    lines.append("-" * 56)
    
    for i in range(num_detected):
        t_cnt = train_ds.class_counts.get(i, 0)
        v_cnt = val_ds.class_counts.get(i, 0)
        c_name = class_names[i] if i < len(class_names) else f"Unknown_{i}"
        lines.append(f"{c_name:<20} | {t_cnt:<15} | {v_cnt:<15}")
        
    lines.append(f"\n* TOTAL samples - Train: {total_train}, Validation: {total_val}")
    
    lines.append("\n* RANDOM SAMPLE FILES FROM EACH CLASS:")
    for i in range(num_detected):
        c_name = class_names[i] if i < len(class_names) else f"Unknown_{i}"
        lines.append(f"  Class: {c_name}")
        class_samples = [p for p, l in train_ds.samples if l == i]
        if not class_samples:
            class_samples = [p for p, l in val_ds.samples if l == i]
            
        num_to_show = min(len(class_samples), 5)
        samples_to_show = random.sample(class_samples, num_to_show) if class_samples else []
        for s in samples_to_show:
            lines.append(f"    - {s}")
            
    lines.append("\n* FIRST 20 FILE PATHS (TRAIN):")
    for p in train_paths[:20]:
        lines.append(f"  - {p}")
        
    lines.append("\n* FIRST 20 FILE PATHS (VAL):")
    for p in val_paths[:20]:
        lines.append(f"  - {p}")
        
    # Warnings
    if total_samples < 100:
        lines.append(f"\n[WARNING] Dataset size is too small ({total_samples} samples) — possible dummy or incorrect dataset loaded")
        print(f"[WARNING] Dataset size is too small ({total_samples} samples)")
    
    if num_detected < 3:
        lines.append(f"\n[WARNING] Only {num_detected} classes detected — check dataset loading logic")
        print(f"[WARNING] Only {num_detected} classes detected")

    # Print critical verification info to terminal immediately
    print("\n" + "="*40)
    print("DATASET VERIFICATION SUMMARY")
    print("="*40)
    print(f"Root: {dataset_root}")
    print(f"Total Samples: {total_samples} (Train: {total_train}, Val: {total_val})")
    print(f"Classes Detected: {num_detected} ({', '.join(class_names[:num_detected])})")
    print("="*40 + "\n")
        
    # ---------------------------------------------------------
    # Setup Absolute Output Path
    # ---------------------------------------------------------
    PROJECT_ROOT = os.getcwd()
    if exact_path:
        output_path = exact_path
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    else:
        output_dir = get_evaluation_report_dir()
        os.makedirs(output_dir, exist_ok=True)
        base_filename = filename
        if add_timestamp:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out_filename = f"{base_filename}_{timestamp}.txt"
        else:
            out_filename = f"{base_filename}.txt"
        output_path = os.path.join(output_dir, out_filename)

    print(">>> Current Working Directory:", PROJECT_ROOT)
    print(">>> Report path:", output_path)
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
        
    print(">>> Diagnostic report saved at:", output_path)
