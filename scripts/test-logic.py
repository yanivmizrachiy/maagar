#!/usr/bin/env python3
"""
test-logic.py
Simulates the website's JavaScript filtering logic in Python.
Verifies every navigation path, detects orphaned files, checks counts,
and produces a full QA report.

Usage:  python3 scripts/test-logic.py
Run from the repo root.
Exit 0 = all checks passed.  Exit 1 = failures found.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent

def load(path):
    with open(REPO / path, encoding='utf-8') as f:
        return json.load(f)

index     = load('metadata/index.json')
taxonomy  = load('metadata/taxonomy.json')
structure = load('metadata/site-structure.json')

files = index['files']
errors   = []
warnings = []

# ── helpers matching index.html JS logic ─────────────────────

def grade_match(f, grade):
    return f.get('grade') == grade or grade in (f.get('grades') or [])

def files_for_grade_cat(grade, category):
    def match(f):
        if not grade_match(f, grade):
            return False
        if category == 'uncategorized':
            return f.get('primary_category') in ('uncategorized', 'unknown')
        return f.get('primary_category') == category
    return [f for f in files if match(f)]

def files_for_unit(unit_level):
    return [f for f in files
            if f.get('school_stage') == 'high-school'
            and f.get('unit_level') == unit_level]

def count_for_grade(grade):
    return sum(1 for f in files if grade_match(f, grade))

# ── SECTION 1: Navigation path coverage ─────────────────────

print("═" * 52)
print(" MAAGAR — Logic Test Suite")
print("═" * 52)
print()

GRADES     = ['7', '8', '9']
CATEGORIES = ['algebra', 'geometry', 'summaries', 'exams', 'uncategorized']
UNIT_LEVELS = ['3-unit', '4-unit', '5-unit']

# Track which files appear in at least one navigation path
reached_ids = set()

print("── Navigation paths (middle school) ──────────────")
for grade in GRADES:
    total = count_for_grade(grade)
    grade_reached = set()
    print(f"\n  שכבת {'ז' if grade=='7' else 'ח' if grade=='8' else 'ט'}׳ (grade {grade})  — home count: {total}")
    for cat in CATEGORIES:
        cat_files = files_for_grade_cat(grade, cat)
        if cat_files or cat != 'uncategorized':
            label = {'algebra':'אלגברה','geometry':'גיאומטריה',
                     'summaries':'משימות מסכמות','exams':'מבחנים',
                     'uncategorized':'חומרים שונים'}.get(cat, cat)
            status = f"{len(cat_files)} קבצים" if cat_files else "ריק"
            # Only show uncategorized if non-empty (matches site behavior)
            if cat == 'uncategorized' and not cat_files:
                continue
            print(f"    {label:20s} → {status}")
            for f in cat_files:
                print(f"      ✓ {f['id'][:50]}")
                grade_reached.add(f['id'])
                reached_ids.add(f['id'])

    # Check for files counted on home but not reachable in any category
    grade_files_all = [f for f in files if grade_match(f, grade)]
    unreachable = [f for f in grade_files_all if f['id'] not in grade_reached]
    if unreachable:
        for f in unreachable:
            errors.append(
                f"ORPHAN: file '{f['id']}' appears in grade-{grade} home count "
                f"but is unreachable (primary_category='{f.get('primary_category')}')"
            )

print("\n── Navigation paths (high school) ────────────────")
for ul in UNIT_LEVELS:
    ul_files = files_for_unit(ul)
    label = {'3-unit':'שלוש יחידות','4-unit':'ארבע יחידות','5-unit':'חמש יחידות'}.get(ul, ul)
    status = f"{len(ul_files)} קבצים" if ul_files else "ריק"
    print(f"  {label:20s} → {status}")
    for f in ul_files:
        print(f"    ✓ {f['id'][:50]}")
        reached_ids.add(f['id'])

# ── SECTION 2: Orphaned files check ─────────────────────────

print("\n── Orphaned files check ──────────────────────────")
all_ids = {f['id'] for f in files}
truly_orphaned = all_ids - reached_ids

# Files with school_stage=unknown are also genuinely unreachable
for fid in truly_orphaned:
    f = next(x for x in files if x['id'] == fid)
    if f.get('school_stage') == 'high-school':
        errors.append(f"ORPHAN(HS): '{fid}' — high-school file not reached by any unit-level path")
    elif f.get('school_stage') == 'middle-school':
        errors.append(f"ORPHAN(MS): '{fid}' — middle-school file not reached by any grade+category path")
    else:
        warnings.append(f"UNRESOLVED: '{fid}' — school_stage='{f.get('school_stage')}', not navigable")

if not truly_orphaned:
    print("  ✓ All files reachable via navigation")
else:
    for oid in truly_orphaned:
        print(f"  ✗ UNREACHABLE: {oid}")

# ── SECTION 3: Home count accuracy ──────────────────────────

print("\n── Home button count accuracy ────────────────────")
for btn in structure['home']['buttons']:
    bid = btn['id']
    if bid == 'high-school':
        actual = sum(1 for f in files if f.get('school_stage') == 'high-school')
    else:
        actual = count_for_grade(btn['grade'])
    print(f"  {btn['label']:30s} → {actual} קבצים")

# ── SECTION 4: Category card presence ───────────────────────

print("\n── Category cards defined in site-structure ──────")
required_cats = {'algebra', 'geometry', 'summaries', 'exams'}
present_cats  = set(structure.get('category_cards', {}).keys())
for cat in required_cats:
    status = '✓' if cat in present_cats else '✗ MISSING'
    print(f"  {status}  {cat}")
    if cat not in present_cats:
        errors.append(f"MISSING category_card: '{cat}' not in site-structure.json")

# ── SECTION 5: can_embed audit ───────────────────────────────

print("\n── can_embed status audit ────────────────────────")
for f in files:
    ce = f.get('can_embed')
    src = f.get('source_type')
    ext = f.get('extension', '')
    note = ''
    if ce == 'unknown' and src == 'repo-file' and ext == 'pdf':
        note = '← needs real browser test to confirm'
    print(f"  {f['id'][:45]:45s}  can_embed={ce}  {note}")

# ── SUMMARY ──────────────────────────────────────────────────

print()
print("═" * 52)
print(f"  Files total   : {len(files)}")
print(f"  Files reached : {len(reached_ids)}")
print(f"  Errors        : {len(errors)}")
print(f"  Warnings      : {len(warnings)}")
print("═" * 52)

if errors:
    print("\nERRORS:")
    for e in errors:
        print(f"  ✗ {e}")

if warnings:
    print("\nWARNINGS:")
    for w in warnings:
        print(f"  ⚠ {w}")

if not errors:
    print("\n  ✓ ALL LOGIC CHECKS PASSED")
    sys.exit(0)
else:
    print("\n  ✗ LOGIC CHECKS FAILED")
    sys.exit(1)
