# Requirements — EyeTracker: Accurate Gaze Signal for Hands-Free Input

**Date**: 2026-08-06
**Author**: ANALYST_PM_BROWNFIELD
**Status**: Approved — 2026-08-06
**Source**: Local definition (PATH L), grounded in verified brownfield analysis + 7 GitHub defects (#3–#9)

---

## Project Type

- [x] Brownfield (modifying existing system)
- [ ] MVP (Proof of Concept acceptable)
- [x] Production-Ready (NO TODO comments allowed)

## Timeline

**Target Completion**: **TBD** — not supplied at requirements definition
**Hard Deadline**: **TBD** — not supplied at requirements definition

> ⚠️ Both are open. They do not block architecture or planning, but `aire-build-cycles` needs at least a target to sequence against.

---

## Project Overview

EyeTracker estimates where a user is looking on screen using only a consumer webcam. This body of work establishes it as a **trustworthy gaze signal for hands-free input and accessibility use** — users who cannot operate a mouse.

The work is deliberately **signal-and-measurement only**. No clicking, scrolling or pointer control is delivered in this cycle. The rationale is evidential rather than conservative: the head-pose input to the prediction model is **verifiably broken** (defects #4 and #5), and no measurement of gaze error exists anywhere in the system. Binding user actions to a signal whose error is unknown, derived from mislabelled axes and a feature that jumps 6.21 radians at the exact head position a user holds while reading their screen, would be unsafe for the intended audience.

The cycle therefore delivers, in dependency order:

1. **Correct the gaze signal at its source** — the head-pose defects that corrupt every regressor input.
2. **Make accuracy measurable** — an evaluation harness and a recorded baseline, so "improve accuracy" becomes a testable claim rather than a directional aspiration.
3. **Close the remaining defects** and add the foundations that make further work safe: tests, configuration, calibration persistence, and failure feedback appropriate to an accessibility audience.

---

## Current System Context

**Architecture**: Single-process Python desktop monolith. Layered pipeline — one daemon capture thread produces a 38-dimensional feature vector per frame across a Qt signal boundary to GUI-thread consumers. Strictly one-way, acyclic, zero locks. Evidence: [00-system-overview.md](docs/architecture/current/00-system-overview.md)

**Tech Stack**: Python 3.14.6 · MediaPipe 0.10.35 (Tasks API only) · OpenCV 4.14.0.94 · NumPy 2.5.1 · scikit-learn 1.9.0 · PyQt6 6.11.0

**Data Layer**: **None.** No database, no ORM, no persistence. The only durable artifact is a cached MediaPipe model file. Calibration is discarded on exit.

**Integration Points**: One outbound (`storage.googleapis.com`, one-time model download). One inbound (local webcam via OpenCV).

**Test Infrastructure**: **None.** 0% coverage across 1,295 LOC.

**Configuration**: **None.** ~40 tunables are literals across 5 modules.

**Authorization**: **None.** No users, accounts, sessions or permissions exist anywhere in the codebase.

**Affected Modules**:

| Module | Path | Role in this work |
|---|---|---|
| Landmark adapter | [face_mesh.py](eye_tracker/face_mesh.py) | **Primary** — owns both head-pose defects |
| Calibration | [calibration.py](eye_tracker/calibration.py) | **Primary** — persistence, minimum-sample guard |
| UI / calibration machine | [overlay.py](eye_tracker/overlay.py) | **Primary** — abort integrity, failure UX, dot visibility |
| Orchestration | [main.py](main.py) | **Primary** — config wiring, recovery paths, gate unification |
| Capture | [tracker.py](eye_tracker/tracker.py) | **Secondary** — leak, fallback config, failure signalling |
| Feature extraction | [gaze.py](eye_tracker/gaze.py) | **Secondary** — eye-pairing investigation only |
| Smoothing | [one_euro.py](eye_tracker/one_euro.py) | **Indirect** — not modified; consumes changed variance |

---

## Roles & Permissions Matrix

> Canonical role registry. `Origin` = `Existing` (already enforced in the codebase, per deep-dive) or `New` (introduced by this work).

| Role (canonical) | Description | Key Permissions (allow) | Explicitly Denied | Auth Source | Origin |
|------------------|-------------|-------------------------|-------------------|-------------|--------|
| Local User | The single person operating the application on their own machine. Runs calibration, uses the gaze signal, manages their own saved calibration profiles. | `calibration:run`, `calibration:save-own`, `calibration:load-own`, `calibration:delete-own`, `config:edit-local`, `tracking:start`, `tracking:stop` | — (no other actor exists) | Operating-system user account — the application performs no authentication of its own | Existing |

**Permission keys**: `calibration:run`, `calibration:save-own`, `calibration:load-own`, `calibration:delete-own`, `config:edit-local`, `tracking:start`, `tracking:stop`

**Notes**: **No role variation — single actor.** Verified across all 8 source files: the codebase contains no authentication, no authorization, no user model, no sessions and no multi-user concept. Calibration profiles introduced by FR-16 are per-machine files owned by the OS user; they are not an access-control mechanism and must not be presented as one. Any future multi-user or remote capability would be a new architectural concern, not an extension of this matrix.

---

## Functional Requirements

Each requirement cites its evidence. `[#N]` = GitHub defect. All 7 defects are IN scope.

### Theme A — Head-Pose Signal Correctness *(prerequisite for all accuracy work)*

| ID | Requirement | Evidence |
|---|---|---|
| **FR-1** | Each head-pose feature must respond to the physical rotation its name denotes: `FEATURE_YAW` to head turn, `FEATURE_PITCH` to nod, `FEATURE_ROLL` to tilt. | [#4], [03-face-mesh](docs/architecture/current/03-face-mesh-deep-dive.md) |
| **FR-2** | No head-pose feature may contain a discontinuity within the operating envelope. Feature 10's ±π wrap at the neutral head position must be eliminated. | [#5] |
| **FR-3** | The frame-rejection gates must be re-paired to the corrected axes, preserving the *physical* envelope each threshold was tuned for. A rename alone silently retunes the gates and is not acceptable. | [#4], [07-main](docs/architecture/current/07-main-deep-dive.md) |
| **FR-4** | Head **pitch** (nodding) must be gated in both calibration and live inference. It is currently ungated on both paths, so a user looking well above or below the monitor is accepted as a good calibration sample. | [#4] |

### Theme B — Calibration Integrity & Lifecycle

| ID | Requirement | Evidence |
|---|---|---|
| **FR-5** | Aborting calibration must emit exactly one completion event, regardless of when abort occurs. | [#3] |
| **FR-6** | Every scheduled state transition in the calibration machine must be cancellable by the teardown path. | [#3], [05-overlay](docs/architecture/current/05-overlay-deep-dive.md) |
| **FR-7** | The calibration-completion handler must be idempotent — a repeat invocation must not re-fit, duplicate the overlay, or duplicate the frame-signal connection. | [#3] |
| **FR-8** | Calibration must not proceed to live tracking with fewer usable targets than the model's input dimensionality can support. The minimum must be justified against the largest feature subset (currently 25 inputs) and recorded. Falling short must produce a visible message, not silent progression. | [#6], [02-calibration](docs/architecture/current/02-calibration-deep-dive.md) |
| **FR-9** | The minimum-sample precondition must be enforced where it applies — after non-finite row filtering, inside the fitting component — not upstream on an unfiltered count. | [#6] |

### Theme C — Accuracy Measurement *(no numeric target until a baseline exists)*

| ID | Requirement | Evidence |
|---|---|---|
| **FR-10** | A repeatable evaluation harness must measure gaze error against known screen targets and report mean and 95th-percentile error in **both** degrees of visual angle and screen pixels. | User decision: establish baseline first |
| **FR-11** | The evaluation protocol must be documented and reproducible: target count and layout, session count, seating distance, lighting, and camera. Results must be recorded in `docs/` with the commit SHA they were measured against. | Rulebook: measurable criteria |
| **FR-12** | A baseline must be measured **before** the Theme A fixes and re-measured after, with the delta and its confidence interval reported. | User decision: objective is accuracy |

### Theme D — Configuration Layer

| ID | Requirement | Evidence |
|---|---|---|
| **FR-13** | Every tunable currently hardcoded (~40 across 5 modules) must be settable without editing source. | [00-system-overview](docs/architecture/current/00-system-overview.md) |
| **FR-14** | The calibration and live frame-acceptance gates must resolve to a **single** definition. Two independent literal blocks exist today and have already diverged on 4 of 6 thresholds. | [05-overlay](docs/architecture/current/05-overlay-deep-dive.md), [07-main](docs/architecture/current/07-main-deep-dive.md) |
| **FR-15** | Where the live envelope intentionally differs from the calibration envelope, the difference must be expressed as an explicit, documented deviation from a shared base — not as an independently maintained copy. | [07-main](docs/architecture/current/07-main-deep-dive.md) |

### Theme E — Calibration Persistence

| ID | Requirement | Evidence |
|---|---|---|
| **FR-16** | A completed calibration must be saveable and restorable across process restarts, eliminating the mandatory 79–141 second ritual on every launch. | User decision: IN scope |
| **FR-17** | A restored calibration must produce predictions identical to the pre-save model for the same input feature vector, within 1e-6 px. | Derived from FR-16 |
| **FR-18** | 🔴 Persisted calibrations must carry a **feature-semantics version**. Loading a calibration created under different feature semantics must be refused with a clear message, never silently accepted. | See *Critical Interaction* below |
| **FR-19** | Persisted calibration must record the capture resolution and camera identity it was created under, and refuse or warn when restored under materially different conditions. | [#7], [03-face-mesh](docs/architecture/current/03-face-mesh-deep-dive.md) |

> 🔴 **Critical interaction — FR-18 exists because two IN-scope items collide.** Theme A changes what the head-pose features *mean* (their values, not their indices). Theme E makes calibrations outlive the process. Without versioning, a calibration saved before the head-pose fix would be silently loaded into a post-fix system whose features carry different semantics — producing confidently wrong gaze predictions with no error, no warning, and no way for the user to attribute the failure. For an accessibility audience this is the highest-severity latent hazard in this scope. Versioning is not optional and its sequencing matters: persistence must not ship before the semantics are stable, or it must ship with the version gate already enforcing.

### Theme F — Failure Feedback & Guided Recovery *(accessibility-driven)*

| ID | Requirement | Evidence |
|---|---|---|
| **FR-20** | Every capture-thread failure path must surface an actionable on-screen message. Four such paths currently terminate the producer with only a `print()` to a stream a windowed application discards. | [04-tracker](docs/architecture/current/04-tracker-deep-dive.md) |
| **FR-21** | When the face is lost, the gaze dot must be **hidden**, not frozen at its last position. A frozen dot is indistinguishable from a confident, steady gaze — unacceptable for an input signal. The required API (`set_dot_visible`) already exists and is never called. | [05-overlay](docs/architecture/current/05-overlay-deep-dive.md) |
| **FR-22** | The user must be able to recalibrate without restarting the application. The transition to live tracking is currently a one-way door. | [07-main](docs/architecture/current/07-main-deep-dive.md) |
| **FR-23** | Camera failure must offer a retry path rather than an unbounded silent retry loop. A camera unplugged mid-session currently spins at ~100 Hz forever, emitting nothing. | [04-tracker](docs/architecture/current/04-tracker-deep-dive.md) |
| **FR-24** | Frame rejections must be counted and exposed by reason. Five silent `return` paths in the live pipeline currently make "the dot is sluggish" undiagnosable. | [07-main](docs/architecture/current/07-main-deep-dive.md) |
| **FR-25** | Diagnostics must move from `print()` to structured logging with levels and a controllable destination. The existing `[module]` bracket convention is sound and should be preserved as logger names. | [04-tracker](docs/architecture/current/04-tracker-deep-dive.md) |

### Theme G — Test & Packaging Foundations

| ID | Requirement | Evidence |
|---|---|---|
| **FR-26** | Packaging metadata (`pyproject.toml`) must exist so `eye_tracker` is importable from a test directory without `PYTHONPATH` manipulation. **This is a hard precondition for FR-27.** | [00-system-overview](docs/architecture/current/00-system-overview.md) |
| **FR-27** | An automated test suite must reach ≥85% line coverage across `eye_tracker/` and `main.py`, with 100% pass. | AIRE core rule |
| **FR-28** | Every defect fixed in this cycle must be covered by a regression test that fails against the pre-fix code. The deep-dive already specifies failing test cases for #3, #4 and #5. | Rulebook: evidence-based |
| **FR-29** | The verified-correct behaviours must be locked by tests so remediation cannot silently regress them: eye-local roll invariance, the out-of-distribution variance interlock, and the smoother's step response. | [01-gaze](docs/architecture/current/01-gaze-deep-dive.md), [02-calibration](docs/architecture/current/02-calibration-deep-dive.md), [06-one-euro](docs/architecture/current/06-one-euro-deep-dive.md) |

### Theme H — Capture Robustness

| ID | Requirement | Evidence |
|---|---|---|
| **FR-30** | A failure during camera probing must not leak the MediaPipe graph or kill the capture thread silently. | [#8] |
| **FR-31** | Every capture returned by camera selection must be configured identically. Two fallback paths currently skip configuration, which changes the assumed focal length and therefore the meaning of head-pose translation features. | [#7] |
| **FR-32** | The `viable` camera-viability check must either be enforced or removed, and the system overview's configuration table corrected accordingly. It is currently computed, never read, and documented as live configuration. | [#9] |

### Theme I — Blocking Investigation

| ID | Requirement | Evidence |
|---|---|---|
| **FR-33** | 🔴 **First story of the plan.** Determine whether the landmark-derived eye geometry and the blendshape-derived eye signals describe the **same physical eye**. Procedure: log `A_EAR`, `A_BLINK`, `B_EAR`, `B_BLINK`; wink one eye; observe whether the same letter's EAR falls while its BLINK rises. If crossed, per-eye quality weighting is invalid and must be corrected or removed before accuracy work is trusted. | [01-gaze](docs/architecture/current/01-gaze-deep-dive.md) |

---

## Success Criteria (MUST HAVE)

Measurable and testable. No directional claims.

1. **Axis correctness** — For each camera axis, applying a known rotation θ changes the correspondingly-named head-pose feature by θ ± 0.01 rad and leaves the other two unchanged within ±0.01 rad. Verified by automated test using the synthetic-projection harness. *(FR-1)*
2. **Continuity** — No head-pose feature changes by more than 0.10 rad for any 1° change of head orientation anywhere in the envelope |yaw| ≤ 40°, |pitch| ≤ 30°, |roll| ≤ 30°. Specifically, feature 10 exhibits no ±π wrap. *(FR-2)*
3. **Pitch gating** — A synthetic frame at nod > threshold is rejected by both the calibration and live gates. *(FR-4)*
4. **Single completion event** — Aborting calibration at any point, including within the inter-target gap, emits exactly one completion event. Verified by an automated test that fails against the current code. *(FR-5, FR-28)*
5. **Minimum-sample enforcement** — Attempting to fit with fewer than the recorded minimum usable targets raises a handled error and surfaces a visible message; it never proceeds to live tracking. *(FR-8, FR-9)*
6. **Baseline recorded** — A gaze-error baseline exists in `docs/`, stating mean and 95th-percentile error in degrees and pixels, the full protocol, and the commit SHA measured against. *(FR-10, FR-11)*
7. **Delta reported** — Post-remediation accuracy is re-measured under the identical protocol and the change from baseline is reported with a 95% confidence interval. Accuracy must not regress. *(FR-12)*
8. **Zero hardcoded tunables** — No behavioural constant remains a literal at its use site; the gate thresholds resolve to one definition with any live/calibration difference expressed as an explicit deviation. *(FR-13, FR-14, FR-15)*
9. **Persistence round-trip** — A saved calibration restored in a new process produces predictions identical within 1e-6 px for the same input vector. *(FR-17)*
10. **Version gate** — Loading a calibration whose feature-semantics version does not match the running code is refused with a clear message. Verified by a test that attempts exactly this. *(FR-18)*
11. **No silent failure** — Each enumerated failure path produces a visible on-screen message within 3 seconds of the failure, and offers a recovery action. *(FR-20, FR-23)*
12. **Dot hidden on face loss** — The gaze dot is hidden within 500 ms of the face being lost and restored within 500 ms of reacquisition. *(FR-21)*
13. **Recalibration without restart** — The user can return from live tracking to calibration and complete it, with the smoother and history state reset. *(FR-22)*
14. **Coverage** — ≥85% line coverage across `eye_tracker/` and `main.py`; 100% of tests pass. *(FR-27)*
15. **Regression tests exist** — Every one of the 7 defects has a test that fails against pre-fix code and passes after. *(FR-28)*
16. **Eye pairing resolved** — FR-33 is answered with recorded evidence, and per-eye quality weighting is either confirmed sound or corrected. *(FR-33)*

## Failure Criteria (UNACCEPTABLE)

1. **Any silent failure survives.** A path that fails without telling the user is a defect in this cycle regardless of severity, given the accessibility audience.
2. **A frozen dot presented as a live one.** The dot must never remain visible and stationary when the signal is stale, lost, or rejected.
3. **A persisted calibration loaded across a feature-semantics change.** Confidently wrong predictions with no error and no attribution path — the highest-severity outcome available in this scope.
4. **Accuracy regresses** relative to the recorded baseline under the identical protocol.
5. **A verified-correct behaviour regresses**: eye-local roll invariance ceases to be exact; the out-of-distribution variance interlock stops clamping; camera selection stops preferring face detection over brightness; the model download stops being atomic.
6. **The 38-D contract changes index numbering** without every one of its four consumers being updated in the same change.
7. **Coverage below 85%**, or any test skipped or marked expected-failure to reach the gate.
8. **`TODO` comments** in delivered code.
9. **Gate thresholds renamed without re-pairing** — preserving the literal numbers against corrected axis names silently retunes the physical envelope. This is the specific trap FR-3 exists to prevent.
10. **Concurrency model broken** — introducing shared mutable state across the capture/GUI boundary, or constructing a signal receiver off the GUI thread, converting Qt's queued connection to a direct one.

---

## Technical Constraints

- **Patterns to follow**: the 45 patterns catalogued across the deep-dives. Specifically preserve — named vector indices, epsilon-guarded division at the point of construction, atomic temp-then-replace for any file write (directly applicable to FR-16), factory-function definition for anything instantiated more than once, and platform workarounds documented with their observed symptom.
- **Database**: none exists and none is introduced. Persistence (FR-16) must be local file-based, following the atomic-write pattern already established in [face_mesh.py:56-71](eye_tracker/face_mesh.py#L56-L71).
- **Test coverage**: minimum 85%.
- **Tests location**: `tests/` — **does not exist yet**; blocked on FR-26.
- **Runtime**: Python 3.14.6 with the bounded dependency set in `requirements.txt`. `opencv-contrib-python` must stay major-aligned with `opencv-python`.
- **Single primary display.** Multi-monitor is explicitly OUT; both windows may continue to size to the primary screen.
- 🔴 **Verified sequencing constraint**: `QApplication.setQuitOnLastWindowClosed(False)` — or constructing the overlay up front — **must land before** the blocking GP fit is moved off the GUI thread. Reproduced: the application survives the calibration→live transition only because the overlay is shown synchronously before the calibration window closes. Threading the fit first causes a silent application exit. See [05-overlay](docs/architecture/current/05-overlay-deep-dive.md).
- **GUI-thread affinity** is an unasserted correctness dependency: both frame-signal receivers must be constructed on the GUI thread or Qt switches to direct connections and paints from the capture thread.
- **Environment**: `.venv/` currently lacks `Scripts/python.exe` and `pyvenv.cfg` and cannot be activated. Must be rebuilt before FR-27 can run.

## Quality Gates

- All tests pass (100%)
- Coverage ≥85%
- Follows existing patterns (per the 45-pattern catalogue)
- Code review approved
- No TODO comments
- Every defect fix has a regression test that fails pre-fix
- Accuracy re-measured and reported against baseline before sign-off

---

## Explicit Scope

### IN Scope

- All 7 defects: [#3](https://github.com/raminmardani/EyeTracker/issues/3), [#4](https://github.com/raminmardani/EyeTracker/issues/4), [#5](https://github.com/raminmardani/EyeTracker/issues/5), [#6](https://github.com/raminmardani/EyeTracker/issues/6), [#7](https://github.com/raminmardani/EyeTracker/issues/7), [#8](https://github.com/raminmardani/EyeTracker/issues/8), [#9](https://github.com/raminmardani/EyeTracker/issues/9)
- Head-pose axis correction and de-discontinuation (FR-1 – FR-4)
- Gaze-error measurement harness, protocol, baseline and post-fix delta (FR-10 – FR-12)
- Configuration layer with unified frame gates (FR-13 – FR-15)
- Calibration persistence with feature-semantics versioning (FR-16 – FR-19)
- Failure feedback and guided recovery, incl. recalibration without restart and dot hiding (FR-20 – FR-25)
- Packaging metadata and test suite to ≥85% (FR-26 – FR-29)
- Capture robustness fixes (FR-30 – FR-32)
- Eye-pairing investigation (FR-33)

### OUT of Scope

| Excluded | Rationale |
|---|---|
| Dwell-click, scroll, drag, pointer control, OS input injection | User decision: signal + baseline only. Binding actions to an unmeasured signal is unsafe for this audience. Revisit once a baseline exists |
| A numeric accuracy target | Deferred by decision until FR-10/FR-11 establish what is achievable. Setting one now would be invented, not derived |
| Multi-monitor support | Explicitly deselected. Primary-display-only remains acceptable; predictions stay clipped to its bounds |
| The dead `mp.solutions` branch decision | Not among the 7 defects and not accuracy-relevant. Remains tracked as technical debt in the system overview; it would zero 12 features if ever activated |
| Removing redundant/collinear feature dimensions | Real (11 of 38 exactly determined, binocular subsets 28–29% redundant) but a modelling change. Deferred to architecture once the head-pose signal is trustworthy and measurable |
| GP kernel / model-class redesign | The near-linear-regime finding is significant but must not be acted on before a baseline exists to judge it against |
| Multi-user, authentication, remote or cloud capability | No such concept exists in the codebase; single-actor by design |
| Changing the 38-D contract's index numbering | Values change under Theme A; positional numbering does not |
| Real-time performance optimisation (full-window repaint, probe latency) | Documented but not accuracy- or safety-relevant this cycle |

### IMPACT Scope (indirect — modules affected but not directly modified)

| Area | Impact |
|---|---|
| [one_euro.py](eye_tracker/one_euro.py) | Not modified, but consumes `fused_var`. Corrected head-pose features change the fitted models, therefore the variance distribution, therefore smoothing behaviour. The measured baseline scale (≈0.78–0.81 in normal operation) may shift |
| [gaze.py](eye_tracker/gaze.py) | Feature *values* at indices 8/9/10 change meaning. All four consumers read by index and will see different distributions |
| **All existing calibrations** | Invalidated by Theme A. This is the entire reason FR-18 exists |
| Live gate thresholds | Their effective physical envelope changes when axes are corrected, even if the numbers are preserved (FR-3) |
| [tracker.py](eye_tracker/tracker.py) probe path | Configuration changes (FR-13) alter probe cost and therefore startup latency |
| Deep-dive documents | [00-system-overview](docs/architecture/current/00-system-overview.md) needs its `viable` configuration row corrected (FR-32); head-pose sections in [01](docs/architecture/current/01-gaze-deep-dive.md) and [03](docs/architecture/current/03-face-mesh-deep-dive.md) need updating once FR-1/FR-2 land |

---

## Design References

**Location**: `SPEC/references/`

| File | Type | Description | Used In |
|------|------|-------------|---------|
| *(none)* | — | Directory contains only empty `builds/` and `devops/` subfolders | — |

**Note**: No PRD, UI design, legacy specification or build document was available. Verified at STEP 0 of this workflow — 0 files, 0 requiring `aire read`. Nothing in this document is constrained by prior approved material; every requirement derives from the verified codebase analysis or from explicit user decisions recorded in this session. **No Build Sequence is defined** — `SPEC/references/builds/` is empty, so `aire-build-cycles` will derive cycles from this document rather than from supplied build files.

---

## Patterns to Follow

| Pattern | Reference |
|---------|-----------|
| Named vector indices over magic offsets | [01-gaze-deep-dive.md](docs/architecture/current/01-gaze-deep-dive.md) — Pattern 1 |
| Epsilon-guarded division at point of construction | [01-gaze-deep-dive.md](docs/architecture/current/01-gaze-deep-dive.md) — Pattern 3 |
| Factory function for repeated construction | [02-calibration-deep-dive.md](docs/architecture/current/02-calibration-deep-dive.md) — Pattern 1 *(the model for FR-14)* |
| Atomic temp-then-replace file write | [03-face-mesh-deep-dive.md](docs/architecture/current/03-face-mesh-deep-dive.md) — Pattern 1 *(directly applicable to FR-16)* |
| Actionable error messages with remediation | [03-face-mesh-deep-dive.md](docs/architecture/current/03-face-mesh-deep-dive.md) — Pattern 2 *(the standard for FR-20)* |
| Platform branching in a single helper | [03-face-mesh-deep-dive.md](docs/architecture/current/03-face-mesh-deep-dive.md) — Pattern 5 |
| Cross-thread publication by value (no locks) | [04-tracker-deep-dive.md](docs/architecture/current/04-tracker-deep-dive.md) — Pattern 4 |
| Robust statistics for sample selection | [05-overlay-deep-dive.md](docs/architecture/current/05-overlay-deep-dive.md) — Pattern 1 |
| Cancellable member timers for state transitions | [05-overlay-deep-dive.md](docs/architecture/current/05-overlay-deep-dive.md) — Pattern 3 *(the fix shape for FR-6)* |
| Platform workarounds with stated symptoms | [05-overlay-deep-dive.md](docs/architecture/current/05-overlay-deep-dive.md) — Pattern 5 |
| Cite the algorithm, state the behaviour | [06-one-euro-deep-dive.md](docs/architecture/current/06-one-euro-deep-dive.md) — Pattern 1 |
| Guard-clause pipeline | [07-main-deep-dive.md](docs/architecture/current/07-main-deep-dive.md) — Pattern 3 |
| **Anti-pattern to eliminate** — duplicated threshold blocks | [07-main-deep-dive.md](docs/architecture/current/07-main-deep-dive.md) — Pattern 4 *(target of FR-14)* |
| **Anti-pattern to eliminate** — `print()` as sole diagnostics | [04-tracker-deep-dive.md](docs/architecture/current/04-tracker-deep-dive.md) — Pattern 6 *(target of FR-25)* |

---

## Open Items

Recorded rather than invented. None blocks architecture; all should be closed before or during planning.

| # | Item | Needed by | Impact if unresolved |
|---|---|---|---|
| 1 | **Target completion date / hard deadline** | `aire-build-cycles` | Cycles cannot be sequenced against a date |
| 2 | **Target deployment hardware** — which cameras, OS versions, and screen configurations must be supported | Architecture | FR-19's "materially different conditions" cannot be defined; the 1920×1080 capture request is unvalidated against real accessibility hardware |
| 3 | **Evaluation protocol specifics** — seating distance, lighting, target count, number of sessions | FR-11 | The baseline is not reproducible without them |
| 4 | **Eye-pairing answer** | FR-33 | Per-eye quality weighting may be invalid. Scheduled as the first story by decision |
| 5 | **Calibration profile key** — per user, per camera, per lighting, or a named profile chosen by the user | FR-16 | Persistence cannot be designed without it |
| 6 | **`.venv/` rebuild** | FR-27 | No test runner can execute; the current venv lacks an interpreter and `pyvenv.cfg` |

---

## Traceability — Defects to Requirements

| Defect | Title | Requirements |
|---|---|---|
| [#3](https://github.com/raminmardani/EyeTracker/issues/3) | Esc abort emits `finished` twice | FR-5, FR-6, FR-7 |
| [#4](https://github.com/raminmardani/EyeTracker/issues/4) | Head-pose angle labels cyclically permuted | FR-1, FR-3, FR-4 |
| [#5](https://github.com/raminmardani/EyeTracker/issues/5) | `FEATURE_ROLL` discontinuous at neutral | FR-2 |
| [#6](https://github.com/raminmardani/EyeTracker/issues/6) | Abort at 5-target minimum → unusable model | FR-8, FR-9 |
| [#7](https://github.com/raminmardani/EyeTracker/issues/7) | Resolution/FPS skipped on fallback paths | FR-31, FR-19 |
| [#8](https://github.com/raminmardani/EyeTracker/issues/8) | MediaPipe graph leaked if probing raises | FR-30, FR-20 |
| [#9](https://github.com/raminmardani/EyeTracker/issues/9) | `viable` check computed but never read | FR-32 |
