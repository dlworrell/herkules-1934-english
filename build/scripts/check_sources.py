#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
english = root / 'source' / 'english'
missing = []

for path in sorted(english.glob('*.md')):
    text = path.read_text(encoding='utf-8').strip()
    if not text:
        missing.append(str(path.relative_to(root)))

if missing:
    print('Empty source files:')
    for item in missing:
        print(item)
    raise SystemExit(1)

print('source check passed')
