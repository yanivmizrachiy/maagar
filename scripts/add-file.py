#!/usr/bin/env python3
"""
add-file.py — Smart file ingestion helper for yanivmizrachiy/maagar.

Usage:
  python3 scripts/add-file.py --help
  python3 scripts/add-file.py \\
      --file /path/to/worksheet.pdf \\
      --grade 8 \\
      --category algebra \\
      --doctype worksheet \\
      --year 2024 \\
      --author "יניב" \\
      --topics "אלגברה,משוואות"

What this script does:
  1. Validates inputs against taxonomy
  2. Computes SHA-1 content hash
  3. Checks for duplicate in metadata/index.json
  4. Determines physical destination path
  5. Copies file to files/<school_stage>/<grade>/<category>/
  6. Generates a metadata record and adds it to metadata/index.json
  7. Runs validate-all.sh + test-logic.py and prints result

What this script does NOT do:
  - It does not invent or fill missing metadata (you must provide --year / --author or accept "unknown")
  - It does not push to git (you do that after reviewing)
  - It does not create fake or demo files

Run from repo root:
  python3 scripts/add-file.py [options]
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent

# ── Taxonomy constants ─────────────────────────────────────────────────────────

VALID_SCHOOL_STAGES = {'middle-school', 'high-school'}

GRADE_TO_STAGE = {
    '7': 'middle-school',
    '8': 'middle-school',
    '9': 'middle-school',
}

HS_UNIT_LEVELS = {'3-unit', '4-unit', '5-unit'}

VALID_CATEGORIES = {
    'algebra', 'geometry', 'summaries', 'exams', 'uncategorized'
}

VALID_DOCTYPES = {
    'worksheet', 'summary-work', 'exam', 'link',
    'digital-task', 'printable-task', 'embedded-resource', 'mixed'
}


def load_taxonomy():
    with open(REPO / 'metadata' / 'taxonomy.json', encoding='utf-8') as f:
        return json.load(f)


def load_index():
    with open(REPO / 'metadata' / 'index.json', encoding='utf-8') as f:
        return json.load(f)


def save_index(data):
    with open(REPO / 'metadata' / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def slugify(text: str) -> str:
    """Convert to filesystem-safe ASCII-ish slug, preserving Hebrew characters."""
    text = text.strip().lower()
    # Replace spaces/slashes/special chars with hyphens
    text = re.sub(r'[\s/\\|]+', '-', text)
    # Remove unsafe characters (keep Hebrew letters, digits, hyphens, dots)
    text = re.sub(r'[^\w֐-׿\-.]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def determine_path(grade: str, unit_level: str, category: str, filename: str) -> Path:
    """Determine where in files/ the PDF should live."""
    if grade in GRADE_TO_STAGE:
        stage = 'middle-school'
        return REPO / 'files' / stage / f'grade-{grade}' / category / filename
    else:
        stage = 'high-school'
        return REPO / 'files' / stage / unit_level / filename


def build_id(grade: str, unit_level: str, category: str, title: str,
             doctype: str, year: str) -> str:
    """Build a deterministic record ID."""
    parts = [
        grade or unit_level or 'unknown',
        category,
        slugify(title)[:50],
        doctype,
        year,
        '001'
    ]
    return '__'.join(p for p in parts if p and p != 'unknown_unknown')


def parse_args():
    p = argparse.ArgumentParser(
        description='Add a real file to yanivmizrachiy/maagar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    p.add_argument('--file',       required=True,  help='Path to the PDF/file to add')
    p.add_argument('--title',                      help='Hebrew title (default: filename without extension)')
    p.add_argument('--grade',                      help='Grade: 7, 8, or 9 (for middle school)')
    p.add_argument('--unit-level', dest='unit_level', help='Unit level: 3-unit, 4-unit, 5-unit (for high school)')
    p.add_argument('--grades',                     help='Comma-separated grades if file fits multiple (e.g. "7,8")')
    p.add_argument('--category',   required=True,  help=f'Category: {", ".join(sorted(VALID_CATEGORIES))}')
    p.add_argument('--doctype',    required=True,  help=f'Document type: {", ".join(sorted(VALID_DOCTYPES))}')
    p.add_argument('--year',       default='unknown', help='Year (e.g. 2024). Default: unknown')
    p.add_argument('--author',     default='unknown', help='Author name. Default: unknown')
    p.add_argument('--topics',     default='',     help='Comma-separated topics (Hebrew ok)')
    p.add_argument('--tags',       default='',     help='Comma-separated tags')
    p.add_argument('--notes',      default='',     help='Free-text notes for this file')
    p.add_argument('--dry-run',    action='store_true', help='Show what would happen without writing anything')
    return p.parse_args()


def err(msg):
    print(f'\n  ✗ ERROR: {msg}', file=sys.stderr)
    sys.exit(1)


def main():
    args = parse_args()

    src = Path(args.file)
    if not src.exists():
        err(f'File not found: {src}')
    if not src.is_file():
        err(f'Not a file: {src}')

    # ── Validate inputs ────────────────────────────────────────────────────────
    category = args.category.strip().lower()
    if category not in VALID_CATEGORIES:
        err(f'Invalid category "{category}". Valid: {sorted(VALID_CATEGORIES)}')

    doctype = args.doctype.strip().lower()
    if doctype not in VALID_DOCTYPES:
        err(f'Invalid doctype "{doctype}". Valid: {sorted(VALID_DOCTYPES)}')

    grade      = (args.grade or '').strip()
    unit_level = (args.unit_level or '').strip()
    grades     = [g.strip() for g in args.grades.split(',')] if args.grades else []

    if not grade and not unit_level:
        err('Must provide --grade (7/8/9) or --unit-level (3-unit/4-unit/5-unit)')

    if grade and grade not in GRADE_TO_STAGE:
        err(f'Invalid grade "{grade}". Use 7, 8, or 9.')

    if unit_level and unit_level not in HS_UNIT_LEVELS:
        err(f'Invalid unit-level "{unit_level}". Use 3-unit, 4-unit, or 5-unit.')

    if not grades:
        grades = [grade] if grade else []

    school_stage = GRADE_TO_STAGE.get(grade, 'high-school')
    title = args.title or src.stem
    ext   = src.suffix.lower().lstrip('.')

    topics = [t.strip() for t in args.topics.split(',') if t.strip()] or ['unknown']
    tags   = [t.strip() for t in args.tags.split(',')   if t.strip()]
    year   = args.year.strip()
    author = args.author.strip()

    # ── Content hash + duplicate check ────────────────────────────────────────
    print(f'\n  Computing hash for {src.name}...')
    content_hash = sha1_file(src)
    print(f'  SHA-1: {content_hash}')

    index = load_index()
    for existing in index['files']:
        if existing.get('content_hash') == content_hash:
            print(f'\n  ⚠  DUPLICATE DETECTED')
            print(f'     Existing record: {existing["id"]}')
            print(f'     Title: {existing["title"]}')
            print(f'     This file is already in the index. No changes made.')
            print(f'\n     If you need to update metadata (e.g. add a grade), edit metadata/index.json directly.')
            sys.exit(0)

    # ── Build destination path ─────────────────────────────────────────────────
    dest_filename = f'{slugify(src.stem)[:80]}.{ext}'
    dest_path     = determine_path(grade, unit_level, category, dest_filename)
    rel_path      = dest_path.relative_to(REPO)

    record_id = build_id(grade or unit_level, category, title, doctype, year)

    print(f'\n  Source      : {src}')
    print(f'  Destination : {rel_path}')
    print(f'  Record ID   : {record_id}')
    print(f'  Title       : {title}')
    print(f'  Stage       : {school_stage}')
    print(f'  Grade(s)    : {grades or "N/A"}')
    print(f'  Unit level  : {unit_level or "N/A"}')
    print(f'  Category    : {category}')
    print(f'  Doc type    : {doctype}')
    print(f'  Year        : {year}')
    print(f'  Author      : {author}')
    print(f'  Topics      : {topics}')
    print(f'  Hash        : {content_hash}')

    if args.dry_run:
        print('\n  [DRY RUN] No changes written.')
        return

    # ── Confirm ────────────────────────────────────────────────────────────────
    print('\nProceed? [y/N] ', end='', flush=True)
    answer = input().strip().lower()
    if answer not in ('y', 'yes', 'כן'):
        print('  Aborted.')
        sys.exit(0)

    # ── Copy file ──────────────────────────────────────────────────────────────
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_path)
    print(f'\n  ✓ File copied to {rel_path}')

    # ── Build metadata record ──────────────────────────────────────────────────
    record = {
        'id':                  record_id,
        'title':               title,
        'path':                str(rel_path).replace('\\', '/'),
        'file_name':           dest_filename,
        'extension':           ext,
        'content_hash':        content_hash,
        'school_stage':        school_stage,
        'grade':               grade or 'unknown',
        'grades':              grades,
        'unit_level':          unit_level or 'unknown',
        'track':               'unknown',
        'primary_category':    category,
        'topics':              topics,
        'document_type':       doctype,
        'exam_kind':           'unknown',
        'bagrut_questionnaire':'unknown',
        'year':                year,
        'author':              author,
        'source_type':         'repo-file',
        'source_url':          None,
        'embed_url':           None,
        'can_embed':           'unknown',
        'print_ready':         doctype in ('worksheet', 'summary-work', 'exam', 'printable-task'),
        'download_ready':      True,
        'tags':                tags,
        'notes':               args.notes or f'Added via add-file.py on {datetime.now().strftime("%Y-%m-%d")}.'
    }

    index['files'].append(record)
    save_index(index)
    print(f'  ✓ Record added to metadata/index.json')

    # ── Run validation ─────────────────────────────────────────────────────────
    print('\n  Running validate-all.sh...')
    r1 = subprocess.run(['bash', 'scripts/validate-all.sh'], cwd=REPO, capture_output=True, text=True)
    if r1.returncode == 0:
        print('  ✓ validate-all.sh PASSED')
    else:
        print('  ✗ validate-all.sh FAILED')
        print(r1.stdout[-1000:])
        print(r1.stderr[-500:])

    print('\n  Running test-logic.py...')
    r2 = subprocess.run(['python3', 'scripts/test-logic.py'], cwd=REPO, capture_output=True, text=True)
    if r2.returncode == 0:
        print('  ✓ test-logic.py PASSED')
    else:
        print('  ✗ test-logic.py FAILED')
        print(r2.stdout[-1000:])

    if r1.returncode != 0 or r2.returncode != 0:
        print('\n  ⚠  Validation failed. Review errors above before committing.')
        sys.exit(1)

    print('\n' + '─' * 52)
    print('  ✓ FILE ADDED SUCCESSFULLY')
    print('─' * 52)
    print(f'  Now run:')
    print(f'    git add files/{rel_path.parts[1] if len(rel_path.parts)>1 else ""}/... metadata/index.json')
    print(f'    git commit -m "feat(files): add {title}"')
    print(f'    git push')


if __name__ == '__main__':
    main()
