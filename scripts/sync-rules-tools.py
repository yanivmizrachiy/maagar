#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync-rules-tools.py

מסנכרן את RULES.md עם הכלים החדשים של נושאים/כותרות.
הכלי לא יוצר דף כללים נוסף; הוא מעדכן רק את RULES.md.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "RULES.md"

BLOCK = """

## נספח כלים פעילים לסידור המאגר

הנספח הזה הוא חלק מ־RULES.md ולכן הוא עדיין בתוך דף הכללים היחיד.

מקורות אמת:
- `metadata/index.json` — הקבצים הפעילים.
- `metadata/topic-map.json` — מפת הנושאים הקנונית.
- `metadata/taxonomy.json` — ערכי סיווג חוקיים.

כלים פעילים:
- `scripts/topic-organizer.py` — סידור topics, שיפור קטגוריה כאשר היא unknown/uncategorized, וסידור רשומות כך שקבצים דומים יופיעו יחד.
- `scripts/validate-topic-map.py` — בדיקת מפת הנושאים.
- `scripts/metadata-audit.py` — דוח איכות metadata.
- `scripts/title-cleaner.py` — יצירת `display_title_clean` לתצוגה בלבד.
- `scripts/patch-site-display-title.py` — הכנת האתר להצגת `display_title_clean`.

שדה תצוגה:
- `display_title_clean` מותר לצורכי תצוגה בלבד.
- אין לשנות שם קובץ פיזי רק כדי לנקות תצוגה.
- אין למחוק את `title` המקורי.

workflow מרכזי:
- `.github/workflows/topic-organizer.yml`
- במצב `apply=true` הוא מריץ סידור topics, ניקוי כותרות תצוגה, patch לאתר, בדיקות ו־commit אם יש שינוי.

כלל עבודה:
- אין למחוק קבצים אמיתיים.
- אין להזיז קבצים פיזיים בשלב סידור topics.
- שינוי נושאים וקטגוריות מבוסס רק על metadata קיים ועל `metadata/topic-map.json`.
""".strip()

START = "\n## נספח כלים פעילים לסידור המאגר\n"


def main() -> int:
    text = RULES.read_text(encoding="utf-8")
    if START in text:
        before = text.split(START, 1)[0].rstrip()
        text = before + "\n" + BLOCK + "\n"
    else:
        text = text.rstrip() + "\n\n" + BLOCK + "\n"
    RULES.write_text(text, encoding="utf-8", newline="\n")
    print("RULES.md synced with active topic/title tools.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
