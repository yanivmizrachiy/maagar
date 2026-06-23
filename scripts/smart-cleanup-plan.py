#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart-cleanup-plan.py

מייצר תוכנית עבודה חכמה מתוך metadata והדוחות הקיימים:
- תיקוני topic בעדיפות גבוהה.
- תיקוני category כאשר אפשר להסיק אותם מ-topic-map.
- כותרות תצוגה שכדאי לנקות.
- קבצים כבדים שדורשים החלטה.
- אזורי unknown לפי שכבה/קטגוריה.

הסקריפט לא משנה metadata ולא מוחק כלום.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
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


def fields(record: Dict[str, Any]) -> Dict[str, str]:
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
    result = []
    for order, topic in enumerate(data.get("topics", [])):
        result.append({
            "order": order,
            "id": topic.get("id"),
            "topic": topic.get("label_he"),
            "category": topic.get("category", "unknown"),
            "keywords": [str(k).strip() for k in topic.get("keywords", []) if str(k).strip()],
        })
    return result


def match_best(record: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any] | None:
    flds = fields(record)
    best = None
    existing = set(str(t) for t in record.get("topics", []) if t and t != "unknown") if isinstance(record.get("topics"), list) else set()

    for rule in rules:
        for keyword in rule["keywords"]:
            nk = normalize(keyword)
            if not nk:
                continue
            for field, value in flds.items():
                if nk in value:
                    score = FIELD_WEIGHTS.get(field, 60)
                    item = {
                        "topic": rule["topic"],
                        "category": rule["category"],
                        "keyword": keyword,
                        "matched_field": field,
                        "confidence": score,
                        "topic_missing": rule["topic"] not in existing,
                    }
                    if best is None or item["confidence"] > best["confidence"]:
                        best = item
    return best


def file_size_mb(record: Dict[str, Any]) -> float | None:
    path = record.get("path")
    if not path:
        return None
    full = REPO / path
    if not full.exists() or not full.is_file():
        return None
    return round(full.stat().st_size / 1024 / 1024, 2)


def messy_title(record: Dict[str, Any]) -> bool:
    title = str(record.get("title") or "")
    if not title:
        return True
    if record.get("display_title_clean"):
        return False
    if "_" in title or "  " in title:
        return True
    if re.search(r"\.(pdf|docx?|pptx?)$", title, re.IGNORECASE):
        return True
    return False


def short_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record.get("id"),
        "title": record.get("title"),
        "grade": record.get("grade"),
        "category": record.get("primary_category"),
        "topics": record.get("topics"),
        "path": record.get("path"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate smart cleanup plan for maagar.")
    parser.add_argument("--json", default="reports/smart-cleanup-plan.json")
    parser.add_argument("--md", default="reports/smart-cleanup-plan.md")
    args = parser.parse_args()

    index = load_json(INDEX)
    files: List[Dict[str, Any]] = index.get("files", [])
    rules = load_topic_rules()

    high_conf_topic = []
    medium_conf_topic = []
    category_fixes = []
    title_fixes = []
    large_files = []
    unknown_by_bucket: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()
    field_counter: Counter[str] = Counter()

    for record in files:
        best = match_best(record, rules)
        if best:
            topic_counter[best["topic"]] += 1
            field_counter[best["matched_field"]] += 1
            item = short_record(record)
            item["suggestion"] = best
            if best["topic_missing"] and best["confidence"] >= 95:
                high_conf_topic.append(item)
            elif best["topic_missing"] and best["confidence"] >= 78:
                medium_conf_topic.append(item)
            if record.get("primary_category") in (None, "", "unknown", "uncategorized") and best.get("category") not in (None, "", "unknown"):
                cat_item = short_record(record)
                cat_item["suggested_category"] = best["category"]
                cat_item["because_topic"] = best["topic"]
                cat_item["confidence"] = best["confidence"]
                category_fixes.append(cat_item)

        if messy_title(record):
            title_fixes.append(short_record(record))

        size = file_size_mb(record)
        if size is not None and size >= 10:
            lf = short_record(record)
            lf["size_mb"] = size
            large_files.append(lf)

        topics = record.get("topics")
        if not isinstance(topics, list) or not topics or all(t == "unknown" for t in topics):
            key = f"grade={record.get('grade','unknown')} | category={record.get('primary_category','unknown')}"
            unknown_by_bucket[key] += 1

    plan = {
        "summary": {
            "total_files": len(files),
            "topic_rules": len(rules),
            "high_conf_topic_fixes": len(high_conf_topic),
            "medium_conf_topic_fixes": len(medium_conf_topic),
            "category_fixes": len(category_fixes),
            "title_fixes": len(title_fixes),
            "large_files_10mb_plus": len(large_files),
            "unknown_buckets": len(unknown_by_bucket),
            "top_suggested_topics": dict(topic_counter.most_common(20)),
            "top_matched_fields": dict(field_counter.most_common()),
        },
        "priority_1_high_conf_topic_fixes": high_conf_topic[:100],
        "priority_2_category_fixes": category_fixes[:100],
        "priority_3_title_fixes": title_fixes[:100],
        "priority_4_large_files": sorted(large_files, key=lambda x: x["size_mb"], reverse=True),
        "unknown_topic_buckets": dict(unknown_by_bucket.most_common()),
    }

    json_path = (REPO / args.json).resolve()
    md_path = (REPO / args.md).resolve()
    for path in (json_path, md_path):
        if not str(path).startswith(str(REPO.resolve())):
            raise SystemExit("report path must be inside repository")
        path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Smart Cleanup Plan — maagar")
    lines.append("")
    lines.append("דוח עבודה בלבד. הכללים נשארים רק ב-RULES.md.")
    lines.append("")
    lines.append("## Summary")
    for key, value in plan["summary"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Priority 1 — high confidence topic fixes")
    for item in high_conf_topic[:30]:
        s = item["suggestion"]
        lines.append(f"- `{item['id']}` — {item.get('title','')} → **{s['topic']}** ({s['confidence']}, {s['matched_field']}: `{s['keyword']}`)")
    lines.append("")
    lines.append("## Priority 2 — category fixes")
    for item in category_fixes[:30]:
        lines.append(f"- `{item['id']}` — {item.get('title','')} → **{item['suggested_category']}** בגלל {item['because_topic']}")
    lines.append("")
    lines.append("## Priority 3 — title display cleanup")
    for item in title_fixes[:30]:
        lines.append(f"- `{item['id']}` — {item.get('title','')}")
    lines.append("")
    lines.append("## Priority 4 — large files")
    for item in sorted(large_files, key=lambda x: x["size_mb"], reverse=True)[:30]:
        lines.append(f"- `{item['id']}` — {item.get('title','')} — {item['size_mb']}MB")
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("MAAGAR SMART CLEANUP PLAN")
    for key, value in plan["summary"].items():
        print(f"{key}: {value}")
    print(f"JSON: {json_path.relative_to(REPO)}")
    print(f"MD: {md_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
