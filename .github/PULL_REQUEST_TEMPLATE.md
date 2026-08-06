# Summary

<!-- What this PR does, in one or two sentences. -->

## Changes

<!-- Bullet the notable changes. Call out anything touching the 38-D feature vector
     contract in eye_tracker/gaze.py, since four modules depend on its shape. -->

-

## Testing

<!-- Paste ACTUAL test output. "Tests pass" without evidence is not acceptable. -->

```
$ pytest -q --cov=eye_tracker --cov-report=term-missing

```

- [ ] Unit tests added or updated alongside the code
- [ ] Coverage ≥ 85% (paste the coverage line above)
- [ ] Integration tests passing
- [ ] Manually exercised end-to-end: launch → calibrate → live gaze

## Accessibility

<!-- This app renders a gaze overlay on top of the desktop. Consider: -->

- [ ] Overlay remains legible against light and dark desktop backgrounds
- [ ] No reliance on colour alone to convey state
- [ ] Keyboard path exists for every action reachable by gaze or mouse
- [ ] Behaviour verified at non-100% display scaling
- [ ] N/A — no user-facing surface changed

## Screenshots

<!-- Before/after for any overlay, calibration, or window change. Delete if N/A. -->

## Related Issues

<!-- "Closes #12" / "Part of #8". Link the story issue so the project board advances. -->

Closes #
