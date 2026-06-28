#!/usr/bin/env python3
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'output'
out.mkdir(exist_ok=True)

terms = root / 'reference' / 'glossary' / 'terms.csv'
md = out / 'glossary.md'

with terms.open(newline='', encoding='utf-8') as source, md.open('w', encoding='utf-8') as target:
    reader = csv.DictReader(source)
    target.write('# Glossary\n\n')
    for row in reader:
        target.write(f"- **{row['swedish']}**: {row['english']}\n")

print(f'wrote {md}')
