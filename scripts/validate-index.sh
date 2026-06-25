#!/usr/bin/env bash
# validate-index.sh
# Validates that every record in metadata/index.json is internally consistent
# and that every repo-file path points to a real existing file.
# Existing older records may omit exam_kind; the validator treats that as unknown.
# New records should include exam_kind according to RULES.md.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$REPO_ROOT/metadata/index.json"
TAXONOMY="$REPO_ROOT/metadata/taxonomy.json"

# Force UTF-8 and a native-OS path for Python so this behaves identically on
# Windows (Git-bash + Windows Python) and Linux/CI. cygpath -m turns /c/... into
# C:/...; on Linux cygpath is absent and the MSYS paths are already native.
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
if command -v cygpath >/dev/null 2>&1; then
  PYROOT="$(cygpath -m "$REPO_ROOT")"
else
  PYROOT="$REPO_ROOT"
fi
PYINDEX="$PYROOT/metadata/index.json"
PYTAXONOMY="$PYROOT/metadata/taxonomy.json"

if [ ! -f "$INDEX" ]; then
  echo "ERROR: metadata/index.json not found."
  exit 1
fi
if [ ! -f "$TAXONOMY" ]; then
  echo "ERROR: metadata/taxonomy.json not found."
  exit 1
fi

if ! python3 -c "import json; json.load(open('$PYINDEX', encoding='utf-8'))" 2>/dev/null; then
  echo "ERROR: metadata/index.json is not valid JSON."
  exit 1
fi
if ! python3 -c "import json; json.load(open('$PYTAXONOMY', encoding='utf-8'))" 2>/dev/null; then
  echo "ERROR: metadata/taxonomy.json is not valid JSON."
  exit 1
fi

echo "=== MAAGAR INDEX VALIDATOR ==="
echo "Index: $INDEX"
echo "Taxonomy: $TAXONOMY"
echo ""

python3 << PYEOF
import json, os, sys

repo_root = "$PYROOT"
index_path = "$PYINDEX"
taxonomy_path = "$PYTAXONOMY"
errors = 0
warnings = 0

with open(index_path, encoding="utf-8") as f:
    data = json.load(f)
with open(taxonomy_path, encoding="utf-8") as f:
    tax = json.load(f)

records = data.get("files", [])
required_fields = [
    "id", "title", "school_stage", "grade", "grades", "primary_category",
    "topics", "document_type", "source_type", "can_embed",
    "print_ready", "download_ready", "author", "year"
]

valid_school_stage = set(tax.get("school_stage", []))
valid_grades = set(tax.get("grades", []))
valid_primary_categories = set(tax.get("primary_categories", []))
valid_document_types = set(tax.get("document_types", []))
valid_source_types = set(tax.get("source_types", []))
valid_exam_kinds = set(tax.get("exam_kinds", []))
valid_bool = {True, False, "unknown", None}

seen_hashes = {}
seen_ids = {}
missing_exam_kind = 0

for i, rec in enumerate(records):
    label = rec.get("id", f"record[{i}]")

    for field in required_fields:
        if field not in rec:
            print(f"ERROR [{label}]: missing required field '{field}'")
            errors += 1

    rid = rec.get("id")
    if rid in seen_ids:
        print(f"ERROR [{label}]: duplicate id '{rid}'")
        errors += 1
    else:
        seen_ids[rid] = i

    chash = rec.get("content_hash")
    if chash and chash != "unknown" and chash is not None:
        if chash in seen_hashes:
            print(f"ERROR [{label}]: duplicate content_hash '{chash}'")
            errors += 1
        else:
            seen_hashes[chash] = label

    if rec.get("school_stage") not in valid_school_stage:
        print(f"ERROR [{label}]: invalid school_stage '{rec.get('school_stage')}'")
        errors += 1

    if rec.get("grade") not in valid_grades:
        print(f"ERROR [{label}]: invalid grade '{rec.get('grade')}'")
        errors += 1

    grades = rec.get("grades")
    if not isinstance(grades, list):
        print(f"ERROR [{label}]: grades must be an array")
        errors += 1
    else:
        for grade in grades:
            if grade not in valid_grades:
                print(f"ERROR [{label}]: invalid value in grades '{grade}'")
                errors += 1

    if rec.get("primary_category") not in valid_primary_categories:
        print(f"ERROR [{label}]: invalid primary_category '{rec.get('primary_category')}'")
        errors += 1

    if rec.get("document_type") not in valid_document_types:
        print(f"ERROR [{label}]: invalid document_type '{rec.get('document_type')}'")
        errors += 1

    if rec.get("source_type") not in valid_source_types:
        print(f"ERROR [{label}]: invalid source_type '{rec.get('source_type')}'")
        errors += 1

    if "exam_kind" not in rec:
        missing_exam_kind += 1
    exam_kind = rec.get("exam_kind", "unknown")
    if exam_kind not in valid_exam_kinds:
        print(f"ERROR [{label}]: invalid exam_kind '{exam_kind}'")
        errors += 1

    topics = rec.get("topics")
    if not isinstance(topics, list):
        print(f"ERROR [{label}]: topics must be an array")
        errors += 1

    for bfield in ["can_embed", "print_ready", "download_ready"]:
        if rec.get(bfield) not in valid_bool:
            print(f"ERROR [{label}]: {bfield} has invalid value '{rec.get(bfield)}'")
            errors += 1

    if rec.get("source_type") == "repo-file":
        path = rec.get("path")
        if not path:
            print(f"ERROR [{label}]: source_type=repo-file but path is missing")
            errors += 1
        else:
            full_path = os.path.join(repo_root, path)
            if not os.path.isfile(full_path):
                print(f"ERROR [{label}]: file not found at path '{path}'")
                errors += 1

if missing_exam_kind:
    print(f"WARN: {missing_exam_kind} legacy records have no exam_kind; treated as unknown")
    warnings += 1

print("=== RESULTS ===")
print(f"Records checked : {len(records)}")
print(f"Errors          : {errors}")
print(f"Warnings        : {warnings}")
if errors > 0:
    print("VALIDATION FAILED")
    sys.exit(1)
print("VALIDATION PASSED")
PYEOF
