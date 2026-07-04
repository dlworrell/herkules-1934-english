# HERKULES P0-P5 Diagnostic and Implementation Audit

Date: 2026-07-04

## Scope

This audit covers the HERKULES book project repository:

```text
dlworrell/herkules-1934-english
```

The Engineering Docs Toolkit is treated as an external reusable toolchain. HERKULES owns its source material, generated outputs, reports, CI behavior, and acceptance artifacts.

## Current diagnosis

The repository has the correct high-level shape for a book project, but it is still partly in a bootstrap state. The project boundary is now explicit, and EDT can be installed as a dependency. The CI and build scripts can run, but several targets still reflect early placeholder assumptions rather than a fully truthful publication pipeline.

Important current facts:

- The book repo declares EDT as a dependency in `pyproject.toml`.
- The project manifest is `edt/project.yml`.
- The manifest points the pilot import at `source/original/herkules-manual.pdf`.
- The manifest defines generated pilot output roots under `output/pilot` and `reports/pilot`.
- Legacy build scripts still read `source/english/*.md` and write top-level `output/book.*` artifacts.
- The EDT pilot now writes canonical EDOM, Markdown, HTML, and status outputs under the book repo.
- GitHub Actions runners are disposable, so generated files only appear in the repository when a workflow explicitly commits them or uploads them as artifacts.

## P0 — Repository boundary, reproducibility, and truthful CI

P0 is about preventing misleading green builds and misplaced artifacts.

### Findings

1. **Project boundary must remain strict**

   HERKULES is the originator project. EDT is a dependency. HERKULES-specific source files, outputs, reports, CI decisions, pilot artifacts, and acceptance results belong in this repository.

2. **Generated outputs do not appear in Git unless committed**

   CI can produce `output/` and `reports/` on a runner and still leave no files in the repository. This is normal GitHub Actions behavior, but it is misleading if users expect generated files to appear after a green workflow.

3. **Legacy and EDT output paths are split**

   Legacy build output currently uses top-level `output/book.md`, `output/book.html`, `output/book.docx`, and `output/book.epub`.

   EDT pilot output uses:

   ```text
   output/pilot/edom
   output/pilot/markdown
   output/pilot/html
   reports/pilot
   ```

   This is acceptable during transition, but must be documented and checked.

4. **`source/english` is editorial source, not generated output**

   Generated files must not be written into `source/english`. Promotion from generated pilot material into reviewed English source should be a deliberate editorial action.

### P0 remediation steps

- Keep the project boundary document authoritative.
- Ensure workflows that are expected to persist generated output either upload artifacts or commit expected output paths back to the repo.
- Add diagnostics that verify expected generated pilot files exist after `make edt-pilot`.
- Add a status report that tells users exactly where generated files were written.
- Avoid writing generated files into `source/english`.

## P1 — Pilot import and publication path

P1 is about making the HERKULES pilot a real acceptance path rather than a smoke test.

### Findings

1. **The EDT pilot currently exercises only the first slice of the manual**

   The manifest defines pilot pages 1 through 3. This is good for early integration, but not full manual acceptance.

2. **The pilot path now publishes Markdown and HTML from canonical EDOM**

   This is the correct direction. The next step is to make this path produce enough diagnostics to decide whether the generated output is meaningful, not merely present.

3. **The pilot is not yet a semantic quality gate**

   Presence of EDOM, Markdown, and HTML does not prove correct OCR, segmentation, page mapping, translation readiness, or reference quality.

### P1 remediation steps

- Add a pilot verification script that checks for import report, canonical EDOM, Markdown, HTML, and pilot status files.
- Record page count, source path, source existence, and output paths in one machine-readable status file.
- Add CI coverage for `make edt-pilot` plus pilot output verification.
- Promote the first real pilot failure into a specific issue: OCR, import, EDOM assembly, renderer, report, or workflow.

## P2 — Source corpus and provenance discipline

P2 is about ensuring source material can be trusted and traced.

### Findings

1. **The original PDF path is known**

   The manifest expects:

   ```text
   source/original/herkules-manual.pdf
   ```

2. **Provenance policy exists conceptually but is not fully enforced**

   The README and manifest mention provenance, archive preservation, and rebuildable output, but source checks do not yet verify checksums, source notes, or archival metadata.

3. **Archive policy needs enforcement**

   Older work should remain available in `archive/pre-edt-work`, but the repository needs checks that prevent silent loss or accidental replacement of source material.

### P2 remediation steps

- Add checksums for original source files.
- Add provenance notes for scans, uploads, source dates, and manual edition identity.
- Add a source manifest for original PDFs and OCR/transcription sources.
- Verify that archive material is preserved and not overwritten by generated output.

## P3 — Translation, terminology, concordance, and editorial workflow

P3 is about turning generated material into a reliable English technical edition.

### Findings

1. **Translation memory and glossary paths exist**

   The manifest names glossary and TM resources, but current checks do not verify completeness, schema, or usage.

2. **English source is not automatically updated from generated output**

   This is correct. Generated pilot Markdown can inform editorial work, but reviewed English chapters should be promoted deliberately.

3. **Terminology and concordance are underdeveloped as quality gates**

   Current glossary/index scripts are simple and do not yet enforce terminology consistency or part-number cross-reference integrity.

### P3 remediation steps

- Add glossary schema validation.
- Add translation memory validation.
- Add concordance checks for duplicate or conflicting part references.
- Add an explicit promotion workflow from generated pilot Markdown to reviewed `source/english` chapters.
- Track reviewed/unreviewed status per page or section.

## P4 — Publication outputs and format profiles

P4 is about generating credible book outputs.

### Findings

1. **Legacy build output is Markdown/HTML from `source/english`**

   This remains useful for human-edited source, but it is separate from the EDT pilot path.

2. **Pandoc outputs are generated from top-level `output/book.md`**

   DOCX and EPUB generation depend on the legacy build path rather than the EDT pilot path.

3. **No format-specific acceptance criteria exist yet**

   There are no profile checks for DOCX, EPUB, PDF, print layout, accessibility, image handling, indexes, or cross references.

### P4 remediation steps

- Define publication profiles for HTML, DOCX, EPUB, PDF, and print-ready outputs.
- Decide when EDT-generated canonical output should replace or feed the legacy `output/book.md` path.
- Add accessibility checks for generated HTML.
- Add artifact manifesting so each published output records its source, fingerprint, and generation command.

## P5 — Automation, release engineering, and long-term maintenance

P5 is about making the book project maintainable over time.

### Findings

1. **CI exists but is workflow-oriented rather than release-oriented**

   The workflows can run checks and builds, but they do not yet define releases, tagged artifacts, or durable publication packages.

2. **Generated outputs can be committed by manual runs**

   This is useful now, but later release automation should distinguish routine CI, generated previews, and official release artifacts.

3. **The toolkit dependency is currently pulled from GitHub**

   This keeps the book moving quickly, but reproducible releases eventually need pinned versions or commit SHAs.

### P5 remediation steps

- Pin EDT dependency for release builds.
- Add release workflow for tagged book snapshots.
- Upload full output packages as release artifacts.
- Add changelog/provenance entries for each generated release.
- Add long-term checks for stale generated outputs versus current source.

## Recommended execution order

1. P0: Verify and persist outputs truthfully.
2. P1: Make the pilot acceptance path diagnostic-rich.
3. P2: Lock down source provenance and checksums.
4. P3: Add terminology, translation memory, and editorial promotion workflow.
5. P4: Define and validate publication output profiles.
6. P5: Add release automation and dependency pinning.

## Immediate next P0 commit recommendation

Add `build/scripts/check_edt_pilot_outputs.py` and wire it into `make edt-pilot` or CI. It should fail when the pilot claims success but expected files are missing, empty, invalid JSON, or outside the HERKULES repository boundary.
