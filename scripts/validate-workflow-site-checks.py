#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-workflow-site-checks.py

Checks that the main GitHub workflow protects the active browser/site layer:
- every assets/*.js file gets a syntax check;
- the site shell, real-button guard, data contract and file links are tested;
- premium teacher navigation, high-school unit navigation and exam classifier are protected through validate-all.

The check does not modify files.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets"
MAIN_WORKFLOW = ".github/workflows/validate.yml"
OPTIONAL_WORKFLOWS = [
    ".github/workflows/site-button-smoke.yml",
    ".github/workflows/topic-organizer.yml",
    ".github/workflows/health-check.yml",
    ".github/workflows/auto-metadata-cleanup.yml",
]

MAIN_REQUIRED_CHECKS = [
    "python3 scripts/validate-site-shell.py",
    "python3 scripts/validate-real-buttons.py",
    "python3 scripts/validate-site-data-contract.py",
    "python3 scripts/validate-file-links.py",
    "bash scripts/validate-all.sh",
]

VALIDATE_ALL_REQUIRED_SNIPPETS = [
    "assets/site-premium-nav.css",
    "assets/site-highschool-units.css",
    "scripts/classify-exams.py",
    "scripts/validate-highschool-units.py",
    "python3 scripts/classify-exams.py",
    "python3 scripts/validate-highschool-units.py",
    "python3 scripts/validate-site-shell.py",
    "python3 scripts/validate-real-buttons.py",
]

SITE_SHELL_REQUIRED_SNIPPETS = [
    "PREMIUM_CSS",
    "SITE_STRUCTURE",
    "TAXONOMY",
    "EXPECTED_HOME_LABELS",
    "EXPECTED_EXAM_NAV",
    "EXPECTED_EXAM_KINDS",
    "validate_structure",
]


def site_js_checks() -> list[str]:
    files = sorted(ASSETS.glob("*.js"))
    return [f"node --check assets/{path.name}" for path in files]


def read(rel: str, errors: list[str], required: bool = True) -> str:
    path = REPO / rel
    if not path.exists():
        if required:
            errors.append(f"missing file: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def require_all(label: str, text: str, needles: list[str], errors: list[str]) -> None:
    for needle in needles:
        if needle not in text:
            errors.append(f"{label}: missing {needle}")


def main() -> int:
    errors: list[str] = []
    js_checks = site_js_checks()
    if not js_checks:
        errors.append("no assets/*.js files found")

    main_workflow = read(MAIN_WORKFLOW, errors)
    validate_all = read("scripts/validate-all.sh", errors)
    site_shell = read("scripts/validate-site-shell.py", errors)

    require_all(MAIN_WORKFLOW, main_workflow, MAIN_REQUIRED_CHECKS + js_checks, errors)
    require_all("scripts/validate-all.sh", validate_all, VALIDATE_ALL_REQUIRED_SNIPPETS, errors)
    require_all("scripts/validate-site-shell.py", site_shell, SITE_SHELL_REQUIRED_SNIPPETS, errors)

    for rel in OPTIONAL_WORKFLOWS:
        text = read(rel, errors, required=False)
        if text and "site-button-smoke" in rel:
            require_all(rel, text, ["python3 scripts/validate-real-buttons.py"], errors)

    print("MAAGAR WORKFLOW SITE CHECKS")
    print(f"Main workflow checked: {MAIN_WORKFLOW}")
    print(f"Discovered JS checks: {len(js_checks)}")
    for check in js_checks:
        print(f"CHECK {check}")
    print(f"Main required checks: {len(MAIN_REQUIRED_CHECKS)}")
    print(f"validate-all required snippets: {len(VALIDATE_ALL_REQUIRED_SNIPPETS)}")
    print(f"site-shell required snippets: {len(SITE_SHELL_REQUIRED_SNIPPETS)}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    workflows protect browser JS files, premium teacher navigation, high-school unit navigation, real actions, metadata navigation and exam classifier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
