"""
Re-scan evaluation/detailed_results and regenerate:
  - results_comparisons/batch_{n}_comparisons/* for selected batches
  - new_runs_report.txt and new_runs_comparison.png

Does not retrain. Use after runs exist or after copying artifacts from the server.

Usage (from tasnim/):
  python regenerate_eval_comparisons.py
  python regenerate_eval_comparisons.py --eval-base "E:\\...\\tasnim\\evaluation"
  python regenerate_eval_comparisons.py --batches 4 5 6 7 8 9
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--eval-base",
        default=None,
        help="SECURESIGHT_EVAL_BASE (folder containing detailed_results and results_comparisons)",
    )
    ap.add_argument(
        "--batches",
        type=int,
        nargs="*",
        default=list(range(1, 10)),
        help="Batch indices to regenerate (default 1-9)",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    if args.eval_base:
        eval_base = os.path.abspath(args.eval_base)
    else:
        eval_base = str(root / "evaluation")

    os.environ["SECURESIGHT_EVAL_BASE"] = eval_base

    # Import after env is set
    sys.path.insert(0, str(root))
    from run_tracker import RunTracker
    from path_setup import get_evaluation_base_dir

    RunTracker.refresh_output_paths()
    print("Evaluation base:", get_evaluation_base_dir())

    for b in sorted(set(args.batches)):
        RunTracker.generate_batch_report(b)

    RunTracker.generate_new_runs_report()
    print("Updated batch comparison reports and new_runs_* under:", eval_base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
