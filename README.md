# HERKULES 1934 English Technical Edition

This repository contains the working English technical edition of Pelle Soderstrom's HERKULES 1934 workshop manual.

The goal is a reproducible technical publication: Swedish source notes, English translation, glossary, concordance, indexes, translation memory, review reports, accessibility reports, and generated outputs from one source tree.

## Relationship to EDT

This repository is the book project. Engineering Docs Toolkit (EDT) is the reusable engine.

HERKULES should contain HERKULES-specific assets, editorial history, source notes, translation work, glossary decisions, generated reports, and publication output. EDT should contain reusable document-processing code.

## Current structure

- `source/swedish/` original-language transcription and page notes
- `source/english/` translated chapters
- `reference/glossary/` terminology tables
- `reference/indexes/` generated and curated indexes
- `reference/concordance/` parts and cross-reference tables
- `reference/tm/` translation memory files and TMX exports
- `reports/` OCR, semantic, translation, accessibility, and build reports
- `archive/pre-edt-work/` older exploratory work preserved for provenance and future reuse
- `build/scripts/` build tooling
- `output/` generated files, ignored unless intentionally committed
- `edt-project.yml` EDT project manifest

## Archive policy

Older work should not be thrown away. Material that predates the EDT-driven layout should move into `archive/pre-edt-work/` until reviewed.

Reusable material can later be promoted into the active folders:

- transcription and page notes into `source/swedish/`
- English draft material into `source/english/`
- terminology into `reference/glossary/`
- translation units into `reference/tm/`
- indexing and part-number work into `reference/indexes/` or `reference/concordance/`

## Build

Run:

```sh
make build
```

The existing build currently creates a placeholder output. The next step is replacing the placeholder with an EDT-backed pipeline that reads `edt-project.yml` and produces structured reports and publication outputs.
