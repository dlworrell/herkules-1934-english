from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "edt" / "project.yml"
PILOT_REPORT = ROOT / "reports" / "pilot" / "import-report.json"


def main() -> int:
    if not MANIFEST.exists():
        print("Missing edt/project.yml manifest.")
        return 1

    command = [sys.executable, "-m", "edt.cli", "import", "--manifest", str(MANIFEST.relative_to(ROOT))]
    subprocess.run(command, cwd=ROOT, check=True)
    print(f"Wrote: {PILOT_REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
