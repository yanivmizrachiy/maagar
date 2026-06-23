#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart-topic-review.py

דוח חכם שמסביר למה קובץ מתאים לנושא:
- ציון ביטחון.
- מילת מפתח שהתאימה.
- שדה שבו נמצאה ההתאמה: title / file_name / path / topics / tags / notes.
- הצעת topic וקטגוריה.

הסקריפט לא משנה metadata ולא מוחק כלום.
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
TOPIC_MAP = REPO / "metadata" / "topic-map.json"

FIELD_WEIGHTS = {
    "title": 100,
    "file_name": 95,
    "topics": 92,
    "tags": 88,
    "path": 78,
    "notes": 65,
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = " ".join(str(x) for x in value)
    text = str(value).lower()
    text = text.replace("_", " ").replace("-", " ").replace("/", " ").replace("\\", " ")
    text = text.replace("־", " ").replace("–", " ").replace("—", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def record_fields(record: Dict[str, Any]) -> Dict[str, str]:
    return {
        "title": normalize(record.get("title")),
        "file_name": normalize(record.get("file_name")),
        "path": normalize(record.get("path")),
        "topics": normalize(record.get("topics", [])),
        "tags": normalize(record.get("tags", [])),
        "notes": normalize(record.get("notes")),
    }


def load_topic_rules() -> List[Dict[str, Any]]:
    data = load_json(TOPIC_MAP)
    rules = []
    for order, topic in enumerate(data.get("topics", [])):
        rules.append({
            "order": order,
            "id": topic.get("id"),
            "topic": topic.get("label_he"),
            "category": topic.get("category", "unknown"),
            "keywords": [str(k).strip() for k in topic.get("keywords", []) if str(k).strip()],
        })
    return rules


def confidence_label(score: int) -> str:
    if score >= 95:
        return "high"
    if score >= 80:
        return "medium"
    return "low"


def existing_topics(record: Dict[str, Any]) -> set[str]:
    values = record.get("topics")
    if not isinstance(values, list):
        return set()
    return {str(v) for v in values if v and v != "unknown"}


def review_record(record: Dict[str, Any], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    fields = record_fields(record)
    suggestions = []
    already = existing_topics(record)

    for rule in rules:
        best = None
        for keyword in rule["keywords"]:
            nk = normalize(keyword)
            if not nk:
                continue
            for field, text in fields.items():
                if nk and nk in text:
                    score = FIELD_WEIGHTS.get(field, 60)
                    candidate = {
                        "topic": rule["topic"],
                        "category": rule["category"],
                        "keyword": keyword,
                        "matched_field": field,
                        "confidence": score,
                        "confidence_label": confidence_label(score),
                        "already_has_topic": rule["topic"] in already,
                    }
                    if best is None or candidate["confidence"] > best["confidence"]:
                        best = candidate
        if best is not None:
            suggestions.append(best)

    suggestions.sort(key=lambda x: (-x["confidence"], x["topic"]))
    return suggestions


def pick_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id"),
        "title": record.get("title"),
        "display_title_clean": record.get("display_title_clean"),
        "grade": record.get("grade"),
        "category": record.get("primary_category"),
        "topics": record.get("topics"),
        "document_type": record.get("document_type"),
        "path": record.get("path"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smart explainable topic review for maagar metadata.")
    parser.add_argument("--report", default="reports/smart-topic-review.json")
    parser.add_argument("--min-confidence", type=int, default=65)
    args = parser.parse_args()

    index = load_json(INDEX)
    rules = load_topic_rules()
    files: List[Dict[str, Any]] = index.get("files", [])

    rows = []
    confidence_counter = Counter()
    topic_counter = Counter()
    field_counter = Counter()
    needs_topic_update = 0
    needs_category_update = 0

    for record in files:
        suggestions = [s for s in review_record(record, rules) if s["confidence"] >= args.min_confidence]
        if not suggestions:
            continue
        top = suggestions[0]
        current_category = record.get("primary_category")
        current_topics = existing_topics(record)
        topic_missing = top["topic"] not in current_topics
        category_missing = current_category in (None, "", "unknown", "uncategorized") and top.get("category") not in (None, "", "unknown")

        if topic_missing:
            needs_topic_update += 1
        if category_missing:
            needs_category_update += 1

        confidence_counter[top["confidence_label"]] += 1
        topic_counter[top["topic"]] += 1
        field_counter[top["matched_field"]] += 1

        item = pick_record(record)
        item["top_suggestion"] = top
        item["all_suggestions"] = suggestions[:5]
        item["needs_topic_update"] = topic_missing
        item["needs_category_update"] = category_missing
        rows.append(item)

    report = {
        "summary": {
            "total_files": len(files),
            "topic_rules": len(rules),
            "reviewed_matches": len(rows),
            "needs_topic_update": needs_topic_update,
            "needs_category_update": needs_category_update,
            "by_confidence": dict(sorted(confidence_counter.items())),
            "by_matched_field": dict(sorted(field_counter.items())),
            "top_topics": dict(topic_counter.most_common(30)),
        },
        "matches": rows,
    }

    report_path = (REPO / args.report).resolve()
    if not str(report_path).startswith(str(REPO.resolve())):
        raise SystemExit("report path must be inside repository")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("MAAGAR SMART TOPIC REVIEW")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    print(f"Report: {report_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
