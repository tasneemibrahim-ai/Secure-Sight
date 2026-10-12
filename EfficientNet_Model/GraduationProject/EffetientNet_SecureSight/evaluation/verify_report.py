from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

path = Path('tasnim/evaluation/statistical_analysis/reports/statistical_analysis_report.docx')
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(path, 'r') as z:
    data = z.read('word/document.xml')
root = ET.fromstring(data)

root_tables = root.findall('.//w:tbl', ns)
print('tables', len(root_tables))
rows = root_tables[0].findall('.//w:tr', ns)
print('header', [ ''.join(t.text or '' for t in c.findall('.//w:t', ns)).strip() for c in rows[0].findall('.//w:tc', ns)])
print('row1', [ ''.join(t.text or '' for t in c.findall('.//w:t', ns)).strip() for c in rows[1].findall('.//w:tc', ns)])
print('last paragraphs:')
paras = [ ''.join(t.text or '' for t in p.findall('.//w:t', ns)).strip() for p in root.findall('.//w:p', ns)]
for line in paras[-10:]:
    if line:
        print(line)
