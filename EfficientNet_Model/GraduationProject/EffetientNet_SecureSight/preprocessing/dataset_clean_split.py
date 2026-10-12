"""
Video-level dataset verification and leak-free split (FINAL FIXED VERSION)
"""

from __future__ import annotations

import os
import re
import random
import shutil
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple


_IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


# =========================
# VIDEO ID EXTRACTION
# =========================
def video_id_from_filename(filename: str) -> Optional[str]:
    """
    Extract video id from filename:
    v_Arrest_001_frame010.jpg -> v_Arrest_001
    """
    m = re.match(r"(v_.*?_\d+)_frame", filename, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


# =========================
# HELPERS
# =========================
def _list_classes(root: str) -> List[str]:
    if not os.path.isdir(root):
        return []
    return sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d)) and not d.startswith(".")
    )


def _gather_frames(class_dir: str) -> List[str]:
    out: List[str] = []
    for dp, _, fnames in os.walk(class_dir):
        for f in fnames:
            if f.lower().endswith(_IMG_EXT):
                out.append(os.path.join(dp, f))
    return sorted(set(out))


# =========================
# BUILD VIDEO POOL
# =========================
def collect_videos_by_class(train_root: str, val_root: str) -> Dict[str, Dict[str, List[str]]]:
    """
    class_name -> video_id -> list of file paths
    """
    classes = sorted(set(_list_classes(train_root)) | set(_list_classes(val_root)))
    pool: Dict[str, Dict[str, List[str]]] = {c: defaultdict(list) for c in classes}

    for root in (train_root, val_root):
        if not root or not os.path.isdir(root):
            continue

        for cls in classes:
            cdir = os.path.join(root, cls)
            if not os.path.isdir(cdir):
                continue

            frames = _gather_frames(cdir)

            for fp in frames:
                parent = os.path.dirname(fp)
                base = os.path.basename(fp)

                vid = video_id_from_filename(base)

                if parent == cdir:
                    if vid is None:
                        vid = os.path.splitext(base)[0]
                else:
                    if vid is None:
                        vid = os.path.basename(parent)

                pool[cls][vid].append(fp)

    # remove duplicates
    for cls in pool:
        for vid in pool[cls]:
            pool[cls][vid] = sorted(set(pool[cls][vid]))

    return pool


# =========================
# VERIFY SPLIT
# =========================
def train_val_video_ids(train_root: str, val_root: str) -> Tuple[Set[str], Set[str]]:
    train_ids, val_ids = set(), set()

    def scan(root: str, into: Set[str]):
        if not os.path.isdir(root):
            return
        for dp, _, fnames in os.walk(root):
            for f in fnames:
                if not f.lower().endswith(_IMG_EXT):
                    continue
                vid = video_id_from_filename(f)
                if vid:
                    into.add(vid)

    scan(train_root, train_ids)
    scan(val_root, val_ids)

    return train_ids, val_ids


# =========================
# MAIN CLEAN SPLIT
# =========================
def build_clean_split_video_level(
    train_root: str,
    val_root: str,
    clean_root: str,
    seed: int = 42,
    train_frac: float = 0.8,
) -> Dict:

    random.seed(seed)

    print("\n========== BUILDING CLEAN SPLIT ==========")

    pool = collect_videos_by_class(train_root, val_root)

    # delete old split
    if os.path.isdir(clean_root):
        shutil.rmtree(clean_root)

    train_base = os.path.join(clean_root, "train")
    val_base = os.path.join(clean_root, "val")

    os.makedirs(train_base, exist_ok=True)
    os.makedirs(val_base, exist_ok=True)

    summary = {
        "classes": {},
        "total_frames_train": 0,
        "total_frames_val": 0
    }

    for cls, vdict in pool.items():

        vids = list(vdict.keys())

        # ⚠️ WARNING FOR SMALL CLASSES
        if len(vids) < 5:
            print(f"[WARNING] Class {cls} has VERY FEW videos: {len(vids)}")

        # ✅ reproducible shuffle
        vids = sorted(vids)
        random.Random(seed).shuffle(vids)

        n_train = int(len(vids) * train_frac)

        if n_train == 0 and len(vids) > 0:
            n_train = 1
        if n_train == len(vids) and len(vids) > 1:
            n_train = len(vids) - 1

        train_vids = set(vids[:n_train])
        val_vids = set(vids[n_train:])

        print(f"\nClass: {cls}")
        print(f"  Train videos: {len(train_vids)}")
        print(f"  Val videos:   {len(val_vids)}")

        summary["classes"][cls] = {
            "videos_train": len(train_vids),
            "videos_val": len(val_vids),
            "frames_train": 0,
            "frames_val": 0,
        }

        # ================= TRAIN COPY =================
        for vid in train_vids:
            dst_dir = os.path.join(train_base, cls, vid)
            os.makedirs(dst_dir, exist_ok=True)

            for src in vdict[vid]:
                dst = os.path.join(dst_dir, os.path.basename(src))
                shutil.copy2(src, dst)

                summary["classes"][cls]["frames_train"] += 1
                summary["total_frames_train"] += 1

        # ================= VAL COPY =================
        for vid in val_vids:
            dst_dir = os.path.join(val_base, cls, vid)
            os.makedirs(dst_dir, exist_ok=True)

            for src in vdict[vid]:
                dst = os.path.join(dst_dir, os.path.basename(src))
                shutil.copy2(src, dst)

                summary["classes"][cls]["frames_val"] += 1
                summary["total_frames_val"] += 1

    print("\n========== SPLIT SUMMARY ==========")
    print(f"Total train frames: {summary['total_frames_train']}")
    print(f"Total val frames:   {summary['total_frames_val']}")

    return summary