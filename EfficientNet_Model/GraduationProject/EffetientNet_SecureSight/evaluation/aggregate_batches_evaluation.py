"""
Build evaluation/final_report.txt from existing evaluation/detailed_results (batches 5-9).
Run after syncing from the server or when working offline from local artifacts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

EVAL = Path(__file__).resolve().parent / "evaluation"
DETAILED = EVAL / "detailed_results"
COMPARISONS = EVAL / "results_comparisons"
DIAG = EVAL / "report" / "diagnostic_report.txt"


def main() -> None:
    lines: list[str] = []
    lines.append("SecureSight — Final consolidated report (batches 5–9)")
    lines.append(f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append(
        "NOTE: This file was assembled from local files under tasnim/evaluation/. "
        "SSH from this Cursor session to the training host:22 failed (no route/firewall). "
        "When you have VPN/internal network access, run sync_eval_from_server.py "
        "with SSH_PASS set, then re-run this script if desired."
    )
    lines.append("")

    all_rows: list[dict] = []
    for batch_num in range(5, 10):
        bdir = DETAILED / f"batch_{batch_num}"
        if not bdir.is_dir():
            continue
        for run_dir in sorted(bdir.iterdir()):
            sj = run_dir / "run_summary.json"
            if not sj.is_file():
                continue
            try:
                data = json.loads(sj.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            data["_batch"] = batch_num
            data["_folder"] = run_dir.name
            all_rows.append(data)

    if not all_rows:
        lines.append("ERROR: No run_summary.json files found under detailed_results/batch_*.")
        EVAL.mkdir(parents=True, exist_ok=True)
        (EVAL / "final_report.txt").write_text("\n".join(lines), encoding="utf-8")
        return

    lines.append("==============================")
    lines.append("1. GLOBAL SUMMARY")
    lines.append("==============================")
    accs = [float(r.get("final_val_acc") or 0) for r in all_rows]
    f1s = [float(r.get("final_val_f1") or 0) for r in all_rows]
    lines.append(f"Total runs parsed: {len(all_rows)}")
    lines.append(f"Mean validation accuracy: {sum(accs) / len(accs):.6f}")
    lines.append(f"Mean validation F1 (macro, stored summary): {sum(f1s) / len(f1s):.6f}")

    best = max(all_rows, key=lambda r: float(r.get("final_val_f1") or -1))
    bb = int(best["_batch"])
    lines.append("")
    lines.append("Best run (by final_val_f1):")
    lines.append(f"  batch_{bb} / {best.get('_folder')}")
    lines.append(f"  val_acc={best.get('final_val_acc')} val_f1={best.get('final_val_f1')}")
    best_path = DETAILED / f"batch_{bb}" / str(best.get("_folder", ""))
    lines.append(f"  path: {best_path}")

    lines.append("")
    lines.append("==============================")
    lines.append("2. PER-BATCH MEANS")
    lines.append("==============================")
    for bn in range(5, 10):
        rows = [r for r in all_rows if r["_batch"] == bn]
        if not rows:
            continue
        a = sum(float(r.get("final_val_acc") or 0) for r in rows) / len(rows)
        f = sum(float(r.get("final_val_f1") or 0) for r in rows) / len(rows)
        lines.append(f"  batch_{bn}: n={len(rows)} mean_acc={a:.6f} mean_f1={f:.6f}")

    lines.append("")
    lines.append("==============================")
    lines.append("3. ALL RUNS (compact)")
    lines.append("==============================")
    hdr = f"{'batch':>7} {'run_folder':<42} {'val_acc':>10} {'val_f1':>10}"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for r in sorted(all_rows, key=lambda x: (x["_batch"], x["_folder"])):
        lines.append(
            f"{r['_batch']:>7} {r['_folder']:<42} "
            f"{float(r.get('final_val_acc') or 0):10.6f} {float(r.get('final_val_f1') or 0):10.6f}"
        )

    lines.append("")
    lines.append("==============================")
    lines.append("4. BATCH COMPARISON FILES (on disk)")
    lines.append("==============================")
    for bn in range(5, 10):
        comp_dir = COMPARISONS / f"batch_{bn}_comparisons"
        if comp_dir.is_dir():
            txts = sorted(comp_dir.glob("*.txt"))
            pngs = sorted(comp_dir.glob("*.png"))
            lines.append(f"  batch_{bn}: {comp_dir.relative_to(EVAL)}")
            for t in txts:
                lines.append(f"    - {t.name}")

    lines.append("")
    lines.append("==============================")
    lines.append("5. DIAGNOSTIC REPORT SNAPSHOT")
    lines.append("==============================")
    if DIAG.is_file():
        snap = DIAG.read_text(encoding="utf-8", errors="replace").splitlines()
        lines.extend(snap[:60])
        if len(snap) > 60:
            lines.append(f"... ({len(snap) - 60} more lines in evaluation/report/diagnostic_report.txt)")
    else:
        lines.append(f"(No file at {DIAG})")

    EVAL.mkdir(parents=True, exist_ok=True)
    out = EVAL / "final_report.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")

    gs = EVAL / "global_summary_batches_5_9.txt"
    gs_lines = [
        "Mean accuracy (all parsed runs): %.6f" % (sum(accs) / len(accs)),
        "Mean F1 (all parsed runs): %.6f" % (sum(f1s) / len(f1s)),
        f"Best: batch_{best['_batch']} {best.get('_folder')} F1={best.get('final_val_f1')}",
    ]
    gs.write_text("\n".join(gs_lines), encoding="utf-8")
    print(f"Wrote {gs}")


if __name__ == "__main__":
    main()
