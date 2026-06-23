#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-site-shell.py

בדיקת מעטפת לאתר החדש:
- index.html טוען assets/site.css, assets/site.js, assets/site-url-state.js, assets/site-deeplink.js, assets/site-share.js ו-assets/site-view-share.js.
- קבצי CSS/JS קיימים.
- קיימים ה-IDs שה-JS משתמש בהם.
- קיימת טעינת metadata/index.json.
- קיימת שמירת מצב סינון ב-URL.
- קיימת שכבת קישור עומק: ?file=ID.
- קיימת שכבת שיתוף קובץ: העתק קישור ו-WhatsApp.
- קיימת שכבת שיתוף תצוגה נוכחית.

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


def main() -> int:
    errors: list[str] = []

    if not INDEX.exists():
        errors.append("index.html missing")
    if not CSS.exists():
        errors.append("assets/site.css missing")
    if not JS.exists():
        errors.append("assets/site.js missing")
    if not URL_STATE_JS.exists():
        errors.append("assets/site-url-state.js missing")
    if not DEEPLINK_JS.exists():
        errors.append("assets/site-deeplink.js missing")
    if not SHARE_JS.exists():
        errors.append("assets/site-share.js missing")
    if not VIEW_SHARE_JS.exists():
        errors.append("assets/site-view-share.js missing")

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
    css = CSS.read_text(encoding="utf-8", errors="ignore")

    if 'href="assets/site.css"' not in html:
        errors.append("index.html does not load assets/site.css")
    if 'src="assets/site.js"' not in html:
        errors.append("index.html does not load assets/site.js")
    if 'src="assets/site-url-state.js"' not in html:
        errors.append("index.html does not load assets/site-url-state.js")
    if 'src="assets/site-deeplink.js"' not in html:
        errors.append("index.html does not load assets/site-deeplink.js")
    if 'src="assets/site-share.js"' not in html:
        errors.append("index.html does not load assets/site-share.js")
    if 'src="assets/site-view-share.js"' not in html:
        errors.append("index.html does not load assets/site-view-share.js")
    if html.find('src="assets/site-url-state.js"') > html.find('src="assets/site-deeplink.js"'):
        errors.append("site-url-state.js must load before site-deeplink.js")
    if html.find('src="assets/site-deeplink.js"') > html.find('src="assets/site-share.js"'):
        errors.append("site-deeplink.js must load before site-share.js")
    if html.find('src="assets/site-share.js"') > html.find('src="assets/site-view-share.js"'):
        errors.append("site-share.js must load before site-view-share.js")

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

    for css_class in [".file", ".act", ".modal", ".viewer", ".chip"]:
        if css_class not in css:
            errors.append(f"assets/site.css missing class: {css_class}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    standalone site shell, URL state, deep links, file sharing and view sharing are wired correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
