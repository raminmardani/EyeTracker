# Knowledge Graph — EyeTracker

## Provenance
- **Source**: atlas
- **Helix solution**: 704 (`EyeTracker`)
- **Repository**: https://github.com/raminmardani/EyeTracker (branch `main`)
- **Atlas last_ingested_commit**: `745e086f569a7a9d30e0f185bb4f6fc6126a0af2` ("head movement")
- **Drift vs this cycle's base**: **ZERO source drift.** `git diff 745e086..main -- eye_tracker/ main.py`
  returns only deleted `.pyc` artifacts; every commit since ingestion is docs/chore. The graph is
  commit-exact for all Python source.
- **Pulled**: 2026-09-14T17:32:23Z
- **Read-only input.** Never edited to fit a plan (`helix-atlas-integration.md` Section 4.3).

## Components (7 files, 9 classes)

| Module | Classes | Parsed methods |
|---|---|---|
| `eye_tracker/face_mesh.py` | `FaceMeshWrapper` | `_cache_dir`, `_ensure_tasks_model` |
| `eye_tracker/gaze.py` | — | `extract_gaze_features`, `_centroid`, `_eye_geometry`, `_blendshape_score` |
| `eye_tracker/calibration.py` | `GazeCalibrator`, `_ScreenRegressor` | `_make_gp`, `_quality_weight` |
| `eye_tracker/tracker.py` | `GazeTracker` | `_preferred_backends` |
| `eye_tracker/overlay.py` | `GazeOverlay`, `CalibrationWindow` | `_representative_feature` |
| `eye_tracker/one_euro.py` | `OneEuro2D`, `_OneEuro1D` | `_alpha` |
| `main.py` | `AppController` | `main` |

## Internal dependency edges (from :IMPORTS)

```
face_mesh  ──▶ gaze ──┬──▶ calibration
                      ├──▶ overlay
                      └──▶ tracker ──▶ face_mesh
one_euro (standalone)

main ──▶ one_euro, calibration, gaze, overlay, tracker
```

- `gaze` is the **hub**: imported by calibration, overlay and tracker.
- `face_mesh` is the **base layer**: imported by gaze and tracker; imports nothing internal.
- `one_euro` has **no internal dependencies** — a self-contained filter.
- `main` is the **composition root**, importing five of the six modules.

## External dependencies (from :IMPORTS, 45 edges)

| Module | External |
|---|---|
| calibration | `sklearn.preprocessing`, `sklearn.gaussian_process`, `sklearn.gaussian_process.kernels`, `numpy` |
| face_mesh | `mediapipe`, `cv2`, `numpy`, `urllib.request`, `urllib.error`, `os`, `pathlib`, `sys`, `time` |
| gaze | `numpy`, `math` |
| one_euro | `numpy`, `math`, `time` |
| overlay | `PyQt6.QtGui`, `PyQt6.QtWidgets`, `PyQt6.QtCore`, `numpy`, `sys` |
| tracker | `PyQt6.QtCore`, `cv2`, `numpy`, `threading`, `time`, `sys` |
| main | `PyQt6.QtCore`, `PyQt6.QtWidgets`, `numpy`, `collections`, `time`, `sys` |

**Graph totals**: 45 `IMPORTS`, 12 `HAS_METHOD`, 9 `CONTAINS` (Class), 1 `CALLS`.
