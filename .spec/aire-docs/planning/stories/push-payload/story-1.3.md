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

---
**AIRE Framework: v1.0** · Built with AIRE v1.0
