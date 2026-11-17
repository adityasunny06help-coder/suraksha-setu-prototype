#!/usr/bin/env bash
# Suraksha Setu v4 — saare tests: backend pytest + frontend node tests.
set -e
cd "$(dirname "$0")"
export TMPDIR="${TMPDIR:-$HOME/.cache/tool-tmp}"
mkdir -p "$TMPDIR"
[ -f /run/hatch/egress-tls/ca-bundle.pem ] && export SSL_CERT_FILE="${SSL_CERT_FILE:-/run/hatch/egress-tls/ca-bundle.pem}"
if [ ! -x backend/.venv/bin/pytest ]; then
  echo "venv bana raha hu + dependencies install ho rahi hain..."
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements.txt
fi
echo "== Backend (pytest) =="
backend/.venv/bin/python -m pytest backend/tests -q
echo "== Frontend (node --test) =="
if [ ! -d tests/node_modules/jsdom ]; then
  (cd tests && npm install --no-audit --no-fund)
fi
# Dhyaan: 'node --test tests/' (trailing slash) is Node par MODULE_NOT_FOUND deta hai — explicit files hi chalao
node --test tests/frontend.test.mjs tests/dom.test.mjs
echo "ALL TESTS DONE"
