#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'output'
book = out / 'book.md'

if not book.exists():
    raise SystemExit('output/book.md does not exist; run make build first')

pandoc = shutil.which('pandoc')
if not pandoc:
    print('pandoc not found; skipping pandoc outputs')
    raise SystemExit(0)

subprocess.run([pandoc, str(book), '-o', str(out / 'book.docx')], check=True)
subprocess.run([pandoc, str(book), '-o', str(out / 'book.epub')], check=True)
print('wrote pandoc outputs')
