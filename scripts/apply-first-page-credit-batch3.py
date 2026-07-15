#!/usr/bin/env python3
"""Apply the first verified page-1 credit batch to metadata/index.json.

Temporary helper for PR 41. Every mapping below is backed by explicit text on
page 1 of the exact PDF. The script refuses to overwrite an existing real value.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "metadata" / "index.json"
OUTPUT = ROOT / "reports" / "index-with-first-page-credits.json"

AUTHOR_UPDATES = {
    "8__algebra__ratio-proportion-scale-לתלמידים-1-רמה-ב-8-3-0107-2013-2014__unknown__001": "משבצת",
    "8__summaries__grade-8-ratio-proportion-וscale-summary-pages-לתלמידים-1-רמה-א-טופס-8-3-0106-2013-2014__unknown__001": "משבצת",
    "8__geometry__גאומטריה-במערכת-צירים-כיתה-ח___worksheet__unknown__001": "סמיון ויינר",
    "9__geometry__גאומטריה-במערכת-צירים-כיתה-ט___worksheet__unknown__001": "סמיון ויינר",
    "8__geometry__תיכון-במשולש-2__worksheet__unknown__001": "אפשר גם אחרת",
    "8__uncategorized__geometry__worksheet__unknown__001": "משרד החינוך",
    "7__algebra__אלגברה-ז__worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__משוואות-לחטיבה-2__worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__משוואות-לחטיבה-3__worksheet__unknown__001": "יניב מזרחי",
    "9__uncategorized__הוצאת-גורם-משותף-2-2__worksheet__unknown__001": "יניב מזרחי",
    "9__uncategorized__הוצאת-גורם-משותף-2__worksheet__unknown__001": "יניב מזרחי",
}

EDITOR_UPDATES = {
    "9__geometry__יחסי-שטחים__worksheet__unknown__001": "שרית ביטון ושגית רסולי",
}

UNKNOWN = {None, "", "unknown", "לא ידוע"}


def main() -> int:
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    files = payload["files"]
    by_id = {item["id"]: item for item in files}

    expected_ids = set(AUTHOR_UPDATES) | set(EDITOR_UPDATES)
    missing = sorted(expected_ids - set(by_id))
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

    for material_id, editor in EDITOR_UPDATES.items():
        item = by_id[material_id]
        current = item.get("editor")
        if current not in UNKNOWN and current != editor:
            raise SystemExit(
                f"Refusing to overwrite editor for {material_id}: {current!r} -> {editor!r}"
            )
        item["editor"] = editor

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Prepared {len(AUTHOR_UPDATES)} author updates and "
        f"{len(EDITOR_UPDATES)} editor update in {OUTPUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
