# HERKULES EDT Migration Inventory

This document tracks the migration from the original HERKULES repository layout into an EDT-driven project structure.

## Migration status key

- `Keep` - already canonical or should remain active.
- `Move` - should be moved into the new canonical structure.
- `Archive` - should be preserved under `archive/pre-edt-work/`.
- `Regenerate` - should not be treated as canonical; rebuild from source.
- `Review` - needs inspection before deciding.

## Current known layout

| Current path | Proposed destination | Status | Notes |
| --- | --- | --- | --- |
| `source/swedish/` | `source/swedish/` | Keep | Original-language transcription and page notes remain canonical. |
| `source/english/` | `source/english/` | Keep | English translation drafts remain canonical. |
| `reference/glossary/` | `reference/glossary/` | Keep | Terminology work remains active. |
| `reference/indexes/` | `reference/indexes/` | Keep | Curated or generated indexes remain under reference. |
| `reference/concordance/` | `reference/concordance/` | Keep | Parts and cross-reference tables remain active. |
| `build/scripts/` | `archive/pre-edt-work/build-scripts/` or EDT wrappers | Review | Old scripts may contain useful logic, but should not remain the long-term build engine if EDT replaces them. |
| `output/` | `output/` | Regenerate | Generated outputs are not canonical unless saved as release artifacts. |
| source manual PDF | `source/original/` | Move | The scanned/source manual belongs in the original source directory. |
| OCR artifacts | `reports/` or `source/original/ocr/` | Review | Keep reviewed OCR checkpoints; regenerate transient OCR. |
| translation memory | `reference/tm/` | Move | Project-specific TMX and translation unit files belong here. |
| old exploratory notes | `archive/pre-edt-work/notes/` | Archive | Preserve for provenance. |

## Migration sequence

1. Preserve pre-EDT archive area.
2. Establish canonical EDT project layout.
3. Inventory current content.
4. Document EDT-facing layout and deployment plan.
5. Add EDT dependency and build wrappers.
6. Migrate useful content one logical area per commit.
7. Run the first EDT pilot on a small page range.
8. Promote validated outputs into the normal workflow.

## Current step

Step 6 complete: EDT dependency metadata and conservative build wrapper targets have been added. No existing content has been moved yet.
