#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate that the active site has real actions, smart organization and no visible demo text.

This script checks active website files and active metadata only. It does not scan
RULES.md or docs, because those files may legitimately mention demo/fake as a
prohibition.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
SITE_JS = REPO / "assets" / "site.js"
HELP_JS = REPO / "assets" / "site-help.js"
METADATA = REPO / "metadata" / "index.json"

ACTIVE_SITE_FILES = [
    REPO / "index.html",
    REPO / "assets" / "site.js",
    REPO / "assets" / "site.css",
    REPO / "assets" / "site-url-state.js",
    REPO / "assets" / "site-deeplink.js",
    REPO / "assets" / "site-share.js",
    REPO / "assets" / "site-modal-share.js",
    REPO / "assets" / "site-help.js",
]

REQUIRED_SITE_SNIPPETS = [
    "data-view",
    "downloadable(f)",
    "downloadUrl(f)",
    "downloadName(f)",
    "downloadButton(f)",
    "fast-download",
    "data-download",
    "הורדה מהירה",
    "`./${f.path}`",
]

REQUIRED_SMART_ORGANIZATION_SNIPPETS = [
    "const GO",
    "const CO",
    "const TO",
    "const SORTS",
    "groupLabel(f)",
    "compareFiles",
    "compareGroups",
    "gradeLabel(f)",
    "categoryLabel(f)",
    "typeLabel(f)",
    "data-sort",
    "sortbar",
    "sort-chip",
    "מיון נוח",
    "מיון: שכבה › תחום › נושא",
]

REQUIRED_PERFORMANCE_SNIPPETS = [
    "prepareFiles",
    "enrichFile",
    "renderSoon",
    "S.byId",
    "_search",
    "_smartKey",
    "_groupKey",
]

REQUIRED_HELP_SNIPPETS = [
    "normalizeActionButtons",
    "setAttribute('type', 'button')",
    "noopener noreferrer",
    "aria-disabled",
    "אין קישור פעיל",
    "seen.has(key)",
    "a.remove()",
]

FORBIDDEN_VISIBLE_PATTERNS = [
    re.compile(r"\bdemo\b", re.IGNORECASE),
    re.compile(r"\bdummy\b", re.IGNORECASE),
    re.compile(r"\bmock\b", re.IGNORECASE),
    re.compile(r"\blorem\b", re.IGNORECASE),
    re.compile(r"\bfake\b", re.IGNORECASE),
    re.compile(r"דמו"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for item in value.values():
            out.extend(flatten_strings(item))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_strings(item))
        return out
    if isinstance(value, str):
        return [value.strip()]
    return []


def strip_legitimate_placeholders(text: str) -> str:
    text = re.sub(r'placeholder="[^"]*"', "", text)
    text = re.sub(r"placeholder='[^']*'", "", text)
    return text


def visible_demo_errors(label: str, text: str) -> list[str]:
    cleaned = strip_legitimate_placeholders(text)
    errors: list[str] = []
    for pattern in FORBIDDEN_VISIBLE_PATTERNS:
        for match in pattern.finditer(cleaned):
            start = max(0, match.start() - 45)
            end = min(len(cleaned), match.end() + 45)
            context = " ".join(cleaned[start:end].split())
            errors.append(f"{label} contains forbidden visible text '{match.group(0)}' near: {context}")
    return errors


def validate_metadata(errors: list[str]) -> None:
    if not METADATA.exists():
        errors.append("metadata/index.json missing")
        return
    try:
        data = json.loads(read_text(METADATA))
    except Exception as exc:
        errors.append(f"metadata/index.json invalid JSON: {exc}")
        return

    files = data.get("files")
    if not isinstance(files, list) or not files:
        errors.append("metadata/index.json has no active files")
        return

    if not any(isinstance(item, dict) and item.get("source_type") == "repo-file" and str(item.get("path", "")).startswith("files/") for item in files):
        errors.append("metadata/index.json has no repo-file records under files/")

    if not any(isinstance(item, dict) and item.get("source_type") == "repo-file" and item.get("path") and item.get("file_name") and item.get("download_ready") is True for item in files):
        errors.append("metadata/index.json has no real downloadable repo-file records")

    if not any(isinstance(item, dict) and item.get("grade") in {"7", "8", "9", "high-school"} and item.get("primary_category") for item in files):
        errors.append("metadata/index.json does not contain grade/category data needed for smart organization")

    if not any(isinstance(item, dict) and isinstance(item.get("topics"), list) and [topic for topic in item.get("topics", []) if topic and topic != "unknown"] for item in files):
        errors.append("metadata/index.json does not contain usable topics needed for smart organization")

    metadata_text = "\n".join(flatten_strings(data))
    for value in ("#", "javascript:void(0)", "demo"):
        if value in metadata_text:
            errors.append(f"metadata/index.json contains forbidden value: {value}")
    errors.extend(visible_demo_errors("metadata/index.json", metadata_text))


def main() -> int:
    errors: list[str] = []
    site = read_text(SITE_JS)
    help_js = read_text(HELP_JS)

    if not site:
        errors.append("assets/site.js missing or empty")
    if not help_js:
        errors.append("assets/site-help.js missing or empty")

    for snippet in REQUIRED_SITE_SNIPPETS:
        if snippet not in site:
            errors.append(f"assets/site.js missing real action snippet: {snippet}")

    for snippet in REQUIRED_SMART_ORGANIZATION_SNIPPETS:
        if snippet not in site:
            errors.append(f"assets/site.js missing smart organization snippet: {snippet}")

    for snippet in REQUIRED_PERFORMANCE_SNIPPETS:
        if snippet not in site:
            errors.append(f"assets/site.js missing performance snippet: {snippet}")

    for snippet in REQUIRED_HELP_SNIPPETS:
        if snippet not in help_js:
            errors.append(f"assets/site-help.js missing button guard snippet: {snippet}")

    for path in ACTIVE_SITE_FILES:
        if not path.exists():
            errors.append(f"{path.relative_to(REPO)} missing")
            continue
        errors.extend(visible_demo_errors(str(path.relative_to(REPO)), read_text(path)))

    validate_metadata(errors)

    print("MAAGAR REAL ACTION, SMART SORTING, PERFORMANCE AND VISIBLE DEMO VALIDATION")
    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    active site has real actions, convenient sorting, precomputed search keys and no visible demo/fake/mock/dummy/lorem text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
