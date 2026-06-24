#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify exam_kind in metadata/index.json using existing real text only.

Default mode is dry-run. Use --apply to update metadata.
The script does not invent author/year/topic. It only fills exam_kind when the
existing title, file_name, topics, tags, notes or category gives a clear signal.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "metadata" / "index.json"

EXAM_LABELS = {
    "start": "מבחני תחילת שנה",
    "mid": "מבחני אמצע שנה",
    "end": "מבחני סוף שנה",
    "skill": "מבחני מיומנות",
    "unknown": "לא ידוע",
}

SIGNALS = [
    ("skill", ["מיומנות", "מיומנויות", "skill"]),
    ("end", ["סוף שנה", "סוף", "מסכם", "final", "end"]),
    ("mid", ["אמצע", "מחצית", "mid"]),
    ("start", ["תחילת", "תחילה", "מיפוי", "פתיחה", "start", "diagnostic"]),
]


def text_of(item: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["title", "file_name", "primary_category", "document_type", "notes", "author", "year"]:
        value = item.get(key)
        if isinstance(value, str):
            parts.append(value)
    for key in ["topics", "tags"]:
        value = item.get(key)
        if isinstance(value, list):
            parts.extend(str(x) for x in value if x)
    return " ".join(parts).lower()


def looks_like_exam(item: dict[str, Any]) -> bool:
    text = text_of(item)
    return (
        item.get("primary_category") == "exams"
        or item.get("document_type") == "exam"
        or "מבחן" in text
        or "מבחני" in text
        or "בוחן" in text
        or "מיפוי" in text
        or "מיומנות" in text
        or "מחצית" in text
    )


def classify(item: dict[str, Any]) -> str:
    if not looks_like_exam(item):
        return "unknown"
    text = text_of(item)
    for kind, words in SIGNALS:
        if any(word.lower() in text for word in words):
            return kind
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="update metadata/index.json")
    args = parser.parse_args()

    data = json.loads(META.read_text(encoding="utf-8"))
    files = data.get("files", [])
    if not isinstance(files, list):
        raise SystemExit("metadata/index.json: files is not a list")

    changed = 0
    counts = {key: 0 for key in EXAM_LABELS}
    samples: list[str] = []

    for item in files:
        if not isinstance(item, dict):
            continue
        kind = classify(item)
        if looks_like_exam(item):
            counts[kind] = counts.get(kind, 0) + 1
        current = item.get("exam_kind", "unknown")
        if kind != "unknown" and current != kind:
            changed += 1
            samples.append(f"{item.get('id','?')} | {current} -> {kind} | {item.get('title') or item.get('file_name')}")
            if args.apply:
                item["exam_kind"] = kind
                tags = item.get("tags") if isinstance(item.get("tags"), list) else []
                label = EXAM_LABELS[kind]
                if label not in tags:
                    tags.append(label)
                item["tags"] = tags

    print("MAAGAR EXAM CLASSIFIER")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print(f"exam candidates by detected kind: {counts}")
    print(f"metadata changes proposed: {changed}")
    for line in samples[:30]:
        print("CHANGE", line)
    if changed > 30:
        print(f"... {changed - 30} additional changes not shown")

    if args.apply and changed:
        META.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("UPDATED metadata/index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
