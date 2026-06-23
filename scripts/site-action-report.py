#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site-action-report.py

דוח שימושיות לאתר:
- כמה כרטיסים יקבלו צפייה מוטמעת.
- כמה יקבלו הורדה.
- כמה יקבלו פתיחה בכרטיסייה.
- כמה הם PDF / Office / קישור חיצוני / לא מזוהים.

הסקריפט לא משנה קבצים.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "metadata" / "index.json"

OFFICE_EXTS = {"doc", "docx", "ppt", "pptx", "xls", "xlsx"}
DIRECT_EMBED_EXTS = {"pdf", "png", "jpg", "jpeg", "gif", "webp", "txt"}


def ext_of(record: Dict[str, Any]) -> str:
    ext = str(record.get("extension") or "").lower().lstrip(".")
    if ext:
        return ext
    name = str(record.get("file_name") or record.get("path") or "")
    if "." in name:
        return name.rsplit(".", 1)[-1].lower()
    return "unknown"


def pick(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id"),
        "title": record.get("title"),
        "grade": record.get("grade"),
        "category": record.get("primary_category"),
        "document_type": record.get("document_type"),
        "extension": ext_of(record),
        "path": record.get("path"),
        "source_url": record.get("source_url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate site action coverage report.")
    parser.add_argument("--report", default="reports/site-action-report.json")
    args = parser.parse_args()

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    files: List[Dict[str, Any]] = data.get("files", [])

    by_ext: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    by_grade: Counter[str] = Counter()
    repo_files = []
    external_links = []
    direct_embed = []
    office_embed = []
    download_ready = []
    open_ready = []
    no_action = []

    for record in files:
        ext = ext_of(record)
        by_ext[ext] += 1
        by_grade[str(record.get("grade", "unknown"))] += 1
        by_category[str(record.get("primary_category", "unknown"))] += 1

        source_type = record.get("source_type")
        path = record.get("path")
        source_url = record.get("source_url")
        is_repo = source_type == "repo-file" and bool(path)
        has_url = bool(source_url)

        if is_repo:
            repo_files.append(pick(record))
            open_ready.append(pick(record))
            download_ready.append(pick(record))
            if ext in DIRECT_EMBED_EXTS:
                direct_embed.append(pick(record))
            elif ext in OFFICE_EXTS:
                office_embed.append(pick(record))
        elif has_url:
            external_links.append(pick(record))
            open_ready.append(pick(record))
        else:
            no_action.append(pick(record))

    total = len(files)
    report = {
        "summary": {
            "total_files": total,
            "repo_files": len(repo_files),
            "external_links": len(external_links),
            "open_action_cards": len(open_ready),
            "download_action_cards": len(download_ready),
            "direct_embed_cards": len(direct_embed),
            "office_embed_cards": len(office_embed),
            "embedded_view_total": len(direct_embed) + len(office_embed),
            "no_action_cards": len(no_action),
            "download_coverage_percent": round((len(download_ready) / total * 100), 2) if total else 0,
            "open_coverage_percent": round((len(open_ready) / total * 100), 2) if total else 0,
            "embed_coverage_percent": round(((len(direct_embed) + len(office_embed)) / total * 100), 2) if total else 0,
            "by_extension": dict(sorted(by_ext.items())),
            "by_grade": dict(sorted(by_grade.items())),
            "by_category": dict(sorted(by_category.items())),
        },
        "no_action_cards": no_action,
        "direct_embed_examples": direct_embed[:50],
        "office_embed_examples": office_embed[:50],
    }

    report_path = (REPO / args.report).resolve()
    if not str(report_path).startswith(str(REPO.resolve())):
        raise SystemExit("report path must be inside repository")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("MAAGAR SITE ACTION REPORT")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    print(f"Report: {report_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
