#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-site-shell.py

בדיקת מעטפת לאתר החדש:
- index.html טוען assets/site.css ואת כל קבצי ה-JS של האתר.
- קבצי CSS/JS קיימים.
- קיימים ה-IDs שה-JS משתמש בהם.
- קיימת טעינת metadata/index.json.
- קיימת שמירת מצב סינון ב-URL.
- קיימת שכבת קישור עומק: ?file=ID.
- קיימת שכבת שיתוף קובץ מכרטיס.
- קיימת שכבת שיתוף תצוגה נוכחית.
- קיימת שכבת שיתוף קובץ מתוך חלון הצפייה.
- קיימת שכבת עזרה מהירה למורים.
- קיימות הגדרות התאמה מתקדמות למובייל.

הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "assets" / "site.css"
JS = REPO / "assets" / "site.js"
URL_STATE_JS = REPO / "assets" / "site-url-state.js"
DEEPLINK_JS = REPO / "assets" / "site-deeplink.js"
SHARE_JS = REPO / "assets" / "site-share.js"
VIEW_SHARE_JS = REPO / "assets" / "site-view-share.js"
MODAL_SHARE_JS = REPO / "assets" / "site-modal-share.js"
HELP_JS = REPO / "assets" / "site-help.js"

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

REQUIRED_HTML_SNIPPETS = [
    "viewport-fit=cover",
    'name="theme-color"',
    'name="color-scheme"',
    'apple-mobile-web-app-capable',
    'black-translucent',
]

REQUIRED_JS_SNIPPETS = [
    "metadata/index.json",
    "function card(",
    "function open(",
    "download",
    "view.officeapps.live.com",
]

REQUIRED_URL_STATE_SNIPPETS = [
    "searchParams",
    "grade",
    "category",
    "type",
    "history.replaceState",
    "data-k",
]

REQUIRED_DEEPLINK_SNIPPETS = [
    "searchParams.get('file')",
    "window.maagarFileLink",
    "data-view",
    "scrollIntoView",
]

REQUIRED_SHARE_SNIPPETS = [
    "navigator.clipboard",
    "WhatsApp",
    "https://wa.me/",
    "MutationObserver",
    "העתק קישור",
    "maagarFileLink",
]

REQUIRED_VIEW_SHARE_SNIPPETS = [
    "currentViewLink",
    "copy-view-link",
    "share-view-whatsapp",
    "העתק תצוגה",
    "שתף תצוגה",
    "searchParams.delete('file')",
]

REQUIRED_MODAL_SHARE_SNIPPETS = [
    "currentFileLink",
    "currentFileTitle",
    "copy-modal-file-link",
    "share-modal-file-whatsapp",
    "קישור לקובץ הועתק",
    "https://wa.me/",
]

REQUIRED_HELP_SNIPPETS = [
    "site-help-open",
    "site-help-panel",
    "עזרה מהירה",
    "צפייה מוטמעת",
    "שיתוף תצוגה",
    "help-card",
]

REQUIRED_RESPONSIVE_CSS_SNIPPETS = [
    "safe-area-inset-top",
    "overflow-x:hidden",
    "@media(max-width:920px)",
    "@media(max-width:760px)",
    "@media(max-width:390px)",
    "@media(max-height:620px)",
    "minmax(min(285px,100%),1fr)",
]


def main() -> int:
    errors: list[str] = []

    for path, label in [
        (INDEX, "index.html"),
        (CSS, "assets/site.css"),
        (JS, "assets/site.js"),
        (URL_STATE_JS, "assets/site-url-state.js"),
        (DEEPLINK_JS, "assets/site-deeplink.js"),
        (SHARE_JS, "assets/site-share.js"),
        (VIEW_SHARE_JS, "assets/site-view-share.js"),
        (MODAL_SHARE_JS, "assets/site-modal-share.js"),
        (HELP_JS, "assets/site-help.js"),
    ]:
        if not path.exists():
            errors.append(f"{label} missing")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    html = INDEX.read_text(encoding="utf-8", errors="ignore")
    js = JS.read_text(encoding="utf-8", errors="ignore")
    url_state_js = URL_STATE_JS.read_text(encoding="utf-8", errors="ignore")
    deeplink_js = DEEPLINK_JS.read_text(encoding="utf-8", errors="ignore")
    share_js = SHARE_JS.read_text(encoding="utf-8", errors="ignore")
    view_share_js = VIEW_SHARE_JS.read_text(encoding="utf-8", errors="ignore")
    modal_share_js = MODAL_SHARE_JS.read_text(encoding="utf-8", errors="ignore")
    help_js = HELP_JS.read_text(encoding="utf-8", errors="ignore")
    css = CSS.read_text(encoding="utf-8", errors="ignore")

    script_order = [
        "site.js",
        "site-url-state.js",
        "site-deeplink.js",
        "site-share.js",
        "site-view-share.js",
        "site-modal-share.js",
        "site-help.js",
    ]

    if 'href="assets/site.css"' not in html:
        errors.append("index.html does not load assets/site.css")

    for snippet in REQUIRED_HTML_SNIPPETS:
        if snippet not in html:
            errors.append(f"index.html missing responsive/mobile snippet: {snippet}")

    last_pos = -1
    for script in script_order:
        needle = f'src="assets/{script}"'
        pos = html.find(needle)
        if pos < 0:
            errors.append(f"index.html does not load assets/{script}")
        elif pos < last_pos:
            errors.append(f"assets/{script} is loaded out of order")
        else:
            last_pos = pos

    for item_id in REQUIRED_IDS:
        if f'id="{item_id}"' not in html:
            errors.append(f"index.html missing id={item_id}")

    for snippet in REQUIRED_JS_SNIPPETS:
        if snippet not in js:
            errors.append(f"assets/site.js missing snippet: {snippet}")

    for snippet in REQUIRED_URL_STATE_SNIPPETS:
        if snippet not in url_state_js:
            errors.append(f"assets/site-url-state.js missing snippet: {snippet}")

    for snippet in REQUIRED_DEEPLINK_SNIPPETS:
        if snippet not in deeplink_js:
            errors.append(f"assets/site-deeplink.js missing snippet: {snippet}")

    for snippet in REQUIRED_SHARE_SNIPPETS:
        if snippet not in share_js:
            errors.append(f"assets/site-share.js missing snippet: {snippet}")

    for snippet in REQUIRED_VIEW_SHARE_SNIPPETS:
        if snippet not in view_share_js:
            errors.append(f"assets/site-view-share.js missing snippet: {snippet}")

    for snippet in REQUIRED_MODAL_SHARE_SNIPPETS:
        if snippet not in modal_share_js:
            errors.append(f"assets/site-modal-share.js missing snippet: {snippet}")

    for snippet in REQUIRED_HELP_SNIPPETS:
        if snippet not in help_js:
            errors.append(f"assets/site-help.js missing snippet: {snippet}")

    for css_class in [".file", ".act", ".modal", ".viewer", ".chip"]:
        if css_class not in css:
            errors.append(f"assets/site.css missing class: {css_class}")

    for snippet in REQUIRED_RESPONSIVE_CSS_SNIPPETS:
        if snippet not in css:
            errors.append(f"assets/site.css missing responsive snippet: {snippet}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    standalone site shell, responsive adaptation, URL state, deep links, sharing and teacher help are wired correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
