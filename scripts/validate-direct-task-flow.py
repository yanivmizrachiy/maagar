#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guard the direct task-list navigation contract.

The active product flow is:
בית → שכבה → תחום → רשימת משימות/קבצים → split viewer.

Topics remain metadata, tags and search/filter data. They must not be a required
screen between a domain and the file list.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES = REPO / "RULES.md"
README = REPO / "README.md"
INDEX = REPO / "index.html"
DIRECT_JS = REPO / "assets" / "site-direct-tasks.js"
DIRECT_CSS = REPO / "assets" / "site-direct-tasks.css"
RESPONSIVE_SPEC = REPO / "tests" / "site-responsive.spec.js"
ACCESSIBILITY_SPEC = REPO / "tests" / "site-accessibility.spec.js"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def require(text: str, snippet: str, label: str, errors: list[str]) -> None:
    if snippet not in text:
        errors.append(f"{label} missing required direct-flow snippet: {snippet}")


def forbid(text: str, snippet: str, label: str, errors: list[str]) -> None:
    if snippet in text:
        errors.append(f"{label} still contains old required topic-drill snippet: {snippet}")


def main() -> int:
    errors: list[str] = []
    rules = read(RULES)
    readme = read(README)
    index = read(INDEX)
    direct_js = read(DIRECT_JS)
    direct_css = read(DIRECT_CSS)
    responsive = read(RESPONSIVE_SPEC)
    accessibility = read(ACCESSIBILITY_SPEC)

    for path in [RULES, README, INDEX, DIRECT_JS, DIRECT_CSS, RESPONSIVE_SPEC, ACCESSIBILITY_SPEC]:
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(REPO)}")

    require(rules, "בית → שכבה → תחום → רשימת משימות/קבצים", "RULES.md", errors)
    require(rules, "אין שלב נושא חובה", "RULES.md", errors)
    require(rules, "`topics`", "RULES.md", errors)
    require(readme, "רשימת קבצים ישירה", "README.md", errors)
    require(index, 'href="assets/site-direct-tasks.css"', "index.html", errors)
    require(index, 'src="assets/site-direct-tasks.js"', "index.html", errors)
    require(index, 'aria-labelledby="mt"', "index.html", errors)
    require(index, 'aria-describedby="ms"', "index.html", errors)
    require(direct_js, "split-view", "assets/site-direct-tasks.js", errors)
    require(direct_js, "details", "assets/site-direct-tasks.js", errors)
    require(direct_js, "S.topic = ''", "assets/site-direct-tasks.js", errors)
    require(direct_js, "task-title", "assets/site-direct-tasks.js", errors)
    require(direct_css, ".split-view", "assets/site-direct-tasks.css", errors)
    require(direct_css, ".detail-panel", "assets/site-direct-tasks.css", errors)
    require(responsive, "Direct flow: grade -> domain -> files + split viewer", "tests/site-responsive.spec.js", errors)
    require(accessibility, "Direct flow: home shows grade cards", "tests/site-accessibility.spec.js", errors)

    forbid(responsive, "grade -> domain -> topic", "tests/site-responsive.spec.js", errors)
    forbid(accessibility, "grade -> domain -> topic", "tests/site-accessibility.spec.js", errors)
    forbid(responsive, "await page.locator('.topic-chip').first().click()", "tests/site-responsive.spec.js", errors)
    forbid(accessibility, "await page.locator('.topic-chip').first().click()", "tests/site-accessibility.spec.js", errors)

    print("MAAGAR DIRECT TASK FLOW VALIDATION")
    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1
    print("OK    direct domain task list and split viewer contract are protected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
