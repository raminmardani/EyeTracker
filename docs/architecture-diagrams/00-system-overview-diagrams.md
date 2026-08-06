# Architecture Diagrams — EyeTracker System Overview

**Date**: 2026-08-06
**Source**: [docs/architecture/current/00-system-overview.md](../architecture/current/00-system-overview.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the system overview, for review by BA / product stakeholders without reading the full analysis.

---

## 1. System Architecture — Components & Threading

How a webcam frame becomes a dot on screen. The dashed lines are the one-time model download that happens on first run only.

```mermaid
flowchart TB
  subgraph capture["Capture Thread — daemon threading.Thread"]
    CAM["Webcam<br/>cv2.VideoCapture"]
    PROBE["Camera selection + probe<br/>tracker.py"]
    FLIP["Mirror flip<br/>cv2.flip"]
    MESH["FaceMeshWrapper<br/>face_mesh.py"]
    POSE["Head pose<br/>cv2.solvePnP"]
    FEAT["extract_gaze_features<br/>gaze.py"]
  end

  subgraph bridge["Qt Signal Boundary"]
    SIG["features_ready<br/>pyqtSignal object"]
  end

  subgraph gui["GUI Thread — Qt event loop"]
    CTRL["AppController<br/>main.py"]
    CALWIN["CalibrationWindow<br/>overlay.py"]
    CALIB["GazeCalibrator<br/>calibration.py"]
    SMOOTH["OneEuro2D<br/>one_euro.py"]
    OVER["GazeOverlay<br/>overlay.py"]
  end

  subgraph ext["External"]
    CDN["Google Storage CDN<br/>face_landmarker.task"]
    CACHE["Local model cache<br/>~/.cache/eyee"]
  end

  CAM --> PROBE --> FLIP --> MESH
  MESH --> POSE --> FEAT
  FEAT --> SIG
  SIG --> CALWIN
  SIG --> CTRL
  CALWIN -->|"finished X, Y"| CTRL
  CTRL -->|fit| CALIB
  CTRL -->|predict_with_variance| CALIB
  CALIB -->|"mean + variance"| SMOOTH
  SMOOTH --> OVER
  MESH -.->|first run only| CDN
  CDN -.-> CACHE
  CACHE -.-> MESH
```

---

## 2. Runtime Modes

The application has exactly two sequential modes. Note there is **no path back to calibration** once live tracking begins — recalibrating requires restarting the app.

```mermaid
stateDiagram-v2
  [*] --> Starting
  Starting --> AwaitingFace : tracker thread started
  AwaitingFace --> Calibrating : first finite feature vector
  Calibrating --> Calibrating : advance through N dots
  Calibrating --> Aborted : Esc pressed or fewer than 5 points
  Calibrating --> Fitting : all dots collected
  Fitting --> LiveTracking : 6 GP models fitted
  LiveTracking --> LiveTracking : gate, median, predict, smooth, draw
  Aborted --> [*]
  LiveTracking --> [*] : app quit
```

---

## 3. Prediction Model Structure

Calibration does not train one model — it trains **six** Gaussian Process regressors (three regressors × two screen axes), each reading a different subset of the 38 features. Their outputs are fused by confidence, so a partially occluded or squinting eye automatically loses influence.

```mermaid
flowchart LR
  F["38-D feature vector"]
  F --> AX["Eye A subset X<br/>12 features"]
  F --> AY["Eye A subset Y<br/>14 features"]
  F --> BX["Eye B subset X<br/>12 features"]
  F --> BY["Eye B subset Y<br/>14 features"]
  F --> NX["Binocular subset X<br/>14 features"]
  F --> NY["Binocular subset Y<br/>25 features"]
  AX --> GA["GP → mean, std"]
  AY --> GA
  BX --> GB["GP → mean, std"]
  BY --> GB
  NX --> GN["GP → mean, std"]
  NY --> GN
  GA --> FUSE["Inverse-variance fusion<br/>weighted by eye + pose quality"]
  GB --> FUSE
  GN --> FUSE
  FUSE --> OUT["fused x, y + fused variance"]
```

---

**Diagram count**: 3 (1 component/threading flowchart, 1 state diagram, 1 model-structure flowchart)
