#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "metadata" / "index.json"
VALID = {"3-unit", "4-unit", "5-unit", "unknown"}


def is_high_school(item):
    return item.get("school_stage") == "high-school" or item.get("grade") == "high-school" or "high-school" in item.get("grades", []) or "files/high-school/" in str(item.get("path", ""))


def main():
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    files = data.get("files", [])
    items = [item for item in files if is_high_school(item)]
    counts = {"3-unit": 0, "4-unit": 0, "5-unit": 0, "unknown": 0}
    print("MAAGAR HIGH SCHOOL UNIT AUDIT")
    print(f"high-school records: {len(items)}")
    bad = []
    unknown = []
    for item in items:
        unit = item.get("unit_level", "unknown")
        if unit not in VALID:
            bad.append(item)
        else:
            counts[unit] += 1
        if unit == "unknown":
            unknown.append(item)
        print(f"- {item.get('id','')} | unit={unit} | {item.get('title','')} | {item.get('path','')}")
    print("summary:")
    for unit in ["3-unit", "4-unit", "5-unit", "unknown"]:
        print(f"  {unit}: {counts[unit]}")
    if bad:
        print("FAIL invalid unit_level values:")
        for item in bad:
            print(f"  {item.get('id','')} -> {item.get('unit_level')}")
        return 1
    if unknown:
        print("WARN unknown unit_level records:")
        for item in unknown:
            print(f"  {item.get('id','')} | {item.get('title','')} | {item.get('path','')}")
        return 2
    print("OK all high-school records have a concrete unit_level")
    return 0


if __name__ == "__main__":
    sys.exit(main())
