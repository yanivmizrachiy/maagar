#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-single-rules-page.py

בודק ש-RULES.md הוא דף הכללים היחיד.
הבדיקה לא מונעת שימוש במילים רגילות, אלא מחפשת ניסוחים שמצהירים על מקור כללים חלופי.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "RULES.md"

FORBIDDEN_PATTERNS = [
    re.compile(r"source\s+of\s+truth", re.IGNORECASE),
    re.compile(r"דף\s+הכללים", re.IGNORECASE),
    re.compile(r"מקור\s+האמת\s+של\s+הכללים", re.IGNORECASE),
    re.compile(r"כללים\s+מחייבים", re.IGNORECASE),
]

SKIP_DIRS = {".git", "files", "node_modules", "__pycache__"}
SCAN_EXTS = {".md", ".txt"}


def main() -> int:
    errors = []

    if not RULES.exists():
        print("FAIL  RULES.md missing")
        return 1

    rules_text = RULES.read_text(encoding="utf-8", errors="ignore")
    if "דף הכללים היחיד" not in rules_text:
        errors.append("RULES.md must explicitly say it is the single rules page")

    for dirpath, dirnames, filenames in __import__("os").walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            path = Path(dirpath) / fname
            if path == RULES:
                continue
            if path.suffix.lower() not in SCAN_EXTS:
                continue
            rel = path.relative_to(REPO)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{rel}: looks like an alternative rules source ({pattern.pattern})")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    RULES.md is the only rules source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
