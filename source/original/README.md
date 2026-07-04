# Original Source Material

This directory holds the canonical source artifacts for the HERKULES book project.

The EDT pilot manifest currently expects the primary source PDF at:

```text
source/original/herkules-manual.pdf
```

`make edt-pilot` will fail before generating pilot output when this file is missing. That is intentional: generated Markdown, HTML, reports, and EDOM are not meaningful without the configured source PDF.

Expected contents include:

- scanned manual PDFs
- original page images
- source checksums
- acquisition or provenance notes

After adding or replacing the source PDF, record provenance and checksums in this directory. The EDT import pipeline may also write source provenance files when the source is present.

Large generated artifacts should not be committed unless they are intentionally preserved as source material.
