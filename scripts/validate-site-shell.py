#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-site-shell.py

בדיקת מעטפת לאתר החדש:
- index.html טוען assets/site.css ו-assets/site.js.
- קבצי CSS/JS קיימים.
- קיימים ה-IDs שה-JS משתמש בהם.
- קיימת טעינת metadata/index.json.

הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "assets" / "site.css"
JS = REPO / "assets" / "site.js"

REQUIRED_IDS = [
    "q",
    "clear",
    "stats",
    "filters",
    "ttl",
    "meta",
    "app",
    "modal",
    "mt",
    "ms",
    "mo",
    "md",
    "x",
    "viewer",
]

REQUIRED_JS_SNIPPETS = [
    "metadata/index.json",
    "function card(",
    "function open(",
    "download",
    "view.officeapps.live.com",
]


def main() -> int:
    errors: list[str] = []

    if not INDEX.exists():
        errors.append("index.html missing")
    if not CSS.exists():
        errors.append("assets/site.css missing")
    if not JS.exists():
        errors.append("assets/site.js missing")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    html = INDEX.read_text(encoding="utf-8", errors="ignore")
    js = JS.read_text(encoding="utf-8", errors="ignore")
    css = CSS.read_text(encoding="utf-8", errors="ignore")

    if 'href="assets/site.css"' not in html:
        errors.append("index.html does not load assets/site.css")
    if 'src="assets/site.js"' not in html:
        errors.append("index.html does not load assets/site.js")

    for item_id in REQUIRED_IDS:
        if f'id="{item_id}"' not in html:
            errors.append(f"index.html missing id={item_id}")

    for snippet in REQUIRED_JS_SNIPPETS:
        if snippet not in js:
            errors.append(f"assets/site.js missing snippet: {snippet}")

    for css_class in [".file", ".act", ".modal", ".viewer", ".chip"]:
        if css_class not in css:
            errors.append(f"assets/site.css missing class: {css_class}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    standalone site shell is wired correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
