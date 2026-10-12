#!/usr/bin/env python3
"""
SecureSight Statistical Analysis - Usage Script

Run complete statistical analysis and generate professional Word report.
"""

import os
from statistical_analysis_generator import run_full_statistical_analysis


def main():
    """Execute statistical analysis."""
    
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    evaluation_path = os.path.join(current_dir, 'evaluation')
    
    # Run analysis
    print("=" * 70)
    print("SecureSight Statistical Analysis System")
    print("=" * 70)
    print(f"\nEvaluation path: {evaluation_path}")
    
    if not os.path.exists(evaluation_path):
        print(f"\nERROR: Evaluation path not found: {evaluation_path}")
        return False
    
    print("\nStarting analysis pipeline...")
    success = run_full_statistical_analysis(evaluation_path)
    
    if success:
        output_dir = os.path.join(current_dir, 'statistical_analysis')
        print("\n" + "=" * 70)
        print("Analysis completed successfully!")
        print("=" * 70)
        print(f"\nOutput directory: {output_dir}")
        print("\nGenerated files:")
        print("  - statistical_analysis/raw_data/all_runs.csv")
        print("  - statistical_analysis/summary/global_metrics.json")
        print("  - statistical_analysis/summary/per_batch_metrics.json")
        print("  - statistical_analysis/summary/confidence_intervals.json")
        print("  - statistical_analysis/summary/correlation_matrix.json")
        print("  - statistical_analysis/summary/best_worst_runs.json")
        print("  - statistical_analysis/plots/ (all visualizations)")
        print("  - statistical_analysis/reports/statistical_analysis_report.docx")
        print("  - statistical_analysis/reports/report.txt")
        print("  - statistical_analysis/logs/analysis_log.txt")
        return True
    else:
        print("\n" + "=" * 70)
        print("ERROR: Analysis pipeline failed!")
        print("=" * 70)
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
