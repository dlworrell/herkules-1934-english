#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PILOT_REPORT_DIR = ROOT / "reports" / "pilot"
PILOT_STATUS = PILOT_REPORT_DIR / "pilot-status.json"
SOURCE_QUEUE = PILOT_REPORT_DIR / "source-queue.json"
OCR_REPORT_DIR = ROOT / "reports" / "ocr"
OCR_REPORT_JSON = OCR_REPORT_DIR / "pilot-quality-report.json"
OCR_REPORT_MD = OCR_REPORT_DIR / "pilot-quality-report.md"
CLEANING_REPORT_JSON = OCR_REPORT_DIR / "pilot-cleaning-report.json"
CLEANING_REPORT_MD = OCR_REPORT_DIR / "pilot-cleaning-report.md"
SWEDISH_PILOT_DIR = ROOT / "source" / "swedish" / "pilot"
EXPECTED_STAGE_STATUSES = {
    "image_results": {"extracted"},
    "ocr_results": {"complete"},
    "layout_results": {"complete"},
    "semantic_results": {"complete"},
    "edom_results": {"complete"},
}
STRAY_LINES = {"uv", "lr", "huvet"}
HEADER_HINTS = ("HERKULES", "Söderström", "Rak 16")


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

    for stage_name, expected_statuses in EXPECTED_STAGE_STATUSES.items():
        results = report.get(stage_name)
        if not isinstance(results, list) or not results:
            issues.append(f"{label}: import report has no {stage_name}")
            continue
        incomplete = []
        for result in results:
            if isinstance(result, dict) and result.get("status") not in expected_statuses:
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


def _root_children(canonical: dict[str, Any]) -> list[dict[str, Any]]:
    root = canonical.get("root")
    if not isinstance(root, dict):
        return []
    children = root.get("children")
    return [child for child in children if isinstance(child, dict)] if isinstance(children, list) else []


def _node_page(node: dict[str, Any]) -> int | None:
    regions = node.get("source_regions")
    if not isinstance(regions, list) or not regions or not isinstance(regions[0], dict):
        return None
    page = regions[0].get("page")
    return page if isinstance(page, int) else None


def _text_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _is_suspicious_line(line: str) -> bool:
    stripped = line.strip()
    lowered = stripped.lower()
    if lowered in STRAY_LINES:
        return True
    if stripped.startswith(("e ", "ee ", ".", "«")):
        return True
    if ".." in stripped or "”s" in stripped:
        return True
    return False


def _analyze_ocr_source(result: dict[str, Any]) -> dict[str, Any] | None:
    canonical_path = ROOT / str(result.get("canonical_edom", ""))
    report_path = ROOT / str(result.get("import_report", ""))
    if not canonical_path.exists() or not report_path.exists():
        return None
    canonical, canonical_error = _load_json(canonical_path)
    import_report, report_error = _load_json(report_path)
    if canonical_error or report_error or canonical is None or import_report is None:
        return None

    nodes = _root_children(canonical)
    page_count = int(canonical.get("page_count", 0) or 0)
    page_stats: dict[int, dict[str, int]] = defaultdict(lambda: {"nodes": 0, "characters": 0, "words": 0, "lines": 0, "suspicious": 0, "headers": 0})
    line_counts: Counter[str] = Counter()
    suspicious_counts: Counter[str] = Counter()

    for node in nodes:
        page = _node_page(node)
        if page is None:
            continue
        text = str(node.get("text", ""))
        lines = _text_lines(text)
        page_stats[page]["nodes"] += 1
        page_stats[page]["characters"] += len(text.strip())
        page_stats[page]["words"] += len(text.replace("\n", " ").split())
        page_stats[page]["lines"] += len(lines)
        for line in lines:
            line_counts[line] += 1
            if _is_suspicious_line(line):
                page_stats[page]["suspicious"] += 1
                suspicious_counts[line] += 1

    repeated_headers = {
        line: count
        for line, count in line_counts.items()
        if count >= 3 and any(hint in line for hint in HEADER_HINTS)
    }
    for node in nodes:
        page = _node_page(node)
        if page is None:
            continue
        for line in _text_lines(str(node.get("text", ""))):
            if line in repeated_headers:
                page_stats[page]["headers"] += 1

    pages = []
    for page in range(1, page_count + 1):
        pages.append({"page": page, **page_stats[page]})

    return {
        "slug": result.get("slug"),
        "source_pdf": result.get("source_pdf"),
        "sha256": import_report.get("sha256"),
        "page_range": import_report.get("page_range"),
        "page_count": page_count,
        "node_count": len(nodes),
        "word_count": sum(page["words"] for page in pages),
        "character_count": sum(page["characters"] for page in pages),
        "empty_pages": [page["page"] for page in pages if page["characters"] == 0],
        "low_text_pages": [page["page"] for page in pages if 0 < page["characters"] < 80],
        "repeated_headers": repeated_headers,
        "suspicious_lines": dict(suspicious_counts.most_common(40)),
        "pages_needing_review": sorted(pages, key=lambda page: (page["suspicious"] + page["headers"], -page["characters"]), reverse=True)[:25],
        "pages": pages,
    }


def _write_ocr_quality_report(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    OCR_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sources = []
    for result in results:
        analyzed = _analyze_ocr_source(result)
        if analyzed is not None:
            sources.append(analyzed)

    report = {"source_count": len(sources), "sources": sources}
    OCR_REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# HERKULES OCR Quality Report", "", "Generated from queued EDT pilot outputs.", ""]
    for source in sources:
        lines.extend([
            f"## {source['slug']}",
            "",
            f"- Source PDF: `{source['source_pdf']}`",
            f"- SHA-256: `{source['sha256']}`",
            f"- Pages: {source['page_count']}",
            f"- EDOM nodes: {source['node_count']}",
            f"- OCR words: {source['word_count']}",
            f"- OCR characters: {source['character_count']}",
            f"- Empty pages: {len(source['empty_pages'])}",
            f"- Low-text pages: {len(source['low_text_pages'])}",
            "",
            "### Repeated header/footer candidates",
            "",
        ])
        repeated = source["repeated_headers"]
        if repeated:
            for text, count in sorted(repeated.items(), key=lambda item: (-item[1], item[0]))[:20]:
                lines.append(f"- `{text}` — {count}")
        else:
            lines.append("None detected.")
        lines.extend(["", "### Suspicious OCR lines", ""])
        suspicious = source["suspicious_lines"]
        if suspicious:
            for text, count in list(suspicious.items())[:20]:
                lines.append(f"- `{text}` — {count}")
        else:
            lines.append("None detected.")
        lines.extend(["", "### Pages needing review", "", "| Page | Chars | Suspicious | Header/footer |", "|---:|---:|---:|---:|"])
        for page in source["pages_needing_review"]:
            lines.append(f"| {page['page']} | {page['characters']} | {page['suspicious']} | {page['headers']} |")
        lines.append("")

    OCR_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote: {OCR_REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote: {OCR_REPORT_MD.relative_to(ROOT)}")
    return sources


def _clean_line(line: str, repeated_headers: dict[str, int]) -> tuple[str | None, str | None]:
    stripped = line.strip()
    lowered = stripped.lower()
    if stripped in repeated_headers:
        return None, "suppressed_repeated_header"
    if lowered in STRAY_LINES:
        return None, "suppressed_stray_line"
    for prefix in (". - ", ".- ", ". ", ".« ", "«  ", "« ", "ee ", "e  ", "e "):
        if stripped.startswith(prefix):
            return "- " + stripped[len(prefix):].strip(), "normalized_bullet"
    return stripped, None


def _write_clean_swedish_source(results: list[dict[str, Any]], sources: list[dict[str, Any]]) -> None:
    SWEDISH_PILOT_DIR.mkdir(parents=True, exist_ok=True)
    source_by_slug = {str(source.get("slug")): source for source in sources}
    cleaning_sources = []

    for result in results:
        slug = str(result.get("slug"))
        source_quality = source_by_slug.get(slug, {})
        repeated_headers = source_quality.get("repeated_headers", {})
        canonical_path = ROOT / str(result.get("canonical_edom", ""))
        canonical, error = _load_json(canonical_path)
        if error or canonical is None:
            continue

        page_lines: dict[int, list[str]] = defaultdict(list)
        counts = Counter()
        for node in _root_children(canonical):
            page = _node_page(node)
            if page is None:
                continue
            for line in _text_lines(str(node.get("text", ""))):
                cleaned, action = _clean_line(line, repeated_headers)
                if action:
                    counts[action] += 1
                if cleaned:
                    page_lines[page].append(cleaned)

        page_count = int(canonical.get("page_count", 0) or 0)
        output_path = SWEDISH_PILOT_DIR / f"{slug}.cleaned.md"
        markdown = [f"# {slug} — cleaned Swedish pilot source", "", "<!-- generated from EDT pilot EDOM; do not edit generated file directly -->", ""]
        for page in range(1, page_count + 1):
            markdown.extend([f"<!-- source-page: {page:04d} -->", ""])
            markdown.extend(page_lines.get(page, []))
            markdown.append("")
        output_path.write_text("\n".join(markdown), encoding="utf-8")

        cleaning_sources.append({
            "slug": slug,
            "cleaned_markdown": _relative(output_path),
            "page_count": page_count,
            "suppressed_repeated_headers": counts["suppressed_repeated_header"],
            "suppressed_stray_lines": counts["suppressed_stray_line"],
            "normalized_bullets": counts["normalized_bullet"],
        })
        print(f"Wrote: {_relative(output_path)}")

    report = {"source_count": len(cleaning_sources), "sources": cleaning_sources}
    CLEANING_REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# HERKULES Swedish Source Cleaning Report", "", "Generated from queued EDT pilot EDOM and OCR quality findings.", ""]
    for source in cleaning_sources:
        lines.extend([
            f"## {source['slug']}",
            "",
            f"- Cleaned Markdown: `{source['cleaned_markdown']}`",
            f"- Pages: {source['page_count']}",
            f"- Suppressed repeated headers/footers: {source['suppressed_repeated_headers']}",
            f"- Suppressed stray lines: {source['suppressed_stray_lines']}",
            f"- Normalized bullet lines: {source['normalized_bullets']}",
            "",
        ])
    CLEANING_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {CLEANING_REPORT_JSON.relative_to(ROOT)}")
    print(f"Wrote: {CLEANING_REPORT_MD.relative_to(ROOT)}")


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
        valid_results = [result for result in results if isinstance(result, dict)]
        sources = _write_ocr_quality_report(valid_results)
        _write_clean_swedish_source(valid_results, sources)
        for result in results:
            print(f"- {result.get('slug')}: {result.get('source_pdf')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
