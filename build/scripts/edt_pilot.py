from __future__ import annotations

import json
from pathlib import Path

from edt.edom_markdown import write_edom_markdown
from edt.html import write_edom_html
from edt.project_import import import_project, load_project_import_config


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "edt" / "project.yml"
SOURCE_DIR = ROOT / "source" / "original"
WORK_DIR = ROOT / ".edt" / "work" / "pilot"
PILOT_REPORT_DIR = ROOT / "reports" / "pilot"
PILOT_OUTPUT_DIR = ROOT / "output" / "pilot"
PILOT_STATUS = PILOT_REPORT_DIR / "pilot-status.json"
SOURCE_QUEUE = PILOT_REPORT_DIR / "source-queue.json"
OCR_ENGINE = "tesseract"
OCR_LANGUAGE = "swe"


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _slug(path: Path) -> str:
    safe = []
    for char in path.stem:
        if char.isalnum() or char in ("-", "_", "."):
            safe.append(char)
        else:
            safe.append("-")
    return "".join(safe).strip("-._") or "source"


def _discover_source_pdfs() -> list[Path]:
    sources = []
    if SOURCE_DIR.exists():
        sources.extend(SOURCE_DIR.glob("*.pdf"))
        sources.extend(SOURCE_DIR.glob("*.PDF"))
    return sorted({path for path in sources if path.is_file()})


def _write_queue_manifest(source_pdf: Path, slug: str, base_config) -> Path:
    manifest = WORK_DIR / f"{slug}.project.yml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "source:\n"
        f"  primary_pdf: {_relative(source_pdf)}\n"
        "  pilot_pages:\n"
        f"    start: {base_config.first_page}\n"
        f"    end: {base_config.last_page}\n"
        "ocr:\n"
        f"  engine: {OCR_ENGINE}\n"
        f"  language: {OCR_LANGUAGE}\n"
        "outputs:\n"
        f"  edom: output/pilot/{slug}/edom\n"
        f"  reports: reports/pilot/{slug}\n"
        f"  pages: .edt/work/pilot/{slug}/pages\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    if not MANIFEST.exists():
        print("Missing edt/project.yml manifest.")
        return 1

    base_config = load_project_import_config(ROOT, MANIFEST)
    source_pdfs = _discover_source_pdfs()
    if not source_pdfs:
        print(f"No source PDFs found in {SOURCE_DIR.relative_to(ROOT)}")
        print("Add one or more original PDF files before running make edt-pilot.")
        return 1

    PILOT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    queue = []
    results = []

    for index, source_pdf in enumerate(source_pdfs, start=1):
        slug = _slug(source_pdf)
        queue.append({"index": index, "source_pdf": _relative(source_pdf), "slug": slug})

    SOURCE_QUEUE.write_text(json.dumps({"sources": queue}, indent=2) + "\n", encoding="utf-8")

    for item in queue:
        source_pdf = ROOT / item["source_pdf"]
        slug = item["slug"]
        queue_manifest = _write_queue_manifest(source_pdf, slug, base_config)

        import_project(ROOT, queue_manifest)

        canonical_edom = PILOT_OUTPUT_DIR / slug / "edom" / "canonical-document.edom.json"
        import_report = PILOT_REPORT_DIR / slug / "import-report.json"
        markdown = PILOT_OUTPUT_DIR / "markdown" / f"{slug}.md"
        html = PILOT_OUTPUT_DIR / "html" / f"{slug}.html"

        if not canonical_edom.exists():
            print(f"Missing canonical pilot EDOM: {canonical_edom.relative_to(ROOT)}")
            return 1

        write_edom_markdown(canonical_edom, markdown)
        write_edom_html(canonical_edom, html, title=f"HERKULES Pilot: {source_pdf.name}")

        results.append(
            {
                "index": item["index"],
                "source_pdf": item["source_pdf"],
                "slug": slug,
                "manifest": _relative(queue_manifest),
                "import_report": _relative(import_report),
                "canonical_edom": _relative(canonical_edom),
                "markdown": _relative(markdown),
                "html": _relative(html),
            }
        )
        print(f"Processed: {source_pdf.relative_to(ROOT)}")
        print(f"Wrote: {markdown.relative_to(ROOT)}")
        print(f"Wrote: {html.relative_to(ROOT)}")

    status = {"source_queue": _relative(SOURCE_QUEUE), "source_count": len(queue), "results": results}
    PILOT_STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote: {SOURCE_QUEUE.relative_to(ROOT)}")
    print(f"Wrote: {PILOT_STATUS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
