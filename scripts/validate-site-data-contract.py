#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-site-data-contract.py

בודק שה-metadata מספק לאתר את השדות המינימליים לבניית כרטיס קובץ תקין.
הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "metadata" / "index.json"

REQUIRED_ALWAYS = ["id", "source_type", "grade", "primary_category", "document_type"]


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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

    seen_ids: set[str] = set()

    for i, record in enumerate(files):
        if not isinstance(record, dict):
            errors.append(f"files[{i}] is not an object")
            continue

        rid = str(record.get("id") or f"files[{i}]")

        for field in REQUIRED_ALWAYS:
            if not has_text(record.get(field)):
                errors.append(f"{rid}: missing required site field: {field}")

        if has_text(record.get("id")):
            if record["id"] in seen_ids:
                errors.append(f"{rid}: duplicate id")
            seen_ids.add(record["id"])

        if not has_text(record.get("title")) and not has_text(record.get("file_name")):
            errors.append(f"{rid}: must have title or file_name for display")

        source_type = record.get("source_type")
        path = record.get("path")
        source_url = record.get("source_url")

        if source_type == "repo-file" and not has_text(path):
            errors.append(f"{rid}: repo-file must have path")
        elif source_type != "repo-file" and not has_text(path) and not has_text(source_url):
            warnings.append(f"{rid}: non repo-file without path/source_url will not have useful actions")

        grades = record.get("grades")
        if grades is not None and not isinstance(grades, list):
            errors.append(f"{rid}: grades must be a list when present")

        topics = record.get("topics")
        if topics is not None and not isinstance(topics, list):
            errors.append(f"{rid}: topics must be a list when present")

        tags = record.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append(f"{rid}: tags must be a list when present")

    print("MAAGAR SITE DATA CONTRACT")
    print(f"Records checked: {len(files)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}")

    for warning in warnings[:50]:
        print(f"WARN  {warning}")

    if errors:
        for error in errors[:100]:
            print(f"FAIL  {error}")
        if len(errors) > 100:
            print(f"FAIL  ... and {len(errors) - 100} more errors")
        return 1

    print("OK    metadata has the fields required by the browser site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
