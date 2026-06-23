#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metadata-audit.py

מפיק דוח על שדות חסרים/unknown במאגר:
- topics unknown
- author unknown
- year unknown
- category unknown/uncategorized
- קבצים גדולים
- כותרות שנראות לא נקיות

הסקריפט לא משנה כלום. רק מפיק דוח JSON.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "metadata" / "index.json"


def load_index() -> Dict[str, Any]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    if value == "unknown":
        return True
    if isinstance(value, list):
        return not value or all(is_unknown(v) for v in value)
    return False


def file_size(path: str | None) -> int | None:
    if not path:
        return None
    full = REPO / path
    if not full.exists() or not full.is_file():
        return None
    return full.stat().st_size


def messy_title(title: str) -> bool:
    if not title:
        return True
    if "__" in title or "  " in title:
        return True
    if title.endswith("_") or title.startswith("_"):
        return True
    if re.search(r"[-_]{2,}", title):
        return True
    return False


def pick(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id"),
        "title": record.get("title"),
        "grade": record.get("grade"),
        "category": record.get("primary_category"),
        "document_type": record.get("document_type"),
        "path": record.get("path"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit maagar metadata quality.")
    parser.add_argument("--report", default="reports/metadata-audit.json")
    args = parser.parse_args()

    data = load_index()
    files: List[Dict[str, Any]] = data.get("files", [])

    by_grade = Counter(str(f.get("grade", "unknown")) for f in files)
    by_category = Counter(str(f.get("primary_category", "unknown")) for f in files)
    by_document_type = Counter(str(f.get("document_type", "unknown")) for f in files)
    by_extension = Counter(str(f.get("extension", "unknown")) for f in files)

    topic_unknown = []
    author_unknown = []
    year_unknown = []
    category_unknown = []
    large_files = []
    messy_titles = []

    for record in files:
        if is_unknown(record.get("topics")):
            topic_unknown.append(pick(record))
        if is_unknown(record.get("author")):
            author_unknown.append(pick(record))
        if is_unknown(record.get("year")):
            year_unknown.append(pick(record))
        if record.get("primary_category") in ("unknown", "uncategorized", None):
            category_unknown.append(pick(record))
        if messy_title(str(record.get("title", ""))):
            messy_titles.append(pick(record))

        size = file_size(record.get("path"))
        if size is not None and size >= 10 * 1024 * 1024:
            item = pick(record)
            item["size_bytes"] = size
            item["size_mb"] = round(size / 1024 / 1024, 2)
            large_files.append(item)

    report = {
        "summary": {
            "total_files": len(files),
            "by_grade": dict(sorted(by_grade.items())),
            "by_category": dict(sorted(by_category.items())),
            "by_document_type": dict(sorted(by_document_type.items())),
            "by_extension": dict(sorted(by_extension.items())),
            "topic_unknown_count": len(topic_unknown),
            "author_unknown_count": len(author_unknown),
            "year_unknown_count": len(year_unknown),
            "category_unknown_count": len(category_unknown),
            "large_file_count_10mb_plus": len(large_files),
            "messy_title_count": len(messy_titles),
        },
        "topic_unknown": topic_unknown,
        "author_unknown": author_unknown,
        "year_unknown": year_unknown,
        "category_unknown_or_uncategorized": category_unknown,
        "large_files_10mb_plus": sorted(large_files, key=lambda x: x.get("size_bytes", 0), reverse=True),
        "messy_titles": messy_titles,
    }

    report_path = (REPO / args.report).resolve()
    if not str(report_path).startswith(str(REPO.resolve())):
        raise SystemExit("report path must be inside repository")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("MAAGAR METADATA AUDIT")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    print(f"Report: {report_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
