#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECKS = {
    "index.html": ["assets/site-highschool-units.css"],
    "assets/site.js": ["const UNIT_BUTTONS", "unitButton", "highSchoolHub", "data-unit", "unit_level", "unitKey", "unitLabel"],
    "assets/site-url-state.js": ["u: 'unit'", "cleanUnit", "activeUnit", "clickUnit", "data-unit"],
    "assets/site-highschool-units.css": ["High school unit navigation", ".unit-hub", ".unitbar", ".unit-chip"],
    "metadata/taxonomy.json": ["3-unit", "4-unit", "5-unit"],
    "metadata/site-structure.json": ["high_school_home", "3-unit", "4-unit", "5-unit"],
}

errors = []
for rel, snippets in CHECKS.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing: {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{rel} missing: {snippet}")

print("MAAGAR HIGH SCHOOL UNIT NAVIGATION VALIDATION")
if errors:
    for err in errors:
        print("FAIL ", err)
    sys.exit(1)
print("OK    high school 3/4/5 unit navigation is wired and documented in metadata")
