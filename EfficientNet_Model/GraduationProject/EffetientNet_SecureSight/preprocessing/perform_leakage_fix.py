import os
import re
import shutil
import random
import numpy as np
import sys
from collections import defaultdict
import datetime

# Mocking project structure access (will work when run on server in project root)
sys.path.append(os.getcwd())

def get_video_id(filename):
    # Pattern: v_<Class>_<ID>_frameXXX.jpg
    match = re.match(r'(v_.*?_\d+)_frame', filename)
    if match:
        return match.group(1)
    return None

def detect_leakage(train_dir, val_dir):
    print(f"\n[STEP 1] Detecting Leakage...")
    
    def scan_dir(directory):
        vids = set()
        if not os.path.exists(directory): return vids
        for root, _, files in os.walk(directory):
            for f in files:
                vid = get_video_id(f)
                if vid: vids.add(vid)
        return vids

    train_ids = scan_dir(train_dir)
    val_ids = scan_dir(val_dir)
    shared = train_ids.intersection(val_ids)

    print(f"  Total train videos: {len(train_ids)}")
    print(f"  Total val videos:   {len(val_ids)}")
    print(f"  Shared videos:      {len(shared)}")
    
    if len(shared) > 0:
        print("  🚨 CRITICAL: DATA LEAKAGE DETECTED")
        return list(shared)
    else:
        print("  ✅ No video-level leakage detected.")
        return []

def fix_leakage(src_dirs, clean_root):
    print(f"\n[STEP 2] Fixing Leakage (Rebuilding Split)...")
    
    train_root = os.path.join(clean_root, "train")
    val_root = os.path.join(clean_root, "val")
    
    if os.path.exists(clean_root):
        shutil.rmtree(clean_root)
    os.makedirs(train_root, exist_ok=True)
    os.makedirs(val_root, exist_ok=True)

    # Collect all frames by video ID and Class
    class_videos = defaultdict(lambda: defaultdict(list)) # class -> video_id -> [paths]
    
    for src in src_dirs:
        if not os.path.exists(src): continue
        for root, dirs, files in os.walk(src):
            # Assume class name is the immediate parent dir name
            class_name = os.path.basename(root)
            for f in files:
                vid = get_video_id(f)
                if vid:
                    class_videos[class_name][vid].append(os.path.join(root, f))

    # Split each class
    for cls, vids_dict in class_videos.items():
        vid_ids = list(vids_dict.keys())
        random.seed(42)
        random.shuffle(vid_ids)
        
        split_idx = int(len(vid_ids) * 0.8)
        train_vids = vid_ids[:split_idx]
        val_vids = vid_ids[split_idx:]
        
        print(f"  Class {cls:<15}: {len(vid_ids):>4} videos -> {len(train_vids):>4} Train, {len(val_vids):>4} Val")
        
        # Move files
        cls_train_dir = os.path.join(train_root, cls)
        cls_val_dir = os.path.join(val_root, cls)
        os.makedirs(cls_train_dir, exist_ok=True)
        os.makedirs(cls_val_dir, exist_ok=True)
        
        for vid in train_vids:
            for fpath in vids_dict[vid]:
                shutil.copy2(fpath, os.path.join(cls_train_dir, os.path.basename(fpath)))
        for vid in val_vids:
            for fpath in vids_dict[vid]:
                shutil.copy2(fpath, os.path.join(cls_val_dir, os.path.basename(fpath)))

    print(f"  New split created at: {clean_root}")

def retrain_and_evaluate(clean_root):
    print(f"\n[STEP 4] Retraining Model on Clean Split...")
    
    # Update config paths
    import config
    config.TRAIN_DIRS = [os.path.join(clean_root, "train")]
    config.VAL_DIRS = [os.path.join(clean_root, "val")]
    config.NUM_EPOCHS = 20 # Match historical batches
    
    import train
    # Capture old metrics from the most recent run summary if possible
    old_acc, old_f1 = 0.9800, 0.9700 # Defaults based on latest Batch 9 reports
    
    # Run training
    print("  Starting retraining...")
    # Mocking sys.argv for train.main()
    sys.argv = ["train.py", "--run_name", "after_fix", "--batch", "10"]
    train.main()
    
    # The training generates diagnostic_report_*.txt in evaluation/report/
    # We need to find the latest one and rename it
    report_dir = "evaluation/report"
    reports = sorted([f for f in os.listdir(report_dir) if f.startswith("diagnostic_report_")])
    if reports:
        latest = reports[-1]
        target = "diagnostic_report_AFTER_FIX.txt"
        shutil.copy2(os.path.join(report_dir, latest), os.path.join(report_dir, target))
        print(f"  Final report saved as: {target}")

    # For Step 7: We'll print the comparison
    # We'd ideally pull this from the newly created run_summary.json
    print(f"\n{'='*40}")
    print("FINAL COMPARISON")
    print(f"{'='*40}")
    print(f"Old Accuracy: {old_acc:.4f}")
    print(f"Old F1-Score: {old_f1:.4f}")
    # We will let the train.py output show the new ones.
    print(f"{'='*40}")

if __name__ == "__main__":
    TRAIN_SRC = "/home/secure-sight/Code/extracted_features_merged"
    VAL_SRC = "/home/secure-sight/Code/extracted_featuers_merged_split/Val"
    CLEAN_ROOT = "/home/secure-sight/Code/clean_split"
    
    shared = detect_leakage(TRAIN_SRC, VAL_SRC)
    
    if shared:
        fix_leakage([TRAIN_SRC, VAL_SRC], CLEAN_ROOT)
        
        # Step 3: Verify
        print(f"\n[STEP 3] Verifying Fix...")
        still_shared = detect_leakage(os.path.join(CLEAN_ROOT, "train"), os.path.join(CLEAN_ROOT, "val"))
        if not still_shared:
            retrain_and_evaluate(CLEAN_ROOT)
        else:
            print("  ❌ ERROR: Fix failed, leakage still present!")
    else:
        print("  No fix needed. Re-evaluating existing split...")
        retrain_and_evaluate("/home/secure-sight/Code/extracted_featuers_merged_split")
