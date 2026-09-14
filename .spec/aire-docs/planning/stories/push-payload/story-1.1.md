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
**AIRE Framework: v1.0** · Built with AIRE v1.0
