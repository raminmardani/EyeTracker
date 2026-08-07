# Target Architecture Diagrams — EyeTracker

**Source**: `docs/architecture/design/02-target-architecture-brownfield.md`
**Generated**: 2026-08-07

> Mermaid diagrams extracted verbatim from the target architecture document for easy preview.
> Annotations follow the source: NEW / MODIFIED / unchanged.

---

## Target System Context

```mermaid
flowchart TB
  USER(["Local User<br/>single actor — the OS user account<br/>is the only auth source"])

  subgraph sys["EyeTracker — single-process desktop application"]
    direction TB
    APP["Existing pipeline<br/>capture → features → calibration<br/>→ prediction → overlay"]
    NEWCAP["NEW capabilities<br/>config, persistence,<br/>diagnostics, evaluation"]
  end

  subgraph net["Network — unchanged"]
    CDN["Google Storage CDN<br/>one-time model download"]
  end

  subgraph local["Local machine — files owned by the OS user"]
    direction TB
    CAM["Local webcam<br/>via OpenCV — existing"]
    CACHE[("face_landmarker.task<br/>model cache — existing")]
    CFG[("eyetracker.toml<br/>NEW — optional config")]
    PROF[("profiles/*.eyecal<br/>NEW — versioned calibration")]
    LOGS[("logs/eyetracker.log<br/>NEW — structured diagnostics")]
    REP[("docs/evaluation/*<br/>NEW — baseline and deltas")]
  end

  USER -->|"calibrates, recalibrates, retries, quits"| APP
  NEWCAP -->|"gaze dot, status, actionable messages"| USER
  CAM -->|"frames"| APP
  APP -->|"downloads once"| CDN
  CDN -->|"model asset"| CACHE
  CACHE -->|"loaded at startup"| APP
  CFG -->|"read at startup NEW"| NEWCAP
  NEWCAP -->|"saved after a successful fit NEW"| PROF
  PROF -->|"restored at launch — refused on any mismatch NEW"| NEWCAP
  NEWCAP -->|"written NEW"| LOGS
  NEWCAP -->|"written NEW"| REP
```

---

## Component Architecture (Target)

```mermaid
flowchart TB
  subgraph core["CORE — pure. No Qt, no cv2, no sklearn, no I/O"]
    GAZE["gaze.py<br/>38-D contract, semantics version, layout digest<br/>MODIFIED"]
    POSE["pose.py<br/>Euler extraction, wrap_to_pi<br/>NEW"]
    GATES["gates.py<br/>FrameGate, RejectionReason<br/>NEW"]
    CFG["config.py<br/>Settings tree, TOML overlay<br/>NEW"]
    ERR["errors.py<br/>Fault taxonomy F0 to F4<br/>NEW"]
    DIAG["diagnostics.py<br/>RejectionCounters, rate limiter<br/>NEW"]
    EUR["one_euro.py<br/>plus reset<br/>MODIFIED"]
    MET["evaluation/metrics.py<br/>error stats, degrees and pixels<br/>NEW"]
  end

  subgraph appl["APPLICATION — orchestration and model policy"]
    PIPE["pipeline.py<br/>LivePipeline: gate, motion, median, predict, smooth<br/>NEW"]
    CALIB["calibration.py<br/>6 GPs, min-sample enforcement, witness set<br/>MODIFIED"]
    PROF["profile.py<br/>bundle write, refuse-before-unpickle load<br/>NEW"]
    APP["app.py<br/>AppController and session state machine<br/>NEW - relocated"]
    RUN["evaluation/runner.py<br/>target sequence, report writer<br/>NEW"]
  end

  subgraph infra["INFRASTRUCTURE — frameworks, devices, filesystem"]
    TRK["tracker.py<br/>capture thread, fault signal, bounded retry<br/>MODIFIED"]
    FM["face_mesh.py<br/>MediaPipe adapter, solvePnP, model cache<br/>MODIFIED"]
    OVL["overlay.py<br/>GazeOverlay, CalibrationWindow<br/>MODIFIED"]
    STAT["status_window.py<br/>messages, Recalibrate, Retry, Quit, counters<br/>NEW"]
    LOG["logging_setup.py<br/>file, ring buffer, Qt bridge<br/>NEW"]
    ENTRY["main.py<br/>thin shim<br/>MODIFIED"]
  end

  subgraph artifacts["LOCAL ARTIFACTS"]
    A1[("eyetracker.toml<br/>NEW")]
    A2[("profiles/*.eyecal<br/>NEW")]
    A3[("logs/eyetracker.log<br/>NEW")]
    A4[("docs/evaluation/*<br/>NEW")]
    A5[("face_landmarker.task<br/>unchanged")]
  end

  ENTRY --> APP
  APP --> TRK
  APP --> OVL
  APP --> STAT
  APP --> PIPE
  APP --> PROF
  APP --> CFG
  APP --> LOG
  PIPE --> CALIB
  PIPE --> GATES
  PIPE --> EUR
  PIPE --> DIAG
  OVL --> GATES
  OVL --> GAZE
  CALIB --> GAZE
  PROF --> CALIB
  PROF --> GAZE
  TRK --> FM
  TRK --> GAZE
  TRK --> ERR
  FM --> POSE
  RUN --> PIPE
  RUN --> MET
  CFG --> GATES
  A1 -.-> CFG
  PROF -.-> A2
  LOG -.-> A3
  RUN -.-> A4
  FM -.-> A5
```

---

## Session State Machine

```mermaid
stateDiagram-v2
  [*] --> Starting
  Starting --> Restoring : profile restore enabled
  Starting --> AwaitingFace : no stored profile
  Restoring --> Live : manifest accepted and witness verified
  Restoring --> AwaitingFace : refused - reason shown in StatusWindow
  AwaitingFace --> Calibrating : first finite feature vector
  AwaitingFace --> Faulted : first-face timeout elapsed
  Calibrating --> Fitting : all targets attempted
  Calibrating --> Faulted : usable targets below the recorded minimum
  Calibrating --> [*] : user aborts - explicit quit
  Fitting --> Live : 6 GPs fitted, profile saved best-effort
  Live --> Calibrating : Recalibrate - disconnect, reset smoother and history, fresh window
  Live --> Faulted : capture fault or sustained prediction failure
  Faulted --> AwaitingFace : Retry accepted
  Faulted --> [*] : Quit
  Live --> [*] : Quit
```

---

## Target Lifecycle Sequence

```mermaid
sequenceDiagram
  participant U as Local User
  participant M as main shim
  participant AC as AppController
  participant SW as StatusWindow NEW
  participant PS as profile store NEW
  participant TR as GazeTracker
  participant CW as CalibrationWindow
  participant LP as LivePipeline NEW
  participant OV as GazeOverlay

  M->>M: parse args, load Settings, configure logging
  M->>M: setQuitOnLastWindowClosed False - NEW, owns lifetime
  M->>AC: construct on the GUI thread
  AC->>SW: show - state Starting
  AC->>TR: start - probing runs asynchronously
  AC->>PS: load_profile(fingerprint)
  alt profile accepted
    PS-->>AC: fitted calibrator, witnesses verified
    AC->>OV: construct and show
    AC->>LP: construct with the restored calibrator
    AC->>SW: state Live - restored from saved calibration
  else refused or absent
    PS-->>AC: refusal reason or none
    AC->>SW: show the named reason - never silent
    AC->>CW: construct - single use, WA_DeleteOnClose
    CW-->>AC: finished(CalibrationResult)
    Note over AC: no-op unless state is Calibrating - FR-7
    AC->>AC: enforce coverage rule inside fit - FR-8, FR-9
    AC->>OV: construct and show
    AC->>PS: save_profile - best effort, failure only warns
    AC->>SW: state Live
  end
  loop every frame
    TR-->>LP: features_ready - queued to the GUI thread
    LP->>LP: gate, motion, median, predict, smooth
    alt accepted
      LP->>OV: update_position and ensure dot visible
    else rejected or face lost
      LP->>LP: count by typed reason - FR-24
      LP->>OV: set_dot_visible False after debounce - FR-21
    end
  end
  TR-->>AC: fault(Fault) - NEW channel, replaces four silent deaths
  AC->>SW: message, remediation, Retry action - FR-20, FR-23
  U->>SW: Recalibrate - FR-22
  AC->>TR: disconnect the live receiver
  AC->>LP: reset smoother and history
  AC->>CW: construct a fresh window
```

---

## Gate Resolution and Rejection Accounting

```mermaid
flowchart TB
  subgraph def["ONE DEFINITION - config.py NEW"]
    BASE["CALIBRATION_GATE<br/>ear_min 0.16, blink 0.55, squint 0.55<br/>yaw 0.45, pitch 0.35, roll 0.60"]
    DEV["live_deviation<br/>blink +0.03, squint +0.03<br/>yaw +0.10, pitch +0.10, roll +0.10"]
    BASE --> LIVE["LIVE_GATE = base.widened(deviation)<br/>yaw 0.55, pitch 0.45, roll 0.70"]
    DEV --> LIVE
  end

  subgraph use["TWO CONSUMERS - one predicate each"]
    CAL["CalibrationWindow._on_feat<br/>MODIFIED - literals removed"]
    PIP["LivePipeline.step<br/>NEW - literals removed"]
  end

  BASE --> CAL
  LIVE --> PIP

  subgraph eval["FrameGate.check returns a typed result"]
    E1{"any feature non-finite ?"}
    E1 -->|yes| RJ1["NON_FINITE"]
    E1 -->|no| E2{"pose features NaN ?"}
    E2 -->|yes| RJ2["POSE_UNAVAILABLE - NEW, DR-16"]
    E2 -->|no| E3{"either EAR below floor ?"}
    E3 -->|yes| RJ3["EAR_A_LOW or EAR_B_LOW"]
    E3 -->|no| E4{"blink or squint above ceiling ?"}
    E4 -->|yes| RJ4["BLINK_HIGH or SQUINT_HIGH"]
    E4 -->|no| E5{"yaw above ceiling ?"}
    E5 -->|yes| RJ5["YAW_HIGH - now truly yaw"]
    E5 -->|no| E6{"pitch above ceiling ?"}
    E6 -->|yes| RJ6["PITCH_HIGH - NEW, FR-4. Nodding was ungated"]
    E6 -->|no| E7{"roll above ceiling ?"}
    E7 -->|yes| RJ7["ROLL_HIGH - now truly roll"]
    E7 -->|no| OK["ACCEPTED"]
  end

  CAL --> E1
  PIP --> E1

  RJ1 --> CNT["RejectionCounters<br/>count by typed reason - FR-24"]
  RJ2 --> CNT
  RJ3 --> CNT
  RJ4 --> CNT
  RJ5 --> CNT
  RJ6 --> CNT
  RJ7 --> CNT
  CNT --> SURF["StatusWindow table, periodic INFO log,<br/>evaluation report section"]
  CNT --> STALE{"sustained rejection<br/>beyond stale_after_ms ?"}
  STALE -->|yes| HIDE["hide the dot - FR-21,<br/>failure criterion 2"]
  OK --> SHOW["show the dot, update position"]
```

---

## Data Model — Local Artifacts

```mermaid
erDiagram
  PROFILE_BUNDLE ||--|| PROFILE_MANIFEST : "contains as manifest.json"
  PROFILE_BUNDLE ||--|| MODEL_PAYLOAD : "contains as model.joblib"
  PROFILE_MANIFEST ||--|| CAPTURE_FINGERPRINT : embeds
  PROFILE_MANIFEST ||--o{ WITNESS_SAMPLE : "embeds 3"
  PROFILE_MANIFEST ||--o{ TARGET_PROVENANCE : "embeds one per target"
  CONFIG_FILE ||--o{ SETTINGS_SECTION : contains
  EVALUATION_REPORT ||--|| PROTOCOL_RECORD : embeds
  EVALUATION_REPORT ||--o{ TARGET_ERROR : "embeds one per target"
  MODEL_CACHE_ASSET {
    string filename
    int bytes
  }
  PROFILE_BUNDLE {
    string path
    int bundle_format
    string created_utc
  }
  PROFILE_MANIFEST {
    int bundle_format
    string app_version
    int feature_semantics_version
    string feature_layout_digest
    int feature_count
    bool blendshapes_available
    string payload_sha256
    string joblib_version
    string sklearn_version
    string numpy_version
  }
  CAPTURE_FINGERPRINT {
    string backend_name
    int camera_index
    int capture_width
    int capture_height
    int capture_fps
    int screen_width
    int screen_height
  }
  WITNESS_SAMPLE {
    string feature_vector_hex
    float expected_x
    float expected_y
  }
  TARGET_PROVENANCE {
    int target_index
    string quality
    int strict_samples
    int total_samples
  }
  MODEL_PAYLOAD {
    string estimator
    int gp_count
  }
  CONFIG_FILE {
    string path
    string format
  }
  SETTINGS_SECTION {
    string name
    int field_count
  }
  EVALUATION_REPORT {
    string commit_sha
    bool worktree_dirty
    string measured_utc
    float mean_error_px
    float p95_error_px
    float mean_error_deg
    float p95_error_deg
  }
  PROTOCOL_RECORD {
    int target_count
    int session_count
    int viewing_distance_mm
    string lighting
    string camera
  }
  TARGET_ERROR {
    int target_index
    float error_px
    float error_deg
  }
```

---

## Profile Load — Refuse Before Unpickle

```mermaid
flowchart TB
  A["load_profile(fingerprint)"] --> B{"bundle exists ?"}
  B -->|no| N1["no profile - proceed to calibration<br/>not a fault"]
  B -->|yes| C["open zip, read manifest.json only"]
  C --> D{"bundle_format supported ?"}
  D -->|no| R1["REFUSE - format newer than this build"]
  D -->|yes| E{"feature_semantics_version matches ?"}
  E -->|no| R2["REFUSE - FR-18. Saved under different feature semantics"]
  E -->|yes| F{"feature_layout_digest matches ?"}
  F -->|no| R3["REFUSE - 38-D layout renumbered"]
  F -->|yes| G{"blendshapes_available matches ?"}
  G -->|no| R4["REFUSE - detector no longer supplies blendshapes"]
  G -->|yes| H{"capture fingerprint and screen match ?"}
  H -->|no| R5["REFUSE - FR-19. Camera, capture resolution or screen changed"]
  H -->|yes| I{"payload sha256 matches manifest ?"}
  I -->|no| R6["REFUSE - bundle corrupt"]
  I -->|yes| J{"joblib, sklearn, numpy majors compatible ?"}
  J -->|no| R7["REFUSE - serialised model not loadable by this build"]
  J -->|yes| K["unpickle model.joblib"]
  K --> L{"fitted and feature subsets identical ?"}
  L -->|no| R8["REFUSE - model shape differs from this build"]
  L -->|yes| M{"3 witness vectors reproduce within 1e-6 px ?"}
  M -->|no| R9["REFUSE - FR-17 round-trip identity failed"]
  M -->|yes| OK["ACCEPT - enter Live directly"]
  R1 --> Z["StatusWindow shows the named mismatch<br/>plus a Calibrate action. Never a silent load"]
  R2 --> Z
  R3 --> Z
  R4 --> Z
  R5 --> Z
  R6 --> Z
  R7 --> Z
  R8 --> Z
  R9 --> Z
```

---

## Migration Phase Dependencies

```mermaid
flowchart TB
  M0["M0 - Investigation and foundations<br/>FR-33 eye pairing, venv rebuild,<br/>pyproject.toml, logging, tests scaffold"]
  M1["M1 - Measurement FIRST<br/>FR-10, FR-11 harness plus<br/>PRE-FIX BASELINE recorded"]
  M2["M2 - Config and unified gates<br/>FR-13, FR-14, FR-15"]
  M3["M3 - Head-pose correctness<br/>FR-1, FR-2, FR-3, FR-4<br/>bumps FEATURE_SEMANTICS_VERSION to 2"]
  M4["M4 - Lifetime and calibration integrity<br/>FR-5, FR-6, FR-7, FR-22<br/>setQuitOnLastWindowClosed False"]
  M5["M5 - Minimum-sample enforcement<br/>FR-8, FR-9"]
  M6["M6 - Failure feedback and capture robustness<br/>FR-20 to FR-25, FR-30, FR-31, FR-32"]
  M7["M7 - Persistence LAST<br/>FR-16, FR-17, FR-18, FR-19"]
  M8["M8 - Post-fix re-measure<br/>FR-12 delta with 95 percent CI"]
  M0 --> M1
  M1 --> M2
  M2 --> M3
  M1 --> M3
  M3 --> M5
  M2 --> M4
  M4 --> M6
  M3 --> M7
  M5 --> M7
  M6 --> M7
  M3 --> M8
  M7 --> M8
  M1 -.->|"baseline is the comparison basis"| M8
  M3 -.->|"semantics must be stable before a profile can be written"| M7
```

---
