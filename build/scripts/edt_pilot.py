from __future__ import annotations

import json
from pathlib import Path

from edt.edom_markdown import write_edom_markdown
from edt.html import write_edom_html
from edt.project_import import import_project, load_project_import_config


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "edt" / "project.yml"
PILOT_REPORT = ROOT / "reports" / "pilot" / "import-report.json"
PILOT_EDOM = ROOT / "output" / "pilot" / "edom" / "canonical-document.edom.json"
PILOT_MARKDOWN = ROOT / "output" / "pilot" / "markdown" / "herkules-pilot.md"
PILOT_HTML = ROOT / "output" / "pilot" / "html" / "herkules-pilot.html"
PILOT_STATUS = ROOT / "reports" / "pilot" / "pilot-status.json"


def main() -> int:
    if not MANIFEST.exists():
        print("Missing edt/project.yml manifest.")
        return 1

    config = load_project_import_config(ROOT, MANIFEST)
    if not config.source_pdf.exists():
        print(
            "Missing HERKULES source PDF: "
            f"{config.source_pdf.relative_to(ROOT)}"
        )
        print("Add the source PDF at the manifest path before running make edt-pilot.")
        return 1

    import_project(ROOT, MANIFEST)

    if not PILOT_EDOM.exists():
        print(f"Missing canonical pilot EDOM: {PILOT_EDOM.relative_to(ROOT)}")
        return 1

    write_edom_markdown(PILOT_EDOM, PILOT_MARKDOWN)
    write_edom_html(PILOT_EDOM, PILOT_HTML, title="HERKULES 1934 English Technical Edition")

    PILOT_STATUS.parent.mkdir(parents=True, exist_ok=True)
    status = {
        "import_report": str(PILOT_REPORT.relative_to(ROOT)),
        "canonical_edom": str(PILOT_EDOM.relative_to(ROOT)),
        "markdown": str(PILOT_MARKDOWN.relative_to(ROOT)),
        "html": str(PILOT_HTML.relative_to(ROOT)),
    }
    PILOT_STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote: {PILOT_REPORT.relative_to(ROOT)}")
    print(f"Wrote: {PILOT_EDOM.relative_to(ROOT)}")
    print(f"Wrote: {PILOT_MARKDOWN.relative_to(ROOT)}")
    print(f"Wrote: {PILOT_HTML.relative_to(ROOT)}")
    print(f"Wrote: {PILOT_STATUS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
