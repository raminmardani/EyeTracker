#!/usr/bin/env bash
# CI self-repair. Given the failure; never hunts for one.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="$ROOT/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"
exec "$PY" "$ROOT/.evals/scripts/auto_fix_agent.py" "${1:-}"
