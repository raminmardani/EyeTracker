# Requirements — EVAL-1: Diagnostics & Threshold Unification

**Depth**: Standard · **Cycle**: EVAL-1 · **Base**: `main` · **Tracker**: GITHUB `raminmardani/EyeTracker`

Derived from `docs/requirements.md` (FR-14, FR-15, FR-24, FR-25, FR-27, FR-29). Every claim below was
verified against the code at this commit; none is assumed.

---

## Functional Requirements

### REQ-F-01 — Single definition for frame-acceptance thresholds
*Source: FR-14, FR-15*

The calibration gate (`eye_tracker/overlay.py:182-188`) and the live gate (`main.py:94-100`) must
resolve to ONE definition.

- **REQ-F-01.1** A single module owns the base envelope: `A_EAR` min, `B_EAR` min, `blink` max,
  `squint` max, `yaw` max, `pitch` max.
- **REQ-F-01.2** The live envelope is expressed as an **explicit, named deviation** from the base —
  never as an independently maintained copy.
- **REQ-F-01.3** 🔴 The *physical* envelope each site enforces today must be preserved exactly.
  Unification is a refactor, not a retune: for every input, the accept/reject verdict at both sites
  must be identical before and after.
- **REQ-F-01.4** The current divergence (blink, squint, yaw, pitch) must be recorded as a deliberate
  deviation with a stated rationale, not silently normalised away.

### REQ-F-02 — Frame rejections counted and exposed by reason
*Source: FR-24*

- **REQ-F-02.1** Every rejection path in the live pipeline increments a counter naming its reason.
- **REQ-F-02.2** Reasons are distinguishable at minimum as: `no_feature`, `ear_a`, `ear_b`, `blink`,
  `squint`, `yaw`, `pitch`, `predictor_error`, `non_finite_prediction`.
- **REQ-F-02.3** Counts are readable as a snapshot without stopping the pipeline.
- **REQ-F-02.4** Counting must not change any accept/reject verdict.

### REQ-F-03 — Structured logging replaces `print()`
*Source: FR-25*

- **REQ-F-03.1** A logging setup module provides levelled loggers with a controllable destination.
- **REQ-F-03.2** Logger names preserve the existing `[module]` convention (`calibration`, `tracker`,
  `predict`).
- **REQ-F-03.3** All 10 `print()` sites migrate to the appropriate level; a windowed application must
  no longer discard diagnostics to a dropped stream.
- **REQ-F-03.4** Destination and level are configurable without editing source.

---

## Non-Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| **REQ-NF-01** | New/changed code meets the `unitTestCoverageMin` threshold in `.evals/config.json`, 100% pass. | FR-27 |
| **REQ-NF-02** | 🔴 Zero behavioural change to the gaze pipeline. Every frame accepted today is accepted after; every frame rejected today is rejected after, for the same reason. | FR-29 |
| **REQ-NF-03** | New modules are importable without a camera, GPU, display, or model download — they must be unit-testable in CI. | Derived from REQ-NF-01 |
| **REQ-NF-04** | No new third-party runtime dependency. Standard library only for the new modules. | Technical Constraints |
| **REQ-NF-05** | Logging must never emit secrets, frame contents, or personally identifying imagery. | Security Baseline (mandatory extension) |

---

## Traceability

| Req | Source FR | Evidence |
|---|---|---|
| REQ-F-01 | FR-14, FR-15 | `main.py:94-100` vs `overlay.py:182-188` — 4 of 6 thresholds diverged |
| REQ-F-02 | FR-24 | silent `return` paths in `main.py::_on_feat` |
| REQ-F-03 | FR-25 | 10 `print()` sites across 3 modules |
| REQ-NF-01 | FR-27 | AIRE core rule |
| REQ-NF-02 | FR-29 | "verified-correct behaviours must be locked by tests" |

## Assumptions

1. **The live/calibration divergence is intentional.** FR-15 says deviations must be *documented*,
   not removed. Treated as a refactor with byte-identical verdicts (REQ-F-01.3).
2. **No numeric threshold changes in this cycle.** Retuning is Theme A/D work and out of scope.
3. **Counters are in-process only.** No metrics backend, no export format — FR-24 asks for
   "counted and exposed", nothing more.

## Open questions

None blocking. All three requirements are independently implementable against verified evidence.
