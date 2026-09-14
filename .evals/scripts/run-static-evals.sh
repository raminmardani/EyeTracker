#!/usr/bin/env bash
# D1-D7 static eval gate, delta-scoped. The local gate AND CI both call THIS.
set -uo pipefail
BASE="${1:?usage: run-static-evals.sh <base-ref>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"
exec "$PY" "$ROOT/.evals/scripts/static_evals.py" "$BASE"
