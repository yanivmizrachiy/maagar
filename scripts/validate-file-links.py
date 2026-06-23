#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-file-links.py

בודק שכל קובץ פנימי שמופיע ב-metadata/index.json באמת קיים בריפו,
ושניתן לייצר לו פעולות אתר: צפייה, פתיחה והורדה.
הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "metadata" / "index.json"

VIEW_EXTS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx"}
DIRECT_EXTS = {"pdf", "png", "jpg", "jpeg", "gif", "webp", "txt"}
OFFICE_EXTS = {"doc", "docx", "ppt", "pptx", "xls", "xlsx"}


def ext_of(record: Dict[str, Any]) -> str:
    ext = str(record.get("extension") or "").lower().lstrip(".")
    if ext:
        return ext
    name = str(record.get("file_name") or record.get("path") or "")
    if "." in name:
        return name.rsplit(".", 1)[-1].lower()
    return "unknown"


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    if not INDEX.exists():
        print("FAIL  metadata/index.json missing")
        return 1

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    files = data.get("files", [])
    if not isinstance(files, list):
        print("FAIL  metadata/index.json files must be a list")
        return 1

    repo_files = 0
    external_links = 0
    by_ext: Counter[str] = Counter()
    viewable = 0
    office_viewer = 0
    direct_viewer = 0

    for i, record in enumerate(files):
        if not isinstance(record, dict):
            errors.append(f"files[{i}] is not an object")
            continue

        rid = record.get("id", f"files[{i}]")
        source_type = record.get("source_type")
        path = record.get("path")
        source_url = record.get("source_url")
        ext = ext_of(record)
        by_ext[ext] += 1

        if source_type == "repo-file":
            repo_files += 1
            if not path:
                errors.append(f"{rid}: repo-file missing path")
                continue
            full = REPO / str(path)
            if not full.exists():
                errors.append(f"{rid}: file path does not exist: {path}")
                continue
            if not full.is_file():
                errors.append(f"{rid}: path is not a file: {path}")
                continue
            if ext in VIEW_EXTS:
                viewable += 1
            if ext in OFFICE_EXTS:
                office_viewer += 1
            if ext in DIRECT_EXTS:
                direct_viewer += 1
        else:
            if source_url:
                external_links += 1
            elif not path:
                warnings.append(f"{rid}: no repo path and no source_url")

    print("MAAGAR FILE LINK VALIDATION")
    print(f"Total records: {len(files)}")
    print(f"Repo files: {repo_files}")
    print(f"External links: {external_links}")
    print(f"Potentially viewable files: {viewable}")
    print(f"Direct browser viewer candidates: {direct_viewer}")
    print(f"Office viewer candidates: {office_viewer}")
    print(f"Extensions: {dict(sorted(by_ext.items()))}")

    for warning in warnings[:50]:
        print(f"WARN  {warning}")

    if errors:
        for error in errors[:100]:
            print(f"FAIL  {error}")
        if len(errors) > 100:
            print(f"FAIL  ... and {len(errors) - 100} more errors")
        return 1

    print("OK    all repo-file links exist and can receive site actions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
