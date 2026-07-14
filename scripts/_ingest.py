"""
_ingest.py — Shared ingestion logic for add-file.py and batch-add.py.
Internal module — not a CLI tool.
"""

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent

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

VALID_CAN_EMBED = {'true', 'false', 'unknown'}

PRINT_READY_TYPES = {'worksheet', 'summary-work', 'exam', 'printable-task'}


def load_index() -> dict:
    with open(REPO / 'metadata' / 'index.json', encoding='utf-8') as f:
        return json.load(f)


def save_index(data: dict):
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
    """Filesystem-safe slug preserving Hebrew characters."""
    text = text.strip().lower()
    text = re.sub(r'[\s/\\|]+', '-', text)
    text = re.sub(r'[^\wא-ת\-.]', '', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


def determine_path(grade: str, unit_level: str, category: str, filename: str) -> Path:
    if grade in GRADE_TO_STAGE:
        return REPO / 'files' / 'middle-school' / f'grade-{grade}' / category / filename
    return REPO / 'files' / 'high-school' / unit_level / filename


def unique_id(base_id: str, existing_ids: set) -> str:
    """Append incrementing suffix until the id is unique."""
    if base_id not in existing_ids:
        return base_id
    for n in range(2, 1000):
        candidate = re.sub(r'__\d+$', '', base_id) + f'__{n:03d}'
        if candidate not in existing_ids:
            return candidate
    raise RuntimeError(f'Could not generate unique ID for: {base_id}')


def build_id(grade: str, unit_level: str, category: str, title: str,
             doctype: str, year: str) -> str:
    parts = [
        grade or unit_level or 'unknown',
        category,
        slugify(title)[:50],
        doctype,
        year,
        '001'
    ]
    return '__'.join(p for p in parts if p and p != 'unknown_unknown')


def build_record(*, record_id, title, rel_path, dest_filename, ext,
                 content_hash, grade, grades, unit_level, category,
                 topics, doctype, year, author, tags, notes,
                 can_embed_val, editor='unknown', credit='unknown') -> dict:
    can_embed_typed = (True  if can_embed_val == 'true'  else
                       False if can_embed_val == 'false' else
                       'unknown')
    return {
        'id':                   record_id,
        'title':                title,
        'path':                 str(rel_path).replace('\\', '/'),
        'file_name':            dest_filename,
        'extension':            ext,
        'content_hash':         content_hash,
        'school_stage':         GRADE_TO_STAGE.get(grade, 'high-school'),
        'grade':                grade or 'unknown',
        'grades':               grades,
        'unit_level':           unit_level or 'unknown',
        'track':                'unknown',
        'primary_category':     category,
        'topics':               topics,
        'document_type':        doctype,
        'exam_kind':            'unknown',
        'bagrut_questionnaire': 'unknown',
        'year':                 year,
        'author':               author,
        'editor':               editor,
        'credit':               credit,
        'source_type':          'repo-file',
        'source_url':           None,
        'embed_url':            None,
        'can_embed':            can_embed_typed,
        'print_ready':          doctype in PRINT_READY_TYPES,
        'download_ready':       True,
        'tags':                 tags,
        'notes':                notes or f'Added via ingestion script on {datetime.now().strftime("%Y-%m-%d")}.'
    }


def run_checks() -> bool:
    """Run validate-all.sh and test-logic.py. Return True if both pass."""
    print('\n  Running validate-all.sh...')
    r1 = subprocess.run(
        ['bash', 'scripts/validate-all.sh'], cwd=REPO, capture_output=True, text=True
    )
    ok1 = r1.returncode == 0
    print(f'  {"✓" if ok1 else "✗"} validate-all.sh {"PASSED" if ok1 else "FAILED"}')
    if not ok1:
        print(r1.stdout[-1500:])
        print(r1.stderr[-500:])

    print('\n  Running test-logic.py...')
    r2 = subprocess.run(
        ['python3', 'scripts/test-logic.py'], cwd=REPO, capture_output=True, text=True
    )
    ok2 = r2.returncode == 0
    print(f'  {"✓" if ok2 else "✗"} test-logic.py {"PASSED" if ok2 else "FAILED"}')
    if not ok2:
        print(r2.stdout[-1500:])

    return ok1 and ok2
