#!/usr/bin/env bash
# validate-all.sh
# Master validation script for yanivmizrachiy/maagar.
# Runs all checks: JSON syntax, required fields, file existence,
# taxonomy value correctness, site-structure integrity, and contamination scan.
#
# Usage:  bash scripts/validate-all.sh
# Run from the repo root.
# Exit code 0 = all passed. Exit code 1 = at least one failure.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
WARN=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}  OK${RESET}    $1"; ((PASS++)); }
fail() { echo -e "${RED}  FAIL${RESET}  $1"; ((FAIL++)); }
warn() { echo -e "${YELLOW}  WARN${RESET}  $1"; ((WARN++)); }
head() { echo -e "\n${CYAN}━━ $1 ━━${RESET}"; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   MAAGAR — Full Validation Suite     ║"
echo "╚══════════════════════════════════════╝"
echo "Repo: $REPO_ROOT"
echo ""

# ─────────────────────────────────────────────────────────────
# 1. JSON SYNTAX — all metadata files
# ─────────────────────────────────────────────────────────────
head "1. JSON Syntax"

for f in metadata/index.json metadata/taxonomy.json metadata/site-structure.json metadata/authors.json; do
  full="$REPO_ROOT/$f"
  if [ ! -f "$full" ]; then
    fail "File not found: $f"
  elif python3 -c "import json; json.load(open('$full'))" 2>/dev/null; then
    ok "$f — valid JSON"
  else
    fail "$f — INVALID JSON"
  fi
done

# ─────────────────────────────────────────────────────────────
# 2. INDEX RECORDS — required fields + file existence
# ─────────────────────────────────────────────────────────────
head "2. Index Records"

python3 << PYEOF
import json, os, sys

repo_root = "$REPO_ROOT"
errors = 0
warnings = 0

with open(f"{repo_root}/metadata/index.json") as f:
    data = json.load(f)
with open(f"{repo_root}/metadata/taxonomy.json") as f:
    tax = json.load(f)

records = data.get("files", [])
required = ["id","title","school_stage","grade","grades","primary_category",
            "topics","document_type","source_type","can_embed",
            "print_ready","download_ready","author","year"]

valid_school_stages   = set(tax.get("school_stage", []))
valid_primary_cats    = set(tax.get("primary_categories", []))
valid_doc_types       = set(tax.get("document_types", []))
valid_source_types    = set(tax.get("source_types", []))
valid_bool_or_unknown = {True, False, "unknown"}

seen_hashes = {}
seen_ids    = {}

for i, rec in enumerate(records):
    label = rec.get("id", f"record[{i}]")

    for field in required:
        if field not in rec:
            print(f"  FAIL  [{label}]: missing required field '{field}'")
            errors += 1

    rid = rec.get("id")
    if rid in seen_ids:
        print(f"  FAIL  [{label}]: duplicate id '{rid}'")
        errors += 1
    else:
        seen_ids[rid] = i

    chash = rec.get("content_hash")
    if chash and chash not in ("unknown", None):
        if chash in seen_hashes:
            print(f"  FAIL  [{label}]: duplicate content_hash (same as '{seen_hashes[chash]}')")
            errors += 1
        else:
            seen_hashes[chash] = label

    # Taxonomy value checks
    ss = rec.get("school_stage", "")
    if valid_school_stages and ss not in valid_school_stages:
        print(f"  FAIL  [{label}]: school_stage='{ss}' not in taxonomy")
        errors += 1

    pc = rec.get("primary_category", "")
    if valid_primary_cats and pc not in valid_primary_cats:
        print(f"  FAIL  [{label}]: primary_category='{pc}' not in taxonomy")
        errors += 1

    dt = rec.get("document_type", "")
    if valid_doc_types and dt not in valid_doc_types:
        print(f"  FAIL  [{label}]: document_type='{dt}' not in taxonomy")
        errors += 1

    st = rec.get("source_type", "")
    if valid_source_types and st not in valid_source_types:
        print(f"  FAIL  [{label}]: source_type='{st}' not in taxonomy")
        errors += 1

    for bfield in ["can_embed", "print_ready", "download_ready"]:
        val = rec.get(bfield)
        if val not in valid_bool_or_unknown:
            print(f"  FAIL  [{label}]: {bfield}='{val}' — must be true, false, or 'unknown'")
            errors += 1

    # Physical file existence for repo-file records
    if rec.get("source_type") == "repo-file":
        path = rec.get("path")
        if not path:
            print(f"  FAIL  [{label}]: source_type=repo-file but 'path' is missing")
            errors += 1
        else:
            full = os.path.join(repo_root, path)
            if not os.path.isfile(full):
                print(f"  FAIL  [{label}]: file not found — {path}")
                errors += 1
            else:
                print(f"  OK    [{label}]: file exists — {path}")

print(f"\n  Records checked: {len(records)}")
print(f"  Errors: {errors} | Warnings: {warnings}")
sys.exit(1 if errors > 0 else 0)
PYEOF

if [ $? -eq 0 ]; then ok "All index records valid"; else fail "Index record errors found"; fi

# ─────────────────────────────────────────────────────────────
# 3. TAXONOMY INTEGRITY
# ─────────────────────────────────────────────────────────────
head "3. Taxonomy Integrity"

python3 << PYEOF
import json, sys

repo_root = "$REPO_ROOT"
errors = 0

with open(f"{repo_root}/metadata/taxonomy.json") as f:
    tax = json.load(f)

required_keys = [
    "school_stage", "grades", "unit_levels", "tracks",
    "primary_categories", "document_types", "source_types",
    "exam_kinds", "bagrut_questionnaires",
    "primary_category_labels_he", "document_type_labels_he"
]

for key in required_keys:
    if key not in tax:
        print(f"  FAIL  taxonomy.json: missing key '{key}'")
        errors += 1
    else:
        print(f"  OK    taxonomy.json: '{key}' present")

# Check labels_he cover all values
cats = set(tax.get("primary_categories", []))
cat_labels = set(tax.get("primary_category_labels_he", {}).keys())
for c in cats:
    if c not in cat_labels:
        print(f"  WARN  primary_category '{c}' has no Hebrew label in taxonomy")

sys.exit(1 if errors > 0 else 0)
PYEOF

if [ $? -eq 0 ]; then ok "Taxonomy structure valid"; else fail "Taxonomy errors found"; fi

# ─────────────────────────────────────────────────────────────
# 4. SITE-STRUCTURE INTEGRITY
# ─────────────────────────────────────────────────────────────
head "4. Site-Structure Integrity"

python3 << PYEOF
import json, sys

repo_root = "$REPO_ROOT"
errors = 0

with open(f"{repo_root}/metadata/site-structure.json") as f:
    ss = json.load(f)

# Required top-level keys
for key in ["home", "middle_school_screens", "category_cards", "high_school_home", "empty_state_he"]:
    if key not in ss:
        print(f"  FAIL  site-structure.json: missing top-level key '{key}'")
        errors += 1
    else:
        print(f"  OK    '{key}' present")

# Home must have 4 buttons
home_btns = ss.get("home", {}).get("buttons", [])
if len(home_btns) != 4:
    print(f"  FAIL  home.buttons: expected 4, got {len(home_btns)}")
    errors += 1
else:
    print(f"  OK    home.buttons: {len(home_btns)} buttons")

# High school must have 3 unit-level buttons
hs_btns = ss.get("high_school_home", {}).get("buttons", [])
if len(hs_btns) != 3:
    print(f"  FAIL  high_school_home.buttons: expected 3, got {len(hs_btns)}")
    errors += 1
else:
    print(f"  OK    high_school_home.buttons: {len(hs_btns)} buttons")

# Category cards must cover 4 categories
required_cats = {"algebra", "geometry", "summaries", "exams"}
present_cats  = set(ss.get("category_cards", {}).keys())
missing = required_cats - present_cats
if missing:
    print(f"  FAIL  category_cards missing: {missing}")
    errors += 1
else:
    print(f"  OK    category_cards: all 4 present")

# Every button must have style.background
for btn in home_btns + hs_btns:
    if not btn.get("style", {}).get("background"):
        print(f"  FAIL  button '{btn.get('id')}' missing style.background")
        errors += 1

sys.exit(1 if errors > 0 else 0)
PYEOF

if [ $? -eq 0 ]; then ok "Site-structure valid"; else fail "Site-structure errors found"; fi

# ─────────────────────────────────────────────────────────────
# 5. CONTAMINATION SCAN
# ─────────────────────────────────────────────────────────────
head "5. Contamination Scan (Gmail/Calendar/unrelated)"

# Specific patterns that would indicate actual unrelated API contamination.
# These are precise enough to avoid false positives:
#   - fonts.googleapis.com is fine (Hebrew font CDN)
#   - This script itself is excluded from the scan
FOUND_CONTAMINATION=0
THIS_SCRIPT="$(basename "$0")"

python3 << PYEOF
import os, re, sys

repo_root = "$REPO_ROOT"
this_script = "$THIS_SCRIPT"

# These patterns indicate real contamination — not just documentation mentions
CONTAMINATION_PATTERNS = [
    (r'gmail\.googleapis\.com',        "Gmail API endpoint"),
    (r'calendar\.googleapis\.com',     "Calendar API endpoint"),
    (r'import\s+smtplib',              "SMTP email library import"),
    (r'from\s+googleapiclient',        "Google API client library import"),
    (r'credentials\.json',             "OAuth credentials file reference"),
    (r'token\.json',                   "OAuth token file reference"),
    (r'InstalledAppFlow',              "OAuth installed app flow"),
    (r'server\.py.*flask|flask.*server\.py', "Flask server"),
    (r'app\.route\s*\(',               "Flask/Express route definition"),
    (r'nodemailer',                    "Node.js email library"),
    (r'GMAIL_CLIENT|CALENDAR_CLIENT',  "Gmail/Calendar client env var"),
]

SCAN_EXTS = {'.html', '.js', '.py', '.sh', '.json', '.md', '.css', '.ts'}
SKIP_DIRS = {'.git', 'files', '__pycache__', 'node_modules'}

errors = []

for dirpath, dirnames, filenames in os.walk(repo_root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fname in filenames:
        if fname == this_script:
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in SCAN_EXTS:
            continue
        fpath = os.path.join(dirpath, fname)
        relpath = os.path.relpath(fpath, repo_root)
        try:
            content = open(fpath, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for pattern, desc in CONTAMINATION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(f"{relpath}  [{desc}]")

if errors:
    for e in errors:
        print(f"  FAIL  Contamination: {e}")
    sys.exit(1)
else:
    print("  OK    No unrelated API contamination found")
    sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then ok "Contamination scan passed"; else fail "Contamination detected — review above"; FOUND_CONTAMINATION=1; fi

# ─────────────────────────────────────────────────────────────
# 6. KEY FILES EXIST
# ─────────────────────────────────────────────────────────────
head "6. Key Files Present"

KEY_FILES=(
  "RULES.md"
  "AGENTS.md"
  "README.md"
  "index.html"
  "metadata/index.json"
  "metadata/taxonomy.json"
  "metadata/site-structure.json"
  "metadata/authors.json"
  "scripts/validate-index.sh"
  "scripts/validate-all.sh"
  "scripts/serve-local.sh"
)

for f in "${KEY_FILES[@]}"; do
  if [ -f "$REPO_ROOT/$f" ]; then
    ok "$f"
  else
    fail "$f — MISSING"
  fi
done

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo -e "  PASSED:  ${GREEN}${PASS}${RESET}"
echo -e "  FAILED:  ${RED}${FAIL}${RESET}"
echo -e "  WARNED:  ${YELLOW}${WARN}${RESET}"
echo "════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  echo -e "${RED}  VALIDATION FAILED${RESET}"
  exit 1
else
  echo -e "${GREEN}  ALL CHECKS PASSED${RESET}"
  exit 0
fi
