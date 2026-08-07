# Cycle Plan — Calibration Integrity & Recalibration

**Cycle ID**: cycle-3
**BUILDID**: CYCLE-3
**Date**: 2026-08-07
**Author**: AIRE_BUILD_CYCLE_PLANNER
**Migration Phases**: M4 + M5
**Expected Outcome**: Aborting calibration at any point — including inside the inter-target gap — emits **exactly one** completion event. A user can **recalibrate without restarting the application**, with the smoother and history state reset. And a calibration with too few usable targets produces a **visible refusal** instead of silently proceeding to an unusable model.

> **What a stakeholder sees**: press `Esc` mid-calibration and the application behaves once, not twice. Then press Recalibrate from live tracking and go round again — something the application has never been able to do, because the transition to live is currently a one-way door.

---

## Scope

### In Scope (this cycle)

| Requirement | Deliverable | Owning file(s) |
|---|---|---|
| **FR-5** | Aborting calibration emits **exactly one** completion event, regardless of when abort occurs | `eye_tracker/overlay.py` |
| **FR-6** | Every scheduled state transition in the calibration machine is cancellable by the teardown path. **3 of 5 transitions currently use uncancellable static timers** | `eye_tracker/overlay.py` |
| **FR-7** | The calibration-completion handler is idempotent — a repeat invocation does not re-fit, duplicate the overlay, or duplicate the frame-signal connection | `eye_tracker/app.py` 🆕 |
| **FR-22** | The user can recalibrate **without restarting**, with the smoother and history state reset | `eye_tracker/app.py` 🆕, `eye_tracker/one_euro.py` |
| **FR-8** | Calibration must not proceed to live tracking with fewer usable targets than the model can support. Falling short produces a **visible message**, never silent progression | `eye_tracker/calibration.py` |
| **FR-9** | The precondition is enforced **where it applies** — after non-finite row filtering, inside the fitting component — not upstream on an unfiltered count | `eye_tracker/calibration.py` |
| **FR-28** *(partial)* | Failing-first regression tests for defects **#3** and **#6** | `tests/regression/test_defect_003.py`, `test_defect_006.py` 🆕 |
| **DR-5** | `AppController` moves into the package; `main.py` becomes a ~10-line shim so FR-27's coverage requirement over `main.py` is meetable | `eye_tracker/app.py` 🆕, `main.py` |
| **DR-9** | `CalibrationWindow.finished` → `pyqtSignal(object)` carrying a `CalibrationResult` dataclass. ⚠️ **The design's only deliberate breaking contract change** — internal Qt signal, one consumer, both ends change in one commit | `eye_tracker/overlay.py`, `eye_tracker/app.py` 🆕 |
| **DR-11** | `CalibrationWindow` becomes single-use — constructed per calibration, `WA_DeleteOnClose` set, never reused. **Removes the bug class by lifetime rather than guarding it** | `eye_tracker/overlay.py` |

### The FR-8 minimum — and why its stated basis was unsatisfiable

🔴 **FR-8 as written cannot be satisfied.** It requires the minimum to be "justified against the largest feature subset (currently 25 inputs)" — but the binocular Y subset has **25 columns** and the calibration grid yields **at most 25 targets**. A "samples > input dimensions" rule is unachievable at any reachable target count.

The architecture substitutes an evidence-based **coverage** rule, which is also the better guard given row-major collection:

```
usable_targets >= 15  AND  rows >= 3  AND  cols >= 3  AND  usable >= 0.60 * requested
```

Row-major collection means an early abort produces targets clustered in the top rows — a count-only check would pass a calibration with no lower-screen coverage at all. The `rows`/`cols` terms are what actually catch that.

⚠️ **This is a substitution, not an interpretation.** It is recorded here so the requirements owner ratifies it rather than discovering it in code.

### The verified sequencing constraint

🔴 `QApplication.setQuitOnLastWindowClosed(False)` **must land in this cycle**, and it must land with `StatusWindow`'s quit affordance or an equivalent explicit exit path. Reproduced in the deep-dive: the application survives the calibration → live transition **only** because the overlay is shown synchronously before the calibration window closes. Once lifetime is owned explicitly, the app must quit deliberately — and `StatusWindow` does not arrive until Cycle 4.

**Resolution**: this cycle ships an explicit programmatic exit path in `app.py`; Cycle 4 attaches the user-facing Quit control to it. The migration plan notes M4's items are "one unit of work — revert together".

### Deferred to Next Cycle

| Deferred | Reason |
|---|---|
| `StatusWindow` and all failure messaging (FR-20, FR-21, FR-23, FR-24) | Cycle 4. M4 → M6. This cycle's FR-8 refusal message uses the existing calibration surface; the persistent banner arrives with `StatusWindow` |
| `print()` → logger call-site migration (FR-25) | Cycle 4 |
| Capture robustness (FR-30 – FR-32) | Cycle 4 |
| Persistence (FR-16 – FR-19) | Cycle 5 — **M5 → M7**, so this cycle is one of its three prerequisites |
| Post-fix re-measure (FR-12) | Cycle 5 |

---

## Workshop Plan (4 half-days)

**Day 1**: Application lifetime and the composition root
→ Goal: production-ready code for `eye_tracker/app.py` — the session state machine, `setQuitOnLastWindowClosed(False)` with an explicit exit path, and `main.py` reduced to a shim. ⚠️ The GP fit is **deliberately not threaded** (DR-14): the multi-second freeze is real and documented, but no FR requires fixing it and the requirements' OUT-scope table excludes real-time performance work. Recorded so its absence is not read as an oversight.

**Day 2**: Cancellable calibration machine
→ Goal: production-ready code for `overlay.py` — all 5 scheduled transitions on cancellable member timers, `WA_DeleteOnClose`, single-use lifetime, and the `CalibrationResult` payload. Regression test for **#3** written **failing-first** and observed failing against pre-fix code, with output pasted as evidence.

**Day 3**: Idempotent completion and recalibration
→ Goal: production-ready code for the idempotent completion handler, the Live → Calibrating transition, and `OneEuro2D.reset()`. ⚠️ `one_euro.py` was classified **IMPACT-only** in the requirements; this one additive method is flagged as a delta, not absorbed silently.

**Day 4**: Minimum-usable-calibration enforcement, integration, stakeholder review and scope sign-off
→ Goal: the coverage rule enforced **inside `fit`** after non-finite filtering, with a visible refusal; regression test for **#6** failing-first; full suite green; coverage reported; the abort-once and recalibrate-without-restart behaviours demonstrated live.

Each day ends with **production-ready, deployable code** — no partial or broken states overnight.

---

## Acceptance Criteria

1. **Single completion event.** Aborting calibration at any point, **including within the inter-target gap**, emits exactly one completion event. Verified by an automated test that fails against pre-fix code. *(Success criterion 4 — FR-5, FR-28)*
2. **All 5 scheduled transitions cancellable.** No static `QTimer.singleShot` survives in the calibration machine. *(FR-6)*
3. **Idempotent completion.** A repeat invocation does not re-fit, does not duplicate the overlay, and does not duplicate the frame-signal connection. *(FR-7)*
4. **Recalibration without restart.** The user returns from live tracking to calibration and completes it, with the smoother and history state reset. *(Success criterion 13 — FR-22)*
5. **Minimum-sample enforcement.** Attempting to fit with fewer than the recorded minimum usable targets raises a handled error and surfaces a visible message; it **never** proceeds to live tracking. *(Success criterion 5 — FR-8, FR-9)*
6. **Enforcement is in the right place** — inside `fit`, after non-finite row filtering, not upstream on an unfiltered count. Verified by a test that supplies rows which pass the count but fail the filter. *(FR-9)*
7. **Regression tests for #3 and #6 observed failing pre-fix**, output pasted as evidence. *(Success criterion 15 — FR-28)*
8. **The application still exits.** With `setQuitOnLastWindowClosed(False)` active, an explicit exit path is proven by test — no orphaned process. *(DR-14, verified sequencing constraint)*
9. **GUI-thread affinity asserted** in every new signal receiver. Constructing a receiver off the GUI thread converts Qt's queued connection to a direct one and paints from the capture thread. *(Failure criterion 10, patterns §10)*
10. **No verified-correct behaviour regressed** — Cycle 1's invariants and Cycle 2's axis tests still pass. *(Failure criterion 5)*
11. **`ruff check` / `ruff format --check` clean**; functions ≤30 lines or allowlisted **with a reason**. *(Patterns §13, §14)*

---

## Open Items

| Item | Owner | Needed by | Impact if unresolved |
|---|---|---|---|
| 🔴 **Ratify the FR-8 coverage rule substitution** — FR-8's stated basis ("justified against the largest feature subset") is arithmetically unsatisfiable; the architecture substitutes `≥15 usable AND ≥3 rows AND ≥3 cols AND ≥60% of requested` | Requirements owner | **Day 4** | The cycle ships a minimum the requirement did not authorise. Better than today's silent progression, but it must be an owner's decision |
| **`CalibrationWindow.finished` payload change** — the only deliberate breaking contract change in the design | Requirements owner | Day 2 | Internal, single-consumer, both ends change in one commit. Flagged because the workflow rules prefer additive changes |
| **`one_euro.py` moving from IMPACT to Modified** — one additive `reset()` method | Requirements owner | Day 3 | Requirements classified this module as not-modified. A one-method delta, flagged not absorbed |
| **The explicit exit path is not yet user-reachable** — `setQuitOnLastWindowClosed(False)` lands here, `StatusWindow`'s Quit control lands in Cycle 4 | Dev | Day 1 | Between cycles the only exit is programmatic. Must be covered by test, and Cycle 4 must not slip independently |

---

## Prerequisites

| Prerequisite | Status |
|---|---|
| **Cycle 2 complete** — config layer and unified gates exist (M2 → M4) | Gating |
| Head-pose semantics stable at version 2 (M3 → M5) | Gating for the FR-8 work |
| A green test suite with `pytest-qt` and the offscreen Qt fixture | From Cycle 1 |
| `docs/ui-ux/ui-ux-spec.md` — for the FR-8 refusal wording (`event_then_action`, `never_blame_user`) | ✅ Approved 2026-08-07 |

---

## `shared_files` Touched This Cycle

Two stories touching the same entry **cannot run in parallel**. From patterns §18.

| File | Concerns |
|---|---|
| `eye_tracker/app.py` 🆕 | 🔴 The composition root and session state machine — created here; every later lifecycle and UX concern wires in |
| `eye_tracker/errors.py` | `InsufficientCalibrationDataError` added |
| `eye_tracker/config.py` | Lifetime and minimum-calibration settings groups |
| `tests/conftest.py` | Session-machine and fitted-calibrator fixtures |
| `pyproject.toml` | ruff allowlist |
| `docs/status.md` | `merge=union` already configured |

---

## Cycle Dependencies

**Depends on**: Cycle 2 complete (M2 → M4 for the lifetime work; M3 → M5 for the minimum-sample work).
**Blocks**: Cycle 4 (M4 → M6), Cycle 5 (M5 → M7).

**Rollback**: M4's items revert **together** — the migration plan classifies them as one unit of work, because owning application lifetime without a quit affordance is worse than either state alone. M5 reverts independently.

---

## GitHub Release Plan

**Release Option**: `CYCLE-3 — Calibration Integrity & Recalibration`
**Release Option ID**: `7a2facd4`
**Release Field ID**: `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`
**Draft Release**: [untagged-2182e9844584801d7a3d](https://github.com/raminmardani/EyeTracker/releases/tag/untagged-2182e9844584801d7a3d) — publishes as tag `v1.0.0-cycle-3` against `main`

> Downstream (`aire-brownfield-plan`, `aire-qa-triage`) sets the **Release** field to option `7a2facd4` on every issue it creates for this cycle. Defects [#3](https://github.com/raminmardani/EyeTracker/issues/3) and [#6](https://github.com/raminmardani/EyeTracker/issues/6) belong to this option.
