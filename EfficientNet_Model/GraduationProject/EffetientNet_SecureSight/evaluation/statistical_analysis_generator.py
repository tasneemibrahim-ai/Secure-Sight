"""
SecureSight Statistical Analysis and Reporting System

Complete statistical analysis and professional Word report generation
for deep learning model evaluation across multiple batches and runs.
"""

import os
import sys
import json
import logging
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import f_oneway, ttest_ind
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

warnings.filterwarnings('ignore')


class StatisticalAnalysisLogger:
    """Setup logging for the statistical analysis process."""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('SecureSight_StatAnalysis')
        logger.setLevel(logging.DEBUG)
        
        log_file = os.path.join(self.log_dir, 'analysis_log.txt')
        
        handler = logging.FileHandler(log_file, mode='w')
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger


class DataAggregator:
    """Aggregate evaluation results from all batches and runs."""
    
    def __init__(self, evaluation_path: str, logger: logging.Logger):
        self.evaluation_path = evaluation_path
        self.logger = logger
        self.data = []
    
    def aggregate_results(self) -> pd.DataFrame:
        """Load and aggregate results from all runs."""
        self.logger.info("Starting data aggregation...")
        
        detailed_batches_path = os.path.join(self.evaluation_path, 'detailed_batches')
        
        if not os.path.exists(detailed_batches_path):
            self.logger.error(f"detailed_batches path not found: {detailed_batches_path}")
            raise FileNotFoundError(f"Cannot find: {detailed_batches_path}")
        
        batch_dirs = sorted([d for d in os.listdir(detailed_batches_path) 
                           if d.startswith('batch_')])
        
        self.logger.info(f"Found {len(batch_dirs)} batches")
        
        for batch_dir in batch_dirs:
            batch_num = int(batch_dir.split('_')[1])
            batch_path = os.path.join(detailed_batches_path, batch_dir)
            
            run_dirs = sorted([d for d in os.listdir(batch_path) 
                             if d.startswith('run_')])
            
            self.logger.info(f"Batch {batch_num}: Processing {len(run_dirs)} runs")
            
            for run_dir in run_dirs:
                run_num = int(run_dir.split('_')[1])
                run_path = os.path.join(batch_path, run_dir)
                
                summary_file = os.path.join(run_path, 'run_summary.json')
                
                if os.path.exists(summary_file):
                    try:
                        with open(summary_file, 'r') as f:
                            summary = json.load(f)
                        
                        metrics = summary.get('final_metrics', {})
                        run_record = {
                            'batch_id': batch_num,
                            'run_id': run_num,
                            'accuracy': metrics.get('accuracy', np.nan),
                            'precision': metrics.get('precision', np.nan),
                            'recall': metrics.get('recall', np.nan),
                            'f1_score': metrics.get('f1', np.nan),
                            'auc': metrics.get('auc', np.nan),
                            'loss': metrics.get('loss', np.nan)
                        }
                        self.data.append(run_record)
                    except Exception as e:
                        self.logger.warning(f"Failed to load {summary_file}: {str(e)}")
        
        df = pd.DataFrame(self.data)
        self.logger.info(f"Aggregated {len(df)} runs successfully")
        self.logger.info(f"Dataframe shape: {df.shape}")
        
        return df


class StatisticalAnalyzer:
    """Perform comprehensive statistical analysis on aggregated data."""
    
    def __init__(self, df: pd.DataFrame, logger: logging.Logger):
        self.df = df
        self.logger = logger
        self.metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'loss']
    
    def compute_global_statistics(self) -> Dict[str, Dict[str, float]]:
        """Compute global statistics for all metrics."""
        self.logger.info("Computing global statistics...")
        
        global_stats = {}
        
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue
            
            values = self.df[metric].dropna()
            
            if len(values) > 0:
                global_stats[metric] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'variance': float(values.var()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'median': float(values.median()),
                    'count': int(len(values))
                }
        
        self.logger.info(f"Computed statistics for {len(global_stats)} metrics")
        return global_stats
    
    def compute_per_batch_statistics(self) -> Dict[int, Dict[str, Dict[str, float]]]:
        """Compute statistics for each batch."""
        self.logger.info("Computing per-batch statistics...")
        
        per_batch_stats = {}
        
        for batch_id in sorted(self.df['batch_id'].unique()):
            batch_data = self.df[self.df['batch_id'] == batch_id]
            per_batch_stats[batch_id] = {}
            
            for metric in self.metrics:
                if metric not in batch_data.columns:
                    continue
                
                values = batch_data[metric].dropna()
                
                if len(values) > 0:
                    per_batch_stats[batch_id][metric] = {
                        'mean': float(values.mean()),
                        'std': float(values.std()),
                        'variance': float(values.var()),
                        'min': float(values.min()),
                        'max': float(values.max()),
                        'median': float(values.median())
                    }
        
        self.logger.info(f"Computed statistics for {len(per_batch_stats)} batches")
        return per_batch_stats
    
    def compute_confidence_intervals(self, confidence: float = 0.95) \
            -> Dict[str, Dict[str, float]]:
        """Compute confidence intervals for all metrics."""
        self.logger.info(f"Computing {confidence*100}% confidence intervals...")
        
        ci_data = {}
        
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue
            
            values = self.df[metric].dropna()
            
            if len(values) > 1:
                mean = values.mean()
                sem = stats.sem(values)
                ci = sem * stats.t.ppf((1 + confidence) / 2., len(values) - 1)
                
                ci_data[metric] = {
                    'mean': float(mean),
                    'ci_lower': float(mean - ci),
                    'ci_upper': float(mean + ci),
                    'ci_width': float(2 * ci)
                }
        
        return ci_data
    
    def compute_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Compute correlation matrix between all metrics."""
        self.logger.info("Computing correlation matrix...")
        
        metrics_df = self.df[self.metrics].dropna()
        
        if len(metrics_df) > 1:
            corr_matrix = metrics_df.corr()
            corr_dict = corr_matrix.to_dict()
            return {k: {k2: float(v2) for k2, v2 in v.items()} 
                    for k, v in corr_dict.items()}
        
        return {}
    
    def identify_stability_issues(self, std_threshold: float = 0.15) \
            -> Dict[str, List[Dict[str, Any]]]:
        """Identify batches/runs with high variance (unstable)."""
        self.logger.info("Analyzing stability...")
        
        stability_issues = {
            'unstable_batches': [],
            'unstable_runs': []
        }
        
        # Per-batch analysis
        for batch_id in sorted(self.df['batch_id'].unique()):
            batch_data = self.df[self.df['batch_id'] == batch_id]
            
            for metric in ['f1_score', 'accuracy', 'auc']:
                if metric in batch_data.columns:
                    std = batch_data[metric].std()
                    if std > std_threshold:
                        stability_issues['unstable_batches'].append({
                            'batch_id': int(batch_id),
                            'metric': metric,
                            'std': float(std)
                        })
        
        # Per-run analysis
        for _, row in self.df.iterrows():
            avg_metric = row[['accuracy', 'precision', 'recall']].mean()
            if avg_metric < 0.7:
                stability_issues['unstable_runs'].append({
                    'batch_id': int(row['batch_id']),
                    'run_id': int(row['run_id']),
                    'avg_metric': float(avg_metric)
                })
        
        return stability_issues
    
    def find_best_worst_runs(self) -> Dict[str, Dict[str, Any]]:
        """Identify best and worst runs based on f1_score."""
        self.logger.info("Identifying best and worst runs...")
        
        best_worst = {}
        
        for metric in ['f1_score', 'accuracy', 'auc']:
            if metric in self.df.columns:
                df_valid = self.df.dropna(subset=[metric])
                
                if len(df_valid) > 0:
                    best_idx = df_valid[metric].idxmax()
                    worst_idx = df_valid[metric].idxmin()
                    
                    best_run = df_valid.loc[best_idx]
                    worst_run = df_valid.loc[worst_idx]
                    
                    best_worst[metric] = {
                        'best': {
                            'batch_id': int(best_run['batch_id']),
                            'run_id': int(best_run['run_id']),
                            'value': float(best_run[metric]),
                            'full_metrics': {col: float(best_run[col]) 
                                           for col in self.metrics}
                        },
                        'worst': {
                            'batch_id': int(worst_run['batch_id']),
                            'run_id': int(worst_run['run_id']),
                            'value': float(worst_run[metric]),
                            'full_metrics': {col: float(worst_run[col]) 
                                           for col in self.metrics}
                        }
                    }
        
        return best_worst


class VisualizationGenerator:
    """Generate high-quality visualizations for analysis."""
    
    def __init__(self, df: pd.DataFrame, plots_dir: str, logger: logging.Logger):
        self.df = df
        self.plots_dir = plots_dir
        self.logger = logger
        self.metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc']
        self._setup_style()
    
    def _setup_style(self):
        """Setup matplotlib style for professional plots."""
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def generate_boxplots(self):
        """Generate boxplots for metric distributions across batches."""
        self.logger.info("Generating boxplots...")
        
        boxplot_dir = os.path.join(self.plots_dir, 'boxplots')
        os.makedirs(boxplot_dir, exist_ok=True)
        
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue
            
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=self.df, x='batch_id', y=metric, palette='Set2')
            plt.title(f'{metric.upper()} Distribution Across Batches', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Batch ID', fontsize=12)
            plt.ylabel(metric.capitalize(), fontsize=12)
            plt.grid(True, alpha=0.3)
            
            filepath = os.path.join(boxplot_dir, f'boxplot_{metric}.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Saved boxplot: {filepath}")
    
    def generate_lineplots(self):
        """Generate line plots for metric trends across runs."""
        self.logger.info("Generating line plots...")
        
        lineplot_dir = os.path.join(self.plots_dir, 'lineplots')
        os.makedirs(lineplot_dir, exist_ok=True)
        
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue
            
            plt.figure(figsize=(14, 6))
            
            for batch_id in sorted(self.df['batch_id'].unique()):
                batch_data = self.df[self.df['batch_id'] == batch_id]\
                    .sort_values('run_id')
                plt.plot(batch_data['run_id'], batch_data[metric], 
                        marker='o', label=f'Batch {batch_id}', linewidth=2)
            
            plt.title(f'{metric.upper()} Trends Across Runs', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Run ID', fontsize=12)
            plt.ylabel(metric.capitalize(), fontsize=12)
            plt.legend(loc='best')
            plt.grid(True, alpha=0.3)
            
            filepath = os.path.join(lineplot_dir, f'lineplot_{metric}.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Saved lineplot: {filepath}")
    
    def generate_barplots(self):
        """Generate bar plots with mean ± std."""
        self.logger.info("Generating bar plots...")
        
        barplot_dir = os.path.join(self.plots_dir, 'barplots')
        os.makedirs(barplot_dir, exist_ok=True)
        
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue
            
            batch_stats = self.df.groupby('batch_id')[metric].agg(['mean', 'std'])
            
            plt.figure(figsize=(12, 6))
            x_pos = np.arange(len(batch_stats))
            plt.bar(x_pos, batch_stats['mean'], yerr=batch_stats['std'],
                   capsize=5, alpha=0.7, color='steelblue', edgecolor='black')
            plt.title(f'{metric.upper()} Mean ± Std by Batch', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Batch ID', fontsize=12)
            plt.ylabel(metric.capitalize(), fontsize=12)
            plt.xticks(x_pos, batch_stats.index)
            plt.grid(True, alpha=0.3, axis='y')
            
            filepath = os.path.join(barplot_dir, f'barplot_{metric}.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Saved barplot: {filepath}")
    
    def generate_heatmap(self):
        """Generate correlation heatmap."""
        self.logger.info("Generating correlation heatmap...")
        
        heatmap_dir = os.path.join(self.plots_dir, 'heatmaps')
        os.makedirs(heatmap_dir, exist_ok=True)
        
        metrics_df = self.df[self.metrics].dropna()
        corr_matrix = metrics_df.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix Between Metrics', 
                 fontsize=14, fontweight='bold')
        
        filepath = os.path.join(heatmap_dir, 'correlation_heatmap.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Saved heatmap: {filepath}")
    
    def generate_histograms(self):
        """Generate histograms for metric distributions."""
        self.logger.info("Generating histograms...")
        
        hist_dir = os.path.join(self.plots_dir, 'histograms')
        os.makedirs(hist_dir, exist_ok=True)
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, metric in enumerate(self.metrics):
            if metric not in self.df.columns:
                continue
            
            ax = axes[idx]
            values = self.df[metric].dropna()
            
            ax.hist(values, bins=15, alpha=0.7, color='steelblue', edgecolor='black')
            ax.set_title(f'{metric.capitalize()} Distribution', fontweight='bold')
            ax.set_xlabel(metric.capitalize())
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(hist_dir, 'all_histograms.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Saved histograms: {filepath}")
    
    def generate_all_plots(self):
        """Generate all visualizations."""
        self.generate_boxplots()
        self.generate_lineplots()
        self.generate_barplots()
        self.generate_heatmap()
        self.generate_histograms()
        self.logger.info("All plots generated successfully")


class WordReportGenerator:
    """Generate professional Word report with all analysis."""
    
    def __init__(self, df: pd.DataFrame, analysis_results: Dict[str, Any],
                 plots_dir: str, output_path: str, logger: logging.Logger):
        self.df = df
        self.analysis_results = analysis_results
        self.plots_dir = plots_dir
        self.output_path = output_path
        self.logger = logger
        self.doc = Document()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup document styles."""
        pass
    
    def _add_title_page(self):
        """Add title page."""
        title = self.doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.add_run('SecureSight')
        title_run.font.size = Pt(36)
        title_run.font.bold = True
        
        subtitle = self.doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle_run = subtitle.add_run('Statistical Analysis Report')
        subtitle_run.font.size = Pt(24)
        
        self.doc.add_paragraph()
        
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        info.add_run(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        stats = self.doc.add_paragraph()
        stats.alignment = WD_ALIGN_PARAGRAPH.CENTER
        total_runs = len(self.df)
        total_batches = self.df['batch_id'].nunique()
        stats.add_run(f"Total Runs: {total_runs} | Total Batches: {total_batches}")
        
        self.doc.add_page_break()
    
    def _add_overview(self):
        """Add overview section."""
        self.doc.add_heading('1. Overview', level=1)
        
        self.doc.add_paragraph(
            f"This report presents a comprehensive statistical analysis of the SecureSight "
            f"deep learning model evaluation. The analysis includes {len(self.df)} runs "
            f"distributed across {self.df['batch_id'].nunique()} batches."
        )
        
        self.doc.add_heading('Evaluation Metrics', level=2)
        metrics_text = self.doc.add_paragraph()
        metrics_list = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC', 'Loss']
        metrics_text.add_run(', '.join(metrics_list))
        
        self.doc.add_paragraph(
            "These metrics provide a comprehensive assessment of model performance across "
            "security threat classification tasks."
        )
    
    def _add_global_statistics(self):
        """Add global statistics section."""
        self.doc.add_page_break()
        self.doc.add_heading('2. Global Statistical Analysis', level=1)
        
        global_stats = self.analysis_results['global_statistics']
        
        # Create table
        table = self.doc.add_table(rows=1, cols=7)
        table.style = 'Light Grid Accent 1'
        
        header_cells = table.rows[0].cells
        headers = ['Metric', 'Mean', 'Std Dev', 'Min', 'Max', 'Median', 'Count']
        for i, header in enumerate(headers):
            header_cells[i].text = header
        
        for metric, stats in global_stats.items():
            row = table.add_row().cells
            row[0].text = metric.upper()
            row[1].text = f"{stats['mean']:.6f}"
            row[2].text = f"{stats['std']:.6f}"
            row[3].text = f"{stats['min']:.6f}"
            row[4].text = f"{stats['max']:.6f}"
            row[5].text = f"{stats['median']:.6f}"
            row[6].text = str(stats['count'])
        
        # Confidence intervals
        self.doc.add_heading('Confidence Intervals (95%)', level=2)
        
        ci_data = self.analysis_results['confidence_intervals']
        ci_table = self.doc.add_table(rows=1, cols=4)
        ci_table.style = 'Light Grid Accent 1'
        
        ci_headers = ci_table.rows[0].cells
        ci_headers[0].text = 'Metric'
        ci_headers[1].text = 'Mean'
        ci_headers[2].text = 'CI Lower'
        ci_headers[3].text = 'CI Upper'
        
        for metric, ci in ci_data.items():
            row = ci_table.add_row().cells
            row[0].text = metric.upper()
            row[1].text = f"{ci['mean']:.6f}"
            row[2].text = f"{ci['ci_lower']:.6f}"
            row[3].text = f"{ci['ci_upper']:.6f}"
    
    def _add_per_batch_analysis(self):
        """Add per-batch analysis section."""
        self.doc.add_page_break()
        self.doc.add_heading('3. Per-Batch Analysis', level=1)
        
        per_batch_stats = self.analysis_results['per_batch_statistics']
        
        for batch_id in sorted(per_batch_stats.keys()):
            self.doc.add_heading(f'Batch {batch_id}', level=2)
            
            batch_data = per_batch_stats[batch_id]
            
            table = self.doc.add_table(rows=1, cols=6)
            table.style = 'Light Grid Accent 1'
            
            headers = table.rows[0].cells
            headers[0].text = 'Metric'
            headers[1].text = 'Mean'
            headers[2].text = 'Std Dev'
            headers[3].text = 'Min'
            headers[4].text = 'Max'
            headers[5].text = 'Median'
            
            for metric, stats in batch_data.items():
                row = table.add_row().cells
                row[0].text = metric.upper()
                row[1].text = f"{stats['mean']:.6f}"
                row[2].text = f"{stats['std']:.6f}"
                row[3].text = f"{stats['min']:.6f}"
                row[4].text = f"{stats['max']:.6f}"
                row[5].text = f"{stats['median']:.6f}"
    
    def _add_best_worst_analysis(self):
        """Add best and worst runs section."""
        self.doc.add_page_break()
        self.doc.add_heading('4. Best and Worst Runs Analysis', level=1)
        
        best_worst = self.analysis_results['best_worst_runs']
        
        for metric, data in best_worst.items():
            self.doc.add_heading(f'{metric.upper()}', level=2)
            
            # Best run
            self.doc.add_heading('Best Run', level=3)
            best_run = data['best']
            best_para = self.doc.add_paragraph()
            best_para.add_run(f"Batch {best_run['batch_id']}, Run {best_run['run_id']}: "
                            f"{best_run['value']:.6f}").bold = True
            
            # Best metrics table
            best_table = self.doc.add_table(rows=1, cols=2)
            best_table.style = 'Light Grid Accent 1'
            best_table.rows[0].cells[0].text = 'Metric'
            best_table.rows[0].cells[1].text = 'Value'
            
            for metric_name, value in best_run['full_metrics'].items():
                row = best_table.add_row().cells
                row[0].text = metric_name.upper()
                row[1].text = f"{value:.6f}"
            
            # Worst run
            self.doc.add_heading('Worst Run', level=3)
            worst_run = data['worst']
            worst_para = self.doc.add_paragraph()
            worst_para.add_run(f"Batch {worst_run['batch_id']}, Run {worst_run['run_id']}: "
                             f"{worst_run['value']:.6f}").bold = True
            
            # Worst metrics table
            worst_table = self.doc.add_table(rows=1, cols=2)
            worst_table.style = 'Light Grid Accent 1'
            worst_table.rows[0].cells[0].text = 'Metric'
            worst_table.rows[0].cells[1].text = 'Value'
            
            for metric_name, value in worst_run['full_metrics'].items():
                row = worst_table.add_row().cells
                row[0].text = metric_name.upper()
                row[1].text = f"{value:.6f}"
    
    def _add_correlation_analysis(self):
        """Add correlation analysis section."""
        self.doc.add_page_break()
        self.doc.add_heading('5. Correlation Analysis', level=1)
        
        self.doc.add_paragraph(
            "The following table shows the correlation coefficients between all metrics. "
            "Values range from -1 to 1, where values close to 1 indicate strong positive correlation."
        )
        
        corr_matrix = self.analysis_results['correlation_matrix']
        metrics = list(corr_matrix.keys())
        
        # Correlation table
        table = self.doc.add_table(rows=1, cols=len(metrics) + 1)
        table.style = 'Light Grid Accent 1'
        
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Metric'
        for i, metric in enumerate(metrics):
            header_cells[i + 1].text = metric.upper()
        
        for metric1 in metrics:
            row = table.add_row().cells
            row[0].text = metric1.upper()
            for i, metric2 in enumerate(metrics):
                value = corr_matrix[metric1][metric2]
                row[i + 1].text = f"{value:.4f}"
        
        # Heatmap image
        self.doc.add_heading('Correlation Heatmap', level=2)
        heatmap_path = os.path.join(self.plots_dir, 'heatmaps', 'correlation_heatmap.png')
        if os.path.exists(heatmap_path):
            self.doc.add_picture(heatmap_path, width=Inches(5.5))
    
    def _add_visualizations(self):
        """Add visualization section."""
        self.doc.add_page_break()
        self.doc.add_heading('6. Visualizations', level=1)
        
        # Boxplots
        self.doc.add_heading('Boxplots', level=2)
        self.doc.add_paragraph('Distribution of metrics across batches:')
        
        boxplot_dir = os.path.join(self.plots_dir, 'boxplots')
        if os.path.exists(boxplot_dir):
            for plot_file in sorted(os.listdir(boxplot_dir)):
                if plot_file.endswith('.png'):
                    plot_path = os.path.join(boxplot_dir, plot_file)
                    self.doc.add_picture(plot_path, width=Inches(5.5))
                    self.doc.add_paragraph()
        
        # Lineplots
        self.doc.add_heading('Trend Plots', level=2)
        self.doc.add_paragraph('Metric trends across runs:')
        
        lineplot_dir = os.path.join(self.plots_dir, 'lineplots')
        if os.path.exists(lineplot_dir):
            for plot_file in sorted(os.listdir(lineplot_dir)):
                if plot_file.endswith('.png'):
                    plot_path = os.path.join(lineplot_dir, plot_file)
                    self.doc.add_picture(plot_path, width=Inches(5.5))
                    self.doc.add_paragraph()
        
        # Barplots
        self.doc.add_heading('Mean ± Std Analysis', level=2)
        self.doc.add_paragraph('Mean performance with standard deviation by batch:')
        
        barplot_dir = os.path.join(self.plots_dir, 'barplots')
        if os.path.exists(barplot_dir):
            for plot_file in sorted(os.listdir(barplot_dir)):
                if plot_file.endswith('.png'):
                    plot_path = os.path.join(barplot_dir, plot_file)
                    self.doc.add_picture(plot_path, width=Inches(5.5))
                    self.doc.add_paragraph()
        
        # Histograms
        self.doc.add_heading('Distributions', level=2)
        self.doc.add_paragraph('Histograms showing metric distributions:')
        
        hist_dir = os.path.join(self.plots_dir, 'histograms')
        if os.path.exists(hist_dir):
            hist_path = os.path.join(hist_dir, 'all_histograms.png')
            if os.path.exists(hist_path):
                self.doc.add_picture(hist_path, width=Inches(6))
    
    def _add_insights(self):
        """Add final insights section."""
        self.doc.add_page_break()
        self.doc.add_heading('7. Final Insights', level=1)
        
        # Stability analysis
        stability = self.analysis_results['stability_analysis']
        
        self.doc.add_heading('Model Stability', level=2)
        unstable_batches = stability['unstable_batches']
        unstable_runs = stability['unstable_runs']
        
        if unstable_batches:
            self.doc.add_paragraph(
                f"Found {len(unstable_batches)} instances of high variance in batches, "
                "indicating potential instability in certain batch configurations."
            )
        else:
            self.doc.add_paragraph(
                "No significant stability issues detected. Batches show consistent performance."
            )
        
        if unstable_runs:
            self.doc.add_paragraph(
                f"Identified {len(unstable_runs)} runs with below-average performance. "
                "These may warrant investigation for configuration or data issues."
            )
        
        # Metrics analysis
        self.doc.add_heading('Metrics Summary', level=2)
        
        global_stats = self.analysis_results['global_statistics']
        
        # Find best and worst metrics
        best_metric = max(global_stats.items(), 
                         key=lambda x: x[1]['mean'] if x[0] != 'loss' else -x[1]['mean'])
        
        insights = self.doc.add_paragraph()
        insights.add_run(f"Strongest metric: {best_metric[0].upper()} "
                        f"(mean: {best_metric[1]['mean']:.4f})\n")
        
        if 'f1_score' in global_stats:
            f1_mean = global_stats['f1_score']['mean']
            f1_std = global_stats['f1_score']['std']
            insights.add_run(f"F1-Score consistency: μ={f1_mean:.4f}, σ={f1_std:.4f}\n")
        
        if 'accuracy' in global_stats:
            acc_mean = global_stats['accuracy']['mean']
            insights.add_run(f"Overall accuracy: {acc_mean:.4f}")
        
        # Variance analysis
        self.doc.add_heading('Variance Analysis', level=2)
        
        variance_para = self.doc.add_paragraph()
        for metric, stats in global_stats.items():
            if metric != 'loss':
                variance_para.add_run(f"{metric.upper()}: σ²={stats['variance']:.6f}\n")
    
    def _add_footer_info(self):
        """Add footer information."""
        self.doc.add_page_break()
        self.doc.add_heading('Appendix: Technical Details', level=1)
        
        self.doc.add_paragraph(
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        self.doc.add_paragraph(
            f"Total runs analyzed: {len(self.df)}"
        )
        
        self.doc.add_paragraph(
            f"Total batches: {self.df['batch_id'].nunique()}"
        )
        
        self.doc.add_paragraph(
            "Generated using SecureSight Statistical Analysis System"
        )
    
    def generate_report(self):
        """Generate complete report."""
        self.logger.info("Generating Word report...")
        
        try:
            self._add_title_page()
            self._add_overview()
            self._add_global_statistics()
            self._add_per_batch_analysis()
            self._add_best_worst_analysis()
            self._add_correlation_analysis()
            self._add_visualizations()
            self._add_insights()
            self._add_footer_info()
            
            self.doc.save(self.output_path)
            self.logger.info(f"Report saved successfully: {self.output_path}")
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise


class StatisticalAnalysisPipeline:
    """Main pipeline orchestrating the entire analysis process."""
    
    def __init__(self, results_path: str, output_base_dir: str = None):
        self.results_path = results_path
        self.output_base_dir = output_base_dir or os.path.join(
            os.path.dirname(results_path), 'statistical_analysis'
        )
        self._setup_directories()
        self.logger = self._setup_logger()
    
    def _setup_directories(self):
        """Create required directory structure."""
        self.raw_data_dir = os.path.join(self.output_base_dir, 'raw_data')
        self.summary_dir = os.path.join(self.output_base_dir, 'summary')
        self.plots_dir = os.path.join(self.output_base_dir, 'plots')
        self.reports_dir = os.path.join(self.output_base_dir, 'reports')
        self.logs_dir = os.path.join(self.output_base_dir, 'logs')
        
        for directory in [self.raw_data_dir, self.summary_dir, self.plots_dir,
                         self.reports_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger_instance = StatisticalAnalysisLogger(self.logs_dir)
        return logger_instance.logger
    
    def run(self):
        """Execute complete analysis pipeline."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting SecureSight Statistical Analysis Pipeline")
            self.logger.info("=" * 60)
            self.logger.info(f"Results path: {self.results_path}")
            self.logger.info(f"Output directory: {self.output_base_dir}")
            
            # 1. Data Aggregation
            self.logger.info("\n[STEP 1] Data Aggregation")
            aggregator = DataAggregator(self.results_path, self.logger)
            df = aggregator.aggregate_results()
            
            # Save raw data
            csv_path = os.path.join(self.raw_data_dir, 'all_runs.csv')
            df.to_csv(csv_path, index=False)
            self.logger.info(f"Raw data saved to: {csv_path}")
            
            # 2. Statistical Analysis
            self.logger.info("\n[STEP 2] Statistical Analysis")
            analyzer = StatisticalAnalyzer(df, self.logger)
            
            global_stats = analyzer.compute_global_statistics()
            per_batch_stats = analyzer.compute_per_batch_statistics()
            ci_data = analyzer.compute_confidence_intervals()
            corr_matrix = analyzer.compute_correlation_matrix()
            stability = analyzer.identify_stability_issues()
            best_worst = analyzer.find_best_worst_runs()
            
            # Save analysis results
            summary_files = {
                'global_metrics.json': global_stats,
                'per_batch_metrics.json': per_batch_stats,
                'confidence_intervals.json': ci_data,
                'correlation_matrix.json': corr_matrix,
                'best_worst_runs.json': best_worst
            }
            
            for filename, data in summary_files.items():
                filepath = os.path.join(self.summary_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                self.logger.info(f"Saved: {filepath}")
            
            # 3. Visualization
            self.logger.info("\n[STEP 3] Visualization Generation")
            visualizer = VisualizationGenerator(df, self.plots_dir, self.logger)
            visualizer.generate_all_plots()
            
            # 4. Report Generation
            self.logger.info("\n[STEP 4] Word Report Generation")
            
            analysis_results = {
                'global_statistics': global_stats,
                'per_batch_statistics': per_batch_stats,
                'confidence_intervals': ci_data,
                'correlation_matrix': corr_matrix,
                'stability_analysis': stability,
                'best_worst_runs': best_worst
            }
            
            report_path = os.path.join(self.reports_dir, 'statistical_analysis_report.docx')
            
            report_generator = WordReportGenerator(
                df, analysis_results, self.plots_dir, report_path, self.logger
            )
            report_generator.generate_report()
            
            # 5. Save text report
            self.logger.info("\n[STEP 5] Text Report Generation")
            self._generate_text_report(df, analysis_results)
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("Statistical Analysis Pipeline Completed Successfully!")
            self.logger.info("=" * 60)
            self.logger.info(f"Output directory: {self.output_base_dir}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"\nPipeline failed with error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _generate_text_report(self, df: pd.DataFrame, analysis_results: Dict[str, Any]):
        """Generate text report."""
        report_path = os.path.join(self.reports_dir, 'report.txt')
        
        with open(report_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("SECURESIGHT - STATISTICAL ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Runs: {len(df)}\n")
            f.write(f"Total Batches: {df['batch_id'].nunique()}\n\n")
            
            f.write("GLOBAL STATISTICS\n")
            f.write("-" * 70 + "\n")
            for metric, stats in analysis_results['global_statistics'].items():
                f.write(f"\n{metric.upper()}:\n")
                f.write(f"  Mean:     {stats['mean']:.6f}\n")
                f.write(f"  Std Dev:  {stats['std']:.6f}\n")
                f.write(f"  Variance: {stats['variance']:.6f}\n")
                f.write(f"  Min:      {stats['min']:.6f}\n")
                f.write(f"  Max:      {stats['max']:.6f}\n")
                f.write(f"  Median:   {stats['median']:.6f}\n")
        
        self.logger.info(f"Text report saved to: {report_path}")


def run_full_statistical_analysis(results_path: str, output_base_dir: str = None) -> bool:
    """
    Main function to run complete statistical analysis and generate Word report.
    
    Args:
        results_path: Path to evaluation directory containing detailed_batches
        output_base_dir: Base directory for statistical_analysis output (optional)
    
    Returns:
        True if successful, False otherwise
    """
    pipeline = StatisticalAnalysisPipeline(results_path, output_base_dir)
    return pipeline.run()


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) > 1:
        eval_path = sys.argv[1]
    else:
        eval_path = os.path.join(
            os.path.dirname(__file__), 'evaluation'
        )
    
    success = run_full_statistical_analysis(eval_path)
    sys.exit(0 if success else 1)
