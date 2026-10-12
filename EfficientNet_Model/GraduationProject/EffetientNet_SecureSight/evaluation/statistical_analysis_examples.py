"""
Advanced usage examples for SecureSight Statistical Analysis System

This module demonstrates various ways to use the statistical analysis system.
"""

from statistical_analysis_generator import (
    run_full_statistical_analysis,
    StatisticalAnalysisPipeline,
    DataAggregator,
    StatisticalAnalyzer,
    VisualizationGenerator,
    WordReportGenerator,
)
import os


def example_1_simple_analysis():
    """Example 1: Simple one-line analysis."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    
    success = run_full_statistical_analysis(evaluation_path)
    
    if success:
        print("Analysis completed successfully!")
        print(f"Output saved to: {os.path.join(os.path.dirname(__file__), 'statistical_analysis')}")


def example_2_custom_output_path():
    """Example 2: Analysis with custom output directory."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    output_path = '/custom/path/statistical_analysis'
    
    success = run_full_statistical_analysis(evaluation_path, output_path)
    
    if success:
        print(f"Analysis completed! Output: {output_path}")


def example_3_detailed_control():
    """Example 3: Step-by-step analysis with detailed control."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    
    # Create pipeline
    pipeline = StatisticalAnalysisPipeline(evaluation_path)
    
    # Run analysis
    pipeline.run()


def example_4_data_aggregation_only():
    """Example 4: Extract and work with aggregated data only."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    
    # Setup logger (optional)
    import logging
    logger = logging.getLogger(__name__)
    
    # Aggregate data
    aggregator = DataAggregator(evaluation_path, logger)
    df = aggregator.aggregate_results()
    
    # Work with dataframe
    print(df.head())
    print(df.describe())
    
    # Save for external analysis
    df.to_csv('my_custom_export.csv', index=False)


def example_5_statistics_only():
    """Example 5: Compute statistics without visualization."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Load data
    aggregator = DataAggregator(evaluation_path, logger)
    df = aggregator.aggregate_results()
    
    # Analyze
    analyzer = StatisticalAnalyzer(df, logger)
    
    global_stats = analyzer.compute_global_statistics()
    per_batch_stats = analyzer.compute_per_batch_statistics()
    ci = analyzer.compute_confidence_intervals()
    corr = analyzer.compute_correlation_matrix()
    stability = analyzer.identify_stability_issues()
    best_worst = analyzer.find_best_worst_runs()
    
    print("Global Statistics:")
    for metric, stats in global_stats.items():
        print(f"\n{metric}: μ={stats['mean']:.4f}, σ={stats['std']:.4f}")


def example_6_visualization_only():
    """Example 6: Generate visualizations only."""
    evaluation_path = os.path.join(os.path.dirname(__file__), 'evaluation')
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Load data
    aggregator = DataAggregator(evaluation_path, logger)
    df = aggregator.aggregate_results()
    
    # Generate plots
    plots_dir = './my_plots'
    visualizer = VisualizationGenerator(df, plots_dir, logger)
    visualizer.generate_all_plots()
    
    print(f"Plots saved to: {plots_dir}")


if __name__ == '__main__':
    print("SecureSight Statistical Analysis - Examples")
    print("=" * 70)
    print("\nUncomment the example you want to run:\n")
    
    example_1_simple_analysis()
    
    # example_2_custom_output_path()
    # example_3_detailed_control()
    # example_4_data_aggregation_only()
    # example_5_statistics_only()
    # example_6_visualization_only()
