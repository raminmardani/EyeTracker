# Cycle Plan — Configuration & Head-Pose Truth

**Cycle ID**: cycle-2
**BUILDID**: CYCLE-2
**Date**: 2026-08-07
**Author**: AIRE_BUILD_CYCLE_PLANNER
**Migration Phases**: M2 + M3
**Expected Outcome**: Each named head-pose feature responds to the physical rotation its name denotes, within ±0.01 rad, leaving the other two unchanged — demonstrated by an automated synthetic-projection test. Feature 10's ±π discontinuity at the neutral head position is gone. **Nodding is gated for the first time**, in both calibration and live inference. And the ~40 tunables scattered across 5 modules resolve to one typed settings tree with a **single** frame-gate definition.

> 🔴 **This is the highest-risk cycle in the programme.** M3 changes every regressor input and both frame gates. Three things make it survivable: Cycle 1's baseline exists to measure against, the synthetic-projection harness needs no hardware, and the gate re-pairing table carries recorded provenance per physical axis.

---

## Scope

### In Scope (this cycle)

| Requirement | Deliverable | Owning file(s) |
|---|---|---|
| **FR-13** | Every tunable currently hardcoded (~40 across 5 modules) settable without editing source. Frozen dataclasses + optional TOML via stdlib `tomllib` — **zero new runtime dependency** (DR-2) | `eye_tracker/config.py` 🆕 |
| **FR-14** | The calibration and live frame-acceptance gates resolve to a **single** definition. Two independent literal blocks exist today and have **already diverged on 4 of 6 thresholds** | `eye_tracker/gates.py` 🆕 |
| **FR-15** | Where the live envelope intentionally differs from the calibration envelope, the difference is an explicit named deviation from a shared base — never an independently maintained copy | `eye_tracker/gates.py` 🆕 |
| **FR-1** | Each head-pose feature responds to the rotation its name denotes: `FEATURE_YAW` to head turn, `FEATURE_PITCH` to nod, `FEATURE_ROLL` to tilt | `eye_tracker/pose.py` 🆕, `eye_tracker/face_mesh.py` |
| **FR-2** | No head-pose feature contains a discontinuity within the operating envelope. Feature 10's ±π wrap at the neutral position eliminated | `eye_tracker/pose.py` 🆕 |
| **FR-3** 🔴 | The frame-rejection gates re-paired to the corrected axes, **preserving the physical envelope each threshold was tuned for**. A rename alone silently retunes the gates and is not acceptable | `eye_tracker/gates.py` 🆕 |
| **FR-4** | Head **pitch** (nodding) gated in both calibration and live inference. Currently ungated on both paths, so a user looking well above or below the monitor is accepted as a good calibration sample | `eye_tracker/gates.py` 🆕 |
| **FR-28** *(partial)* | Failing-first regression tests for defects **#4** and **#5**. The deep-dives already contain executable specifications for both | `tests/regression/test_defect_004.py`, `test_defect_005.py` 🆕 |
| **FR-18** *(partial)* | `FEATURE_SEMANTICS_VERSION` bumped to **2**. The constant and its assertion land here; the gate that consumes it lands in Cycle 5 | `eye_tracker/gaze.py` |

### The gate re-pairing table — FR-3's specific trap

🔴 **The single most dangerous table in this programme.** Today's threshold *names* are wrong but the *numbers* were tuned against whichever axis was physically being measured. Keeping the numbers against corrected names would retune both envelopes in opposite directions — **failure criterion 9** names exactly this.

| Physical axis | Feature | Threshold (calib / live) | Provenance |
|---|---|---|---|
| **Yaw** (head turn) | f8 | **0.45 / 0.55** | Inherited from today's `FEATURE_PITCH`-named gate, which physically gated **yaw** |
| **Pitch** (nod) | f9 | **0.35 / 0.45** | ⚠️ **PROVISIONAL** — nodding has never been gated, so no tuned value exists to inherit |
| **Roll** (tilt) | f10 | **0.60 / 0.70** | Inherited from today's `FEATURE_YAW`-named gate, which physically gated **roll** |

⚠️ **The two provisional pitch numbers are the only invented values in the entire design.** They must be marked provisional **in the code**, stating what would settle them: the FR-24 rejection counters plus a measured seating distance, which together give the screen's subtended vertical angle. **Those counters do not arrive until Cycle 4** — see Open Items.

### Deferred to Next Cycle

| Deferred | Reason |
|---|---|
| Calibration integrity, cancellable timers, recalibration (FR-5 – FR-7, FR-22) | Cycle 3. M2 → M4 in the migration graph; no reason to couple them to the head-pose change |
| Minimum-sample enforcement (FR-8, FR-9) | Cycle 3. Depends on M3 completing (M3 → M5) |
| Failure feedback, `StatusWindow`, capture robustness (FR-20 – FR-25, FR-30 – FR-32) | Cycle 4 |
| Persistence (FR-16 – FR-19) | Cycle 5. **Must be last** — a profile written before the semantics settle would be refused by its own version gate the moment this cycle ships |
| Post-fix re-measure (FR-12) | Cycle 5, once all fixes are in |
| Settling the two provisional pitch ceilings | Cycle 5, once Cycle 4's rejection counters have produced real data |

---

## Workshop Plan (4 half-days)

**Day 1**: Configuration layer
→ Goal: production-ready code for `eye_tracker/config.py` — frozen dataclasses, typed defaults, optional TOML through stdlib `tomllib`, absent file reproducing **today's behaviour exactly**. All ~40 literals inventoried against an explicit checklist, none left at its use site. 🔴 Numerical guards (epsilons) are **not** promoted to configuration — patterns §6 draws that boundary, and success criterion 8 would otherwise turn epsilons into tunables.

**Day 2**: Unified gates with golden tests — behaviour still unchanged
→ Goal: production-ready code for `eye_tracker/gates.py` with **golden tests asserting the resolved values equal today's numbers**, and the live envelope expressed as a named deviation from the calibration base. This day is deliberately behaviour-preserving: it is the safety net that lets Day 3 change one thing at a time.

**Day 3**: Head-pose correction
→ Goal: production-ready code for `eye_tracker/pose.py` — the three `atan2` results rebound to their correct names and the X-rotation unwrapped through `wrap_to_pi`. Regression tests for **#4** and **#5** written **failing-first** and observed failing against pre-fix code, with the output pasted as evidence. `FEATURE_SEMANTICS_VERSION` → 2.

**Day 4**: Gate re-pairing, integration, stakeholder review and scope sign-off
→ Goal: the re-pairing table applied with its provenance recorded in code, pitch gating live on both paths, full suite green, coverage reported, and the axis-correctness demonstration shown to stakeholders.

Each day ends with **production-ready, deployable code** — no partial or broken states overnight.

**Why this day order is not arbitrary**: Days 1–2 change no behaviour and establish the golden baseline. Day 3 changes feature semantics. Day 4 changes the envelope. Three separable changes, each individually revertable, in increasing order of blast radius. Collapsing them would make a regression impossible to attribute.

---

## Acceptance Criteria

1. **Axis correctness.** For each camera axis, applying a known rotation θ changes the correspondingly-named head-pose feature by θ ± 0.01 rad and leaves the other two unchanged within ±0.01 rad. Verified by automated test using the synthetic-projection harness. *(Success criterion 1 — FR-1)*
2. **Continuity.** No head-pose feature changes by more than 0.10 rad for any 1° change of head orientation anywhere in |yaw| ≤ 40°, |pitch| ≤ 30°, |roll| ≤ 30°. Specifically, feature 10 exhibits **no ±π wrap**. *(Success criterion 2 — FR-2)*
3. **Pitch gating.** A synthetic frame at nod > threshold is rejected by **both** the calibration and live gates. *(Success criterion 3 — FR-4)*
4. **Zero hardcoded tunables.** No behavioural constant remains a literal at its use site; the gate thresholds resolve to one definition with any live/calibration difference expressed as an explicit deviation. *(Success criterion 8 — FR-13, FR-14, FR-15)*
5. **Config absent ⇒ today's behaviour.** With no TOML file present, every resolved value equals the pre-cycle literal. Asserted by test.
6. **Regression tests for #4 and #5 observed failing pre-fix**, output pasted as evidence, passing after. *(Success criterion 15 — FR-28)*
7. 🔴 **Gate provenance recorded in code.** Each threshold states which physical axis it was tuned for and which mis-named gate it inherited from. *(FR-3, failure criterion 9)*
8. **Provisional values marked provisional in code**, each stating what would settle it. *(Patterns §16)*
9. **`FEATURE_SEMANTICS_VERSION` = 2**, with the `FEATURE_COUNT` assertion intact. The 38-D contract's **index numbering is unchanged** — only values change. *(Failure criterion 6)*
10. **No verified-correct behaviour regressed** — Cycle 1's invariant tests still pass, in particular eye-local roll invariance remaining exact. *(Failure criterion 5, FR-29)*
11. **`ruff check` and `ruff format --check` clean**; functions ≤30 lines or covered by an allowlist entry **with its reason**. *(Patterns §13, §14)*

---

## Open Items

| Item | Owner | Needed by | Impact if unresolved |
|---|---|---|---|
| 🔴 **The two provisional pitch ceilings (0.35 / 0.45 rad)** — the only invented numbers in the design. Settling them needs the FR-24 rejection counters, **which do not arrive until Cycle 4**, plus a measured seating distance (open item 3) | Dev + requirements owner | Ship provisional **this** cycle; revisit in **Cycle 5** | Gating pitch at an unvalidated ceiling either rejects usable frames or fails to reject bad ones. Better than today's total absence of pitch gating, but explicitly not settled |
| **What `pose_quality` is *supposed* to do** — verified to cancel exactly out of the fusion weights, so it can only change smoothing strength, never the predicted point | Requirements owner | Day 3 | A named quality signal that cannot affect the prediction is either a latent bug or a misnamed smoothing control. Not resolved by this cycle |
| **Target deployment hardware** *(open item 2)* | Requirements owner | Before Cycle 5 | `focal = frame_width` makes translation features resolution-dependent; FR-19's "materially different conditions" stays undefinable |
| **FR-33 outcome carried from Cycle 1** — if the eye signals are crossed, per-eye quality weighting must be corrected or removed | Requirements owner | Day 1 | Adds a concern to `gaze.py`, a `shared_files` entry this cycle already touches |

---

## Prerequisites

| Prerequisite | Status |
|---|---|
| **Cycle 1 complete — the pre-fix baseline recorded in `docs/`** 🔴 | Gating. This is the ordering FR-12 forces; without it success criterion 7 is unverifiable |
| A green test suite and importable package | From Cycle 1 (FR-26, FR-27) |
| The synthetic-projection harness | From the deep-dive verification; needs **no hardware** |
| FR-33 answered | From Cycle 1 Day 1 |
| Golden tests pinning today's gate values | Created Day 2, **before** Day 3 changes anything |

---

## `shared_files` Touched This Cycle

Two stories touching the same entry **cannot run in parallel**. From patterns §18.

| File | Concerns |
|---|---|
| `eye_tracker/config.py` | Created here; every later cycle adds its settings group |
| `eye_tracker/gaze.py` | 🔴 The 38-D contract — semantics version bump. Also touched in Cycle 5 |
| `eye_tracker/diagnostics.py` | Gate rejection reasons registered here |
| `pyproject.toml` | ruff allowlist entries |
| `tests/conftest.py` | Synthetic pose fixtures |
| `docs/status.md` | `merge=union` already configured |

---

## Cycle Dependencies

**Depends on**: Cycle 1 complete — **specifically the recorded baseline**, not merely the test suite.
**Blocks**: Cycle 3 (M2 → M4), Cycle 4 transitively, Cycle 5 (M3 → M7, M3 → M8).

**Rollback**: a single semantics version bump. Reverting restores v1 and any v2 profile is refused — which is precisely why persistence is deferred to the last cycle.

---

## GitHub Release Plan

**Release Option**: `CYCLE-2 — Configuration & Head-Pose Truth`
**Release Option ID**: `e3cc008c`
**Release Field ID**: `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`
**Draft Release**: [untagged-f7eaa10fefee9065b57e](https://github.com/raminmardani/EyeTracker/releases/tag/untagged-f7eaa10fefee9065b57e) — publishes as tag `v1.0.0-cycle-2` against `main`

> Downstream (`aire-brownfield-plan`, `aire-qa-triage`) sets the **Release** field to option `e3cc008c` on every issue it creates for this cycle. Defects [#4](https://github.com/raminmardani/EyeTracker/issues/4) and [#5](https://github.com/raminmardani/EyeTracker/issues/5) belong to this option.
