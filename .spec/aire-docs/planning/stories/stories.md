# User Stories — EVAL-1: Diagnostics & Threshold Unification

**Cycle**: EVAL-1 · **Tracker**: GITHUB `raminmardani/EyeTracker` · **Parent Epic**: none
**team_size**: 2 (fixed) · **creation mode**: all-at-once (fixed) · **granularity**: clustered (user chose B)

---

## Story 1.1 — Unified frame-acceptance envelope

**As** Devin the maintainer, **I want** the calibration and live frame-acceptance gates to resolve to
one definition, **so that** a threshold cannot silently diverge between them again.

**Covers**: REQ-F-01, REQ-NF-02, REQ-NF-03, REQ-NF-04
**Persona**: P2 · **Requires**: —

### Acceptance criteria
- **AC-1** A new stdlib-only module defines the base envelope: `A_EAR` min, `B_EAR` min, `blink` max,
  `squint` max, `yaw` max, `pitch` max. → REQ-F-01.1
- **AC-2** The live envelope is derived from the base as an explicitly named deviation, not a copy.
  The four diverged thresholds (blink, squint, yaw, pitch) are expressed as deviation values with a
  stated rationale. → REQ-F-01.2, REQ-F-01.4
- **AC-3** `eye_tracker/overlay.py` and `main.py` both consult the shared definition; no
  frame-acceptance numeric literal remains at either call site. → REQ-F-01.1
- **AC-4** 🔴 For every feature vector, the accept/reject verdict at BOTH sites is identical to the
  pre-change code. Proven by a test that drives the pre-change literals against the new module across
  boundary and interior values. → REQ-F-01.3, REQ-NF-02
- **AC-5** The module imports with no camera, display, model download, or third-party package.
  → REQ-NF-03, REQ-NF-04

---

## Story 1.2 — Frame rejections counted by reason

**As** Aria the hands-free user, **I want** every dropped frame attributed to a named reason,
**so that** "the dot is sluggish" becomes a diagnosable statement rather than a guess.

**Covers**: REQ-F-02, REQ-NF-02, REQ-NF-03, REQ-NF-04
**Persona**: P1, P2 · **Requires**: 1.1

### Acceptance criteria
- **AC-1** A stdlib-only counter records rejections keyed by reason and returns an immutable
  snapshot without stopping the pipeline. → REQ-F-02.1, REQ-F-02.3
- **AC-2** The reason set is at minimum `no_feature`, `ear_a`, `ear_b`, `blink`, `squint`, `yaw`,
  `pitch`, `predictor_error`, `non_finite_prediction`. → REQ-F-02.2
- **AC-3** Every rejection path in `main.py::_on_feat` increments exactly one counter, naming the
  first condition that failed. → REQ-F-02.1
- **AC-4** 🔴 Counting changes no accept/reject verdict — the same frames pass as before.
  → REQ-F-02.4, REQ-NF-02
- **AC-5** Snapshot reads are safe while the capture thread is producing. → REQ-F-02.3

---

## Story 1.3 — Structured logging replaces print diagnostics

**As** Sam the support engineer, **I want** levelled logging with a controllable destination,
**so that** I can triage a failure from a log file instead of a stream a windowed app discards.

**Covers**: REQ-F-03, REQ-NF-04, REQ-NF-05
**Persona**: P3, P1 · **Requires**: —

### Acceptance criteria
- **AC-1** A stdlib-only logging setup module provides levelled loggers whose destination and level
  are configurable without editing source. → REQ-F-03.1, REQ-F-03.4
- **AC-2** Logger names preserve the existing bracket convention: `calibration`, `tracker`,
  `predict`. → REQ-F-03.2
- **AC-3** The 9 `print()` sites owned by this story migrate to an appropriate level —
  `tracker.py` (123, 127, 142, 146, 160), `overlay.py` (206, 212, 217), `main.py` (56).
  → REQ-F-03.3
- **AC-4** No log record contains frame contents, imagery, or personally identifying data.
  → REQ-NF-05
- **AC-5** Configuring logging twice is idempotent — no duplicated handlers, no doubled output.
  → REQ-F-03.1

> 🔗 **Boundary note**: `main.py:116` (`[predict]`) is deliberately EXCLUDED from this story. Story
> 1.2 rewrites that same `except` block to attach the `predictor_error` reason, and owns emitting
> its log line. Splitting ownership this way keeps the two stories from editing one block.
