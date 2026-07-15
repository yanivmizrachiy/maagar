#!/usr/bin/env python3
"""Apply verified neutral metadata credits for unresolved grade 7-8 materials.

Each name comes from the exact PDF metadata and was reviewed together with the
rendered first page. These remain neutral credits because the page itself does
not explicitly label the person as author or editor.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "metadata" / "index.json"

CREDIT_BY_ID = {
    "7__algebra__חוקיות-לכיתה-ז___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__חוקיות__worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__מאגר-המשוואות-1___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__מאגר-המשוואות-2___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__מכינה-לכיתה-ז___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__מספרים-מכוונים-ז___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__משוואות-עם-מכנה-מספרי-1__worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__משוואות-עם-מכנה-מספרי-2___worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__משוואות__worksheet__unknown__002": "יניב מזרחי",
    "7__algebra__סדר-פעולות-במספרים-מכוונים__worksheet__unknown__002": "יניב מזרחי",
    "7__algebra__סדר-פעולות-החשבון-עם-מספרים-מכוונים__worksheet__unknown__001": "יניב מזרחי",
    "7__algebra__סדר-פעולות-חשבון-ללא-מספרים-מכוונים__worksheet__unknown__001": "יניב מזרחי",
    "7__exams__מבחן-ז-מדעית__exam__unknown__001": "יניב מזרחי",
    "7__geometry__גובה-במשולש__worksheet__unknown__002": "יניב מזרחי",
    "7__geometry__זוויות-בין-ישרים-מקבילים__worksheet__unknown__001": "יניב מזרחי",
    "7__geometry__מעגל-ועיגול__worksheet__unknown__001": "יניב מזרחי",
    "7__geometry__שטח-הפנים-של-תיבה__worksheet__unknown__002": "יניב מזרחי",
    "7__geometry__שטח-של-מקבילית__worksheet__unknown__002": "יניב מזרחי",
    "7__geometry__שטח-של-משולש__worksheet__unknown__003": "יניב מזרחי",
    "7__geometry__שטחים-במערכת-הצירים__worksheet__unknown__001": "רותם מזרחי",
    "7__geometry__שטחים-והיקפים-צורות-מורכבות__worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__maagar-z__unknown__001": "יניב מזרחי",
    "7__uncategorized__yfx__worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__הצבה-לכתה-ז___worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__זוויות-לחטיבת-ביניים__worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__זוויות-קודקודיות__worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__מלבן-לכיתה-ז___worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__נפח-של-תיבה-וקוביה___worksheet__unknown__001": "יניב מזרחי",
    "7__uncategorized__סכום-זויות-צמודות-180__worksheet__unknown__001": "יניב מזרחי",
    "8__algebra__02_grade-8_algebra_curriculum__mixed__unknown__001": "גנאדי ארנוביץ",
    "8__algebra__אחוזים-לחטיבת-הביניים__worksheet__unknown__002": "רותם מזרחי",
    "8__algebra__חיתוך-2-פונקציות__worksheet__unknown__001": "יניב מזרחי",
}

UNKNOWN = {None, "", "unknown", "לא ידוע"}


def main() -> int:
    payload = json.loads(INDEX.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload["files"]}

    missing = sorted(set(CREDIT_BY_ID) - set(by_id))
    if missing:
        raise SystemExit(f"Missing material IDs: {missing}")

    for material_id, credit in CREDIT_BY_ID.items():
        item = by_id[material_id]
        current = item.get("credit")
        if current not in UNKNOWN and current != credit:
            raise SystemExit(
                f"Refusing to overwrite credit for {material_id}: {current!r} -> {credit!r}"
            )
        item["credit"] = credit

    INDEX.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Applied {len(CREDIT_BY_ID)} neutral credits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
