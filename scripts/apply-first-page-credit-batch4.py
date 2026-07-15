#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "metadata" / "index.json"

AUTHOR_UPDATES = {
    "9__geometry__מקבילית-במערכת-הצירים-1__worksheet__unknown__001": "יניב מזרחי",
    "8__algebra__חוברת-אחוזים__worksheet__unknown__001": "ויקי שמש",
    "8__algebra__יחס__worksheet__unknown__001": "ד״ר יחיאל תנעמי ואיילת קריספין",
}

UNKNOWN = {None, "", "unknown", "לא ידוע"}

payload = json.loads(INDEX.read_text(encoding="utf-8"))
by_id = {item["id"]: item for item in payload["files"]}

missing = sorted(set(AUTHOR_UPDATES) - set(by_id))
if missing:
    raise SystemExit(f"Missing material IDs: {missing}")

for material_id, author in AUTHOR_UPDATES.items():
    item = by_id[material_id]
    current = item.get("author")
    if current not in UNKNOWN and current != author:
        raise SystemExit(
            f"Refusing to overwrite author for {material_id}: {current!r} -> {author!r}"
        )
    item["author"] = author

INDEX.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"Applied {len(AUTHOR_UPDATES)} verified first-page author updates")
