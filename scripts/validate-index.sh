#!/usr/bin/env bash
# validate-index.sh
# Validates that every record in metadata/index.json is internally consistent
# and that every repo-file path points to a real existing file.
#
# Usage: bash scripts/validate-index.sh
# Run from the repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$REPO_ROOT/metadata/index.json"
ERRORS=0
WARNINGS=0
CHECKED=0

echo "=== MAAGAR INDEX VALIDATOR ==="
echo "Index: $INDEX"
echo ""

if [ ! -f "$INDEX" ]; then
  echo "ERROR: metadata/index.json not found."
  exit 1
fi

# Validate JSON syntax
if ! python3 -c "import json,sys; json.load(open('$INDEX'))" 2>/dev/null; then
  echo "ERROR: metadata/index.json is not valid JSON."
  exit 1
fi

echo "JSON syntax: OK"
echo ""

# Required fields for every record
REQUIRED_FIELDS=("id" "title" "school_stage" "grade" "grades" "primary_category" "topics" "document_type" "source_type" "can_embed" "print_ready" "download_ready" "author" "year")

# Read records
RECORD_COUNT=$(python3 -c "import json; d=json.load(open('$INDEX')); print(len(d.get('files',[])))")
echo "Records in index: $RECORD_COUNT"
echo ""

python3 << PYEOF
import json, os, sys

repo_root = "$REPO_ROOT"
index_path = "$INDEX"
errors = 0
warnings = 0

with open(index_path) as f:
    data = json.load(f)

records = data.get("files", [])
required_fields = ["id","title","school_stage","grade","grades","primary_category","topics","document_type","source_type","can_embed","print_ready","download_ready","author","year"]
seen_hashes = {}
seen_ids = {}

for i, rec in enumerate(records):
    label = rec.get("id", f"record[{i}]")

    # Check required fields
    for field in required_fields:
        if field not in rec:
            print(f"ERROR [{label}]: missing required field '{field}'")
            errors += 1

    # Check for duplicate IDs
    rid = rec.get("id")
    if rid in seen_ids:
        print(f"ERROR [{label}]: duplicate id '{rid}' (also at record {seen_ids[rid]})")
        errors += 1
    else:
        seen_ids[rid] = i

    # Check for duplicate content_hash
    chash = rec.get("content_hash")
    if chash and chash != "unknown" and chash is not None:
        if chash in seen_hashes:
            print(f"ERROR [{label}]: duplicate content_hash '{chash}' (also at '{seen_hashes[chash]}')")
            errors += 1
        else:
            seen_hashes[chash] = label

    # Check physical file existence for repo-file records
    if rec.get("source_type") == "repo-file":
        path = rec.get("path")
        if not path:
            print(f"ERROR [{label}]: source_type=repo-file but 'path' is missing")
            errors += 1
        else:
            full_path = os.path.join(repo_root, path)
            if not os.path.isfile(full_path):
                print(f"ERROR [{label}]: file not found at path '{path}'")
                errors += 1
            else:
                print(f"OK    [{label}]: file exists at '{path}'")

    # Warn if grades is missing or not a list
    grades = rec.get("grades")
    if grades is None:
        print(f"WARN  [{label}]: 'grades' field is missing")
        warnings += 1
    elif not isinstance(grades, list):
        print(f"WARN  [{label}]: 'grades' should be an array, got {type(grades).__name__}")
        warnings += 1

    # Warn if can_embed is not a valid value
    can_embed = rec.get("can_embed")
    if can_embed not in (True, False, "unknown", None):
        print(f"WARN  [{label}]: can_embed has unexpected value '{can_embed}'")
        warnings += 1

print("")
print(f"=== RESULTS ===")
print(f"Records checked : {len(records)}")
print(f"Errors          : {errors}")
print(f"Warnings        : {warnings}")

if errors > 0:
    print("VALIDATION FAILED")
    sys.exit(1)
else:
    print("VALIDATION PASSED")
PYEOF
