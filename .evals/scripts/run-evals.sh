#!/usr/bin/env bash
# J1/J2 judge gates + scorecard merge.
set -uo pipefail
BASE="${1:?usage: run-evals.sh <base-ref>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"
exec "$PY" "$ROOT/.evals/scripts/run_evals.py" "$BASE"
