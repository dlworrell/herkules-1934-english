#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "import_report": ROOT / "reports" / "pilot" / "import-report.json",
    "canonical_edom": ROOT / "output" / "pilot" / "edom" / "canonical-document.edom.json",
    "markdown": ROOT / "output" / "pilot" / "markdown" / "herkules-pilot.md",
    "html": ROOT / "output" / "pilot" / "html" / "herkules-pilot.html",
    "pilot_status": ROOT / "reports" / "pilot" / "pilot-status.json",
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    return True


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return None, f"invalid JSON: {_relative(path)}: {error}"
    if not isinstance(payload, dict):
        return None, f"JSON root is not an object: {_relative(path)}"
    return payload, None


def _check_file(path: Path) -> list[str]:
    issues: list[str] = []
    if not _inside_root(path):
        return [f"pilot output escapes repository boundary: {path}"]
    if not path.exists():
        return [f"missing pilot output: {_relative(path)}"]
    if not path.is_file():
        return [f"pilot output is not a file: {_relative(path)}"]
    if path.stat().st_size == 0:
        issues.append(f"empty pilot output: {_relative(path)}")
    return issues


def _check_status_payload(status: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    expected_status_paths = {
        key: _relative(path)
        for key, path in EXPECTED_FILES.items()
        if key != "pilot_status"
    }
    for key, expected in expected_status_paths.items():
        value = status.get(key)
        if value != expected:
            issues.append(
                f"pilot status has wrong {key}: expected {expected!r}, got {value!r}"
            )
    return issues


def main() -> int:
    issues: list[str] = []

    for path in EXPECTED_FILES.values():
        issues.extend(_check_file(path))

    for key in ("import_report", "canonical_edom", "pilot_status"):
        path = EXPECTED_FILES[key]
        if path.exists() and path.is_file() and path.stat().st_size > 0:
            payload, error = _load_json(path)
            if error:
                issues.append(error)
            elif key == "pilot_status" and payload is not None:
                issues.extend(_check_status_payload(payload))

    markdown = EXPECTED_FILES["markdown"]
    if markdown.exists() and markdown.is_file():
        text = markdown.read_text(encoding="utf-8").strip()
        if not text:
            issues.append(f"empty pilot Markdown content: {_relative(markdown)}")

    html = EXPECTED_FILES["html"]
    if html.exists() and html.is_file():
        text = html.read_text(encoding="utf-8")
        if "<html" not in text or "</html>" not in text:
            issues.append(f"pilot HTML is not a complete HTML document: {_relative(html)}")

    if issues:
        print("EDT pilot output check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("EDT pilot output check passed")
    for key, path in EXPECTED_FILES.items():
        print(f"- {key}: {_relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
