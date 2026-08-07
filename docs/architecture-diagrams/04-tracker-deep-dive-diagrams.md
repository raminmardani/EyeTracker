# Architecture Diagrams — Capture Thread & Camera Selection

**Date**: 2026-08-06
**Source**: [docs/architecture/current/04-tracker-deep-dive.md](../architecture/current/04-tracker-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. Capture Thread Lifecycle and Failure Paths

**Four distinct death paths, none of which reach the user.** When any of them fires, the Qt event loop keeps running and the calibration window displays "Center your face in the camera to start calibration" indefinitely. This is the user-visible symptom of every startup failure in the system.

```mermaid
stateDiagram-v2
  [*] --> Constructed : GazeTracker(cam_index=0)
  Constructed --> ThreadStarted : start() — daemon thread
  ThreadStarted --> MeshInit : _run begins
  MeshInit --> DeadSilent1 : FaceMeshWrapper raises — print, return
  MeshInit --> OpeningCamera : mesh ready
  OpeningCamera --> DeadLeak : probe raises — NOT caught, mesh never closed
  OpeningCamera --> DeadSilent2 : capture not opened — print, close mesh, return
  OpeningCamera --> Capturing : capture opened
  Capturing --> Capturing : frame ok — mirror, detect, emit
  Capturing --> Capturing : read failed — sleep 10ms, retry forever
  Capturing --> Capturing : no face — streak++, emit None
  Capturing --> DeadUnhandled : detect or extract raises — finally runs, thread dies
  Capturing --> Teardown : _stop set by stop()
  Teardown --> [*] : cap.release(), mesh.close()
  DeadSilent1 --> [*]
  DeadSilent2 --> [*]
  DeadLeak --> [*]
  DeadUnhandled --> [*]
```

---

## 2. Camera Discovery and Ranking

Cameras are chosen by **whether a face was actually detected**, not by "first device that opens" — a genuinely good design that correctly prefers a dim front-facing webcam over a bright capture card.

The cost is startup latency: up to 12 index × backend combinations are probed serially, each with 8 warm-up frames and 320 ms of deliberate sleeping. The user sees no indication that any of this is happening.

```mermaid
sequenceDiagram
  participant RUN as _run
  participant OC as _open_capture
  participant PC as _probe_capture
  participant CV as cv2.VideoCapture
  participant FM as FaceMeshWrapper

  RUN->>OC: _open_capture(probe_mesh=mesh)
  loop index in [preferred, 0, 1, 2, 3] minus duplicate
    loop backend in platform list — 3 on Windows, 2 on macOS/Linux
      OC->>CV: VideoCapture(idx, backend)
      alt not opened
        OC->>CV: release, skip
      else opened
        OC->>OC: _configure_capture — 1920x1080 @ 30, buffersize 1
        OC->>PC: _probe_capture(cap, probe_mesh)
        loop 8 warm-up frames
          PC->>CV: read()
          PC->>FM: process(mirrored frame)
          FM-->>PC: result or None — count detections
          PC->>PC: time.sleep(0.04)
        end
        PC->>CV: last frame to grayscale
        PC-->>OC: mean, std, score = mean + 1.5*std, valid_frames, detected_frames, viable
        OC->>CV: release
        OC->>OC: fallback = highest score so far
        OC->>OC: best = most detected_frames, tie-break on score
      end
    end
  end
  OC->>OC: chosen = best or fallback
  alt nothing opened at all
    OC-->>RUN: VideoCapture(cam_index) — unconfigured
  else
    OC->>CV: re-open chosen idx and backend
    OC->>OC: _configure_capture again
    OC-->>RUN: configured capture
  end
```

---

## 3. The Capture Loop

One iteration per camera frame. Note that a read failure retries forever with no counter and emits nothing, so a camera unplugged mid-session is indistinguishable from a steady gaze — and neither `mesh.process` nor `extract_gaze_features` is wrapped in an exception handler, so a single transient error terminates the producer permanently.

```mermaid
flowchart TB
  A["while not _stop"] --> B["cap.read()"]
  B --> C{"ok ?"}
  C -->|no| D["sleep 10ms — no failure counter, retries forever"]
  D --> A
  C -->|yes| E["_prepare_frame — cv2.flip horizontal"]
  E --> F["mesh.process(frame)"]
  F --> G{"result is None ?"}
  G -->|yes| H["_no_face_streak += 1"]
  H --> I{"streak mod 90 == 0 ?"}
  I -->|yes| J["print streak — every ~3 s at 30 fps"]
  I -->|no| K["emit None"]
  J --> K
  K --> A
  G -->|no| L["_no_face_streak = 0"]
  L --> M["extract_gaze_features(result)"]
  M --> N["emit 38-vector"]
  N --> A
```
