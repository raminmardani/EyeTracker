# Architecture Diagrams — Landmark Adapter & Head Pose

**Date**: 2026-08-06
**Source**: [docs/architecture/current/03-face-mesh-deep-dive.md](../architecture/current/03-face-mesh-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. Construction and Backend Selection

Two MediaPipe APIs are supported, but under every version this project has ever pinned, the `SolutionsMode` branch **cannot execute** — the right-hand path is always taken. The unreachable branch carries different confidence thresholds and would zero out 12 of the 38 features if it ever activated.

```mermaid
stateDiagram-v2
  [*] --> CheckSolutions
  CheckSolutions --> SolutionsMode : hasattr mp solutions is True
  CheckSolutions --> CheckTasks : hasattr mp solutions is False
  CheckTasks --> Raise : neither tasks nor tasks.vision
  CheckTasks --> EnsureModel : tasks.vision present
  EnsureModel --> CacheHit : face_landmarker.task exists
  EnsureModel --> Download : not cached
  Download --> TempWrite : urlopen 30s timeout
  TempWrite --> AtomicReplace : write complete
  AtomicReplace --> CacheHit
  Download --> Cleanup : OSError or URLError
  Cleanup --> RaiseRuntime : unlink temp, raise with remediation text
  CacheHit --> TasksMode : create_from_options
  SolutionsMode --> [*] : confidence 0.5, no blendshapes
  TasksMode --> [*] : confidence 0.3, blendshapes on
  RaiseRuntime --> [*]
  Raise --> [*]
```

---

## 2. Per-Frame Detection

One frame in, one `mesh_result` dict out. Note that `facial_matrix` — MediaPipe's own head-pose estimate, computed from all 478 landmarks — is extracted, published, and then read by nobody. The system pays for it, discards it, and re-derives a less-informed pose from 6 landmarks instead.

```mermaid
sequenceDiagram
  participant TR as tracker._run
  participant PR as process
  participant CV as cv2
  participant DL as _detect_landmarks
  participant MP as MediaPipe FaceLandmarker
  participant HP as _head_pose

  TR->>PR: process(frame_bgr, already mirrored)
  PR->>CV: cvtColor BGR to RGB
  PR->>DL: _detect_landmarks(rgb)
  DL->>DL: timestamp_ms = max(last+1, monotonic*1000)
  DL->>MP: detect_for_video(Image, timestamp_ms)
  MP-->>DL: face_landmarks, face_blendshapes, transformation_matrixes
  alt no face
    DL-->>PR: None
    PR-->>TR: None
  else face found
    DL->>DL: blendshapes to name-score dict
    DL-->>PR: landmarks, blendshapes, facial_matrix
    PR->>PR: pts2d = normalised landmarks times w, h
    PR->>HP: _head_pose(pts2d, w, h)
    HP->>CV: solvePnP with SOLVEPNP_ITERATIVE
    CV-->>HP: ok, rvec, tvec
    HP->>CV: Rodrigues(rvec)
    CV-->>HP: rotation matrix
    HP->>HP: extract three Euler angles
    HP-->>PR: 6-vector, or None if solvePnP failed
    PR-->>TR: pts2d, head_pose, size, blendshapes, facial_matrix
  end
```

---

## 3. Head-Pose Extraction

**This is where the deep-dive's most consequential finding lives.** The three `atan2` expressions each correctly recover a rotation, but each result is bound to the wrong name:

| Named | Actually measures |
|---|---|
| `yaw` | **roll** — head tilt |
| `pitch` | **yaw** — head turn |
| `roll` | **pitch** — nod, offset by ±π |

Verified by projecting a synthetic head and rotating each camera axis by a known 15°. The consequence is that the frame-rejection gates act on the wrong axes, and nodding is never gated at all.

```mermaid
flowchart TB
  A["image_points = pts2d at indices 1, 152, 33, 263, 61, 291"] --> B["focal = frame width<br/>principal point = w/2, h/2<br/>distortion = zeros"]
  B --> C["solvePnP with _MODEL_POINTS<br/>flags SOLVEPNP_ITERATIVE"]
  C --> D{"ok ?"}
  D -->|no| E["return None<br/>gaze.py substitutes zeros of length 6"]
  D -->|yes| F["Rodrigues rvec to rotation matrix R"]
  F --> G["sy = sqrt of R00 squared plus R10 squared"]
  G --> H["named pitch = atan2 -R20, sy<br/>named yaw = atan2 R10, R00<br/>named roll = atan2 R21, R22"]
  H --> I["return yaw, pitch, roll, tvec0, tvec1, tvec2"]
  I --> J["gaze.py maps to features 8,9,10 and 12,13,11"]
```
