#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-workflow-site-checks.py

בודק שה-workflows המרכזיים מגנים על כל קבצי ה-JS של האתר.
הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

WORKFLOWS = [
    ".github/workflows/validate.yml",
    ".github/workflows/topic-organizer.yml",
    ".github/workflows/health-check.yml",
    ".github/workflows/auto-metadata-cleanup.yml",
]

SITE_JS_CHECKS = [
    "node --check assets/site.js",
    "node --check assets/site-url-state.js",
    "node --check assets/site-deeplink.js",
    "node --check assets/site-share.js",
    "node --check assets/site-view-share.js",
]

CORE_SITE_CHECKS = [
    "python3 scripts/validate-site-shell.py",
    "python3 scripts/validate-site-data-contract.py",
    "python3 scripts/validate-file-links.py",
]


def main() -> int:
    errors: list[str] = []

    for rel in WORKFLOWS:
        path = REPO / rel
        if not path.exists():
            errors.append(f"missing workflow: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in SITE_JS_CHECKS:
            if needle not in text:
                errors.append(f"{rel}: missing {needle}")
        for needle in CORE_SITE_CHECKS:
            if needle not in text:
                errors.append(f"{rel}: missing {needle}")

    print("MAAGAR WORKFLOW SITE CHECKS")
    print(f"Workflows checked: {len(WORKFLOWS)}")
    print(f"Required JS checks: {len(SITE_JS_CHECKS)}")
    print(f"Required core checks: {len(CORE_SITE_CHECKS)}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    all workflows protect the browser site files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
