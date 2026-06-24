#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-workflow-site-checks.py

בודק שה-workflows המרכזיים מגנים על כל קבצי ה-JS של האתר.
הבדיקה מגלה אוטומטית כל assets/*.js, ולכן קובץ JS חדש שלא נכנס ל-CI ייתפס.
בנוסף היא מוודאת שהגנת כפתורים אמיתיים/אין דמו גלוי נשארת מחוברת ל-CI.
הבדיקה לא משנה קבצים.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets"

WORKFLOWS = [
    ".github/workflows/validate.yml",
    ".github/workflows/topic-organizer.yml",
    ".github/workflows/health-check.yml",
    ".github/workflows/auto-metadata-cleanup.yml",
]

CORE_SITE_CHECKS = [
    "python3 scripts/validate-site-shell.py",
    "python3 scripts/validate-site-data-contract.py",
    "python3 scripts/validate-file-links.py",
]

SPECIFIC_WORKFLOW_CHECKS = {
    ".github/workflows/validate.yml": [
        "python3 scripts/validate-real-buttons.py",
    ],
    ".github/workflows/site-button-smoke.yml": [
        "python3 scripts/validate-real-buttons.py",
    ],
}


def site_js_checks() -> list[str]:
    files = sorted(ASSETS.glob("*.js"))
    return [f"node --check assets/{path.name}" for path in files]


def workflow_text(rel: str, errors: list[str]) -> str:
    path = REPO / rel
    if not path.exists():
        errors.append(f"missing workflow: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    errors: list[str] = []
    js_checks = site_js_checks()

    if not js_checks:
        errors.append("no assets/*.js files found")

    for rel in WORKFLOWS:
        text = workflow_text(rel, errors)
        if not text:
            continue
        for needle in js_checks:
            if needle not in text:
                errors.append(f"{rel}: missing {needle}")
        for needle in CORE_SITE_CHECKS:
            if needle not in text:
                errors.append(f"{rel}: missing {needle}")

    for rel, checks in SPECIFIC_WORKFLOW_CHECKS.items():
        text = workflow_text(rel, errors)
        if not text:
            continue
        for needle in checks:
            if needle not in text:
                errors.append(f"{rel}: missing required guard {needle}")

    print("MAAGAR WORKFLOW SITE CHECKS")
    print(f"Workflows checked: {len(WORKFLOWS)}")
    print(f"Discovered JS checks: {len(js_checks)}")
    for check in js_checks:
        print(f"CHECK {check}")
    print(f"Required core checks: {len(CORE_SITE_CHECKS)}")
    print(f"Required workflow-specific guards: {sum(len(v) for v in SPECIFIC_WORKFLOW_CHECKS.values())}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    workflows protect browser JS files and keep the real-action/no-demo guard wired into CI")
    return 0


if __name__ == "__main__":
    sys.exit(main())
