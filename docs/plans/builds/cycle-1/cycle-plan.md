# Cycle Plan — Foundations & Measurement Baseline

**Cycle ID**: cycle-1
**BUILDID**: CYCLE-1
**Date**: 2026-08-07
**Author**: AIRE_BUILD_CYCLE_PLANNER
**Migration Phases**: M0 + M1
**Expected Outcome**: A green automated test suite runs against an importable package, **and a signed baseline accuracy report exists** — mean and 95th-percentile gaze error in both degrees of visual angle and screen pixels, measured under a documented protocol against a named commit SHA. The eye-pairing question is answered with recorded evidence.

> **Why this cycle exists and why it is first.** Two facts force it. FR-12 requires the accuracy baseline to be measured **before** the Theme A head-pose fixes — if the fix lands first, the pre-fix baseline is unrecoverable without checking out an old commit and re-running a human protocol, and success criterion 7 ("accuracy must not regress") becomes unverifiable. And FR-33's answer can invalidate per-eye quality weighting, which would change the scope of every later cycle. Both are cheap to answer now and expensive to answer later.

---

## Scope

### In Scope (this cycle)

| Requirement | Deliverable | Owning file(s) |
|---|---|---|
| **FR-33** 🔴 | Eye-pairing investigation — determine whether landmark-derived eye geometry and blendshape-derived eye signals describe the **same physical eye**. Designated the first story by requirements decision | `eye_tracker/tools/eye_pairing.py` 🆕 |
| **FR-26** | Packaging metadata so `eye_tracker` imports from `tests/` with no `PYTHONPATH` manipulation. **Hard precondition for FR-27** | `pyproject.toml` 🆕 |
| **FR-25** *(infrastructure only)* | `logging` configuration with levels, controllable destination, and the existing `[module]` bracket convention preserved as logger names. **Call-site migration is Cycle 4** | `eye_tracker/logging_setup.py` 🆕 |
| **FR-27** *(scaffold only)* | Test scaffold — `conftest.py` with offscreen Qt, synthetic `pts2d` builder, stub tracker, fitted-calibrator fixture; the six test directories; the AST import-direction test. **The ≥85% gate itself is met progressively across all five cycles** | `tests/conftest.py` 🆕, `tests/arch/**` 🆕 |
| **FR-10** | Evaluation harness measuring gaze error against known screen targets, reporting mean and 95th-percentile in **both** degrees and pixels | `eye_tracker/evaluation/{metrics,protocol,runner,report}.py` 🆕 |
| **FR-11** | Protocol documented and reproducible — target count and layout, session count, seating distance, lighting, camera. Results recorded in `docs/` with the commit SHA | `docs/evaluation/baseline-<sha>.md` 🆕 |
| **FR-29** *(partial)* | Invariant locks for the three verified-correct behaviours reachable **without hardware**: eye-local roll invariance, the out-of-distribution variance interlock, the smoother's step response | `tests/invariants/**` 🆕 |

**Also in scope — the blocking environment fix**: rebuild `.venv/`. It currently has **no `Scripts/python.exe` and no `pyvenv.cfg`** and cannot be activated. This blocks every test in every cycle. Requirements open item 6.

### Deferred to Next Cycle

| Deferred | Reason |
|---|---|
| Configuration layer (FR-13 – FR-15) | Cycle 2. No dependency forces it earlier, and the golden tests that pin today's gate values are only meaningful immediately before M3 changes them |
| Head-pose correction (FR-1 – FR-4) | Cycle 2. **Must not precede the baseline** — this is the ordering FR-12 forces |
| `print()` → logger call-site migration (FR-25) | Cycle 4. The infrastructure lands here; the 10 call sites across 3 modules migrate with the failure-feedback work that gives them somewhere to surface |
| Reaching ≥85% coverage (FR-27) | Distributed across all five cycles. Tests ship **with** their code — never as a later tier |
| Post-fix re-measure (FR-12) | Cycle 5. Requires the fixes to exist |

---

## Workshop Plan (4 half-days)

**Day 1**: Environment, packaging, and the blocking investigation
→ Goal: production-ready code for `pyproject.toml` (ruff + pytest + coverage config), a rebuilt `.venv/` with `pytest --version` proven, and **FR-33 answered** — `eye_pairing.py` run against a real wink, with the `A_EAR` / `A_BLINK` / `B_EAR` / `B_BLINK` traces recorded. 🔴 **Decision gate at end of day: if the signals are crossed, per-eye quality weighting is invalid and Cycle 2's scope changes.**

**Day 2**: Test scaffold and the dependency rule
→ Goal: production-ready code for `tests/conftest.py` (offscreen Qt, synthetic `pts2d`, stub tracker, fitted-calibrator fixture), all six test directories, and `tests/arch/test_import_direction.py` **passing** — the dependency rule enforced by an AST test rather than a directory restructure (DR-10).

**Day 3**: Evaluation harness and invariant locks
→ Goal: production-ready code for `eye_tracker/evaluation/` — `metrics.py` (degrees **and** pixels), `protocol.py`, `runner.py`, `report.py` — plus `logging_setup.py`, plus the three hardware-free invariant tests from FR-29.

**Day 4**: Baseline measurement, integration, stakeholder review and scope sign-off
→ Goal: **the baseline actually measured with a person and a webcam**, written to `docs/evaluation/baseline-<sha>.md` with the full protocol and commit SHA; full suite green; coverage reported.

Each day ends with **production-ready, deployable code** — no partial or broken states overnight.

⚠️ **Day 4 is human-gated, not a build step.** M1 needs a person, a webcam, controlled lighting and a measured seating distance. It cannot be completed by an agent alone, and it cannot be compressed. If the protocol specifics (open item 3) are not settled by Day 3, Day 4 slips and the whole programme slips with it — Cycle 2 cannot start without this baseline.

---

## Acceptance Criteria

1. **FR-33 answered with evidence.** The wink trace is recorded in `docs/`, and per-eye quality weighting is explicitly either confirmed sound or scheduled for correction. *(Success criterion 16)*
2. **Baseline recorded.** `docs/evaluation/baseline-<sha>.md` states mean and 95th-percentile gaze error in **degrees and pixels**, the full protocol (target count and layout, session count, seating distance, lighting, camera), and the commit SHA measured against. *(Success criterion 6 — FR-10, FR-11)*
3. **`eye_tracker` and `main` import from `tests/` with no `sys.path` manipulation and no `PYTHONPATH`.** *(FR-26)*
4. **`pytest` runs green from a rebuilt `.venv/`**, with output pasted as evidence. *(FR-27, open item 6)*
5. **`tests/arch/test_import_direction.py` passes** — no core module imports outward. *(DR-10, patterns §8)*
6. **The three hardware-free invariants are locked**: eye-local roll invariance is bit-identical across 40° of rotation; the variance interlock clamps (σ 18–23 px in-distribution vs ~6000 px extrapolating); the smoother reaches 90% in 1 frame at scale 1.0 and 6 frames at 0.011. *(FR-29)*
7. **`ruff check` and `ruff format --check` are clean** on all new code — zero warnings. *(Patterns §13)*
8. **No `print()` in any new file.** The `T20` rule is active from this cycle onward. *(FR-25, patterns §13)*
9. **Zero behavioural change to the existing application.** M0's rollback is "revert; nothing behavioural changed" — that must be literally true.

---

## Open Items

| Item | Owner | Needed by | Impact if unresolved |
|---|---|---|---|
| **Evaluation protocol specifics** — seating distance, lighting, target count, number of sessions *(requirements open item 3)* | Requirements owner | **Day 3** | 🔴 The baseline is not reproducible, so FR-11 fails and the Cycle 5 delta has no valid comparison basis |
| **`.venv/` rebuild** *(requirements open item 6)* | Dev | **Day 1** | 🔴 Blocks every test in every cycle |
| **9 requirements-reconciliation items** awaiting ratification — chiefly proposed **FR-19a** (screen geometry in the profile key) and the UI/UX finding that a geometry change must invalidate the **active** calibration | Requirements owner | Before Cycle 5 | FR-19's scope is unsettled; Cycle 5 would build to an unratified requirement |
| **Target completion date / hard deadline** *(requirements open item 1)* | Product owner | Before workshop scheduling | Cycles are sequenced by dependency but carry no dates |
| **FR-33 outcome** — if the eye signals are crossed, does per-eye weighting get corrected or removed? | Requirements owner | **End of Day 1** | Cycle 2's scope changes; `gaze.py` gains a concern |

---

## Prerequisites

Must exist before workshops begin.

| Prerequisite | Status |
|---|---|
| `docs/requirements.md` — 33 FRs, 16 success criteria, 10 failure criteria | ✅ Approved 2026-08-06 |
| `docs/architecture/design/02-target-architecture-brownfield.md` — 17 decision records, M0–M8 graph | ✅ Approved 2026-08-07 |
| `docs/architecture/design/03-patterns-and-standards-brownfield.md` — 16 pattern sections, boundary map | ✅ Approved 2026-08-07 |
| A working Python 3.14.6 interpreter | 🔴 **BLOCKED** — `.venv/` has no interpreter and no `pyvenv.cfg` |
| A webcam, a person, and controlled lighting for Day 4 | ⚠️ Human-gated. Must be scheduled, not assumed |
| Settled evaluation protocol | ⚠️ Open item 3 |

---

## `shared_files` Touched This Cycle

Two stories touching the same entry **cannot run in parallel**. From patterns §18.

| File | Concerns |
|---|---|
| `pyproject.toml` | Packaging + ruff + pytest + coverage — every story in this cycle |
| `tests/conftest.py` | Every test concern adds fixtures |
| `requirements.txt` | Dev dependency declarations (pytest, pytest-cov, pytest-qt, ruff) |
| `docs/status.md` | `merge=union` already configured |

---

## Cycle Dependencies

**Depends on**: nothing — this is the entry point.
**Blocks**: all four remaining cycles. Cycle 2 cannot start until the baseline exists (FR-12).

---

## GitHub Release Plan

**Release Option**: `CYCLE-1 — Foundations & Measurement Baseline`
**Release Option ID**: `cd228d8a`
**Release Field ID**: `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`
**Draft Release**: [untagged-871d034760e821d8adc4](https://github.com/raminmardani/EyeTracker/releases/tag/untagged-871d034760e821d8adc4) — publishes as tag `v1.0.0-cycle-1` against `main`

> Downstream (`aire-brownfield-plan`, `aire-qa-triage`) sets the **Release** field to option `cd228d8a` on every issue it creates for this cycle.
> ⚠️ The draft URL contains `untagged-…` because a draft release creates **no git tag** until it is published — verified: 0 tags exist on the repository.
