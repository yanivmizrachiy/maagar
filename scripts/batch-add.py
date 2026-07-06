#!/usr/bin/env python3
"""
batch-add.py — Batch-add many real files to yanivmizrachiy/maagar.

Two input modes:

── MODE 1: Folder scan ──────────────────────────────────────────────────────
  python3 scripts/batch-add.py \\
      --folder /path/to/pdfs/ \\
      --grade 8 \\
      --category algebra \\
      --doctype worksheet \\
      --dry-run

  Scans every PDF (and common image/office formats) in the folder.
  All files receive the same grade / category / doctype.
  Title defaults to each filename stem.

── MODE 2: CSV manifest ─────────────────────────────────────────────────────
  python3 scripts/batch-add.py --manifest /path/to/manifest.csv --dry-run

  CSV format — first row must be the header:

    file,title,grade,unit_level,grades,category,doctype,year,author,topics,tags,notes,can_embed

  Column notes:
    file       — absolute or relative (to manifest dir) path  [required]
    title      — Hebrew title  [optional; defaults to filename stem]
    grade      — 7 / 8 / 9  [required unless unit_level is set]
    unit_level — 3-unit / 4-unit / 5-unit  [required for high school]
    grades     — pipe-separated extra grades, e.g. "7|8"  [optional]
    category   — algebra / geometry / summaries / exams / uncategorized
    doctype    — worksheet / summary-work / exam / link /
                 digital-task / printable-task / embedded-resource / mixed
    year       — e.g. 2024, or leave blank for unknown
    author     — blank for unknown
    topics     — pipe-separated, e.g. "יחס|פרופורציה"
    tags       — pipe-separated  [optional]
    notes      — free text  [optional]
    can_embed  — true / false / unknown  [default: unknown]

Example manifest.csv:
  file,title,grade,unit_level,grades,category,doctype,year,author,topics,tags,notes,can_embed
  /files/wsheet.pdf,יחס ופרופ,8,,,algebra,worksheet,2024,,יחס|פרופורציה,,,
  /files/exam.pdf,מבחן גיאו,9,,,geometry,exam,2023,,גיאומטריה,,,

After a successful run:
  git add files/ metadata/index.json
  git commit -m "feat(files): batch add N files"
  git push
"""

import argparse
import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ingest import (
    REPO, GRADE_TO_STAGE, HS_UNIT_LEVELS, VALID_CATEGORIES, VALID_DOCTYPES,
    VALID_CAN_EMBED, load_index, save_index, sha1_file, slugify,
    determine_path, unique_id, build_id, build_record, run_checks
)

SCAN_EXTS = {'.pdf', '.png', '.jpg', '.jpeg', '.svg', '.pptx', '.docx'}


# ── Input parsers ──────────────────────────────────────────────────────────────

def parse_manifest(path: Path) -> list[dict]:
    base = path.parent
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            fp = row.get('file', '').strip()
            if not fp:
                print(f'  ⚠  Row {i}: missing "file" — skipped')
                continue
            p = Path(fp)
            if not p.is_absolute():
                p = base / p
            rows.append({
                'file':       p,
                'title':      row.get('title', '').strip() or None,
                'grade':      row.get('grade', '').strip(),
                'unit_level': row.get('unit_level', '').strip(),
                'grades':     [g.strip() for g in row.get('grades', '').split('|') if g.strip()],
                'category':   row.get('category', '').strip().lower(),
                'doctype':    row.get('doctype', '').strip().lower(),
                'year':       row.get('year', '').strip() or 'unknown',
                'author':     row.get('author', '').strip() or 'unknown',
                'topics':     [t.strip() for t in row.get('topics', '').split('|') if t.strip()] or ['unknown'],
                'tags':       [t.strip() for t in row.get('tags', '').split('|') if t.strip()],
                'notes':      row.get('notes', '').strip(),
                'can_embed':  (row.get('can_embed') or 'unknown').strip().lower() or 'unknown',
                '_row':       i,
            })
    return rows


def scan_folder(folder: Path, defaults: dict) -> list[dict]:
    files = sorted(p for p in folder.iterdir()
                   if p.is_file() and p.suffix.lower() in SCAN_EXTS)
    if not files:
        print(f'  ⚠  No supported files found in {folder}')
    return [{**defaults, 'file': f, 'title': f.stem, '_row': i + 1}
            for i, f in enumerate(files)]


# ── Per-spec validation ────────────────────────────────────────────────────────

def validate_spec(spec: dict) -> list[str]:
    errs = []
    if not spec['file'].exists():
        errs.append(f'File not found: {spec["file"]}')
    if spec['category'] not in VALID_CATEGORIES:
        errs.append(f'Invalid category "{spec["category"]}" — '
                    f'valid: {sorted(VALID_CATEGORIES)}')
    if spec['doctype'] not in VALID_DOCTYPES:
        errs.append(f'Invalid doctype "{spec["doctype"]}" — '
                    f'valid: {sorted(VALID_DOCTYPES)}')
    if not spec['grade'] and not spec['unit_level']:
        errs.append('Must set grade (7/8/9) or unit_level (3-unit/4-unit/5-unit)')
    if spec['grade'] and spec['grade'] not in GRADE_TO_STAGE:
        errs.append(f'Invalid grade "{spec["grade"]}" — use 7, 8, or 9')
    if spec['unit_level'] and spec['unit_level'] not in HS_UNIT_LEVELS:
        errs.append(f'Invalid unit_level "{spec["unit_level"]}" — use 3-unit, 4-unit, or 5-unit')
    if spec.get('can_embed', 'unknown') not in VALID_CAN_EMBED:
        errs.append(f'Invalid can_embed "{spec["can_embed"]}" — use true/false/unknown')
    return errs


# ── Core batch loop ────────────────────────────────────────────────────────────

def process_batch(specs: list[dict], dry_run: bool) -> tuple[dict, dict]:
    index        = load_index()
    seen_hashes  = {f['content_hash'] for f in index['files'] if f.get('content_hash')}
    existing_ids = {f['id'] for f in index['files']}
    results      = {'added': [], 'skipped': [], 'errors': []}

    for spec in specs:
        label = f'[{spec["_row"]}] {spec["file"].name}'
        print(f'\n{"─"*60}')
        print(f'  {label}')

        errs = validate_spec(spec)
        if errs:
            for e in errs:
                print(f'  ✗ {e}')
            results['errors'].append({'file': str(spec['file']), 'errors': errs})
            continue

        grade       = spec['grade']
        unit_level  = spec['unit_level']
        title       = spec['title'] or spec['file'].stem
        grades      = spec['grades'] or ([grade] if grade else [])
        can_embed_v = spec.get('can_embed', 'unknown')

        content_hash = sha1_file(spec['file'])

        if content_hash in seen_hashes:
            dup = next((f for f in index['files']
                        if f.get('content_hash') == content_hash), None)
            eid = dup['id'] if dup else '?'
            print(f'  ⚠  DUPLICATE — already in index as: {eid}')
            results['skipped'].append({'file': str(spec['file']), 'reason': f'duplicate of {eid}'})
            continue

        ext           = spec['file'].suffix.lower().lstrip('.')
        dest_filename = f'{slugify(title)[:80]}.{ext}'
        dest_path     = determine_path(grade, unit_level, spec['category'], dest_filename)
        rel_path      = dest_path.relative_to(REPO)

        base_id   = build_id(grade, unit_level, spec['category'], title,
                             spec['doctype'], spec['year'])
        record_id = unique_id(base_id, existing_ids)

        print(f'  Destination : {rel_path}')
        print(f'  ID          : {record_id}')
        print(f'  Title       : {title}')
        print(f'  Grade(s)    : {grades or unit_level or "N/A"}'
              f'  |  Category : {spec["category"]}  |  Type: {spec["doctype"]}')
        print(f'  Year        : {spec["year"]}  |  Author: {spec["author"]}')
        print(f'  Topics      : {spec["topics"]}  |  can_embed: {can_embed_v}')
        print(f'  SHA-1       : {content_hash[:16]}...')

        if dry_run:
            print('  [DRY RUN] Would add.')
            results['added'].append({'file': str(spec['file']), 'dry_run': True, 'id': record_id})
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.exists():
            # Filename collision: copying would silently overwrite another file's
            # content while both index records keep pointing at the same path
            # (this happened once and lost a worksheet). Skip with an error.
            print(f'  [ERROR] destination already exists, skipping: {rel_path}')
            results['errors'].append({'file': str(spec['file']), 'error': f'destination exists: {rel_path}'})
            continue
        shutil.copy2(spec['file'], dest_path)

        record = build_record(
            record_id=record_id, title=title, rel_path=rel_path,
            dest_filename=dest_filename, ext=ext, content_hash=content_hash,
            grade=grade, grades=grades, unit_level=unit_level,
            category=spec['category'], topics=spec['topics'],
            doctype=spec['doctype'], year=spec['year'], author=spec['author'],
            tags=spec['tags'], notes=spec['notes'], can_embed_val=can_embed_v,
        )

        index['files'].append(record)
        seen_hashes.add(content_hash)
        existing_ids.add(record_id)
        print(f'  ✓ Copied + staged')
        results['added'].append({
            'file': str(spec['file']), 'dry_run': False,
            'id': record_id, 'path': str(rel_path)
        })

    return results, index


# ── Summary printer ────────────────────────────────────────────────────────────

def print_summary(results: dict, dry_run: bool):
    added, skipped, errors = results['added'], results['skipped'], results['errors']
    verb = 'Would add' if dry_run else 'Added'
    print(f'\n{"═"*60}')
    print(f'  BATCH SUMMARY')
    print(f'  {verb:12}: {len(added)}')
    print(f'  Duplicates   : {len(skipped)}')
    print(f'  Errors       : {len(errors)}')
    print(f'{"═"*60}')

    if errors:
        print('\n  ERRORS:')
        for e in errors:
            print(f'    {Path(e["file"]).name}')
            for msg in e['errors']:
                print(f'      ✗ {msg}')

    if skipped:
        print('\n  DUPLICATES (skipped):')
        for s in skipped:
            print(f'    {Path(s["file"]).name} → {s["reason"]}')

    if added and not dry_run:
        print('\n  ADDED:')
        for a in added:
            print(f'    ✓ {a["id"]}')
        print('\n  Now run:')
        print('    git add files/ metadata/index.json')
        print('    git commit -m "feat(files): batch add files"')
        print('    git push')

    if dry_run and added:
        print('\n  Re-run without --dry-run to write these files.')


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Batch-add real files to yanivmizrachiy/maagar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--manifest', help='Path to CSV manifest file')
    mode.add_argument('--folder',   help='Path to folder; scans all PDFs inside')

    # Folder-mode defaults (ignored in manifest mode)
    g = p.add_argument_group('Folder-mode defaults (all files in the folder share these)')
    g.add_argument('--grade',       help='Grade: 7 / 8 / 9  (middle school)')
    g.add_argument('--unit-level',  dest='unit_level',
                   help='3-unit / 4-unit / 5-unit  (high school)')
    g.add_argument('--grades',      help='Extra grades, comma-separated, e.g. "7,8"')
    g.add_argument('--category',    help=f'Category: {", ".join(sorted(VALID_CATEGORIES))}')
    g.add_argument('--doctype',     help=f'Doc type: {", ".join(sorted(VALID_DOCTYPES))}')
    g.add_argument('--year',        default='unknown')
    g.add_argument('--author',      default='unknown')
    g.add_argument('--topics',      default='',
                   help='Pipe-separated topics, e.g. "יחס|פרופורציה"')
    g.add_argument('--can-embed',   dest='can_embed', default='unknown',
                   help='true / false / unknown')

    p.add_argument('--dry-run', action='store_true',
                   help='Preview only — no files written, no index changes')
    return p.parse_args()


def main():
    args = parse_args()

    if args.manifest:
        manifest = Path(args.manifest)
        if not manifest.exists():
            print(f'  ✗ Manifest not found: {manifest}', file=sys.stderr)
            sys.exit(1)
        specs = parse_manifest(manifest)

    else:  # folder mode
        folder = Path(args.folder)
        if not folder.is_dir():
            print(f'  ✗ Not a directory: {folder}', file=sys.stderr)
            sys.exit(1)
        if not args.category or not args.doctype:
            print('  ✗ --folder requires --category and --doctype', file=sys.stderr)
            sys.exit(1)
        if not args.grade and not args.unit_level:
            print('  ✗ --folder requires --grade or --unit-level', file=sys.stderr)
            sys.exit(1)

        grade = (args.grade or '').strip()
        extra_grades = [g.strip() for g in args.grades.split(',')] if args.grades else []

        defaults = {
            'grade':      grade,
            'unit_level': (args.unit_level or '').strip(),
            'grades':     extra_grades,
            'category':   args.category.strip().lower(),
            'doctype':    args.doctype.strip().lower(),
            'year':       args.year.strip() or 'unknown',
            'author':     args.author.strip() or 'unknown',
            'topics':     [t.strip() for t in args.topics.split('|') if t.strip()] or ['unknown'],
            'tags':       [],
            'notes':      '',
            'can_embed':  args.can_embed.strip().lower() or 'unknown',
        }
        specs = scan_folder(folder, defaults)

    if not specs:
        print('  No files to process.')
        sys.exit(0)

    print(f'\n  Found {len(specs)} file(s) to process.')
    if args.dry_run:
        print('  DRY RUN — no changes will be written.\n')

    results, index = process_batch(specs, dry_run=args.dry_run)

    if not args.dry_run and results['added']:
        save_index(index)
        print('\n  ✓ metadata/index.json updated')
        passed = run_checks()
        if not passed:
            print('\n  ⚠  Validation failed. Review errors above before committing.')
            sys.exit(1)

    print_summary(results, dry_run=args.dry_run)

    if results['errors']:
        sys.exit(1)


if __name__ == '__main__':
    main()
