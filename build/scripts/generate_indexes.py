#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'output'
out.mkdir(exist_ok=True)

index_dir = root / 'reference' / 'indexes'
summary = out / 'index-summary.md'

with summary.open('w', encoding='utf-8') as handle:
    handle.write('# Index Summary\n\n')
    for path in sorted(index_dir.glob('*.csv')):
        handle.write(f'- {path.name}\n')

print(f'wrote {summary}')
