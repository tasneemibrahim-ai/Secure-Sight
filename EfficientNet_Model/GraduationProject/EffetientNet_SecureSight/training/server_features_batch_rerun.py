"""
Run batches 5–9 on the Ubuntu server using full merged .npz features
(extracted_features_merged + Val split). Produces the same per-run layout as train.py
(detailed_results, plots, run_summary.json) and refreshes batch / new_runs comparisons.

Usage (from the tasnim directory on the server):
  export SECURESIGHT_CODE_ROOT=/home/secure-sight/Code
  # Optional: write evaluation under this repo instead of $CODE_ROOT/output/evaluation
  export SECURESIGHT_EVAL_BASE=/home/secure-sight/tasnim/evaluation

  python server_features_batch_rerun.py --clean-batches 5 6 7 8 9

Requires: merged tree exists (Normal_Videos + Anomaly_Videos) and Val mirror or flat layout.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# --- Hyperparameter grids (match server_efficientnet_pipeline) ---


def hyperparams_batch_5() -> List[Dict[str, Any]]:
    return [
        dict(lr=1e-4, batch_size=32, optimizer="adamw", weight_decay=1e-5, seed=42),
        dict(lr=3e-4, batch_size=16, optimizer="adamw", weight_decay=1e-4, seed=43),
        dict(lr=1e-3, batch_size=32, optimizer="adam", weight_decay=0.0, seed=44),
        dict(lr=5e-5, batch_size=64, optimizer="adamw", weight_decay=1e-4, seed=45),
        dict(lr=2e-4, batch_size=24, optimizer="adamw", weight_decay=5e-5, seed=46),
    ]


def _pick_best_run(eval_base: str, batch_num: int) -> Tuple[str, Dict]:
    import json

    batch_dir = os.path.join(eval_base, "detailed_results", f"batch_{batch_num}")
    best_path = None
    best_f1 = -1.0
    best_summary: Dict = {}
    if not os.path.isdir(batch_dir):
        raise FileNotFoundError(batch_dir)
    for run_name in sorted(os.listdir(batch_dir)):
        rd = os.path.join(batch_dir, run_name)
        sp = os.path.join(rd, "run_summary.json")
        if not os.path.isfile(sp):
            continue
        with open(sp, encoding="utf-8") as f:
            s = json.load(f)
        f1 = float(s.get("final_val_f1", -1) or -1)
        fm = s.get("final_metrics") or {}
        if f1 < 0 and fm:
            f1 = float(fm.get("f1", -1) or -1)
        if f1 > best_f1:
            best_f1 = f1
            best_path = rd
            best_summary = s
    if best_path is None:
        raise RuntimeError(f"No completed runs in batch_{batch_num}")
    return best_path, best_summary


def _pick_best_run_across_batches(eval_base: str, batch_nums: List[int]) -> Tuple[str, Dict]:
    best_path = None
    best_f1 = -1.0
    best_summary: Dict = {}
    import json

    for bn in batch_nums:
        batch_dir = os.path.join(eval_base, "detailed_results", f"batch_{bn}")
        if not os.path.isdir(batch_dir):
            continue
        for run_name in sorted(os.listdir(batch_dir)):
            rd = os.path.join(batch_dir, run_name)
            sp = os.path.join(rd, "run_summary.json")
            if not os.path.isfile(sp):
                continue
            with open(sp, encoding="utf-8") as f:
                s = json.load(f)
            f1 = float(s.get("final_val_f1", -1) or -1)
            fm = s.get("final_metrics") or {}
            if f1 < 0 and fm:
                f1 = float(fm.get("f1", -1) or -1)
            if f1 > best_f1:
                best_f1 = f1
                best_path = rd
                best_summary = s
    if best_path is None:
        raise RuntimeError(f"No runs in batches {batch_nums}")
    return best_path, best_summary


def hyperparams_refine(batch_num: int, best_hp: Dict[str, Any]) -> List[Dict[str, Any]]:
    hp = dict(best_hp)
    lr = float(hp.get("lr", 1e-4))
    bs = int(hp.get("batch_size", 32))
    wd = float(hp.get("weight_decay", 1e-5))
    opt = str(hp.get("optimizer", "adamw")).lower()

    if batch_num == 6:
        mults = [0.5, 0.75, 1.0, 1.25, 1.5]
        out = []
        for i, m in enumerate(mults):
            h = dict(hp)
            h["lr"] = min(lr * m, 3e-3)
            h["seed"] = 42 + i
            out.append(h)
        return out
    if batch_num == 7:
        candidates = sorted(
            {16, 24, 32, 48, 64, max(8, bs // 2), bs, min(128, bs * 2)}
        )
        candidates = [int(c) for c in candidates if 8 <= c <= 128]
        seen: List[int] = []
        for c in candidates:
            if c not in seen:
                seen.append(c)
        candidates = seen
        while len(candidates) < 5:
            candidates.append(min(128, candidates[-1] + 8))
        out = []
        for i, b in enumerate(candidates[:5]):
            h = dict(hp)
            h["batch_size"] = b
            h["seed"] = 42 + i
            out.append(h)
        return out
    if batch_num == 8:
        wds = [
            max(wd * 0.25, 1e-6),
            wd * 0.5,
            wd,
            wd * 2.0,
            min(wd * 4.0, 1e-2),
        ]
        out = []
        for i, w in enumerate(wds):
            h = dict(hp)
            h["weight_decay"] = float(w)
            h["optimizer"] = opt
            h["seed"] = 42 + i
            out.append(h)
        return out
    raise ValueError(f"No refine grid for batch {batch_num}")


def hyperparams_batch_9(best_hp: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for i in range(5):
        h = dict(best_hp)
        h["seed"] = 42 + i
        out.append(h)
    return out


def clean_batches(eval_base: str, batches: List[int], log=print) -> None:
    detailed = os.path.join(eval_base, "detailed_results")
    comparisons = os.path.join(eval_base, "results_comparisons")
    for b in batches:
        p1 = os.path.join(detailed, f"batch_{b}")
        p2 = os.path.join(comparisons, f"batch_{b}_comparisons")
        if os.path.isdir(p1):
            shutil.rmtree(p1)
            log(f"Removed {p1}")
        if os.path.isdir(p2):
            shutil.rmtree(p2)
            log(f"Removed {p2}")


def run_one_train(
    tasnim_root: str,
    env: dict,
    batch_num: int,
    run_idx: int,
    hp: Dict[str, Any],
    log_dir: str,
) -> None:
    train_py = os.path.join(tasnim_root, "train.py")
    python = sys.executable
    run_name = f"b{batch_num}_r{run_idx}_{hp.get('optimizer')} lr{hp['lr']} bs{hp['batch_size']}"
    cmd = [
        python,
        train_py,
        "--epochs",
        "20",
        "--early_stopping_patience",
        "0",
        "--batch",
        str(batch_num),
        "--run_name",
        run_name,
        "--lr",
        str(hp["lr"]),
        "--batch_size",
        str(hp["batch_size"]),
        "--optimizer",
        str(hp["optimizer"]),
        "--weight_decay",
        str(hp["weight_decay"]),
        "--seed",
        str(hp["seed"]),
    ]
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"feature_rerun_batch{batch_num}_r{run_idx}.log")
    print("RUN:", " ".join(cmd))
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8", buffering=1) as lf:
        proc = subprocess.run(
            cmd,
            cwd=tasnim_root,
            env=env,
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    dt = time.time() - t0
    print(f"Done batch {batch_num} run {run_idx} in {dt:.1f}s exit={proc.returncode} log={log_path}")
    if proc.returncode != 0:
        raise RuntimeError(f"Training failed batch={batch_num} run={run_idx}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--code-root",
        default=os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code"),
    )
    ap.add_argument(
        "--tasnim-root",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Directory containing train.py",
    )
    ap.add_argument(
        "--eval-base",
        default=os.environ.get("SECURESIGHT_EVAL_BASE"),
        help="Override evaluation root (detailed_results, results_comparisons). Default: $OUTPUT_ROOT/evaluation",
    )
    ap.add_argument(
        "--eval-in-repo",
        action="store_true",
        help="Set SECURESIGHT_EVAL_BASE to <tasnim-root>/evaluation",
    )
    ap.add_argument(
        "--clean-batches",
        type=int,
        nargs="*",
        default=[],
        help="Delete these batch_* folders under eval base before training (e.g. 5 6 7 8 9)",
    )
    args = ap.parse_args()

    code_root = args.code_root
    tasnim_root = args.tasnim_root
    output_root = os.environ.get(
        "SECURESIGHT_OUTPUT_ROOT",
        os.path.join(code_root, "output"),
    )
    if args.eval_in_repo:
        eval_base = os.path.join(tasnim_root, "evaluation")
    elif args.eval_base:
        eval_base = args.eval_base
    else:
        eval_base = os.path.join(output_root, "evaluation")

    env = os.environ.copy()
    env["SECURESIGHT_CODE_ROOT"] = code_root
    env["SECURESIGHT_OUTPUT_ROOT"] = output_root
    env["SECURESIGHT_EVAL_BASE"] = eval_base
    env["SECURESIGHT_USE_MERGED_NPZ_LAYOUT"] = "1"
    # Do not set SECURESIGHT_TRAIN_ROOT so merged layout is used (or auto-detected)

    if args.clean_batches:
        clean_batches(eval_base, sorted(set(args.clean_batches)))

    log_dir = os.path.join(output_root, "logs")

    for batch_num in range(5, 10):
        if batch_num == 5:
            grid = hyperparams_batch_5()
        elif batch_num in (6, 7, 8):
            prev_b = batch_num - 1
            _, summ = _pick_best_run(eval_base, prev_b)
            best_hp = (summ.get("hyperparams") or {}).copy()
            if not best_hp:
                raise RuntimeError(f"Missing hyperparams for refinement from batch {prev_b}")
            grid = hyperparams_refine(batch_num, best_hp)
        else:
            _, summ9 = _pick_best_run_across_batches(eval_base, [5, 6, 7, 8])
            best_hp = (summ9.get("hyperparams") or {}).copy()
            if not best_hp:
                raise RuntimeError("Missing hyperparams for batch 9")
            grid = hyperparams_batch_9(best_hp)

        for run_idx, hp in enumerate(grid, start=1):
            run_one_train(tasnim_root, env, batch_num, run_idx, hp, log_dir)

    print("All batches complete. Evaluation root:", eval_base)


if __name__ == "__main__":
    main()
