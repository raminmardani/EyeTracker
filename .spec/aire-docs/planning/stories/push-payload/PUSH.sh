#!/usr/bin/env bash
# Run from the clone root. Requires gh authed as an account with push on the repo.
set -euo pipefail
R=raminmardani/EyeTracker
D=.spec/aire-docs/planning/stories/push-payload
for L in "ai-generated|8A2BE2|Created by an AI agent" \
         "aire-v1.0|5319E7|Built with AIRE framework v1.0" \
         "ready-for-development|0E8A16|Ready for Development"; do
  IFS='|' read -r n c d <<< "$L"
  gh label create "$n" --repo "$R" --color "$c" --description "$d" 2>/dev/null || true
done
while IFS='|' read -r num title; do
  gh issue create --repo "$R" \
    --title "[STORY $num] $title" \
    --body-file "$D/story-$num.md" \
    --label story --label ai-generated --label "aire-v1.0" --label ready-for-development
done < "$D/titles.txt"
