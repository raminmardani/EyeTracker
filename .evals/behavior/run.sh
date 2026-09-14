#!/usr/bin/env bash
# THE entry point for the Gherkin behaviour tiers: run.sh <b1|b2|b3>
#   b1 = this work unit's own feature file (UNIT_FEATURE must name it)
#   b2 = every OTHER feature file already in the repo
#   b3 = b1 + b2 + the cross-story journeys in .spec/behavior.feature
#        (last work unit of the cycle only)
#
# The same image and the same command run locally and in CI.
set -uo pipefail

TIER="${1:?usage: run.sh <b1|b2|b3>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

UNIT_DIR=".spec/aire-docs/implementation/code/behavior"

if ! command -v behave >/dev/null 2>&1; then
  echo "ERROR: behave is not installed. The behaviour gate should have run."
  echo "This is an ERROR, never N/A."
  exit 1
fi

case "$TIER" in
  b1)
    FEATURES="${UNIT_FEATURE:-}"
    if [ -z "$FEATURES" ]; then
      echo "ERROR: UNIT_FEATURE must name this work unit's .feature file for tier b1."
      exit 2
    fi
    ;;
  b2)
    EXCLUDE="${UNIT_FEATURE:-__no_such_feature__}"
    FEATURES="$(find "$UNIT_DIR" -name '*.feature' 2>/dev/null \
                | grep -v -F "$EXCLUDE" | tr '\n' ' ')"
    ;;
  b3)
    FEATURES="$(find "$UNIT_DIR" -name '*.feature' 2>/dev/null | tr '\n' ' ')"
    FEATURES="$FEATURES .spec/behavior.feature"
    ;;
  *)
    echo "ERROR: unknown tier '$TIER' (expected b1, b2 or b3)"
    exit 2
    ;;
esac

TRIMMED="$(echo "$FEATURES" | tr -d '[:space:]')"
if [ -z "$TRIMMED" ]; then
  echo "[behaviour] no feature files in scope for tier $TIER - nothing to run."
  exit 0
fi

echo "[behaviour] tier=$TIER"
echo "[behaviour] features: $FEATURES"
exec behave --no-capture --format progress2 --stop $FEATURES
