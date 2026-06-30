# EDT Deployment Plan

This repository consumes Engineering Docs Toolkit as the reusable document engine. The HERKULES repository remains the canonical home for HERKULES-specific source material, translation work, glossary decisions, reports, and generated publication outputs.

## Current migration step

Step 4: document the EDT-facing repository layout before moving content.

No existing content should be moved until the inventory in `MIGRATION.md` has been reviewed.

## Immediate goals

1. Preserve previous HERKULES work in `archive/pre-edt-work/`.
2. Keep active translation and reference work in canonical folders.
3. Use `edt/project.yml` as the project manifest.
4. Add EDT commands incrementally after the repository layout is stable.
5. Run an initial small-page pilot before processing the full manual.

## Canonical active folders

- `source/original/`
- `source/swedish/`
- `source/english/`
- `reference/glossary/`
- `reference/indexes/`
- `reference/concordance/`
- `reference/tm/`
- `reports/`
- `output/`

## Archive migration rule

Move old material into the archive first when it is obsolete, exploratory, or superseded. Promote material back into active folders only after review.

## EDT dependency strategy

The HERKULES project should depend on EDT rather than copying EDT source into this repository.

Expected future dependency form:

```toml
dependencies = [
  "engineering-docs-toolkit @ git+https://github.com/dlworrell/engineering-docs-toolkit.git"
]
```

## First EDT pilot

The first pilot should process a small representative page range before the entire manual:

1. Import source pages.
2. Run OCR if needed.
3. Build layout and semantic models.
4. Generate EDOM.
5. Export translation memory seeds.
6. Produce an accessibility and semantic report.
7. Generate a small HTML or DOCX preview.

The full manual should only be processed after the pilot validates the workflow.
