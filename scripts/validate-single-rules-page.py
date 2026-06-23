#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-single-rules-page.py

בדיקה פשוטה: RULES.md קיים ומסמכי הכניסה הראשיים מפנים אליו.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "RULES.md"
ENTRY_DOCS = [REPO / "AGENTS.md", REPO / "README.md"]


def main() -> int:
    errors: list[str] = []

    if not RULES.exists():
        errors.append("RULES.md missing")
    else:
        text = RULES.read_text(encoding="utf-8", errors="ignore")
        if "דף הכללים היחיד" not in text:
            errors.append("RULES.md must state that it is the single rules page")

    for path in ENTRY_DOCS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "RULES.md" not in text:
            errors.append(f"{path.relative_to(REPO)} must reference RULES.md")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    single rules page check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
