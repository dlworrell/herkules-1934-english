from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "edt" / "project.yml"
SOURCE_PDF = ROOT / "source" / "original" / "herkules-manual.pdf"
PILOT_OUTPUT = ROOT / "output" / "pilot" / "edom"
PILOT_REPORT = ROOT / "reports" / "pilot" / "pilot-status.json"


def main() -> int:
    PILOT_OUTPUT.mkdir(parents=True, exist_ok=True)
    PILOT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    status = {
        "step": "Step 7 EDT pilot",
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "source_pdf": str(SOURCE_PDF.relative_to(ROOT)),
        "output": str(PILOT_OUTPUT.relative_to(ROOT)),
        "ready": False,
        "ran_import": False,
        "notes": [],
    }

    if not MANIFEST.exists():
        status["notes"].append("Missing edt/project.yml manifest.")
        PILOT_REPORT.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        return 1

    if not SOURCE_PDF.exists():
        status["notes"].append("Source PDF is not present yet. Place the manual at source/original/herkules-manual.pdf.")
        PILOT_REPORT.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        print("EDT pilot is configured, but the source PDF is not present yet.")
        print(f"Expected: {SOURCE_PDF.relative_to(ROOT)}")
        print(f"Wrote: {PILOT_REPORT.relative_to(ROOT)}")
        return 0

    command = [sys.executable, "-m", "edt.cli", "import-pdf", str(SOURCE_PDF), str(PILOT_OUTPUT)]
    subprocess.run(command, cwd=ROOT, check=True)
    status["ready"] = True
    status["ran_import"] = True
    status["notes"].append("EDT PDF import completed for the configured pilot source.")
    PILOT_REPORT.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {PILOT_REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
