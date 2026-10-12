"""
Full server pipeline: verify data, leak-free split, EfficientNet B0 training (batches 5-9),
logging under SECURESIGHT_OUTPUT_ROOT, final report, global summary.

Run on Ubuntu from the tasnim directory:
  python server_efficientnet_pipeline.py

Environment (optional overrides):
  SECURESIGHT_CODE_ROOT  default /home/secure-sight/Code
  SECURESIGHT_OUTPUT_ROOT default $CODE_ROOT/output
  SECURESIGHT_EVAL_BASE default $OUTPUT_ROOT/evaluation

Do not commit secrets; never pass passwords on the command line.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# Paths (verified at runtime on the server)
# -----------------------------------------------------------------------------
def _code_root() -> str:
    return os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code")


def _default_raw_train() -> str:
    return os.path.join(_code_root(), "extracted_features_merged")


def _default_raw_val() -> str:
    return os.path.join(_code_root(), "extracted_featuers_merged_split", "Val")


def _clean_split_root() -> str:
    return os.path.join(_code_root(), "clean_split")


def _output_root() -> str:
    return os.environ.get("SECURESIGHT_OUTPUT_ROOT", os.path.join(_code_root(), "output"))


def _eval_base() -> str:
    return os.environ.get(
        "SECURESIGHT_EVAL_BASE",
        os.path.join(_output_root(), "evaluation"),
    )


def _tasnim_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _log(msg: str, log_fp=None) -> None:
    line = f"[{datetime.utcnow().isoformat()}Z] {msg}"
    print(line, flush=True)
    if log_fp:
        log_fp.write(line + "\n")
        log_fp.flush()


def _load_json(path: str) -> Optional[Dict]:
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def step_verify_dataset(raw_train: str, raw_val: str, log_fp) -> Dict[str, Any]:
    from dataset_clean_split import verify_dataset_layout

    stats = verify_dataset_layout(raw_train, raw_val)
    _log("=== STEP 1: DATASET VERIFY ===", log_fp)
    _log(f"Train path: {raw_train} exists={stats['train_exists']}", log_fp)
    _log(f"Val path:   {raw_val} exists={stats['val_exists']}", log_fp)
    if stats.get("invalid"):
        _log("DATASET INVALID  -  missing roots or no samples.", log_fp)
        return stats

    classes = stats["class_names"]
    _log(f"Number of classes: {len(classes)}", log_fp)
    _log(f"Class names: {classes}", log_fp)
    for cls in classes:
        pc = stats["per_class"][cls]
        _log(f"  {cls}: train={pc['train']} val={pc['val']} frames", log_fp)
        ex = stats["samples_example"].get(cls, [])
        for p in ex[:3]:
            _log(f"    sample: {p}", log_fp)
    return stats


def step_leakage_and_split(raw_train: str, raw_val: str, log_fp) -> Tuple[bool, str, str, set]:
    """Returns (used_clean_split, train_root, val_root, shared_before)."""
    from dataset_clean_split import (
        build_clean_split_video_level,
        train_val_video_ids,
    )

    _log("=== STEP 2: LEAKAGE CHECK ===", log_fp)
    tid, vid = train_val_video_ids(raw_train, raw_val)
    shared = tid.intersection(vid)
    _log(f"Unique train videos (regex id): {len(tid)}", log_fp)
    _log(f"Unique val videos:            {len(vid)}", log_fp)
    _log(f"Shared videos (intersection): {len(shared)}", log_fp)
    if shared:
        _log("DATA LEAKAGE DETECTED  -  rebuilding clean_split (copy, video-level 80/20).", log_fp)
        clean = _clean_split_root()
        build_clean_split_video_level(raw_train, raw_val, clean, seed=42, train_frac=0.8)
        tr = os.path.join(clean, "train")
        va = os.path.join(clean, "val")
        tid2, vid2 = train_val_video_ids(tr, va)
        sh2 = tid2.intersection(vid2)
        _log(f"After rebuild  -  shared videos: {len(sh2)}", log_fp)
        if sh2:
            _log(f"CRITICAL: leakage remains  -  sample shared: {list(sh2)[:10]}", log_fp)
            raise RuntimeError("clean_split still has video overlap; check filenames / IDs.")
        os.environ["SECURESIGHT_TRAIN_ROOT"] = tr
        os.environ["SECURESIGHT_VAL_ROOT"] = va
        return True, tr, va, shared

    _log("No video-level leakage  -  using raw train/val paths via env.", log_fp)
    os.environ["SECURESIGHT_TRAIN_ROOT"] = raw_train
    os.environ["SECURESIGHT_VAL_ROOT"] = raw_val
    return False, raw_train, raw_val, shared


def step_validation_summary(
    used_clean: bool,
    train_root: str,
    val_root: str,
    shared_before: set,
    log_fp,
) -> None:
    from dataset_clean_split import verify_dataset_layout

    _log("=== STEP 3: DATA VALIDATION SUMMARY ===", log_fp)
    stats = verify_dataset_layout(train_root, val_root)
    total_tr = sum(stats["per_class"][c]["train"] for c in stats["class_names"])
    total_va = sum(stats["per_class"][c]["val"] for c in stats["class_names"])
    _log(f"Final dataset train root: {train_root}", log_fp)
    _log(f"Final dataset val root:   {val_root}", log_fp)
    _log(f"Classes: {len(stats['class_names'])}", log_fp)
    _log(f"Total samples train={total_tr} val={total_va}", log_fp)
    _log(f"Dataset status: {'clean_split (rebuilt)' if used_clean else 'original paths'}", log_fp)
    _log(
        f"Leakage status: {'fixed (had %d shared videos before)' % len(shared_before) if shared_before else 'no shared videos at verify stage'}",
        log_fp,
    )


def clean_old_experiment_runs(log_fp) -> None:
    """Remove prior batch_5..batch_9 artifacts; keep scripts and configs."""
    _log("=== STEP 8: CLEAN OLD RESULTS (batches 5 - 9 only) ===", log_fp)
    base = _eval_base()
    detailed = os.path.join(base, "detailed_results")
    comparisons = os.path.join(base, "results_comparisons")
    for b in range(5, 10):
        p1 = os.path.join(detailed, f"batch_{b}")
        p2 = os.path.join(comparisons, f"batch_{b}_comparisons")
        if os.path.isdir(p1):
            shutil.rmtree(p1)
            _log(f"Removed {p1}", log_fp)
        if os.path.isdir(p2):
            shutil.rmtree(p2)
            _log(f"Removed {p2}", log_fp)
    # Shared checkpoint dir (legacy); per-run checkpoints live under run dirs.
    ckpt_dir = os.path.join(_output_root(), "checkpoints")
    if os.path.isdir(ckpt_dir):
        for fn in os.listdir(ckpt_dir):
            if fn.endswith(".pth"):
                try:
                    os.remove(os.path.join(ckpt_dir, fn))
                except OSError:
                    pass
        _log(f"Cleared shared checkpoints under {ckpt_dir}", log_fp)


def _pick_best_run_across_batches(batch_nums: List[int]) -> Tuple[str, Dict]:
    best_path = None
    best_f1 = -1.0
    best_summary: Dict = {}
    for bn in batch_nums:
        batch_dir = os.path.join(_eval_base(), "detailed_results", f"batch_{bn}")
        if not os.path.isdir(batch_dir):
            continue
        for run_name in sorted(os.listdir(batch_dir)):
            rd = os.path.join(batch_dir, run_name)
            sp = os.path.join(rd, "run_summary.json")
            if not os.path.isfile(sp):
                continue
            s = _load_json(sp) or {}
            f1 = float(s.get("final_val_f1", -1) or -1)
            fm = s.get("final_metrics") or {}
            if f1 < 0 and fm:
                f1 = float(fm.get("f1", -1) or -1)
            if f1 > best_f1:
                best_f1 = f1
                best_path = rd
                best_summary = s
    if best_path is None:
        raise RuntimeError(f"No completed runs in batches {batch_nums}")
    return best_path, best_summary


def _pick_best_run(batch_num: int) -> Tuple[str, Dict]:
    batch_dir = os.path.join(_eval_base(), "detailed_results", f"batch_{batch_num}")
    best_path = None
    best_f1 = -1.0
    best_summary = {}
    if not os.path.isdir(batch_dir):
        raise FileNotFoundError(batch_dir)
    for run_name in sorted(os.listdir(batch_dir)):
        rd = os.path.join(batch_dir, run_name)
        sp = os.path.join(rd, "run_summary.json")
        if not os.path.isfile(sp):
            continue
        s = _load_json(sp) or {}
        f1 = float(s.get("final_val_f1", -1) or -1)
        fm = s.get("final_metrics") or {}
        if f1 < 0 and fm:
            f1 = float(fm.get("f1", -1) or -1)
        if f1 > best_f1:
            best_f1 = f1
            best_path = rd
            best_summary = s
    if best_path is None:
        raise RuntimeError(f"No completed runs found under batch_{batch_num}")
    return best_path, best_summary


def hyperparams_batch_5() -> List[Dict[str, Any]]:
    return [
        dict(lr=1e-4, batch_size=32, optimizer="adamw", weight_decay=1e-5, seed=42),
        dict(lr=3e-4, batch_size=16, optimizer="adamw", weight_decay=1e-4, seed=43),
        dict(lr=1e-3, batch_size=32, optimizer="adam", weight_decay=0.0, seed=44),
        dict(lr=5e-5, batch_size=64, optimizer="adamw", weight_decay=1e-4, seed=45),
        dict(lr=2e-4, batch_size=24, optimizer="adamw", weight_decay=5e-5, seed=46),
    ]


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
        seen = []
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


def run_train_subprocess(
    batch_num: int,
    run_idx: int,
    hp: Dict[str, Any],
    log_fp,
) -> None:
    train_py = os.path.join(_tasnim_root(), "train.py")
    env = os.environ.copy()
    env.setdefault("SECURESIGHT_CODE_ROOT", _code_root())
    env.setdefault("SECURESIGHT_OUTPUT_ROOT", _output_root())
    env.setdefault("SECURESIGHT_EVAL_BASE", _eval_base())

    root = env["SECURESIGHT_CODE_ROOT"]
    if "SECURESIGHT_TRAIN_ROOT" not in env or "SECURESIGHT_VAL_ROOT" not in env:
        raise RuntimeError("Train/val roots not set  -  run leakage step first.")

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

    _log(f"RUN subprocess: {' '.join(cmd)}", log_fp)
    t0 = time.time()
    log_run = os.path.join(_output_root(), "logs", f"run_batch{batch_num}_r{run_idx}.log")
    os.makedirs(os.path.dirname(log_run), exist_ok=True)
    with open(log_run, "w", encoding="utf-8", buffering=1) as lf:
        proc = subprocess.run(
            cmd,
            cwd=_tasnim_root(),
            env=env,
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    dt = time.time() - t0
    _log(f"Run finished in {dt:.1f}s exit={proc.returncode} log={log_run}", log_fp)
    if proc.returncode != 0:
        raise RuntimeError(f"Training failed batch={batch_num} run={run_idx}")


def write_global_summary(state: Dict[str, Any], log_fp) -> None:
    base = _eval_base()
    summaries: List[Dict] = []
    for b in range(5, 10):
        bd = os.path.join(base, "detailed_results", f"batch_{b}")
        if not os.path.isdir(bd):
            continue
        for run in sorted(os.listdir(bd)):
            sp = os.path.join(bd, run, "run_summary.json")
            d = _load_json(sp)
            if not d:
                continue
            d["_batch"] = b
            d["_run_folder"] = run
            summaries.append(d)

    if not summaries:
        _log("WARNING: no run summaries found for global summary.", log_fp)
        return

    accs = [float(s.get("final_val_acc", 0) or 0) for s in summaries]
    f1s = [float(s.get("final_val_f1", 0) or 0) for s in summaries]
    best = max(summaries, key=lambda s: float(s.get("final_val_f1", -1) or -1))

    out_txt = os.path.join(base, "global_summary.txt")
    by_batch: Dict[int, List[float]] = {}
    for s in summaries:
        by_batch.setdefault(int(s["_batch"]), []).append(float(s.get("final_val_f1", 0) or 0))

    lines = [
        "SecureSight  -  Global summary (batches 5 - 9)",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        f"Total runs: {len(summaries)}",
        f"Mean accuracy: {sum(accs)/max(len(accs),1):.6f}",
        f"Mean macro-F1 (epoch final): {sum(f1s)/max(len(f1s),1):.6f}",
        f"Best run folder: {best.get('_run_folder')} batch={best.get('_batch')}",
        f"Best val F1: {best.get('final_val_f1')}",
        f"Best val Acc: {best.get('final_val_acc')}",
        "",
        "Per-batch mean F1:",
    ]
    for b in sorted(by_batch):
        xs = by_batch[b]
        lines.append(f"  batch_{b}: {sum(xs)/max(len(xs),1):.6f} (n={len(xs)})")

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    state["global_summary_path"] = out_txt
    state["mean_accuracy"] = sum(accs) / max(len(accs), 1)
    state["mean_f1"] = sum(f1s) / max(len(f1s), 1)
    state["best_run_dir"] = os.path.join(
        base, "detailed_results", f"batch_{best['_batch']}", best["_run_folder"]
    )
    state["best_val_acc"] = best.get("final_val_acc")
    state["best_val_f1"] = best.get("final_val_f1")
    _log(f"Global summary written: {out_txt}", log_fp)


def cleanup_minor(log_fp) -> None:
    """Remove run stdout duplicates if needed; keep plots and JSON."""
    _log("=== STEP 11: CLEANUP (temp scan) ===", log_fp)
    troot = _tasnim_root()
    for root, dirs, files in os.walk(troot):
        if "__pycache__" in dirs:
            for d in list(dirs):
                if d == "__pycache__":
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)


def main() -> None:
    raw_train = os.environ.get("SECURESIGHT_RAW_TRAIN", _default_raw_train())
    raw_val = os.environ.get("SECURESIGHT_RAW_VAL", _default_raw_val())

    os.makedirs(os.path.join(_output_root(), "logs"), exist_ok=True)
    master_log = os.path.join(_output_root(), "logs", "pipeline_master.log")

    state_path = os.path.join(_output_root(), "logs", "pipeline_state.json")
    state: Dict[str, Any] = {
        "started": datetime.utcnow().isoformat() + "Z",
        "raw_train": raw_train,
        "raw_val": raw_val,
    }

    with open(master_log, "a", encoding="utf-8") as log_fp:
        _log("======== PIPELINE START ========", log_fp)
        stats = step_verify_dataset(raw_train, raw_val, log_fp)
        if stats.get("invalid"):
            sys.exit(2)

        used_clean, tr_root, va_root, shared_before = step_leakage_and_split(
            raw_train, raw_val, log_fp
        )
        state["used_clean_split"] = used_clean
        state["final_train_root"] = tr_root
        state["final_val_root"] = va_root
        state["shared_videos_before"] = len(shared_before)

        step_validation_summary(used_clean, tr_root, va_root, shared_before, log_fp)

        clean_old_experiment_runs(log_fp)

        best_hp: Optional[Dict[str, Any]] = None

        for batch_num in range(5, 10):
            if batch_num == 5:
                grid = hyperparams_batch_5()
            elif batch_num in (6, 7, 8):
                prev_b = batch_num - 1
                _, summ = _pick_best_run(prev_b)
                best_hp = (summ.get("hyperparams") or {}).copy()
                if not best_hp:
                    raise RuntimeError(
                        f"Batch {prev_b} hyperparams missing; cannot refine batch {batch_num}"
                    )
                grid = hyperparams_refine(batch_num, best_hp)
            else:
                _, summ9 = _pick_best_run_across_batches([5, 6, 7, 8])
                best_hp = (summ9.get("hyperparams") or {}).copy()
                if not best_hp:
                    raise RuntimeError("Could not read hyperparams for batch 9")
                grid = hyperparams_batch_9(best_hp)

            for run_idx, hp in enumerate(grid):
                run_train_subprocess(batch_num, run_idx + 1, hp, log_fp)

        write_global_summary(state, log_fp)

        best_dir = state.get("best_run_dir")
        if best_dir:
            env = os.environ.copy()
            cmd = [
                sys.executable,
                os.path.join(_tasnim_root(), "final_eval_best_run.py"),
                "--run-dir",
                best_dir,
                "--code-root",
                _code_root(),
            ]
            _log(f"Final diagnostic: {' '.join(cmd)}", log_fp)
            subprocess.check_call(cmd, cwd=_tasnim_root(), env=env)

            report_fp = os.path.join(_eval_base(), "final_report.txt")
            if os.path.isfile(report_fp):
                with open(report_fp, "a", encoding="utf-8") as rf:
                    rf.write("\n\n==============================\n")
                    rf.write("PIPELINE  -  VIDEO-LEVEL LEAKAGE CHECK\n")
                    rf.write("==============================\n")
                    rf.write(
                        f"* Original train/val shared video count (before fix): {state.get('shared_videos_before', 0)}\n"
                    )
                    rf.write(
                        f"* Used rebuilt clean_split: {bool(state.get('used_clean_split'))}\n"
                    )
                    rf.write(f"* Final train root: {state.get('final_train_root')}\n")
                    rf.write(f"* Final val root:   {state.get('final_val_root')}\n")

        cleanup_minor(log_fp)

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        _log("======== PIPELINE COMPLETE ========", log_fp)

    # Final required console block
    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    print(f"Dataset status: {'fixed (clean_split)' if state.get('used_clean_split') else 'clean (original paths)'}")
    print(
        f"Leakage status: {'rebuilt split (had overlap)' if state.get('shared_videos_before', 0) > 0 else 'no train/val video overlap at verification'}"
    )
    print("Total runs executed: 25")
    print(f"Best accuracy (val, from summaries): {state.get('best_val_acc')}")
    print(f"Best F1-score (val): {state.get('best_val_f1')}")
    print(f"Final dataset train path: {state.get('final_train_root')}")
    print(f"Final dataset val path:   {state.get('final_val_root')}")
    print(f"Output path: {_output_root()}")
    print(f"Evaluation path: {_eval_base()}")
    print(f"Master log: {master_log}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
