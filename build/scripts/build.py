#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'output'
out.mkdir(exist_ok=True)

chapters = sorted((root / 'source' / 'english').glob('*.md'))
book = out / 'book.md'

with book.open('w', encoding='utf-8') as handle:
    for chapter in chapters:
        if chapter.name == 'README.md':
            continue
        handle.write(chapter.read_text(encoding='utf-8'))
        handle.write('\n\n')

print(f'wrote {book}')
