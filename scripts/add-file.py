#!/usr/bin/env python3
"""
add-file.py — Add one real file to yanivmizrachiy/maagar.

Usage:
  python3 scripts/add-file.py --help

  python3 scripts/add-file.py \\
      --file /path/to/worksheet.pdf \\
      --grade 8 \\
      --category algebra \\
      --doctype worksheet \\
      --year 2024 \\
      --author "שם המחבר" \\
      --topics "אלגברה,משוואות" \\
      --title "כותרת בעברית"

  # Preview without writing:
  python3 scripts/add-file.py --file X.pdf --grade 8 --category algebra --doctype worksheet --dry-run

  # Skip confirmation prompt (for scripting):
  python3 scripts/add-file.py --file X.pdf --grade 8 --category algebra --doctype worksheet --yes

What this script does:
  1. Validates all inputs against taxonomy
  2. Computes SHA-1 content hash
  3. Checks for duplicate in metadata/index.json
  4. Determines destination: files/<school_stage>/<grade>/<category>/
  5. Copies file to destination
  6. Appends metadata record to metadata/index.json
  7. Runs validate-all.sh + test-logic.py

What this script does NOT do:
  - Invent or guess metadata (use "unknown" for unknowns)
  - Push to git (you review and push manually)
  - Add fake or demo files
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ingest import (
    GRADE_TO_STAGE, HS_UNIT_LEVELS, VALID_CATEGORIES, VALID_DOCTYPES,
    VALID_CAN_EMBED, load_index, save_index, sha1_file, slugify,
    determine_path, unique_id, build_id, build_record, run_checks
)

import shutil


def parse_args():
    p = argparse.ArgumentParser(
        description='Add one real file to yanivmizrachiy/maagar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    p.add_argument('--file',        required=True,  help='Path to the file to add')
    p.add_argument('--title',                       help='Hebrew title (default: filename stem)')
    p.add_argument('--grade',                       help='Grade: 7, 8, or 9  (middle school)')
    p.add_argument('--unit-level',  dest='unit_level',
                   help='Unit level: 3-unit / 4-unit / 5-unit  (high school)')
    p.add_argument('--grades',      help='Extra grades if file fits multiple, e.g. "7,8"')
    p.add_argument('--category',    required=True,
                   help=f'Category: {", ".join(sorted(VALID_CATEGORIES))}')
    p.add_argument('--doctype',     required=True,
                   help=f'Document type: {", ".join(sorted(VALID_DOCTYPES))}')
    p.add_argument('--year',        default='unknown', help='Year, e.g. 2024  (default: unknown)')
    p.add_argument('--author',      default='unknown', help='Author name  (default: unknown)')
    p.add_argument('--topics',      default='',  help='Comma-separated topics (Hebrew ok)')
    p.add_argument('--tags',        default='',  help='Comma-separated tags')
    p.add_argument('--notes',       default='',  help='Free-text notes')
    p.add_argument('--can-embed',   dest='can_embed', default='unknown',
                   help='Embed status: true / false / unknown  (default: unknown)')
    p.add_argument('--dry-run',     action='store_true',
                   help='Preview only — no files written')
    p.add_argument('--yes', '-y',   action='store_true',
                   help='Skip confirmation prompt (non-interactive)')
    p.add_argument('--no-validate', action='store_true',
                   help='Skip post-add validation (useful in batch scripts)')
    return p.parse_args()


def err(msg):
    print(f'\n  ✗ {msg}', file=sys.stderr)
    sys.exit(1)


def main():
    args = parse_args()

    src        = Path(args.file)
    category   = args.category.strip().lower()
    doctype    = args.doctype.strip().lower()
    grade      = (args.grade      or '').strip()
    unit_level = (args.unit_level or '').strip()
    can_embed_val = args.can_embed.strip().lower()

    # ── Validate ───────────────────────────────────────────────────────────────
    if not src.exists() or not src.is_file():
        err(f'File not found: {src}')
    if category not in VALID_CATEGORIES:
        err(f'Invalid category "{category}". Valid: {sorted(VALID_CATEGORIES)}')
    if doctype not in VALID_DOCTYPES:
        err(f'Invalid doctype "{doctype}". Valid: {sorted(VALID_DOCTYPES)}')
    if not grade and not unit_level:
        err('Must provide --grade (7/8/9) or --unit-level (3-unit/4-unit/5-unit)')
    if grade and grade not in GRADE_TO_STAGE:
        err(f'Invalid grade "{grade}". Use 7, 8, or 9.')
    if unit_level and unit_level not in HS_UNIT_LEVELS:
        err(f'Invalid unit-level "{unit_level}". Use 3-unit, 4-unit, or 5-unit.')
    if can_embed_val not in VALID_CAN_EMBED:
        err(f'Invalid --can-embed "{can_embed_val}". Use: true, false, unknown.')

    grades = [g.strip() for g in args.grades.split(',')] if args.grades else ([grade] if grade else [])
    title  = args.title or src.stem
    topics = [t.strip() for t in args.topics.split(',') if t.strip()] or ['unknown']
    tags   = [t.strip() for t in args.tags.split(',')   if t.strip()]

    # ── Hash + duplicate check ─────────────────────────────────────────────────
    print(f'\n  Computing hash for {src.name}...')
    content_hash = sha1_file(src)
    print(f'  SHA-1: {content_hash[:16]}...')

    index = load_index()
    for existing in index['files']:
        if existing.get('content_hash') == content_hash:
            print(f'\n  ⚠  DUPLICATE — already in index as: {existing["id"]}')
            print(f'     Title: {existing["title"]}')
            print('     No changes made.')
            sys.exit(0)

    # ── Build destination ──────────────────────────────────────────────────────
    ext           = src.suffix.lower().lstrip('.')
    dest_filename = f'{slugify(title)[:80]}.{ext}'
    dest_path     = determine_path(grade, unit_level, category, dest_filename)
    rel_path      = dest_path.relative_to(Path(__file__).parent.parent)

    existing_ids  = {f['id'] for f in index['files']}
    base_id       = build_id(grade, unit_level, category, title, doctype, args.year.strip())
    record_id     = unique_id(base_id, existing_ids)

    # ── Preview ────────────────────────────────────────────────────────────────
    print(f'\n  Source      : {src}')
    print(f'  Destination : {rel_path}')
    print(f'  Record ID   : {record_id}')
    print(f'  Title       : {title}')
    print(f'  Stage       : {GRADE_TO_STAGE.get(grade, "high-school")}')
    print(f'  Grade(s)    : {grades or "N/A"}')
    print(f'  Unit level  : {unit_level or "N/A"}')
    print(f'  Category    : {category}')
    print(f'  Doc type    : {doctype}')
    print(f'  Year        : {args.year}')
    print(f'  Author      : {args.author}')
    print(f'  Topics      : {topics}')
    print(f'  can_embed   : {can_embed_val}')
    print(f'  SHA-1       : {content_hash}')

    if args.dry_run:
        print('\n  [DRY RUN] No changes written.')
        return

    # ── Confirm ────────────────────────────────────────────────────────────────
    if not args.yes:
        print('\nProceed? [y/N] ', end='', flush=True)
        answer = input().strip().lower()
        if answer not in ('y', 'yes', 'כן'):
            print('  Aborted.')
            sys.exit(0)

    # ── Copy ───────────────────────────────────────────────────────────────────
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        print(f'\n  ✗ Destination already exists: {rel_path}')
        print('    Refusing to overwrite an existing file (would orphan its index record).')
        print('    Rename the source file and retry.')
        sys.exit(1)
    shutil.copy2(src, dest_path)
    print(f'\n  ✓ File copied to {rel_path}')

    # ── Record ─────────────────────────────────────────────────────────────────
    record = build_record(
        record_id=record_id, title=title, rel_path=rel_path,
        dest_filename=dest_filename, ext=ext, content_hash=content_hash,
        grade=grade, grades=grades, unit_level=unit_level,
        category=category, topics=topics, doctype=doctype,
        year=args.year.strip(), author=args.author.strip(),
        tags=tags, notes=args.notes, can_embed_val=can_embed_val,
    )
    index['files'].append(record)
    save_index(index)
    print('  ✓ metadata/index.json updated')

    # ── Validate ───────────────────────────────────────────────────────────────
    if not args.no_validate:
        passed = run_checks()
        if not passed:
            print('\n  ⚠  Validation failed. Review errors above before committing.')
            sys.exit(1)

    print('\n' + '─' * 56)
    print('  ✓ FILE ADDED SUCCESSFULLY')
    print('─' * 56)
    print('  Now run:')
    print(f'    git add "{record["path"]}" metadata/index.json')
    print(f'    git commit -m "feat(files): add {title}"')
    print('    git push')


if __name__ == '__main__':
    main()
