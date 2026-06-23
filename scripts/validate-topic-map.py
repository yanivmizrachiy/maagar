#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-topic-map.py

בודק את metadata/topic-map.json:
- JSON תקין.
- topics היא רשימה.
- לכל נושא יש id, label_he, category, keywords.
- אין id כפול.
- אין label_he כפול.
- category חוקית לפי metadata/taxonomy.json.
- keywords לא ריקה.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOPIC_MAP = REPO / "metadata" / "topic-map.json"
TAXONOMY = REPO / "metadata" / "taxonomy.json"


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def main() -> int:
    errors = 0

    if not TOPIC_MAP.exists():
        fail("metadata/topic-map.json is missing")
        return 1
    if not TAXONOMY.exists():
        fail("metadata/taxonomy.json is missing")
        return 1

    try:
        topic_map = json.loads(TOPIC_MAP.read_text(encoding="utf-8"))
        ok("topic-map.json is valid JSON")
    except Exception as exc:
        fail(f"topic-map.json invalid JSON: {exc}")
        return 1

    try:
        taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
        ok("taxonomy.json is valid JSON")
    except Exception as exc:
        fail(f"taxonomy.json invalid JSON: {exc}")
        return 1

    valid_categories = set(taxonomy.get("primary_categories", []))
    topics = topic_map.get("topics")
    if not isinstance(topics, list):
        fail("topic-map.json must contain top-level topics list")
        return 1

    ok(f"topics list exists: {len(topics)} topics")

    seen_ids: dict[str, int] = {}
    seen_labels: dict[str, int] = {}

    for i, topic in enumerate(topics):
        label = f"topics[{i}]"
        if not isinstance(topic, dict):
            fail(f"{label}: must be an object")
            errors += 1
            continue

        tid = str(topic.get("id", "")).strip()
        label_he = str(topic.get("label_he", "")).strip()
        category = str(topic.get("category", "")).strip()
        keywords = topic.get("keywords")

        if not tid:
            fail(f"{label}: missing id")
            errors += 1
        elif tid in seen_ids:
            fail(f"{label}: duplicate id '{tid}' also in topics[{seen_ids[tid]}]")
            errors += 1
        else:
            seen_ids[tid] = i

        if not label_he:
            fail(f"{label}: missing label_he")
            errors += 1
        elif label_he in seen_labels:
            fail(f"{label}: duplicate label_he '{label_he}' also in topics[{seen_labels[label_he]}]")
            errors += 1
        else:
            seen_labels[label_he] = i

        if not category:
            fail(f"{label}: missing category")
            errors += 1
        elif valid_categories and category not in valid_categories:
            fail(f"{label}: category '{category}' is not in taxonomy primary_categories")
            errors += 1

        if not isinstance(keywords, list):
            fail(f"{label}: keywords must be a list")
            errors += 1
        else:
            clean_keywords = [str(k).strip() for k in keywords if str(k).strip()]
            if not clean_keywords:
                fail(f"{label}: keywords list is empty")
                errors += 1

    if errors:
        fail(f"topic-map validation failed with {errors} error(s)")
        return 1

    ok("topic-map validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
