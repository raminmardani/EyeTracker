# Architecture — EyeTracker · Cycle EVAL-1

**Version**: 1.0.0 · **Cycle**: EVAL-1 · **Base**: `main` · **Code Root**: `eye_tracker/` + `main.py`

> 🔴 **Assembled from approved artifacts, never authored fresh.** Sources: `requirements.md`
> (approved), `stories.md` (GATE 1 approved), the Atlas knowledge graph (solution 704, commit
> `745e086`, verified zero source drift), and the repository's own reviewed
> `docs/architecture/current/` deep-dives.

## 1. System context
Python 3.14 desktop application. A webcam frame becomes a gaze estimate on screen. Single process,
one capture thread producing into a Qt main thread.

## 2. Component inventory (from Atlas)

| Module | Classes | Role |
|---|---|---|
| `eye_tracker/face_mesh.py` | `FaceMeshWrapper` | MediaPipe landmark extraction. Base layer — imports nothing internal. |
| `eye_tracker/gaze.py` | — | Feature derivation. **Hub** — imported by calibration, overlay, tracker. |
| `eye_tracker/calibration.py` | `GazeCalibrator`, `_ScreenRegressor` | GP regression, feature vector → screen point. |
| `eye_tracker/tracker.py` | `GazeTracker` | Capture thread; emits `features_ready`. |
| `eye_tracker/overlay.py` | `GazeOverlay`, `CalibrationWindow` | Qt overlay + calibration UI. |
| `eye_tracker/one_euro.py` | `OneEuro2D`, `_OneEuro1D` | Smoothing filter. Standalone. |
| `main.py` | `AppController` | Composition root. |

## 3. Layering
```
face_mesh ──▶ gaze ──┬──▶ calibration
                     ├──▶ overlay
                     └──▶ tracker ──▶ face_mesh
one_euro (standalone)
main ──▶ one_euro, calibration, gaze, overlay, tracker
```

## 4. The delta this cycle introduces
Three NEW leaf modules, stdlib-only, no internal importers, therefore introducing no cycle:

| New module | Story | Purpose |
|---|---|---|
| `eye_tracker/frame_gate.py` | 1.1 | Base frame-acceptance envelope + named live deviation. |
| `eye_tracker/frame_stats.py` | 1.2 | Per-reason rejection counters. |
| `eye_tracker/logging_setup.py` | 1.3 | Levelled loggers, controllable destination. |

Existing modules change only at their call sites. **No change to gaze math, calibration, or capture.**

## 5. Design stages — explicitly skipped
Functional Design, NFR Requirements, NFR Design, Infrastructure Design and Application Design were
all assessed SKIP against their own criteria (`planning/workflow-plan.md`). 🔴 No decision is invented
here to fill the gap; Section 10 derives from `requirements.md` and the Atlas graph instead.

## 6. Data architecture
None introduced. No schema, no persistence, no serialisation format. Counters are in-process only.

## 7. API / integration contracts
None introduced. No network surface, no IPC, no public API.

## 8. Cross-cutting decisions
- **Stdlib only** for new modules (REQ-NF-04) — the application already carries heavy native
  dependencies; diagnostics must not add more.
- **Import-time purity** — new modules must import with no camera, display, model download or
  network (REQ-NF-03), because the CI gates run headless.
- **Behaviour preservation** — this cycle is a refactor. Verdicts must be byte-identical
  (REQ-NF-02).

## 9. Non-functional targets
Read from `.evals/config.json`. No literal thresholds are restated here.

---

## 10. Verifiable Constraints

Each scores 0 in a diff that violates its *verifiable-as* rule. Weights sum to 1.0.

| ID | Constraint | Verifiable as | Weight | Source |
|---|---|---|---|---|
| **ARCH-01** | The frame-acceptance envelope must have exactly one definition; the live envelope is a named deviation from the base, never an independent copy. | Scores 0 if a frame-acceptance numeric literal (`0.16`, `0.55`, `0.58`, `0.45`, `0.60`, `0.70`) appears in `main.py` or `eye_tracker/overlay.py` in the changed diff, or if two independent literal blocks remain. | 0.25 | REQ-F-01.1, REQ-F-01.2 |
| **ARCH-02** | Unification must preserve the physical envelope. No accept/reject verdict may change. | Scores 0 if any threshold VALUE differs from the pre-change literal at the same call site, or if no test drives pre-change literals against the new module across boundary values. | 0.25 | REQ-F-01.3, REQ-NF-02 |
| **ARCH-03** | New modules must be stdlib-only leaves with no internal importers. | Scores 0 if `frame_gate.py`, `frame_stats.py` or `logging_setup.py` imports a third-party package, or imports another `eye_tracker` module. | 0.20 | REQ-NF-04, Atlas layering |
| **ARCH-04** | New modules must import with no camera, display, model download or network access. | Scores 0 if importing any new module triggers I/O, device access, or a network call at module scope. | 0.15 | REQ-NF-03 |
| **ARCH-05** | Diagnostics must not leak frame contents, imagery or personally identifying data. | Scores 0 if any log or counter record includes a frame buffer, landmark array, or image data. | 0.15 | REQ-NF-05, Security Baseline |

**Total: 1.00**
