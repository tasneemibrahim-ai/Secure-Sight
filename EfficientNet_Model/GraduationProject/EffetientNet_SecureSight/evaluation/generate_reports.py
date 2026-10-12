"""
SecureSight — General Report & Comparison Curve Generator
=========================================================
Usage:
    python generate_reports.py                    # Generate reports for ALL batches
    python generate_reports.py --batch 2          # Generate report for batch 2 only
    python generate_reports.py --batch 1 2 3      # Generate reports for batches 1, 2, 3
    python generate_reports.py --cumulative       # Generate cumulative cross-batch report
    python generate_reports.py --all              # Generate per-batch + cumulative reports

This script reads the detailed_results produced by run_tracker and
regenerates comparison plots and text reports without re-training.
"""

import argparse
import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_tracker import RunTracker


RunTracker.refresh_output_paths()


def discover_batches():
    """Return a sorted list of batch numbers that exist in detailed_results/."""
    base = RunTracker.DETAILED_RESULTS_DIR
    if not os.path.exists(base):
        return []
    batches = []
    for d in sorted(os.listdir(base)):
        if d.startswith("batch_"):
            try:
                batches.append(int(d.replace("batch_", "")))
            except ValueError:
                continue
    return batches


def main():
    parser = argparse.ArgumentParser(
        description="Generate SecureSight comparison reports & curves."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--batch", type=int, nargs="+",
        help="Batch number(s) to generate reports for."
    )
    group.add_argument(
        "--all", action="store_true",
        help="Generate per-batch reports AND cumulative report."
    )
    group.add_argument(
        "--cumulative", action="store_true",
        help="Generate only the cumulative cross-batch report."
    )
    args = parser.parse_args()

    existing = discover_batches()
    if not existing:
        print("No batches found in detailed_results/. Nothing to do.")
        return

    print(f"Discovered batches: {existing}\n")

    # Decide which batches to process
    if args.cumulative:
        batch_list = []
    elif args.batch:
        batch_list = args.batch
    else:  # default or --all
        batch_list = existing

    # Per-batch reports
    for b in batch_list:
        if b not in existing:
            print(f"⚠  Batch {b} not found in detailed_results/, skipping.")
            continue
        print(f"{'='*60}")
        print(f"  Generating report for Batch {b}")
        print(f"{'='*60}")
        RunTracker.generate_batch_report(b)
        print()

    # Cumulative report (always generated for --all or --cumulative)
    if args.all or args.cumulative or (not args.batch):
        print(f"{'='*60}")
        print(f"  Generating cumulative cross-batch report")
        print(f"{'='*60}")
        RunTracker.generate_new_runs_report()
        print()

    print("All reports generated successfully.")


if __name__ == "__main__":
    main()
