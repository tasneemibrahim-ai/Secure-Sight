import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import logging

def setup_logging(log_path):
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directories(base_path):
    dirs = [
        'raw_data',
        'summary',
        'plots/boxplots',
        'plots/lineplots',
        'plots/barplots',
        'plots/heatmaps',
        'reports',
        'logs'
    ]
    for d in dirs:
        os.makedirs(os.path.join(base_path, d), exist_ok=True)

def load_evaluation_results(results_path):
    data = []
    detailed_path = os.path.join(results_path, 'detailed_batches')
    for batch_dir in os.listdir(detailed_path):
        batch_path = os.path.join(detailed_path, batch_dir)
        if os.path.isdir(batch_path):
            batch_id = batch_dir.replace('batch_', '')
            for run_dir in os.listdir(batch_path):
                run_path = os.path.join(batch_path, run_dir)
                summary_path = os.path.join(run_path, 'run_summary.json')
                if os.path.exists(summary_path):
                    with open(summary_path, 'r') as f:
                        summary = json.load(f)
                    final_metrics = summary.get('final_metrics', {})
                    latency = summary.get('latency', {}).get('mean_ms', 0)
                    data.append({
                        'batch_id': batch_id,
                        'run_id': run_dir,
                        'accuracy': final_metrics.get('accuracy', 0),
                        'precision': final_metrics.get('precision', 0),
                        'recall': final_metrics.get('recall', 0),
                        'f1_score': final_metrics.get('f1', 0),
                        'auc': final_metrics.get('auc', 0),
                        'latency': latency
                    })
    df = pd.DataFrame(data)
    return df

def compute_global_metrics(df):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'latency']
    global_metrics = {}
    for metric in metrics:
        values = df[metric].dropna()
        global_metrics[metric] = {
            'mean': float(values.mean()),
            'std': float(values.std()),
            'min': float(values.min()),
            'max': float(values.max())
        }
    return global_metrics

def compute_per_batch_metrics(df):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'latency']
    per_batch = {}
    for batch in df['batch_id'].unique():
        batch_df = df[df['batch_id'] == batch]
        per_batch[batch] = {}
        for metric in metrics:
            values = batch_df[metric].dropna()
            per_batch[batch][metric] = {
                'mean': float(values.mean()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max())
            }
    return per_batch

def compute_confidence_intervals(df, confidence=0.95):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'latency']
    cis = {}
    for metric in metrics:
        values = df[metric].dropna()
        mean = values.mean()
        sem = stats.sem(values)
        ci = stats.t.interval(confidence, len(values)-1, loc=mean, scale=sem)
        cis[metric] = {
            'mean': float(mean),
            'ci_lower': float(ci[0]),
            'ci_upper': float(ci[1])
        }
    return cis

def find_best_worst_runs(df):
    best_run = df.loc[df['f1_score'].idxmax()]
    worst_run = df.loc[df['f1_score'].idxmin()]
    return {
        'best': {
            'batch_id': best_run['batch_id'],
            'run_id': best_run['run_id'],
            'f1_score': float(best_run['f1_score'])
        },
        'worst': {
            'batch_id': worst_run['batch_id'],
            'run_id': worst_run['run_id'],
            'f1_score': float(worst_run['f1_score'])
        }
    }

def plot_boxplots(df, plots_path):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc']
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='batch_id', y=metric, data=df)
        plt.title(f'{metric.capitalize()} Distribution per Batch')
        plt.savefig(os.path.join(plots_path, 'boxplots', f'{metric}_boxplot.png'))
        plt.close()

def plot_lineplots(df, plots_path):
    df_sorted = df.sort_values('f1_score')
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc']
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        plt.plot(df_sorted[metric].values)
        plt.title(f'{metric.capitalize()} Trend Across Runs (Sorted by F1)')
        plt.xlabel('Run Index')
        plt.ylabel(metric.capitalize())
        plt.savefig(os.path.join(plots_path, 'lineplots', f'{metric}_lineplot.png'))
        plt.close()

def plot_barplots(df, plots_path):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'latency']
    batch_means = df.groupby('batch_id')[metrics].mean()
    batch_stds = df.groupby('batch_id')[metrics].std()
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        batch_means[metric].plot(kind='bar', yerr=batch_stds[metric])
        plt.title(f'{metric.capitalize()} Mean ± Std per Batch')
        plt.ylabel(metric.capitalize())
        plt.savefig(os.path.join(plots_path, 'barplots', f'{metric}_barplot.png'))
        plt.close()

def plot_heatmaps(df, plots_path):
    metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc', 'latency']
    corr = df[metrics].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.savefig(os.path.join(plots_path, 'heatmaps', 'correlation_heatmap.png'))
    plt.close()

def generate_reports(global_metrics, cis, per_batch, best_worst, reports_path):
    with open(os.path.join(reports_path, 'report.txt'), 'w') as f:
        f.write("SecureSight Statistical Analysis Report\n")
        f.write("="*50 + "\n\n")
        f.write("Global Metrics:\n")
        for metric, stats in global_metrics.items():
            f.write(f"  {metric}: {stats['mean']:.4f} ± {stats['std']:.4f} (min: {stats['min']:.4f}, max: {stats['max']:.4f})\n")
        f.write("\nConfidence Intervals (95%):\n")
        for metric, ci in cis.items():
            f.write(f"  {metric}: [{ci['ci_lower']:.4f}, {ci['ci_upper']:.4f}]\n")
        f.write("\nStability Insights:\n")
        for batch, metrics in per_batch.items():
            f1_std = metrics['f1_score']['std']
            f.write(f"  Batch {batch}: F1 Std = {f1_std:.4f}\n")
        f.write("\nBest Run:\n")
        f.write(f"  Batch {best_worst['best']['batch_id']}, Run {best_worst['best']['run_id']}: F1 = {best_worst['best']['f1_score']:.4f}\n")
        f.write("\nWorst Run:\n")
        f.write(f"  Batch {best_worst['worst']['batch_id']}, Run {best_worst['worst']['run_id']}: F1 = {best_worst['worst']['f1_score']:.4f}\n")
    
    report_json = {
        'global_metrics': global_metrics,
        'confidence_intervals': cis,
        'per_batch_metrics': per_batch,
        'best_worst_runs': best_worst
    }
    with open(os.path.join(reports_path, 'report.json'), 'w') as f:
        json.dump(report_json, f, indent=2)

def run_full_statistical_analysis(results_path: str):
    base_path = os.path.join(results_path, 'statistical_analysis')
    create_directories(base_path)
    log_path = os.path.join(base_path, 'logs', 'analysis_log.txt')
    setup_logging(log_path)
    logging.info("Starting statistical analysis")
    df = load_evaluation_results(results_path)
    logging.info(f"Loaded {len(df)} runs")
    df.to_csv(os.path.join(base_path, 'raw_data', 'all_runs.csv'), index=False)
    global_metrics = compute_global_metrics(df)
    with open(os.path.join(base_path, 'summary', 'global_metrics.json'), 'w') as f:
        json.dump(global_metrics, f, indent=2)
    per_batch = compute_per_batch_metrics(df)
    with open(os.path.join(base_path, 'summary', 'per_batch_metrics.json'), 'w') as f:
        json.dump(per_batch, f, indent=2)
    cis = compute_confidence_intervals(df)
    with open(os.path.join(base_path, 'summary', 'confidence_intervals.json'), 'w') as f:
        json.dump(cis, f, indent=2)
    best_worst = find_best_worst_runs(df)
    with open(os.path.join(base_path, 'summary', 'best_worst_runs.json'), 'w') as f:
        json.dump(best_worst, f, indent=2)
    plots_path = os.path.join(base_path, 'plots')
    plot_boxplots(df, plots_path)
    plot_lineplots(df, plots_path)
    plot_barplots(df, plots_path)
    plot_heatmaps(df, plots_path)
    reports_path = os.path.join(base_path, 'reports')
    generate_reports(global_metrics, cis, per_batch, best_worst, reports_path)
    logging.info("Statistical analysis complete")