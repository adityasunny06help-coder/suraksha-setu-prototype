#!/usr/bin/env bash
# Suraksha Setu v4 — local dev: backend (FastAPI :8000) + frontend (static :8080) ek saath.
# Ctrl+C dabane par dono band ho jayenge.
set -e
cd "$(dirname "$0")"
export TMPDIR="${TMPDIR:-$HOME/.cache/tool-tmp}"
mkdir -p "$TMPDIR"
# Sandbox ke egress proxy ka CA (agar maujood ho) — RDAP/RSS live calls ke liye
[ -f /run/hatch/egress-tls/ca-bundle.pem ] && export SSL_CERT_FILE="${SSL_CERT_FILE:-/run/hatch/egress-tls/ca-bundle.pem}"
if [ ! -x backend/.venv/bin/uvicorn ]; then
  echo "venv bana raha hu + dependencies install ho rahi hain..."
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi
(cd backend && .venv/bin/uvicorn main:app --port 8000) &
BACK=$!
python3 -m http.server 8080 --bind 127.0.0.1 &
FRONT=$!
trap 'kill $BACK $FRONT 2>/dev/null || true' EXIT INT TERM
echo ""
echo "  Frontend : http://localhost:8080"
echo "  Backend  : http://localhost:8000/api/health"
echo ""
wait
