#!/usr/bin/env bash
# serve-local.sh
# Starts a local web server at the repo root so index.html can be tested.
# Usage: bash scripts/serve-local.sh [port]
# Default port: 8080

PORT="${1:-8080}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== MAAGAR LOCAL SERVER ==="
echo "Root: $REPO_ROOT"
echo "URL:  http://localhost:$PORT"
echo "Stop: Ctrl+C"
echo ""

cd "$REPO_ROOT"

if command -v python3 &>/dev/null; then
  python3 -m http.server "$PORT"
elif command -v python &>/dev/null; then
  python -m SimpleHTTPServer "$PORT"
else
  echo "ERROR: python3 not found. Install Python 3 and retry."
  exit 1
fi
