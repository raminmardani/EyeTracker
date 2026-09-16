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
**AIRE Framework: v1.0** · Built with AIRE v1.0
