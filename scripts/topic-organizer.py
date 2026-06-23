#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topic-organizer.py

סידור נושאים למאגר maagar.

הכלי:
- קורא את metadata/index.json.
- קורא את metadata/topic-map.json כמפת הנושאים הקנונית.
- משפר topics לפי כותרת/שם קובץ/נתיב/תגיות/הערות.
- מסדר את index.json כך שקבצים מאותו נושא יופיעו יחד.
- לא מוחק קבצים.
- לא מזיז קבצים פיזיים.
- ברירת מחדל: dry-run בלבד.

שימוש:
  python3 scripts/topic-organizer.py
  python3 scripts/topic-organizer.py --report reports/topic-audit.json
  python3 scripts/topic-organizer.py --apply --report reports/topic-audit.json

הכללים המחייבים נמצאים רק ב-RULES.md.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

REPO = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO / "metadata" / "index.json"
TOPIC_MAP_PATH = REPO / "metadata" / "topic-map.json"

GRADE_ORDER = {"7": 0, "8": 1, "9": 2, "high-school": 3, "unknown": 9}
CATEGORY_ORDER = {"algebra": 0, "geometry": 1, "summaries": 2, "exams": 3, "uncategorized": 4, "unknown": 9}
DOCTYPE_ORDER = {
    "worksheet": 0,
    "summary-work": 1,
    "exam": 2,
    "mixed": 3,
    "digital-task": 4,
    "printable-task": 5,
    "embedded-resource": 6,
    "link": 7,
    "unknown": 9,
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value)
    text = str(value).lower()
    text = text.replace("_", " ").replace("-", " ").replace("/", " ").replace("\\", " ")
    text = text.replace("־", " ").replace("–", " ").replace("—", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def searchable_text(record: Dict[str, Any]) -> str:
    parts = [
        record.get("title", ""),
        record.get("file_name", ""),
        record.get("path", ""),
        record.get("topics", []),
        record.get("tags", []),
        record.get("notes", ""),
    ]
    return normalize_text(parts)


def load_topic_rules() -> List[Dict[str, Any]]:
    if not TOPIC_MAP_PATH.exists():
        raise SystemExit("Missing metadata/topic-map.json")
    topic_map = load_json(TOPIC_MAP_PATH)
    raw_topics = topic_map.get("topics", [])
    if not isinstance(raw_topics, list):
        raise SystemExit("metadata/topic-map.json must contain a top-level topics list")

    rules: List[Dict[str, Any]] = []
    for i, topic in enumerate(raw_topics):
        label = str(topic.get("label_he", "")).strip()
        if not label:
            raise SystemExit(f"topic-map item #{i} is missing label_he")
        keywords = topic.get("keywords", [])
        if not isinstance(keywords, list):
            raise SystemExit(f"topic-map item '{label}' keywords must be a list")
        rules.append({
            "id": topic.get("id", label),
            "topic": label,
            "category": topic.get("category", "unknown"),
            "keywords": [str(k).strip() for k in keywords if str(k).strip()],
            "order": i,
        })
    return rules


def infer_topics(record: Dict[str, Any], rules: List[Dict[str, Any]]) -> List[str]:
    text = searchable_text(record)
    found: List[str] = []
    for rule in rules:
        for keyword in rule["keywords"]:
            nk = normalize_text(keyword)
            if nk and nk in text:
                found.append(rule["topic"])
                break
    return found


def clean_topics(existing: Iterable[Any], inferred: Iterable[str]) -> List[str]:
    result: List[str] = []
    for topic in existing or []:
        t = str(topic).strip()
        if not t or t == "unknown":
            continue
        if t not in result:
            result.append(t)
    for topic in inferred:
        if topic not in result:
            result.append(topic)
    return result or ["unknown"]


def primary_topic(record: Dict[str, Any], rules: List[Dict[str, Any]]) -> str:
    inferred = infer_topics(record, rules)
    if inferred:
        return inferred[0]
    for topic in record.get("topics") or []:
        if topic and topic != "unknown":
            return str(topic)
    return "unknown"


def topic_order(topic: str, rules: List[Dict[str, Any]]) -> int:
    for rule in rules:
        if rule["topic"] == topic:
            return int(rule["order"])
    return 999


def sort_key(record: Dict[str, Any], rules: List[Dict[str, Any]]) -> Tuple[Any, ...]:
    grade = record.get("grade") or ((record.get("grades") or ["unknown"])[0])
    topic = primary_topic(record, rules)
    return (
        GRADE_ORDER.get(str(grade), 8),
        CATEGORY_ORDER.get(record.get("primary_category", "unknown"), 8),
        topic_order(topic, rules),
        topic,
        DOCTYPE_ORDER.get(record.get("document_type", "unknown"), 8),
        normalize_text(record.get("title", "")),
        normalize_text(record.get("file_name", "")),
        record.get("id", ""),
    )


def build_audit(files: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_grade: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    by_doctype: Counter[str] = Counter()
    by_extension: Counter[str] = Counter()
    by_topic: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    unknown_topic_ids: List[str] = []

    for record in files:
        grade = str(record.get("grade", "unknown"))
        category = str(record.get("primary_category", "unknown"))
        doctype = str(record.get("document_type", "unknown"))
        extension = str(record.get("extension", "unknown"))
        topic = primary_topic(record, rules)

        by_grade[grade] += 1
        by_category[category] += 1
        by_doctype[doctype] += 1
        by_extension[extension] += 1
        by_topic[topic].append({
            "id": str(record.get("id", "")),
            "title": str(record.get("title", "")),
            "grade": grade,
            "category": category,
            "doctype": doctype,
            "extension": extension,
            "path": str(record.get("path", "")),
        })
        if topic == "unknown":
            unknown_topic_ids.append(str(record.get("id", "")))

    groups = {
        topic: sorted(items, key=lambda x: (x["grade"], x["category"], x["title"], x["path"]))
        for topic, items in sorted(by_topic.items(), key=lambda kv: (-len(kv[1]), topic_order(kv[0], rules), kv[0]))
    }

    return {
        "summary": {
            "total_files": len(files),
            "by_grade": dict(sorted(by_grade.items())),
            "by_category": dict(sorted(by_category.items())),
            "by_document_type": dict(sorted(by_doctype.items())),
            "by_extension": dict(sorted(by_extension.items())),
            "unknown_topic_count": len(unknown_topic_ids),
        },
        "topic_groups": groups,
        "unknown_topic_ids": unknown_topic_ids,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Organize maagar metadata by canonical math topics.")
    parser.add_argument("--apply", action="store_true", help="Update metadata/index.json in place.")
    parser.add_argument("--report", default="", help="Optional JSON report path, e.g. reports/topic-audit.json")
    args = parser.parse_args()

    index = load_json(INDEX_PATH)
    rules = load_topic_rules()
    files = index.get("files", [])
    if not isinstance(files, list):
        raise SystemExit("metadata/index.json must contain a top-level 'files' list")

    changed_topics = 0
    for record in files:
        inferred = infer_topics(record, rules)
        new_topics = clean_topics(record.get("topics", []), inferred)
        if new_topics != record.get("topics"):
            changed_topics += 1
            if args.apply:
                record["topics"] = new_topics

    sorted_files = sorted(files, key=lambda r: sort_key(r, rules))
    order_changed = [r.get("id") for r in sorted_files] != [r.get("id") for r in files]

    if args.apply:
        index["files"] = sorted_files
        save_json(INDEX_PATH, index)

    audit = build_audit(sorted_files, rules)

    if args.report:
        report_path = (REPO / args.report).resolve()
        if not str(report_path).startswith(str(REPO.resolve())):
            raise SystemExit("report path must be inside the repository")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(report_path, audit)

    print("MAAGAR TOPIC ORGANIZER")
    print(f"Topic map rules: {len(rules)}")
    print(f"Files scanned: {len(files)}")
    print(f"Records with topic improvements: {changed_topics}")
    print(f"Order would change: {'yes' if order_changed else 'no'}")
    print(f"Unknown-topic records after inference: {audit['summary']['unknown_topic_count']}")
    print()
    print("Top topic groups:")
    for topic, items in list(audit["topic_groups"].items())[:25]:
        print(f"- {topic}: {len(items)}")
    print()
    if not args.apply:
        print("Dry-run only. Run with --apply to update metadata/index.json.")
    else:
        print("metadata/index.json updated. Run validation next:")
        print("  bash scripts/validate-all.sh && python3 scripts/test-logic.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
