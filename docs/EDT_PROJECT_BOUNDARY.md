# EDT Project Boundary

The HERKULES book repository is the originator project and the working directory for HERKULES activity.

The Engineering Docs Toolkit repository provides reusable tooling. It must not become the workspace for HERKULES source material, generated artifacts, pilot outputs, acceptance results, or book-specific CI state.

## Rule

All activity for the HERKULES book stays inside this repository:

```text
dlworrell/herkules-1934-english
```

The book project may call EDT as a dependency, command-line tool, or Python library, but inputs and outputs remain rooted in this repository.

## Source directories

Human-maintained source material belongs under `source/`:

```text
source/original
source/swedish
source/english
```

Generated files must not be written into `source/english`. That directory is reserved for reviewed editorial English source.

## Generated output directories

Generated EDT pilot activity belongs under `output/` and `reports/`:

```text
output/pilot/edom
output/pilot/markdown
output/pilot/html
reports/pilot
```

Current pilot outputs are expected at:

```text
reports/pilot/import-report.json
output/pilot/edom/canonical-document.edom.json
output/pilot/markdown/herkules-pilot.md
output/pilot/html/herkules-pilot.html
reports/pilot/pilot-status.json
```

## CI boundary

CI for this book project runs in this repository. It may install EDT from the toolkit repository as a dependency, but the workflow operates on this repository's source tree and writes only this repository's generated paths.

## Toolkit boundary

The EDT toolkit repository should remain project-neutral. HERKULES-specific acceptance tests, pilot outputs, workflow assumptions, and book corpus paths belong here, not in the toolkit repository.
