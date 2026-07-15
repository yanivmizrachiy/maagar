#!/usr/bin/env python3
"""Extract page-1 text from unresolved grade 7-9 PDF materials.

This is a read-only audit. It never guesses a role or edits metadata. The output
is a JSON report for human review: author/editor/credit should only be added when
the first-page wording explicitly supports it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "metadata" / "index.json"
UNKNOWN_VALUES = {"", "unknown", "לא ידוע", "none", "null"}
TARGET_GRADES = {"7", "8", "9"}


def is_real(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() not in UNKNOWN_VALUES


def normalize_text(text: str) -> str:
    lines = []
    for raw_line in text.replace("\r", "\n").split("\n"):
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def unresolved(item: dict[str, Any]) -> bool:
    return not any(is_real(item.get(field)) for field in ("author", "editor", "credit"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="reports/first-page-credit-audit.json")
    parser.add_argument("--limit", type=int, default=0, help="0 means all matching PDFs")
    args = parser.parse_args()

    payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    items = payload.get("files", payload if isinstance(payload, list) else [])

    selected = [
        item
        for item in items
        if str(item.get("grade")) in TARGET_GRADES
        and str(item.get("path", "")).lower().endswith(".pdf")
        and unresolved(item)
    ]
    if args.limit > 0:
        selected = selected[: args.limit]

    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for item in selected:
        relative_path = str(item.get("path", ""))
        pdf_path = ROOT / relative_path
        record: dict[str, Any] = {
            "id": item.get("id"),
            "title": item.get("title"),
            "grade": item.get("grade"),
            "category": item.get("primary_category"),
            "path": relative_path,
        }
        try:
            reader = PdfReader(str(pdf_path), strict=False)
            page_text = reader.pages[0].extract_text() if reader.pages else ""
            normalized = normalize_text(page_text or "")
            record["first_page_text"] = normalized
            record["has_extractable_text"] = bool(normalized)
            record["page_count"] = len(reader.pages)
            metadata = reader.metadata or {}
            record["pdf_metadata"] = {
                "author": str(metadata.get("/Author", "")).strip(),
                "creator": str(metadata.get("/Creator", "")).strip(),
                "producer": str(metadata.get("/Producer", "")).strip(),
                "title": str(metadata.get("/Title", "")).strip(),
            }
        except Exception as exc:  # audit continues so one damaged file does not block the batch
            record["first_page_text"] = ""
            record["has_extractable_text"] = False
            record["error"] = f"{type(exc).__name__}: {exc}"
            errors.append({"id": str(item.get("id")), "error": record["error"]})
        results.append(record)

    report = {
        "scope": "grades 7-9 PDFs with no real author, editor or credit",
        "matched": len(selected),
        "with_extractable_first_page_text": sum(
            1 for record in results if record.get("has_extractable_text")
        ),
        "without_extractable_first_page_text": sum(
            1 for record in results if not record.get("has_extractable_text")
        ),
        "errors": errors,
        "files": results,
    }

    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"First-page credit audit: {report['matched']} PDFs, "
        f"{report['with_extractable_first_page_text']} with text, "
        f"{report['without_extractable_first_page_text']} without text"
    )
    print(f"Report: {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
