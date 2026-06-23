#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topic-organizer.py

מטרת הכלי:
- למפות את קבצי המאגר לפי נושאי מתמטיקה קנוניים.
- לעדכן topics חסרים/לא מדויקים בזהירות, בלי להמציא מידע מעבר למה שנראה בשם/נתיב/metadata.
- לסדר את metadata/index.json כך שקבצים מאותו נושא יופיעו אחד ליד השני באתר.

הכלי אינו משנה קבצים פיזיים.
הכלי אינו מוחק רשומות.
ברירת המחדל היא dry-run בלבד.

שימוש:
  python3 scripts/topic-organizer.py
  python3 scripts/topic-organizer.py --apply
  python3 scripts/topic-organizer.py --report reports/topic-audit.json

כללים מחייבים נשארים רק ב-RULES.md.
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

# סדר חשוב: נושאים ספציפיים לפני נושאים כלליים.
TOPIC_RULES: List[Dict[str, Any]] = [
    {
        "topic": "משוואות בשני נעלמים",
        "category": "algebra",
        "keywords": [
            "שני נעלמים",
            "שתי נעלמים",
            "2 נעלמים",
            "מערכת משוואות",
            "מערכות משוואות",
            "מערכת של משוואות",
            "משוואות עם שני נעלמים",
            "שיטת ההצבה",
            "שיטת הצבה",
            "השוואת מקדמים",
            "פתרון גרפי",
        ],
    },
    {
        "topic": "משוואות ריבועיות",
        "category": "algebra",
        "keywords": ["משוואה ריבועית", "משוואות ריבועיות", "טרינום", "נוסחת השורשים"],
    },
    {
        "topic": "פונקציה ריבועית",
        "category": "algebra",
        "keywords": ["פונקציה ריבועית", "פונקציות ריבועיות", "פרבולה", "פרבולות"],
    },
    {
        "topic": "פונקציה קווית",
        "category": "algebra",
        "keywords": ["פונקציה קווית", "פונקציות קוויות", "שיפוע", "משוואת ישר", "y=f(x)", "yfx"],
    },
    {
        "topic": "מספרים מכוונים",
        "category": "algebra",
        "keywords": ["מספרים מכוונים", "מכוונים", "מספרים שליליים", "מינוס", "שליליים", "חיוביים ושליליים"],
    },
    {
        "topic": "ביטויים אלגבריים",
        "category": "algebra",
        "keywords": ["ביטויים אלגבריים", "ביטוי אלגברי", "כינוס איברים", "הצבה", "פישוט ביטויים"],
    },
    {
        "topic": "משוואות",
        "category": "algebra",
        "keywords": ["משוואות", "משוואה", "פתרון משוואות", "פתרון משוואה"],
    },
    {
        "topic": "יחס ופרופורציה",
        "category": "algebra",
        "keywords": ["יחס", "פרופורציה", "קנה מידה", "קנמ", "קנ\"מ"],
    },
    {
        "topic": "אחוזים",
        "category": "algebra",
        "keywords": ["אחוז", "אחוזים", "הנחה", "התייקרות"],
    },
    {
        "topic": "חוקיות וסדרות",
        "category": "algebra",
        "keywords": ["חוקיות", "סדרה", "סדרות", "דפוס", "דפוסים"],
    },
    {
        "topic": "מערכת צירים",
        "category": "algebra",
        "keywords": ["מערכת צירים", "ציר x", "ציר y", "נקודות במישור", "מישור קרטזי"],
    },
    {
        "topic": "זוויות",
        "category": "geometry",
        "keywords": ["זוויות", "זווית", "מקבילים", "זוויות מתאימות", "זוויות מתחלפות"],
    },
    {
        "topic": "משולשים",
        "category": "geometry",
        "keywords": ["משולש", "משולשים", "גובה במשולש", "תיכון", "חוצה זווית"],
    },
    {
        "topic": "חפיפת משולשים",
        "category": "geometry",
        "keywords": ["חפיפה", "חפיפת משולשים", "משולשים חופפים"],
    },
    {
        "topic": "דמיון משולשים",
        "category": "geometry",
        "keywords": ["דמיון", "דמיון משולשים", "משולשים דומים"],
    },
    {
        "topic": "דלתון",
        "category": "geometry",
        "keywords": ["דלתון", "דלתונים"],
    },
    {
        "topic": "מלבן וריבוע",
        "category": "geometry",
        "keywords": ["מלבן", "ריבוע", "ריבועים"],
    },
    {
        "topic": "מקבילית",
        "category": "geometry",
        "keywords": ["מקבילית", "מקביליות"],
    },
    {
        "topic": "מעוין",
        "category": "geometry",
        "keywords": ["מעוין", "מעויין"],
    },
    {
        "topic": "טרפז",
        "category": "geometry",
        "keywords": ["טרפז", "טרפזים"],
    },
    {
        "topic": "קטע אמצעים",
        "category": "geometry",
        "keywords": ["קטע אמצעים", "אמצעים במשולש", "אמצעים בטרפז"],
    },
    {
        "topic": "משפט פיתגורס",
        "category": "geometry",
        "keywords": ["פיתגורס", "משפט פיתגורס", "משולש ישר זווית"],
    },
    {
        "topic": "מבחני מיון והקבצה",
        "category": "exams",
        "keywords": ["מבחן מיון", "מיון", "הקבצה", "מדעית"],
    },
    {
        "topic": "מבחן מחצית",
        "category": "exams",
        "keywords": ["מחצית", "מבחן מחצית"],
    },
    {
        "topic": "מבחן סוף שנה",
        "category": "exams",
        "keywords": ["סוף שנה", "מסכם שנה", "מבחן סוף"],
    },
    {
        "topic": "קורס קיץ",
        "category": "summaries",
        "keywords": ["קורס קיץ", "מכינה", "הכנה לכיתה"],
    },
]

GRADE_ORDER = {"7": 0, "8": 1, "9": 2, "high-school": 3, "unknown": 9}
CATEGORY_ORDER = {"algebra": 0, "geometry": 1, "summaries": 2, "exams": 3, "uncategorized": 4, "unknown": 9}
DOCTYPE_ORDER = {"worksheet": 0, "summary-work": 1, "exam": 2, "mixed": 3, "digital-task": 4, "printable-task": 5, "embedded-resource": 6, "link": 7, "unknown": 9}


def load_index() -> Dict[str, Any]:
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: Dict[str, Any]) -> None:
    with INDEX_PATH.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value)
    text = str(value).lower()
    text = text.replace("_", " ").replace("-", " ").replace("/", " ")
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


def infer_topics(record: Dict[str, Any]) -> List[str]:
    text = searchable_text(record)
    found: List[str] = []
    for rule in TOPIC_RULES:
        for keyword in rule["keywords"]:
            if normalize_text(keyword) and normalize_text(keyword) in text:
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


def primary_topic(record: Dict[str, Any]) -> str:
    inferred = infer_topics(record)
    if inferred:
        return inferred[0]
    for topic in record.get("topics") or []:
        if topic and topic != "unknown":
            return str(topic)
    return "unknown"


def sort_key(record: Dict[str, Any]) -> Tuple[Any, ...]:
    grade = record.get("grade") or ((record.get("grades") or ["unknown"])[0])
    return (
        GRADE_ORDER.get(str(grade), 8),
        CATEGORY_ORDER.get(record.get("primary_category", "unknown"), 8),
        primary_topic(record),
        DOCTYPE_ORDER.get(record.get("document_type", "unknown"), 8),
        normalize_text(record.get("title", "")),
        normalize_text(record.get("file_name", "")),
        record.get("id", ""),
    )


def build_audit(files: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        topic = primary_topic(record)

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
            "path": str(record.get("path", "")),
        })
        if topic == "unknown":
            unknown_topic_ids.append(str(record.get("id", "")))

    groups = {
        topic: sorted(items, key=lambda x: (x["grade"], x["category"], x["title"]))
        for topic, items in sorted(by_topic.items(), key=lambda kv: (-len(kv[1]), kv[0]))
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

    index = load_index()
    files = index.get("files", [])
    if not isinstance(files, list):
        raise SystemExit("metadata/index.json must contain a top-level 'files' list")

    changed = 0
    for record in files:
        inferred = infer_topics(record)
        new_topics = clean_topics(record.get("topics", []), inferred)
        if new_topics != record.get("topics"):
            changed += 1
            if args.apply:
                record["topics"] = new_topics

    sorted_files = sorted(files, key=sort_key)
    order_changed = [r.get("id") for r in sorted_files] != [r.get("id") for r in files]

    if args.apply:
        index["files"] = sorted_files
        save_index(index)

    audit = build_audit(sorted_files)

    if args.report:
        report_path = (REPO / args.report).resolve()
        if not str(report_path).startswith(str(REPO.resolve())):
            raise SystemExit("report path must be inside the repository")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(audit, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print("MAAGAR TOPIC ORGANIZER")
    print(f"Files scanned: {len(files)}")
    print(f"Records with topic improvements: {changed}")
    print(f"Order would change: {'yes' if order_changed else 'no'}")
    print(f"Unknown-topic records after inference: {audit['summary']['unknown_topic_count']}")
    print()
    print("Top topic groups:")
    for topic, items in list(audit["topic_groups"].items())[:20]:
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
