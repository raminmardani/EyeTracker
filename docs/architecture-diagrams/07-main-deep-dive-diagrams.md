# Architecture Diagrams — Orchestration & Live Pipeline

**Date**: 2026-08-06
**Source**: [docs/architecture/current/07-main-deep-dive.md](../architecture/current/07-main-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. Application Lifecycle

The two-stage lifecycle: calibrate, then track. There is **no path back** — any calibration problem requires restarting the application and re-running a 79-to-141-second ritual.

The transition hides a verified constraint. The application survives losing the calibration window only because the overlay is created **synchronously** inside the `finished` handler, before `close()` runs. Moving the blocking fit to a worker thread — the obvious fix for the frozen UI — makes the app **exit silently** the moment calibration completes.

```mermaid
sequenceDiagram
  participant M as main()
  participant APP as QApplication
  participant AC as AppController
  participant TR as GazeTracker
  participant CW as CalibrationWindow
  participant GC as GazeCalibrator
  participant OV as GazeOverlay

  M->>APP: QApplication(sys.argv)
  M->>AC: AppController(cam_index=0, n_cal_points=25, samples_per_point=60)
  AC->>TR: GazeTracker(cam_index=0)
  AC->>GC: GazeCalibrator() — unfitted
  AC->>AC: OneEuro2D(min_cutoff=1.6, beta=0.06)
  M->>APP: aboutToQuit connect controller.shutdown
  M->>AC: start()
  AC->>TR: start() — returns immediately, probing runs for seconds
  AC->>CW: CalibrationWindow(tracker, 25, 60) — connects and shows itself
  AC->>CW: finished connect _on_calib_done
  M->>APP: exec() — event loop
  CW-->>AC: finished(X, Y) — synchronous
  alt len(X) < 5
    AC->>TR: stop()
    AC->>APP: quit()
  else
    AC->>GC: fit(X, Y) — BLOCKING, seconds, UI frozen
    AC->>AC: clear _feat_history, _last_live_feat, _last_live_t
    AC->>OV: GazeOverlay() then show()
    AC->>TR: features_ready connect _on_feat
    Note over AC: live tracking — no path back to calibration
  end
```

---

## 2. The Live Per-Frame Pipeline

Six reject gates, a motion-adaptive temporal median, six Gaussian Process evaluations, and a smoothing pass — all on the GUI thread, every frame.

Every one of the five `return` paths drops the frame **silently**. Nothing counts rejections or records why, which makes any "the dot is sluggish" report undiagnosable. A rejected frame also leaves the dot frozen at its last position rather than hiding it, so a lost face looks identical to a steady gaze.

```mermaid
flowchart TB
  A["features_ready(feat)"] --> B{"feat is None<br/>or overlay is None ?"}
  B -->|yes| Z["return — dot stays frozen"]
  B -->|no| C{"6 reject gates<br/>EAR, blink, squint, yaw, pitch"}
  C -->|any fails| Z2["return — no history update, no dot update"]
  C -->|all pass| D["now = time.monotonic()"]
  D --> E["motion = _motion_score(feat, now)"]
  E --> F["_feat_history.append(feat) — deque maxlen 7"]
  F --> G{"motion > 22 ?"}
  G -->|yes| H["window = 2"]
  G -->|no| I{"motion > 10 ?"}
  I -->|yes| J["window = 3"]
  I -->|no| K["window = min(len(history), 5)"]
  H --> L["feat_for_pred = median of the last window frames"]
  J --> L
  K --> L
  L --> M["calibrator.predict_with_variance"]
  M -->|raises| N["print and return"]
  M --> O{"prediction finite ?"}
  O -->|no| Z3["return"]
  O -->|yes| P["smoother.filter(x, y, variance, motion)"]
  P --> Q["overlay.update_position — full-window repaint"]
```

---

## 3. Motion Score Composition

Three rates of change combined by two hand-tuned weights. The three channels have different units — ratios, radians, and blendshape scores — and the weights `0.6` and `0.3` are the only reconciliation between them.

The resulting scalar is then compared against absolute thresholds (22.0, 10.0) and divided by 25.0 in the smoother, so five constants across two modules are jointly tuned to a composite whose scale is an accident of how features are normalised elsewhere.

```mermaid
flowchart LR
  A["current feat"] --> B["gaze_delta<br/>norm over AVG_DX, AVG_DY,<br/>LOOK_H_AVG, LOOK_V_AVG"]
  A --> C["head_delta<br/>norm over YAW, PITCH,<br/>FACE_CX, FACE_CY"]
  A --> D["lid_delta<br/>abs of BLINK_AVG change"]
  E["_last_live_feat"] --> B
  E --> C
  E --> D
  B --> F["all divided by dt"]
  C --> F
  D --> F
  F --> G["motion = gaze + 0.6*head + 0.3*lid"]
  G --> H["median window selection"]
  G --> I["smoother cutoff_scale"]
```
