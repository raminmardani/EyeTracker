# Cycle Plan — No Silent Failures

**Cycle ID**: cycle-4
**BUILDID**: CYCLE-4
**Date**: 2026-08-07
**Author**: AIRE_BUILD_CYCLE_PLANNER
**Migration Phase**: M6
**Expected Outcome**: **Every enumerated failure path produces a visible on-screen message within 3 seconds and offers a recovery action.** The gaze dot is hidden — not frozen — within 500 ms of the face being lost. An unplugged camera offers Retry instead of spinning silently at ~100 Hz forever. And "the dot is sluggish" becomes diagnosable, because frame rejections are counted and exposed by reason.

> **This cycle exists because of failure criterion 1**: "Any silent failure survives" is unacceptable "regardless of severity, given the accessibility audience." Seven of the eight key user flows in the UI/UX discovery are currently silent failures. This is the cycle that closes them.

---

## Scope

### In Scope (this cycle)

| Requirement | Deliverable | Owning file(s) |
|---|---|---|
| **FR-20** | Every capture-thread failure path surfaces an actionable on-screen message. **Four such paths currently terminate the producer with only a `print()`** to a stream a windowed application discards | `eye_tracker/status_window.py` 🆕, `eye_tracker/tracker.py` |
| **FR-21** | When the face is lost the gaze dot is **hidden, not frozen**. A frozen dot is indistinguishable from a confident steady gaze. **The required API `set_dot_visible` already exists and is never called** | `eye_tracker/overlay.py` |
| **FR-23** | Camera failure offers a retry path rather than an unbounded silent retry loop | `eye_tracker/tracker.py`, `eye_tracker/status_window.py` 🆕 |
| **FR-24** | Frame rejections counted and **exposed** by reason. Five silent `return` paths in the live pipeline currently make sluggishness undiagnosable | `eye_tracker/pipeline.py` 🆕, `eye_tracker/diagnostics.py` 🆕 |
| **FR-25** *(call sites)* | `print()` → structured logging. 🔧 **Measured directly: 10 sites across 3 modules** (`main.py` 2, `overlay.py` 3, `tracker.py` 5) — the analysis documents record "nine across four", and the measured figure is authoritative | `main.py`, `eye_tracker/overlay.py`, `eye_tracker/tracker.py` |
| **FR-30** | A failure during camera probing must not leak the MediaPipe graph or kill the capture thread silently | `eye_tracker/tracker.py` |
| **FR-31** | Every capture returned by camera selection configured **identically**. Two fallback paths currently skip configuration, which changes the assumed focal length and therefore the meaning of head-pose translation features | `eye_tracker/tracker.py` |
| **FR-32** | `viable` removed **and its intent enforced** as a configured F3 precondition — if no candidate reaches `min_mean` or `min_std`, raise a fault with Retry instead of silently opening the darkest device. Second clause: correct the Configuration table in `00-system-overview.md` | `eye_tracker/tracker.py`, `docs/architecture/current/00-system-overview.md` |
| **FR-28** *(partial)* | Failing-first regression tests for defects **#7**, **#8**, **#9** | `tests/regression/test_defect_007.py`, `008`, `009` 🆕 |
| **DR-6** | The per-frame path extracted as a pure `LivePipeline` — **the single largest testability lever for the ≥85% gate**, and the natural owner of FR-24's counters | `eye_tracker/pipeline.py` 🆕 |
| **DR-16** | Silent fallbacks become observable: `head_pose is None` yields `NaN` in features 8–13 rather than exact zeros, so the frame is dropped by existing finite filters and counted under `POSE_UNAVAILABLE`. Absent blendshapes become an F3 startup fault instead of 12 silently constant features | `eye_tracker/face_mesh.py`, `eye_tracker/diagnostics.py` 🆕 |

### `StatusWindow` — built to the approved UI/UX spec

The spec is already approved (`docs/ui-ux/ui-ux-spec.md`, 681 tokens), so this cycle **consumes** it rather than needing a design run. Binding constraints from it:

| Constraint | Value |
|---|---|
| Geometry | 420 pt fixed width, bottom-right of primary screen, 24 pt margin |
| Default state in Live | **Collapsed pill**, ~44 pt tall — expands on fault, on focus, or on `F1` |
| Hidden during | Calibration — the full-screen window owns the display |
| Error display | **Persistent banner** — never auto-dismissed |
| 🔴 Focus-stealing rule | `raise_()` + `activateWindow()` **only** on a transition into `Faulted`. Never during normal running |
| Keyboard | Tab order: banner action → Recalibrate → Retry → Quit. Shortcuts `R` `T` `Q` `F1`, `Esc` collapses (**not** quit) |
| Accessibility | **AAA** (7:1) in owned windows; `accessibleName` + `accessibleDescription` on all controls; `QAccessibleEvent` on state and banner changes; **never colour alone** |
| Severity wording | F0/F1 no message · F2 problem + retry · F3 cannot-start + retry\|quit · F4 refused + reason + calibrate |
| Counters | Non-zero reasons only, descending, max 8 |
| Wording | `event_then_action`; **never blame the user** |
| Motion | **None.** Nothing blinks, pulses or auto-dismisses |

**Dual-outline gaze dot** (FR-21's neighbour): the current white outline measures **1.00:1 on a white desktop — invisible**. Dark outer ring + light inner ring holds **≥5.32:1 best-edge contrast on any background**, including the pathological red-on-red case. Radius 14 fill, 2 pt inner, 2 pt dark outer → 18 pt overall.

**Also lands here**: the Quit affordance for Cycle 3's `setQuitOnLastWindowClosed(False)`. Until this cycle ships, the only exit is programmatic.

### Deferred to Next Cycle

| Deferred | Reason |
|---|---|
| Persistence (FR-16 – FR-19) | Cycle 5. **M6 → M7** — this cycle is the last of persistence's three prerequisites |
| Post-fix re-measure (FR-12) | Cycle 5 |
| Settling the two provisional pitch ceilings | Cycle 5, using **this cycle's** FR-24 rejection counters |
| Geometry-change invalidation of the **active** calibration | Cycle 5 — ⚠️ depends on unratified FR-19a. See Open Items |
| Global (OS-level) hotkeys | ⚠️ **OUT of scope.** Qt shortcuts are application-scoped; a genuine global hotkey needs platform-specific hooking. The focus-on-fault rule is the in-scope mitigation, not a full solution |
| Threading the GP fit | ⚠️ **OUT of scope** (DR-14). No FR requires it and the OUT-scope table excludes real-time performance work |

---

## Workshop Plan (4 half-days)

**Day 1**: Diagnostics, error taxonomy, and the pure pipeline
→ Goal: production-ready code for `eye_tracker/diagnostics.py` (every rejection reason registered, rate-limited 1st/10th/100th/then-every-1000th per `(logger, code)`) and `eye_tracker/pipeline.py` — the five silent `return` paths replaced by counted, named rejections. 🔴 **Privacy rule enforced from the first line: no frame, `pts2d` landmark array, blendshape map, or full feature vector may be logged or persisted above DEBUG. This is biometric data.**

**Day 2**: `StatusWindow`
→ Goal: production-ready code for `eye_tracker/status_window.py` and the shared design-tokens module, built to the approved spec — collapsed pill, persistent banner, `CounterTable`, the four actions, full keyboard reachability, `QAccessibleEvent` announcements, and the focus-on-fault rule. 🔴 **AAA contrast verified by computation, not by eye.**

**Day 3**: Capture robustness and the dot
→ Goal: production-ready code for `tracker.py` — graph leak closed, uniform capture configuration on **all** paths, `viable` removed with its intent enforced as an F3 precondition, and camera loss producing a bounded retry with a message. `set_dot_visible` finally called, with the dual outline. Regression tests **#7**, **#8**, **#9** written **failing-first**, output pasted as evidence.

**Day 4**: `print()` migration, integration, stakeholder review and scope sign-off
→ Goal: all 10 `print()` sites migrated with the `[module]` bracket convention preserved as logger names; `T20` clean across `eye_tracker/` and `main.py`; every enumerated failure path demonstrated end-to-end with a stopwatch against the 3-second and 500 ms criteria.

Each day ends with **production-ready, deployable code** — no partial or broken states overnight.

---

## Acceptance Criteria

1. **No silent failure.** Each enumerated failure path produces a visible on-screen message **within 3 seconds** and offers a recovery action. *(Success criterion 11 — FR-20, FR-23)*
2. **Dot hidden on face loss.** Hidden within **500 ms** of the face being lost and restored within 500 ms of reacquisition. Measured, not asserted. *(Success criterion 12 — FR-21)*
3. **The dot is never frozen-and-visible** when the signal is stale, lost, or rejected. *(Failure criterion 2)*
4. **Rejections counted and exposed by reason**, visible in `StatusWindow`. *(FR-24)*
5. **Zero `print()` in `eye_tracker/` or `main.py`** — `ruff`'s `T20` rule passes. All 10 sites migrated. *(FR-25, patterns §3, §13)*
6. **Camera probe failure leaks nothing** and does not silently kill the capture thread. *(FR-30)*
7. **All capture paths configured identically** — asserted by a test that exercises each fallback branch. *(FR-31)*
8. **`viable` is gone and its intent enforced** — an all-dark candidate set raises an F3 fault with Retry, not a silent open of the darkest device. `00-system-overview.md`'s Configuration table corrected. *(FR-32)*
9. **Regression tests for #7, #8, #9 observed failing pre-fix**, output pasted as evidence. *(Success criterion 15 — FR-28)*
10. **AAA contrast verified by computation** for every `StatusWindow` colour pair; the gaze dot's best-edge contrast ≥3:1 on white, black, mid-grey **and** its own red. *(UI/UX spec)*
11. **Every control keyboard-reachable and labelled** — `accessibleName` + `accessibleDescription` present; `QAccessibleEvent` raised on state and banner changes; no state signalled by colour alone. *(UI/UX spec)*
12. **`StatusWindow` never steals focus except on a transition into `Faulted`.** Asserted by test. *(UI/UX spec)*
13. 🔴 **No frame, landmark array, blendshape map or full feature vector is logged or persisted above DEBUG.** Verified by inspection of every new log call. *(Patterns §3)*
14. **GUI-thread affinity asserted** in every new signal receiver. *(Failure criterion 10)*
15. **`ruff check` / `ruff format --check` clean**; functions ≤30 lines or allowlisted **with a reason**; coverage still on track for ≥85%. *(Patterns §13, §14, §15)*

---

## Open Items

| Item | Owner | Needed by | Impact if unresolved |
|---|---|---|---|
| 🔴 **A user who can operate neither mouse nor keyboard cannot self-recover.** FR-20/FR-23 require an offered recovery action; the audience is defined as users who cannot operate a mouse; dwell-click is explicitly OUT of scope | Requirements owner | Recorded, **not solved this cycle** | This is a consequence of the signal-only scope and cannot be closed by UI design. Revisit when dwell-click is scoped |
| **`StatusWindow` as a new UI surface has no numbered FR** — it is derived from FR-20 – FR-24 (DR-12) | Requirements owner | Day 2 | Flagged rather than absorbed. Neither existing window can host any of it: `GazeOverlay` is `WindowTransparentForInput`, `CalibrationWindow` is full-screen and calibration-only |
| **DR-16's two observability changes trace to failure criterion 1, not to a numbered FR** — `NaN` head pose, blendshapes as an F3 precondition | Requirements owner | Day 1 | Both close verified silent failures. Flagged, not silently absorbed |
| **An always-visible window occupies screen area a gaze user may want to look at** — held to ~420 × 44 pt via the collapsed pill | Product owner | Day 2 | A real cost for a gaze-input tool, minimised rather than eliminated |
| **Provisional pitch ceilings** — this cycle's FR-24 counters are the evidence that settles them, together with a measured seating distance | Dev | Feeds **Cycle 5** | Carried forward, not resolved here |

---

## Prerequisites

| Prerequisite | Status |
|---|---|
| **Cycle 3 complete** — session state machine and owned application lifetime exist (M4 → M6) | Gating |
| `docs/ui-ux/ui-ux-spec.md` — design tokens, component map, UX logic, a11y model | ✅ Approved 2026-08-07 |
| `docs/ui-ux/08-visual-foundation.md` — the full token detail the spec compresses | ✅ Approved 2026-08-07 |
| Error taxonomy F0 – F4 and the `EyeTrackerError` hierarchy | From patterns §2; extended here |
| A green test suite with `pytest-qt` | From Cycle 1 |

---

## `shared_files` Touched This Cycle

Two stories touching the same entry **cannot run in parallel**. This is the cycle with the **largest shared-file surface** — sequencing matters most here. From patterns §18.

| File | Concerns |
|---|---|
| `eye_tracker/app.py` | 🔴 Every UX concern wires into the session machine — the serialisation point of this cycle |
| `eye_tracker/errors.py` | `CaptureLostError`, `CameraUnavailableError`, `DetectorUnavailableError` |
| `eye_tracker/diagnostics.py` 🆕 | Every rejection reason registered here |
| `eye_tracker/config.py` | Diagnostics, capture-robustness and `StatusWindow` settings groups |
| `tests/conftest.py` | Fake-capture and `StatusWindow` fixtures |
| `pyproject.toml` | ruff allowlist — `overlay.py` and `status_window.py` `PLR0915` entries |
| `docs/status.md` | `merge=union` already configured |

---

## Cycle Dependencies

**Depends on**: Cycle 3 complete (M4 → M6).
**Blocks**: Cycle 5 (M6 → M7). This is the **last** of persistence's three prerequisites — M3, M5 and M6 must all be complete before a profile can be written.

**Rollback**: per item. M6 is the largest surface in the programme but each item is independent, so a single regression does not force reverting the cycle.

---

## GitHub Release Plan

**Release Option**: `CYCLE-4 — No Silent Failures`
**Release Option ID**: `6236563f`
**Release Field ID**: `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`
**Draft Release**: [untagged-f0dbd571673e3b6ffdda](https://github.com/raminmardani/EyeTracker/releases/tag/untagged-f0dbd571673e3b6ffdda) — publishes as tag `v1.0.0-cycle-4` against `main`

> Downstream (`aire-brownfield-plan`, `aire-qa-triage`) sets the **Release** field to option `6236563f` on every issue it creates for this cycle. Defects [#7](https://github.com/raminmardani/EyeTracker/issues/7), [#8](https://github.com/raminmardani/EyeTracker/issues/8) and [#9](https://github.com/raminmardani/EyeTracker/issues/9) belong to this option.
