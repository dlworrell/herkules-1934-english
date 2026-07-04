# OCR Quality Report Plan

## Boundary

Reusable OCR quality machinery belongs in `engineering-docs-toolkit`.

HERKULES-specific OCR reports, correction lists, and cleaned Swedish source files belong in this repository.

## First HERKULES report outputs

The first project-local OCR quality report should write:

- `reports/ocr/pilot-quality-report.json`
- `reports/ocr/pilot-quality-report.md`

## Inputs

The report should read:

- `reports/pilot/pilot-status.json`
- each queued `import-report.json`
- each queued `canonical-document.edom.json`

## Initial checks

The first report should summarize:

- source PDF path
- source SHA-256
- page range
- page count
- EDOM node count
- OCR character count
- OCR word count
- empty pages
- low-text pages
- repeated header/footer candidates
- suspicious OCR line candidates
- pages needing first cleanup pass

## HERKULES-specific suspicious tokens

Seed tokens observed in the first 100-page pilot include:

- `uv`
- `lr`
- `huvet`
- malformed bullet lines such as `e`, `ee`, `.«`, and `«`
- repeated page furniture containing `Söderström`, `HERKULES`, or `Rak 16-Cylinder`

## Decision

The report is a P1 quality-control artifact. It should not alter raw OCR, generated EDOM, Markdown, or HTML directly.

Cleaned Swedish source should be produced separately under `source/swedish` after quality findings are reviewed.
