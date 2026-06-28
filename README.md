# HERKULES 1934 English Technical Edition

This repository contains the working English technical edition of Pelle Soderstrom's HERKULES 1934 workshop manual.

The goal is a reproducible technical publication: Swedish source notes, English translation, glossary, concordance, indexes, and generated outputs from one source tree.

## Current structure

- `source/swedish/` original-language transcription and page notes
- `source/english/` translated chapters
- `reference/glossary/` terminology tables
- `reference/indexes/` generated and curated indexes
- `reference/concordance/` parts and cross-reference tables
- `build/scripts/` build tooling
- `output/` generated files, ignored by Git

## Build

Run:

```sh
make build
```

The build currently creates a placeholder output. The next step is replacing the placeholder with the real Markdown assembly and Pandoc build path.
