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

run_check() {
  local title="$1"
  local cmd="$2"
  head "$title"
  if bash -lc "cd '$REPO_ROOT' && $cmd"; then
    ok "$title"
  else
    fail "$title"
  fi
}

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   MAAGAR — Full Validation Suite     ║"
echo "╚══════════════════════════════════════╝"
echo "Repo: $REPO_ROOT"
echo ""

# 1. JSON SYNTAX
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

# 2. ORIGINAL INDEX VALIDATION
run_check "2. Index validator" "bash scripts/validate-index.sh"

# 3. SITE SHELL
run_check "3. Site shell and premium navigation" "python3 scripts/validate-site-shell.py"

# 4. REAL BUTTONS / NO VISIBLE DEMO
run_check "4. Real action buttons and no visible demo text" "python3 scripts/validate-real-buttons.py"

# 5. EXAM CLASSIFIER DRY-RUN
run_check "5. Safe exam classifier dry-run" "python3 scripts/classify-exams.py"

# 6. HIGH SCHOOL UNIT NAVIGATION
run_check "6. High school unit navigation" "python3 scripts/validate-highschool-units.py"

# 7. NAVIGATION LOGIC TEST
run_check "7. Navigation logic" "python3 scripts/test-logic.py"

# 8. KEY FILES EXIST
head "8. Key Files Present"
KEY_FILES=(
  "RULES.md"
  "AGENTS.md"
  "README.md"
  "index.html"
  ".gitattributes"
  "assets/site.css"
  "assets/site-premium-nav.css"
  "assets/site-highschool-units.css"
  "assets/site.js"
  "assets/site-url-state.js"
  "assets/site-deeplink.js"
  "assets/site-share.js"
  "assets/site-view-share.js"
  "assets/site-modal-share.js"
  "assets/site-help.js"
  "metadata/index.json"
  "metadata/taxonomy.json"
  "metadata/site-structure.json"
  "metadata/authors.json"
  "scripts/validate-index.sh"
  "scripts/validate-all.sh"
  "scripts/serve-local.sh"
  "scripts/test-logic.py"
  "scripts/add-file.py"
  "scripts/batch-add.py"
  "scripts/classify-exams.py"
  "scripts/validate-highschool-units.py"
  "scripts/_ingest.py"
  "scripts/qa-browser.js"
  "docs/ADDING_REAL_FILES.md"
  "docs/GPT_TO_CLAUDE_FILE_HANDOFF.md"
  "docs/SCALE_READINESS.md"
  "docs/ANALYTICS_OPTIONS.md"
  "docs/REQUIREMENTS_GAP_AUDIT.md"
  "docs/EDITING_GUIDE.md"
  "docs/CONTINUITY_GUIDE.md"
)
for f in "${KEY_FILES[@]}"; do
  if [ -f "$REPO_ROOT/$f" ]; then
    ok "$f"
  else
    fail "$f — MISSING"
  fi
done

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
