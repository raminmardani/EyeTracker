# Intake Brief — EVAL-1: Diagnostics & Threshold Unification

**Tracker**: GITHUB · `raminmardani/EyeTracker` · Parent Epic: `none`
**Source**: derived from the repository's own `docs/requirements.md` (FR-14, FR-15, FR-24, FR-25),
which was authored and reviewed in a prior cycle. No new product direction is invented here.

## Why this slice

EyeTracker's own requirements document states the work is "signal-and-measurement only" because the
gaze signal is not yet trustworthy. Three of its requirements are **pure-diagnostics groundwork**:
they add no behaviour to the gaze pipeline, create no new hardware dependency, and are prerequisites
for every later theme that needs to explain *why* a frame was dropped or a prediction failed.

They are also mutually independent, which makes them implementable in parallel.

## In scope

| Req | Source FR | Summary |
|---|---|---|
| **REQ-F-01** | FR-14, FR-15 | One definition for the frame-acceptance thresholds. Today two independent literal blocks exist and have diverged on 4 of 6 thresholds. |
| **REQ-F-02** | FR-24 | Count and expose frame rejections by reason. Today the live pipeline drops frames through silent `return` paths. |
| **REQ-F-03** | FR-25 | Structured logging with levels and a controllable destination, replacing 10 `print()` sites. Preserve the existing `[module]` convention as logger names. |
| **REQ-NF-01** | FR-27 | ≥ the configured coverage threshold on all new code, 100% pass. |
| **REQ-NF-02** | FR-29 | No behavioural change to the gaze pipeline. Existing accepted/rejected frames must be classified identically. |

## Out of scope

Themes A, B, C, E, H, I. No gaze-math change, no calibration change, no persistence, no UI work.

## Verified evidence (read from the code at this commit, not assumed)

**REQ-F-01 — the divergence is real.** Two independent literal blocks:

| Threshold | `main.py:94-100` (live) | `eye_tracker/overlay.py:182-188` (calibration) | |
|---|---|---|---|
| `A_EAR` min | 0.16 | 0.16 | same |
| `B_EAR` min | 0.16 | 0.16 | same |
| `blink` max | **0.58** | **0.55** | ⚠️ diverged |
| `squint` max | **0.58** | **0.55** | ⚠️ diverged |
| `yaw` max | **0.70** | **0.60** | ⚠️ diverged |
| `pitch` max | **0.55** | **0.45** | ⚠️ diverged |

4 of 6 diverged — exactly as `docs/requirements.md` FR-14 claims.

🔴 **FR-15 constraint**: the live envelope is *intentionally* wider than the calibration envelope.
Unification must express that as an explicit documented deviation from a shared base — NOT collapse
both to one set of numbers. Collapsing them would silently retune the gates, which FR-3 forbids by
analogy.

**REQ-F-03 — 10 `print()` sites**: `overlay.py` 206, 212, 217 · `tracker.py` 123, 127, 142, 146, 160
· `main.py` 56, 116. The `[module]` bracket convention is already consistent and becomes the logger
name.

**REQ-F-02 — silent drops** in `main.py::_on_feat`: the `None` guard, the six-condition envelope
gate, the predictor exception path, and the non-finite prediction guard.

## Existing-system truth (Atlas, solution 704)

Knowledge graph at commit `745e086`, verified zero source drift vs this cycle's base.
`main` is the composition root; `overlay` and `tracker` both sit under it. A shared threshold module
is a NEW leaf with no internal importers, so it introduces no cycle.
