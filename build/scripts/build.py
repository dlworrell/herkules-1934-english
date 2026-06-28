#!/usr/bin/env python3
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'output'
out.mkdir(exist_ok=True)

chapters = sorted((root / 'source' / 'english').glob('*.md'))
book_md = out / 'book.md'
book_html = out / 'book.html'

parts = []
for chapter in chapters:
    if chapter.name == 'README.md':
        continue
    parts.append(chapter.read_text(encoding='utf-8').strip())

book_text = '\n\n'.join(parts) + '\n'
book_md.write_text(book_text, encoding='utf-8')

html_lines = [
    '<!doctype html>',
    '<html lang="en">',
    '<head>',
    '<meta charset="utf-8">',
    '<title>HERKULES 1934 English Technical Edition</title>',
    '</head>',
    '<body>',
]

for line in book_text.splitlines():
    if line.startswith('# '):
        html_lines.append(f'<h1>{escape(line[2:])}</h1>')
    elif line.startswith('## '):
        html_lines.append(f'<h2>{escape(line[3:])}</h2>')
    elif line.startswith('### '):
        html_lines.append(f'<h3>{escape(line[4:])}</h3>')
    elif line.strip():
        html_lines.append(f'<p>{escape(line)}</p>')
    else:
        html_lines.append('')

html_lines.extend(['</body>', '</html>'])
book_html.write_text('\n'.join(html_lines), encoding='utf-8')

print(f'wrote {book_md}')
print(f'wrote {book_html}')
