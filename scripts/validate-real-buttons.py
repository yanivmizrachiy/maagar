#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate that site action buttons are protected against fake or duplicate actions."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE_JS = REPO / "assets" / "site.js"
HELP_JS = REPO / "assets" / "site-help.js"

REQUIRED_SITE_SNIPPETS = [
    "data-view",
    "download",
    "target=\"_blank\"",
    "href=\"${esc(u)}\"",
]

REQUIRED_HELP_SNIPPETS = [
    "normalizeActionButtons",
    "setAttribute('type', 'button')",
    "noopener noreferrer",
    "seen.has(key)",
    "a.remove()",
]


def main() -> int:
    errors: list[str] = []
    site = SITE_JS.read_text(encoding="utf-8", errors="ignore") if SITE_JS.exists() else ""
    help_js = HELP_JS.read_text(encoding="utf-8", errors="ignore") if HELP_JS.exists() else ""

    if not site:
        errors.append("assets/site.js missing or empty")
    if not help_js:
        errors.append("assets/site-help.js missing or empty")

    for snippet in REQUIRED_SITE_SNIPPETS:
        if snippet not in site:
            errors.append(f"assets/site.js missing real-button snippet: {snippet}")

    for snippet in REQUIRED_HELP_SNIPPETS:
        if snippet not in help_js:
            errors.append(f"assets/site-help.js missing button guard snippet: {snippet}")

    print("MAAGAR REAL BUTTON VALIDATION")
    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    real action buttons are guarded against missing type, unsafe blank links and duplicate actions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
