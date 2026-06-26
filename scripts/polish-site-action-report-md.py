#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polish generated site-action-report.md labels after generation."""

from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REPLACEMENTS = {
    "modal_file_share_buttons": "שיתוף קובץ מתוך חלון צפייה",
    "file_share_buttons": "שיתוף קובץ מכרטיס",
    "file_deep_links": "קישור עומק לקובץ",
    "url_state_filters": "שמירת חיפוש/סינון בכתובת",
    "core_browser": "דפדפן מאגר בסיסי",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Polish Hebrew labels in site action Markdown report.")
    parser.add_argument("--md", default="reports/site-action-report.md")
    args = parser.parse_args()

    path = (REPO / args.md).resolve()
    if not str(path).startswith(str(REPO.resolve())):
        raise SystemExit("md path must be inside repository")
    if not path.exists():
        raise SystemExit(f"missing markdown report: {path.relative_to(REPO)}")

    text = path.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(f"Polished Markdown report: {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
