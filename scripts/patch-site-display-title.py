#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch-site-display-title.py

מעדכן את index.html כך שכרטיסי קבצים והמודאל ישתמשו קודם ב-display_title_clean,
ואם אין — ימשיכו להשתמש ב-title הרגיל.

הסקריפט idempotent.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"

REPLACEMENTS = [
    (
        "const title      = h(file.title || 'ללא שם');",
        "const title      = h(file.display_title_clean || file.title || 'ללא שם');",
    ),
    (
        "titleEl.textContent = file.title || 'קובץ';",
        "titleEl.textContent = file.display_title_clean || file.title || 'קובץ';",
    ),
]


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    original = text

    for old, new in REPLACEMENTS:
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f"Expected snippet not found: {old}")
        text = text.replace(old, new, 1)

    if text == original:
        print("No changes needed; display_title_clean is already supported.")
        return 0

    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print("Patched index.html to prefer display_title_clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
