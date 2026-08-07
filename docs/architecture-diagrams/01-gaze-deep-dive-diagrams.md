# Architecture Diagrams — Gaze Feature Extraction

**Date**: 2026-08-06
**Source**: [docs/architecture/current/01-gaze-deep-dive.md](../architecture/current/01-gaze-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. Frame → 38-D Feature Vector

The full extraction path for one camera frame. Note the two silent fallbacks: a missing head pose becomes six zeros, and missing blendshapes make 12 of the 38 features read as `0.0` — in both cases indistinguishable from a genuinely perfect reading.

```mermaid
sequenceDiagram
  participant TR as tracker._run
  participant FM as FaceMeshWrapper.process
  participant EX as extract_gaze_features
  participant EG as _eye_geometry
  participant BS as _blendshape_score

  TR->>FM: process(mirrored frame)
  FM-->>TR: dict pts2d, head_pose, size, blendshapes, facial_matrix
  TR->>EX: extract_gaze_features(mesh_result)
  EX->>EG: eye A - outer, inner, top ring, bottom ring, iris ring
  EG-->>EX: dx, dy, ear, iris_radius, upper_clear, lower_clear, center
  EX->>EG: eye B - same, mirrored indices
  EG-->>EX: dx, dy, ear, iris_radius, upper_clear, lower_clear, center
  EX->>EX: head_pose None becomes zeros of length 6
  EX->>BS: 12 blendshape lookups
  BS-->>EX: score or 0.0 when absent
  EX->>EX: derive averages, vergence, face position and scale
  EX-->>TR: np.ndarray shape 38, dtype float64
```

---

## 2. Eye-Local Coordinate Frame

The module's central algorithm, and the reason gaze measurements survive head tilt. The vertical axis `v` is rebuilt from the eye's own landmarks every frame rather than taken from the image axes.

**Verified**: rotating the same eye geometry by 0°, 10°, 25° and 40° produced bit-identical `dx`, `dy` and `ear` values to 9 decimal places.

```mermaid
flowchart TB
  A["p_out = centroid outer<br/>p_in = centroid inner"] --> B["eye_vec = p_in - p_out"]
  B --> C["eye_w = norm eye_vec + 1e-6<br/>u = eye_vec / eye_w"]
  C --> D["v = perpendicular of u<br/>v = -u.y, u.x"]
  D --> E{"dot lid_vec, v < 0 ?"}
  E -->|yes| F["v = -v<br/>force v to point lid-downward"]
  E -->|no| G["keep v"]
  F --> H["eye_h = abs dot lid_vec, v + 1e-6"]
  G --> H
  H --> I["center = mean of the 4 corner points"]
  I --> J["iris_offset = iris - center"]
  J --> K["dx = dot iris_offset, u / eye_w<br/>dy = dot iris_offset, v / eye_h"]
  K --> L["ear = eye_h / eye_w<br/>upper_clear = dot iris - p_top, v / eye_h<br/>lower_clear = dot p_bot - iris, v / eye_h"]
```
