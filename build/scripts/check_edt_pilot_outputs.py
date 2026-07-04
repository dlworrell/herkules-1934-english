#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PILOT_REPORT_DIR = ROOT / "reports" / "pilot"
PILOT_STATUS = PILOT_REPORT_DIR / "pilot-status.json"
SOURCE_QUEUE = PILOT_REPORT_DIR / "source-queue.json"


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
    if not _inside_root(path):
        return [f"pilot output escapes repository boundary: {path}"]
    if not path.exists():
        return [f"missing pilot output: {_relative(path)}"]
    if not path.is_file():
        return [f"pilot output is not a file: {_relative(path)}"]
    if path.stat().st_size == 0:
        return [f"empty pilot output: {_relative(path)}"]
    return []


def _check_import_report(report: dict[str, Any], label: str) -> list[str]:
    issues: list[str] = []
    if report.get("source_exists") is not True:
        issues.append(f"{label}: pilot source is missing: {report.get('source_pdf')!r}")

    canonical = report.get("canonical_document_edom")
    if isinstance(canonical, dict):
        pages = canonical.get("pages")
        nodes = canonical.get("nodes")
        if not isinstance(pages, int) or pages < 1:
            issues.append(f"{label}: canonical EDOM has no pages: pages={pages!r}")
        if not isinstance(nodes, int) or nodes < 1:
            issues.append(f"{label}: canonical EDOM has no top-level nodes: nodes={nodes!r}")
    else:
        issues.append(f"{label}: import report is missing canonical_document_edom summary")

    for stage_name in ("image_results", "ocr_results", "layout_results", "semantic_results", "edom_results"):
        results = report.get(stage_name)
        if not isinstance(results, list) or not results:
            issues.append(f"{label}: import report has no {stage_name}")
            continue
        incomplete = []
        for result in results:
            if isinstance(result, dict) and result.get("status") != "complete":
                incomplete.append(result)
        if incomplete:
            issues.append(f"{label}: {stage_name} incomplete; first={incomplete[0]!r}")
    return issues


def _check_canonical_edom(payload: dict[str, Any], label: str) -> list[str]:
    issues: list[str] = []
    page_count = payload.get("page_count")
    if not isinstance(page_count, int) or page_count < 1:
        issues.append(f"{label}: canonical EDOM file has no pages: page_count={page_count!r}")
    root = payload.get("root")
    if not isinstance(root, dict):
        issues.append(f"{label}: canonical EDOM file has no root object")
        return issues
    children = root.get("children")
    if not isinstance(children, list) or not children:
        issues.append(f"{label}: canonical EDOM root has no children")
    return issues


def _check_text_outputs(markdown: Path, html: Path, label: str) -> list[str]:
    issues: list[str] = []
    if markdown.exists() and markdown.is_file():
        if not markdown.read_text(encoding="utf-8").strip():
            issues.append(f"{label}: empty pilot Markdown content: {_relative(markdown)}")
    if html.exists() and html.is_file():
        text = html.read_text(encoding="utf-8")
        if "<html" not in text or "</html>" not in text:
            issues.append(f"{label}: pilot HTML is not complete: {_relative(html)}")
    return issues


def main() -> int:
    issues: list[str] = []

    for path in (SOURCE_QUEUE, PILOT_STATUS):
        issues.extend(_check_file(path))

    status, status_error = _load_json(PILOT_STATUS) if PILOT_STATUS.exists() else (None, None)
    queue, queue_error = _load_json(SOURCE_QUEUE) if SOURCE_QUEUE.exists() else (None, None)
    if status_error:
        issues.append(status_error)
    if queue_error:
        issues.append(queue_error)

    if queue is not None:
        sources = queue.get("sources")
        if not isinstance(sources, list) or not sources:
            issues.append("source queue is empty")

    results = None
    if status is not None:
        results = status.get("results")
        source_count = status.get("source_count")
        if not isinstance(results, list) or not results:
            issues.append("pilot status has no results")
        elif source_count != len(results):
            issues.append(f"pilot status source_count mismatch: {source_count!r} != {len(results)}")

    if isinstance(results, list):
        for result in results:
            if not isinstance(result, dict):
                issues.append(f"pilot status result is not an object: {result!r}")
                continue
            label = str(result.get("slug", result.get("index", "source")))
            for key in ("import_report", "canonical_edom", "markdown", "html"):
                value = result.get(key)
                if not isinstance(value, str):
                    issues.append(f"{label}: missing path for {key}")
                    continue
                issues.extend(_check_file(ROOT / value))

            import_report_path = ROOT / str(result.get("import_report", ""))
            canonical_path = ROOT / str(result.get("canonical_edom", ""))
            markdown_path = ROOT / str(result.get("markdown", ""))
            html_path = ROOT / str(result.get("html", ""))

            if import_report_path.exists() and import_report_path.stat().st_size > 0:
                report, error = _load_json(import_report_path)
                if error:
                    issues.append(error)
                elif report is not None:
                    issues.extend(_check_import_report(report, label))

            if canonical_path.exists() and canonical_path.stat().st_size > 0:
                canonical, error = _load_json(canonical_path)
                if error:
                    issues.append(error)
                elif canonical is not None:
                    issues.extend(_check_canonical_edom(canonical, label))

            issues.extend(_check_text_outputs(markdown_path, html_path, label))

    if issues:
        print("EDT pilot output check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("EDT pilot output check passed")
    if isinstance(results, list):
        for result in results:
            print(f"- {result.get('slug')}: {result.get('source_pdf')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
