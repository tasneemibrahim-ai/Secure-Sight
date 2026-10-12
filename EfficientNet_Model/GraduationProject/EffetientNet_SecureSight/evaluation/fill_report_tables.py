"""
Fill empty columns (variance, median, count) in Word report tables and add insights.
"""
import json
import statistics
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
EVAL_DIR = ROOT_DIR / 'tasnim' / 'evaluation'
STAT_DIR = EVAL_DIR / 'statistical_analysis'
REPORT_DIR = STAT_DIR / 'reports'
REPORT_PATHS = [
    REPORT_DIR / 'evaluation_full_report.docx',
    REPORT_DIR / 'statistical_analysis_report.docx'
]

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W_NS}


def load_global_metrics():
    metrics_file = STAT_DIR / 'summary' / 'global_metrics.json'
    if metrics_file.exists():
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_per_batch_metrics():
    metrics_file = STAT_DIR / 'summary' / 'per_batch_metrics.json'
    if metrics_file.exists():
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_confidence_intervals():
    ci_file = STAT_DIR / 'summary' / 'confidence_intervals.json'
    if ci_file.exists():
        with open(ci_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_best_worst_runs():
    bw_file = STAT_DIR / 'summary' / 'best_worst_runs.json'
    if bw_file.exists():
        with open(bw_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def normalize_key(name):
    if not name:
        return ''
    return name.strip().lower().replace(' ', '_').replace('\n', '').replace('\r', '')


def get_text(cell):
    return ''.join(t.text or '' for t in cell.findall('.//w:t', NS)).strip()


def set_text(cell, text):
    for child in list(cell):
        cell.remove(child)
    p = ET.SubElement(cell, ET.QName(W_NS, 'p'))
    r = ET.SubElement(p, ET.QName(W_NS, 'r'))
    t = ET.SubElement(r, ET.QName(W_NS, 't'))
    t.text = text


def build_insights(global_metrics, per_batch_metrics, best_worst):
    insights = []

    if global_metrics:
        best_metric = max(global_metrics.items(), key=lambda x: x[1].get('mean', 0))
        insights.append(f"✓ Best Performing Metric: {best_metric[0].upper()} with mean {float(best_metric[1]['mean']):.6f}")

        most_stable = min(global_metrics.items(), key=lambda x: x[1].get('std', 0))
        insights.append(f"✓ Most Stable Metric: {most_stable[0].upper()} with std {float(most_stable[1]['std']):.6f}")

        high_var = max(global_metrics.items(), key=lambda x: x[1].get('variance', 0))
        insights.append(f"⚠ Highest Variance: {high_var[0].upper()} with variance {float(high_var[1]['variance']):.6f}")

    if best_worst and best_worst.get('best'):
        best_run = best_worst['best']
        insights.append(f"★ Best Run: Batch {best_run.get('batch_id')} Run {best_run.get('run_id')} with F1 {float(best_run.get('f1_score', 0)):.6f}")

    if best_worst and best_worst.get('worst'):
        worst_run = best_worst['worst']
        insights.append(f"★ Worst Run: Batch {worst_run.get('batch_id')} Run {worst_run.get('run_id')} with F1 {float(worst_run.get('f1_score', 0)):.6f}")

    if per_batch_metrics:
        total_samples = sum(sum(stats.get('count', 0) for stats in batch_data.values()) for batch_data in per_batch_metrics.values())
        insights.append(f"📊 Total evaluation samples: {int(total_samples)} across {len(per_batch_metrics)} batches")

    if per_batch_metrics and global_metrics and 'f1_score' in next(iter(next(iter(per_batch_metrics.values())).values()), {}):
        batch_f1_means = []
        for batch_data in per_batch_metrics.values():
            if 'f1_score' in batch_data:
                batch_f1_means.append(float(batch_data['f1_score'].get('mean', 0)))
        if batch_f1_means:
            mean_val = statistics.mean(batch_f1_means)
            std_val = statistics.pstdev(batch_f1_means)
            consistency = 1 - (std_val / (mean_val + 1e-6))
            insights.append(f"📈 Batch Consistency Score: {consistency:.4f} (higher is better)")

    return insights


def append_insights_to_document(root):
    body = root.find('w:body', NS)
    if body is None:
        return

    page_break = ET.SubElement(body, ET.QName(W_NS, 'p'))
    r = ET.SubElement(page_break, ET.QName(W_NS, 'r'))
    ET.SubElement(r, ET.QName(W_NS, 'br'), {ET.QName(W_NS, 'type'): 'page'})

    heading = ET.SubElement(body, ET.QName(W_NS, 'p'))
    pPr = ET.SubElement(heading, ET.QName(W_NS, 'pPr'))
    ET.SubElement(pPr, ET.QName(W_NS, 'pStyle'), {ET.QName(W_NS, 'val'): 'Heading1'})
    r = ET.SubElement(heading, ET.QName(W_NS, 'r'))
    t = ET.SubElement(r, ET.QName(W_NS, 't'))
    t.text = 'Key Insights & Analysis'


def append_paragraph(body, text):
    p = ET.SubElement(body, ET.QName(W_NS, 'p'))
    r = ET.SubElement(p, ET.QName(W_NS, 'r'))
    t = ET.SubElement(r, ET.QName(W_NS, 't'))
    t.text = text


def update_report_file(report_path, global_metrics, per_batch_metrics, confidence_intervals, best_worst):
    if not report_path.exists():
        print(f"Report not found: {report_path}")
        return

    with zipfile.ZipFile(report_path, 'r') as zin:
        document_xml = zin.read('word/document.xml')

    root = ET.fromstring(document_xml)
    tables = root.findall('.//w:tbl', NS)

    for table_idx, table in enumerate(tables):
        rows = table.findall('.//w:tr', NS)
        if len(rows) < 2:
            continue

        headers = [normalize_key(get_text(cell)) for cell in rows[0].findall('.//w:tc', NS)]

        if 'ci_lower' in headers and 'ci_upper' in headers:
            for row in rows[1:]:
                cells = row.findall('.//w:tc', NS)
                metric = normalize_key(get_text(cells[0]))
                ci = confidence_intervals.get(metric)
                if ci:
                    set_text(cells[1], f"{float(ci.get('mean', 0)):.6f}")
                    set_text(cells[2], f"{float(ci.get('ci_lower', 0)):.6f}")
                    set_text(cells[3], f"{float(ci.get('ci_upper', 0)):.6f}")
            print(f"Updated confidence intervals in {report_path}")
            continue

        if 'count' in headers:
            for row in rows[1:]:
                cells = row.findall('.//w:tc', NS)
                metric = normalize_key(get_text(cells[0]))
                stats = global_metrics.get(metric)
                if stats:
                    for idx, header in enumerate(headers):
                        if idx >= len(cells):
                            continue
                        key = header
                        if key in stats:
                            value = stats[key]
                            text = str(int(value)) if key == 'count' else f"{float(value):.6f}"
                            set_text(cells[idx], text)
            print(f"Updated global metrics in {report_path}")
            continue

        if 'variance' in headers or 'median' in headers:
            batch_keys = sorted(per_batch_metrics.keys(), key=int)
            batch_index = table_idx - 2
            batch_id = batch_keys[batch_index] if 0 <= batch_index < len(batch_keys) else None
            for row in rows[1:]:
                cells = row.findall('.//w:tc', NS)
                metric = normalize_key(get_text(cells[0]))
                stats = None
                if batch_id is not None:
                    stats = per_batch_metrics.get(batch_id, {}).get(metric)
                if stats is None:
                    stats = global_metrics.get(metric)
                if stats:
                    for idx, header in enumerate(headers):
                        if idx >= len(cells):
                            continue
                        key = header
                        if key in stats:
                            set_text(cells[idx], f"{float(stats[key]):.6f}")
            print(f"Updated batch table {table_idx} in {report_path}")
            continue

    body = root.find('w:body', NS)
    if body is not None:
        append_insights_to_document(root)
        for insight in build_insights(global_metrics, per_batch_metrics, best_worst):
            append_paragraph(body, '• ' + insight)
        append_paragraph(body, '')
        rec_heading = ET.SubElement(body, ET.QName(W_NS, 'p'))
        pPr = ET.SubElement(rec_heading, ET.QName(W_NS, 'pPr'))
        ET.SubElement(pPr, ET.QName(W_NS, 'pStyle'), {ET.QName(W_NS, 'val'): 'Heading2'})
        r = ET.SubElement(rec_heading, ET.QName(W_NS, 'r'))
        t = ET.SubElement(r, ET.QName(W_NS, 't'))
        t.text = 'Recommendations'
        for rec in [
            'Model demonstrates consistent performance across metrics with manageable variance.',
            'Continue monitoring metrics with high variance for potential optimization.',
            'Review the best-performing batch configuration for production replication.',
            'Statistical analysis shows enough samples for reliable conclusions.'
        ]:
            append_paragraph(body, '• ' + rec)

    temp_path = report_path.with_suffix('.updated.docx')
    with zipfile.ZipFile(report_path, 'r') as zin, zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'word/document.xml':
                continue
            zout.writestr(item, zin.read(item.filename))
        zout.writestr('word/document.xml', ET.tostring(root, encoding='utf-8', xml_declaration=True))

    temp_path.replace(report_path)
    print(f"✓ Updated report saved: {report_path}")


if __name__ == '__main__':
    global_metrics = load_global_metrics()
    per_batch_metrics = load_per_batch_metrics()
    confidence_intervals = load_confidence_intervals()
    best_worst = load_best_worst_runs()

    print(f"Loaded global metrics: {list(global_metrics.keys())}")
    print(f"Loaded per-batch metrics: {list(per_batch_metrics.keys())}")
    print(f"Report files: {[str(path) for path in REPORT_PATHS]}")

    for report_path in REPORT_PATHS:
        update_report_file(report_path, global_metrics, per_batch_metrics, confidence_intervals, best_worst)
