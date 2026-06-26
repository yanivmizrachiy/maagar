#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-site-action-report.py

Validates that reports/site-action-report.json includes the required browser feature coverage fields.
This script does not modify repository files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent

REQUIRED_FEATURES = [
    "core_browser",
    "url_state_filters",
    "file_deep_links",
    "file_share_buttons",
    "modal_file_share_buttons",
    "premium_teacher_navigation_css",
    "high_school_unit_navigation_css",
]

REQUIRED_SUMMARY_FLAGS = [
    "modal_file_share_available",
    "url_state_share_available",
    "deep_link_share_available",
    "premium_teacher_navigation_available",
    "high_school_unit_navigation_available",
]

REQUIRED_DISTRIBUTIONS = [
    "by_extension",
    "by_grade",
    "by_category",
    "by_unit_level",
    "high_school_by_unit_level",
]

REQUIRED_UNIT_KEYS = ["3-unit", "4-unit", "5-unit", "unknown"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated site action report.")
    parser.add_argument("--report", default="reports/site-action-report.json")
    args = parser.parse_args()

    report_path = (REPO / args.report).resolve()
    if not str(report_path).startswith(str(REPO.resolve())):
        raise SystemExit("report path must be inside repository")
    if not report_path.exists():
        raise SystemExit(f"missing report: {report_path.relative_to(REPO)}")

    data: Dict[str, Any] = json.loads(report_path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    features = data.get("browser_features", {})

    errors: list[str] = []

    for key in REQUIRED_FEATURES:
        item = features.get(key)
        if not isinstance(item, dict):
            errors.append(f"missing browser feature: {key}")
            continue
        if not item.get("exists"):
            errors.append(f"feature file missing: {key}")
        if not item.get("loaded_in_index"):
            errors.append(f"feature not loaded in index: {key}")
        if not item.get("required_snippets_present"):
            errors.append(f"feature snippets missing: {key}: {item.get('missing_snippets')}")

    for key in REQUIRED_SUMMARY_FLAGS:
        if key not in summary:
            errors.append(f"summary flag missing: {key}")

    for key in REQUIRED_DISTRIBUTIONS:
        if not isinstance(summary.get(key), dict):
            errors.append(f"summary distribution missing or invalid: {key}")

    unit_distribution = summary.get("by_unit_level") if isinstance(summary.get("by_unit_level"), dict) else {}
    for key in REQUIRED_UNIT_KEYS:
        if key not in unit_distribution:
            errors.append(f"by_unit_level missing unit key: {key}")

    high_school_distribution = summary.get("high_school_by_unit_level") if isinstance(summary.get("high_school_by_unit_level"), dict) else {}
    for key in REQUIRED_UNIT_KEYS:
        if key not in high_school_distribution:
            errors.append(f"high_school_by_unit_level missing unit key: {key}")

    print("MAAGAR SITE ACTION REPORT VALIDATION")
    print(f"Report: {report_path.relative_to(REPO)}")
    print(f"Features checked: {len(REQUIRED_FEATURES)}")
    print(f"Summary flags checked: {len(REQUIRED_SUMMARY_FLAGS)}")
    print(f"Distributions checked: {len(REQUIRED_DISTRIBUTIONS)}")

    if errors:
        for err in errors:
            print(f"FAIL  {err}")
        return 1

    print("OK    site action report includes browser, premium navigation, high school unit and distribution coverage fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
