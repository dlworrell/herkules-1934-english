# P1 Pilot Quality Review

## Status

The HERKULES EDT pilot now processes the first 100 pages of the preserved original source PDF through the queued import pipeline.

Current source queue:

- Source PDF: `source/original/Manual-HERKULES-2015-10-16-1.pdf`
- Queue manifest: `reports/pilot/source-queue.json`
- Import report: `reports/pilot/Manual-HERKULES-2015-10-16-1/import-report.json`
- Canonical EDOM: `output/pilot/Manual-HERKULES-2015-10-16-1/edom/canonical-document.edom.json`
- Markdown: `output/pilot/markdown/Manual-HERKULES-2015-10-16-1.md`
- HTML: `output/pilot/html/Manual-HERKULES-2015-10-16-1.html`

The pilot is now a real book-processing pass rather than a placeholder build.

## Confirmed working

- Source discovery reads PDF files from `source/original`.
- Original source filenames are preserved.
- The source queue records the PDF and per-source output locations.
- The pilot range is pages 1 through 100.
- PDF pages render to images in per-source page artifact directories.
- Swedish Tesseract OCR produces text.
- Layout, semantic, EDOM, Markdown, and HTML outputs are generated.
- CI validates queued outputs rather than a single hard-coded pilot path.

## Quality observations

The first 100-page Markdown output is usable as a raw OCR-derived Swedish source, but it is not yet editorially clean enough to serve as the final translation base without a cleanup pass.

Observed OCR/output artifacts include:

- Stray header/footer fragments such as `uv`, `lr`, and `huvet`.
- OCR punctuation errors, for example smart quote and apostrophe confusion.
- Bullet/list recognition errors such as `e`, `.«`, and doubled punctuation.
- Page headers are retained inside the flowing text.
- Layout segmentation is still coarse; current output often has one text block per page.
- Tables/specification lists need structural cleanup before final translation.
- Figure/photo placeholder pages are detected as text-only notes rather than linked image regions.

## P1 remediation plan

1. Add an OCR quality report summarizing pages, block counts, empty pages, and suspicious tokens.
2. Add header/footer suppression or classification so repeated page furniture does not enter translation memory as body text.
3. Improve block segmentation so headings, paragraphs, lists, tables, captions, and figure placeholders are separated.
4. Preserve raw OCR output, but create a cleaned Swedish source layer under `source/swedish` for translation.
5. Start a project glossary and correction list for recurring OCR mistakes and technical vocabulary.
6. Keep generated `output/pilot` rebuildable; do not hand-edit generated outputs.

## Decision

Proceed with the 100-page pilot as the working baseline.

Do not begin full English translation until the cleaned Swedish source layer and OCR quality report are in place.
