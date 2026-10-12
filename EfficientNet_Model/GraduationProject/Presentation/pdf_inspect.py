import fitz
from pathlib import Path
path = Path('Finial GP1 Presentation template  2025 2026.pdf')
print('exists', path.exists(), 'path', path)
doc = fitz.open(path)
print('pages', len(doc))
for i, p in enumerate(doc):
    print('--- page', i+1, '---')
    print('size', p.rect)
    blocks = p.get_text('dict')['blocks']
    print('blocks', len(blocks))
    for bi, b in enumerate(blocks[:20]):
        if b['type'] == 0:
            text = ' '.join(' '.join(span['text'] for span in line['spans']) for line in b['lines'])
            print('BLOCK', bi, repr(text[:250]))
    if i >= 2:
        break
