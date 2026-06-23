#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
title-cleaner.py

מייצר כותרת תצוגה נקייה בשדה display_title_clean.

הכלי לא משנה שם קובץ פיזי.
הכלי לא מוחק title מקורי.
ברירת המחדל היא dry-run + דוח בלבד.

שימוש:
  python3 scripts/title-cleaner.py --report reports/title-cleanup.json
  python3 scripts/title-cleaner.py --apply --report reports/title-cleanup.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "metadata" / "index.json"

EXT_RE = re.compile(r"\.(pdf|docx?|pptx?|xlsx?|zip)$", re.IGNORECASE)


def load_index() -> Dict[str, Any]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def save_index(data: Dict[str, Any]) -> None:
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_title(value: Any) -> str:
    text = str(value or "").strip()
    text = EXT_RE.sub("", text)
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace("–", " ")
    text = text.replace("—", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([),.:;!?])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create clean display titles for maagar metadata.")
    parser.add_argument("--apply", action="store_true", help="Write display_title_clean into metadata/index.json")
    parser.add_argument("--report", default="reports/title-cleanup.json")
    args = parser.parse_args()

    data = load_index()
    files: List[Dict[str, Any]] = data.get("files", [])
    suggestions = []
    changed = 0

    for record in files:
        title = record.get("title") or record.get("file_name") or ""
        cleaned = clean_title(title)
        current = str(record.get("display_title_clean", "")).strip()

        if cleaned and cleaned != title and cleaned != current:
            item = {
                "id": record.get("id"),
                "title": record.get("title"),
                "display_title_clean": cleaned,
                "file_name": record.get("file_name"),
                "path": record.get("path"),
            }
            suggestions.append(item)
            if args.apply:
                record["display_title_clean"] = cleaned
                changed += 1

    report = {
        "summary": {
            "total_files": len(files),
            "suggestion_count": len(suggestions),
            "applied_count": changed,
        },
        "suggestions": suggestions,
    }

    report_path = (REPO / args.report).resolve()
    if not str(report_path).startswith(str(REPO.resolve())):
        raise SystemExit("report path must be inside repository")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.apply:
        save_index(data)

    print("MAAGAR TITLE CLEANER")
    print(f"Files scanned: {len(files)}")
    print(f"Suggestions: {len(suggestions)}")
    print(f"Applied: {changed}")
    print(f"Report: {report_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
