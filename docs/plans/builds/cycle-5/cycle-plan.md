# Cycle Plan — Persistence & Accuracy Delta

**Cycle ID**: cycle-5
**BUILDID**: CYCLE-5
**Date**: 2026-08-07
**Author**: AIRE_BUILD_CYCLE_PLANNER
**Migration Phases**: M7 + M8
**Expected Outcome**: Launching with a valid stored profile **skips the 79–141 second calibration ritual entirely** and goes straight to live tracking. A profile created under different feature semantics is **refused with a named reason**, never silently accepted. And the **post-fix accuracy delta is reported with a 95% confidence interval** under the identical protocol — the sign-off artifact for the whole programme.

> **Why persistence is last, and why that is not negotiable.** FR-18 exists because two IN-scope items collide: Theme A changes what the head-pose features *mean*, and Theme E makes calibrations outlive the process. A bundle written before the semantics settled would be refused by its own version gate the moment Cycle 2 shipped — best case wasted work, worst case a user's calibration silently invalidated between two releases. **Failure criterion 3 names a silently-loaded stale profile as the highest-severity outcome available in this scope.**

---

## Scope

### In Scope (this cycle)

| Requirement | Deliverable | Owning file(s) |
|---|---|---|
| **FR-16** | A completed calibration is saveable and restorable across process restarts, eliminating the mandatory 79–141 second ritual on every launch | `eye_tracker/profile.py` 🆕 |
| **FR-17** | A restored calibration produces predictions identical to the pre-save model for the same input feature vector, **within 1e-6 px** | `eye_tracker/profile.py` 🆕 |
| **FR-18** 🔴 | Persisted calibrations carry a **feature-semantics version**. Loading one created under different semantics is refused with a clear message, never silently accepted | `eye_tracker/profile.py` 🆕, `eye_tracker/gaze.py` |
| **FR-19** | The profile records the capture resolution and camera identity it was created under, and refuses under materially different conditions | `eye_tracker/profile.py` 🆕 |
| **FR-12** | Post-fix accuracy re-measured under the **identical** protocol; the change from baseline reported with a **95% confidence interval** | `eye_tracker/evaluation/**`, `docs/evaluation/post-fix-<sha>.md` 🆕 |
| **FR-27** | The **≥85% line coverage gate closes** across `eye_tracker/` and `main.py`, 100% pass — accumulated across all five cycles, verified here | `tests/**` |
| **FR-29** | The remaining invariant locks completed — atomic model download, camera selection preferring face detection over brightness | `tests/invariants/**` |
| **DR-3** | One auto profile slot per capture fingerprint + semantics version; saved automatically after a successful fit, restored automatically at launch. **Zero interaction** — suits the accessibility audience and the single-actor model | `eye_tracker/profile.py` 🆕 |
| **DR-7** | Bundle = ZIP containing `manifest.json` + `model.joblib`, written by atomic temp-then-replace, reusing the codebase's best I/O pattern (`face_mesh.py:56-71`) | `eye_tracker/profile.py` 🆕 |

### Refuse before unpickle — a security control, not a convenience

🔴 **`joblib.load` executes arbitrary code.** The manifest is JSON **inside a ZIP** specifically so that every mismatch check completes **before** deserialisation runs. This ordering is the control; it is enforced by the format itself rather than by developer discipline.

```
1. open the ZIP            2. read manifest.json        3. run ALL 10 refusal checks
4. only then joblib.load   5. verify 3 witness vectors within 1e-6 px
```

**All ten refusal conditions** (DR-4 — refuse on *any* mismatch): semantics version · layout digest · blendshape availability · camera fingerprint · capture resolution · screen geometry · payload digest · library majors · subset identity · witness mismatch.

**Three honest statements that must appear in the delivered code and docs:**

- ⚠️ **The SHA-256 detects corruption, not tampering.** It must never be described as a signature. Anyone who can write the file can rewrite the digest.
- ⚠️ **The camera fingerprint is a change detector, not an identity.** OpenCV exposes no portable device identity; the fingerprint is `(backend_name, index, capture_width, capture_height, capture_fps, screen_width, screen_height)`. **Two identical webcams swapped between the same ports would not be distinguished.** Stated because FR-19's "camera identity" could otherwise be read as stronger than it is.
- ⚠️ **Profiles are trusted-local-only.** There is deliberately **no import-from-path UI**. `skops` — a non-executing format — is recorded as the long-term direction and explicitly deferred this cycle (DR-8).

**The three witness vectors** make FR-17's 1e-6 px identity a **runtime invariant**, not merely a test assertion: stored with the profile, re-predicted after every load, and a mismatch refuses the profile.

### Carried forward from earlier cycles

| Carried item | From | Action this cycle |
|---|---|---|
| 🔴 **The two provisional pitch ceilings (0.35 / 0.45 rad)** — the only invented numbers in the design | Cycle 2 | **Settle them.** Cycle 4's FR-24 rejection counters now supply real data; combined with a measured seating distance (open item 3) they give the screen's subtended vertical angle. If they cannot be settled, the code comment must still say so |
| **Geometry-change invalidation of the *active* calibration** | UI/UX spec | ⚠️ Depends on **unratified FR-19a**. Both windows currently capture `primaryScreen().geometry()` once and never revalidate. If FR-19a is ratified, connect to `primaryScreenChanged` / `geometryChanged` and raise a fault + Recalibrate on change while Live |
| **Documentation corrections** | Cycles 2 & 4 | Head-pose sections in `01-gaze-deep-dive.md` and `03-face-mesh-deep-dive.md` updated now that FR-1/FR-2 have landed |

### Deferred beyond this programme

| Deferred | Reason |
|---|---|
| Dwell-click, scroll, drag, pointer control, OS input injection | Requirements OUT scope. **Revisit now that a baseline exists** — this cycle produces exactly the evidence that decision was waiting for |
| A numeric accuracy target | Deferred until FR-10/FR-11 established what is achievable. **This cycle's delta report is the input to setting one** |
| Removing redundant/collinear feature dimensions (11 of 38 exactly determined; binocular subsets 28–29% redundant) | A modelling change. Deferred until the signal is trustworthy and measurable — **which it now is** |
| GP kernel / model-class redesign (4 of 6 kernels saturate the RBF length-scale ceiling) | Significant, but must not be acted on before a baseline exists to judge it against — **which it now does** |
| `skops` migration | Long-term direction for non-executing serialisation (DR-8) |
| Multi-monitor support · threading the GP fit · real-time performance work | Explicitly OUT of scope |
| Global OS-level hotkeys · dwell-click recovery for users with neither mouse nor keyboard | Recorded limitations, out of scope this programme |

---

## Workshop Plan (4 half-days)

**Day 1**: Manifest, refusal path, and the reader
→ Goal: production-ready code for the manifest schema and **all ten refusal checks**, plus the reader — deliberately **before** the writer, so the refusal path is proven before anything can be written. 🔴 A test attempts to load a v1 profile into v2 code and asserts refusal with a named reason.

**Day 2**: The writer, atomic replace, and witness verification
→ Goal: production-ready code for the writer using atomic temp-then-replace, the three witness vectors, and auto-save after a successful fit. Round-trip test asserting predictions identical within **1e-6 px** in a **genuinely new process**, not merely a new object.

**Day 3**: Auto-restore, coverage close-out, and the carried items
→ Goal: auto-restore at launch with the refusal surfacing as an F4 banner (`refused + reason + calibrate`) in `StatusWindow`; the **≥85% coverage gate closed** with output pasted as evidence; the two provisional pitch ceilings settled from Cycle 4's counters; deep-dive documentation corrected.

**Day 4**: Post-fix measurement, integration, stakeholder review and programme sign-off
→ Goal: **the delta actually measured with a person and a webcam** under the identical Cycle 1 protocol, written to `docs/evaluation/post-fix-<sha>.md` with a 95% CI; full suite green; the whole programme demonstrated end-to-end.

Each day ends with **production-ready, deployable code** — no partial or broken states overnight.

⚠️ **Day 4 is human-gated, exactly as Cycle 1 Day 4 was.** It needs a person, a webcam, and the **identical** protocol — same seating distance, same lighting, same camera, same target layout. A protocol drift between Cycle 1 and here invalidates the comparison and with it success criterion 7.

---

## Acceptance Criteria

1. **Persistence round-trip.** A saved calibration restored in a **new process** produces predictions identical within **1e-6 px** for the same input vector. *(Success criterion 9 — FR-17)*
2. **Version gate.** Loading a calibration whose feature-semantics version does not match the running code is **refused with a clear message**. Verified by a test that attempts exactly this. *(Success criterion 10 — FR-18)*
3. **Delta reported.** Post-remediation accuracy re-measured under the identical protocol, change from baseline reported with a **95% confidence interval**. **Accuracy must not regress.** *(Success criterion 7 — FR-12, failure criterion 4)*
4. **Refuse-before-unpickle proven by test** — all ten checks complete before `joblib.load` is reached. A test with a deliberately mismatched manifest asserts that deserialisation never runs. *(DR-4, DR-7)*
5. **Witness vectors verified at runtime**, not only in tests — a post-load mismatch refuses the profile. *(FR-17)*
6. **Atomic write.** A crash mid-write leaves either the old valid bundle or no bundle — never a valid-looking corrupt one. *(Patterns §4)*
7. **Coverage ≥85%** across `eye_tracker/` and `main.py`, **100% pass**, with **no `skip` or `xfail` used to reach the gate**. Output pasted as evidence. *(Success criterion 14 — FR-27, failure criterion 7)*
8. **All 7 defects have a regression test that fails pre-fix and passes after** — #3 – #9 complete across cycles 2, 3 and 4. *(Success criterion 15 — FR-28)*
9. **All FR-29 invariants locked**, including atomic model download and camera selection preferring face detection over brightness. *(Failure criterion 5)*
10. **The digest is documented as corruption detection, never as a signature**; the fingerprint documented as a change detector, never as identity. *(Security design)*
11. **No `TODO` comments anywhere in delivered code.** *(Failure criterion 8)*
12. **`ruff check` / `ruff format --check` clean** across the entire codebase — not just new files. *(Patterns §13)*
13. **The two provisional pitch ceilings are either settled with recorded evidence, or their code comment states they remain provisional and why.** *(Patterns §16)*

---

## Open Items

| Item | Owner | Needed by | Impact if unresolved |
|---|---|---|---|
| 🔴 **Ratify proposed FR-19a** — screen geometry belongs in the profile key, and a mid-session geometry change must invalidate the **active** calibration, not only stored ones | Requirements owner | **Day 1** | Blocks part of the scope. Without ratification the profile key is incomplete and a resolution change mid-session serves predictions calibrated for a different screen |
| **Target deployment hardware** *(open item 2)* — which cameras, OS versions and screen configurations must be supported | Requirements owner | **Day 1** | FR-19's "materially different conditions" cannot be defined precisely; the 1920×1080 capture request remains unvalidated against real accessibility hardware |
| **Identical evaluation protocol available and repeatable** *(open item 3)* | Dev + requirements owner | **Day 4** | 🔴 The delta is uncomparable and success criterion 7 is unverifiable |
| **The `.venv/` must still be intact** for the coverage gate | Dev | Day 3 | Blocks FR-27's close-out |
| **Whether to set a numeric accuracy target now** — deferred until a baseline existed, and after Day 4 one does | Product owner | Programme sign-off | The next programme has no accuracy bar to build against |
| **Whether dwell-click is now in scope** — the signal-only scope was justified by "binding actions to an unmeasured signal is unsafe". After Day 4 the signal is measured | Product owner | Programme sign-off | The accessibility audience still cannot self-recover without mouse or keyboard. **This is the item that closes that limitation** |

---

## Prerequisites

| Prerequisite | Status |
|---|---|
| **Cycle 2 complete** — head-pose semantics **stable at version 2** (M3 → M7) 🔴 | Gating. A profile written before this is refused by its own gate |
| **Cycle 3 complete** — minimum-usable-calibration enforced (M5 → M7) | Gating |
| **Cycle 4 complete** — failure feedback exists to host the F4 refusal banner (M6 → M7) | Gating |
| **Cycle 1's baseline report** — the comparison basis for M8 | Gating for Day 4 |
| A person, a webcam, and the **identical** lighting, seating distance and camera as Cycle 1 | ⚠️ Human-gated. Must be scheduled |
| FR-19a ratified | ⚠️ Open |

---

## `shared_files` Touched This Cycle

Two stories touching the same entry **cannot run in parallel**. From patterns §18.

| File | Concerns |
|---|---|
| `eye_tracker/gaze.py` | 🔴 The 38-D contract — the semantics version the manifest records. Also touched in Cycle 2 |
| `eye_tracker/app.py` | Auto-restore wiring at launch, auto-save after fit |
| `eye_tracker/errors.py` | `ProfileRefusedError` |
| `eye_tracker/config.py` | `profile.enabled` — the flag that disables the feature entirely |
| `requirements.txt` | `joblib` declared explicitly (already present transitively via scikit-learn — a declaration, not a new dependency) |
| `tests/conftest.py` | Profile-bundle fixtures |
| `docs/status.md` | `merge=union` already configured |

---

## Cycle Dependencies

**Depends on**: Cycles 2, 3 **and** 4 all complete (M3, M5, M6 → M7), plus Cycle 1's baseline (M1 → M8).
**Blocks**: nothing — this is the final cycle and the programme sign-off.

**Rollback**: `profile.enabled = false` disables persistence entirely; deleting the profiles directory removes all state. M8 is purely additive — delete the report.

---

## GitHub Release Plan

**Release Option**: `CYCLE-5 — Persistence & Accuracy Delta`
**Release Option ID**: `3d6ce045`
**Release Field ID**: `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`
**Draft Release**: [untagged-1f9f90321ce25b960d7f](https://github.com/raminmardani/EyeTracker/releases/tag/untagged-1f9f90321ce25b960d7f) — publishes as tag `v1.0.0-cycle-5` against `main`

> Downstream (`aire-brownfield-plan`, `aire-qa-triage`) sets the **Release** field to option `3d6ce045` on every issue it creates for this cycle.
> This is the **programme sign-off release** — publishing it should coincide with the post-fix delta report landing in `docs/evaluation/`.
