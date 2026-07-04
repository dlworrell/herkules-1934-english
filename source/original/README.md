# Original Source Material

This directory holds the canonical source artifacts for the HERKULES book project.

Keep original source filenames. Do not rename incoming manual files just to normalize them.

The EDT pilot manifest currently expects the primary source PDF at:

```text
source/original/Manual-HERKULES-2015-10-16-1.pdf
```

`make edt-pilot` will fail before generating pilot output when this file is missing.

Expected contents include:

- scanned manual PDFs
- original page images
- source checksums
- acquisition or provenance notes

After adding or replacing the source PDF, record provenance and checksums in this directory.

Large generated artifacts should not be committed unless they are intentionally preserved as source material.
