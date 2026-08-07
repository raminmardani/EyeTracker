# Patterns & Standards — EyeTracker

**Date**: 2026-08-07
**Author**: ARCHITECT
**Status**: **Approved** — all 11 pattern decisions user-approved 2026-08-07
**Version**: 1.0
**Based On**:
- [docs/architecture/current/00-system-overview.md](docs/architecture/current/00-system-overview.md)
- `docs/architecture/current/01-*-deep-dive.md` — 7 modules, 45 catalogued patterns
- [docs/architecture/design/02-target-architecture-brownfield.md](docs/architecture/design/02-target-architecture-brownfield.md) — approved 2026-08-07
- [docs/requirements.md](docs/requirements.md)
- [SPEC/rulebooks/aire-design-patterns.md](SPEC/rulebooks/aire-design-patterns.md), [aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md), [aire-clean-architecture.md](SPEC/rulebooks/aire-clean-architecture.md)

> **Reference check (mandatory)**: `SPEC/references/`, `SPEC/references/builds/` and `SPEC/references/devops/` contain **0 files**. No approved external material constrains any decision below.

> **Where the "recommended" side comes from.** [aire-design-patterns.md](SPEC/rulebooks/aire-design-patterns.md) is a generic Gang-of-Four quick reference written in JavaScript (Factory, Strategy, Repository, Observer, Adapter, plus an anti-pattern table). It contains no guidance on logging, configuration, API response format or naming. For those categories the recommended side is drawn from [aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md) (typed errors, never swallow, log with context, ≤20–30-line functions, no god classes, descriptive names, no secrets) and [aire-clean-architecture.md](SPEC/rulebooks/aire-clean-architecture.md) (the dependency rule). Each section states its own source rather than attributing a recommendation to a rulebook that does not make it.

---

## Pattern Adoption Summary

| # | Pattern | Decision | Migration Required | Traced to |
|---|---------|----------|--------------------|-----------|
| 1 | Project Structure | [Current — kept + extended] | No | DR-10 |
| 2 | Error Handling | **[New adoption]** | **Yes** — medium | FR-20, FR-24 |
| 3 | Logging | **[New adoption]** | **Yes** — low, 10 sites | FR-25 |
| 4 | Persistence & File I/O | [Current — kept + extended] | No | DR-7 |
| 5 | Internal Contract Format | [Current — kept] | No | — |
| 6 | Configuration | **[New adoption]** | **Yes** — medium, ~40 literals | FR-13, FR-14, FR-15 |
| 7 | Naming Conventions | [Current — kept, one scoped exception] | No | — |
| 8 | Code Organisation | [Current — kept + **enforced**] | No | DR-10 |
| 9 | UI Components / Shared Library | [Current — kept] | No | DR-12 |
| 10 | Concurrency & Thread Affinity | [Current — kept, **made explicit**] | No | Approved architecture |
| 11 | Numerical Guards | [Current — kept] | No | — |
| 12 | Annotations & Docstrings | **[New adoption]** | No — new/touched code only | Implementation rulebook |
| 13 | Lint & Format Tooling | **[New adoption]** — ruff | **Yes** — low, 3 lines | Quality gates |
| 14 | Function & File Length | **[New adoption]** — ≤30 + allowlist | **Yes** — as code is touched | Implementation rulebook |
| 15 | Testing | **[New adoption]** — none exists | **Yes** — high, 0% today | FR-26 – FR-29 |
| 16 | Documentation | **[New adoption]** | No | Implementation rulebook |

**Two workflow categories are N/A and were reframed rather than left empty:**

| Workflow category | Why N/A | Reframed as |
|---|---|---|
| Database Access | No database, no ORM, no persistence layer exists, and the approved architecture introduces none. The rulebook's **Repository** pattern abstracts database access and has nothing to abstract here | **§4 Persistence & File I/O** |
| API Response Format | No HTTP, RPC or network API exists and none is introduced. The only outbound call is a one-time model download | **§5 Internal Contract Format** — Qt signal payloads and module public surfaces |

---

## Legend

| Marker | Meaning |
|---|---|
| `[Current — kept]` | The codebase already does this and it stays the standard |
| `[New adoption]` | New standard. A **Migration Note** states what changes and when |
| 🔴 | Violating this is a review failure |
| ⚠️ | Permitted only with the stated justification recorded in code |

---

## 1. Project Structure  `[Current — kept + extended]`

**Current** (verified): flat `eye_tracker/` package plus `main.py` at the root. Dependencies are strictly one-way and acyclic — the single strongest structural property of this codebase.

**Recommended** ([aire-clean-architecture.md](SPEC/rulebooks/aire-clean-architecture.md)): physical `domain/` `application/` `infrastructure/` directories.

**Decision**: keep the flat package; declare the layers **logically** and enforce the dependency rule with a test. Rationale in DR-10 — a physical restructure would break the import paths of the 38-D contract's four consumers and every file path cited across eight analysis documents, for no behavioural gain.

### Target layout

```
EyeTracker/
├── pyproject.toml               # NEW — packaging, ruff, pytest, coverage (FR-26)
├── main.py                      # thin entry shim only
├── eye_tracker/
│   ├── __init__.py              # __version__ only — no re-exports
│   │   # ---- CORE: pure. No PyQt6, no cv2, no sklearn, no mediapipe, no I/O ----
│   ├── gaze.py                  # the 38-D contract + semantics version
│   ├── pose.py                  # NEW — Euler extraction, wrap_to_pi
│   ├── gates.py                 # NEW — FrameGate, RejectionReason
│   ├── config.py                # NEW — Settings tree, TOML overlay
│   ├── errors.py                # NEW — EyeTrackerError hierarchy, Fault
│   ├── diagnostics.py           # NEW — counters, rate limiter
│   ├── one_euro.py              # + reset()
│   │   # ---- APPLICATION: orchestration and model policy. No PyQt6 ----
│   ├── pipeline.py              # NEW — LivePipeline
│   ├── calibration.py           # 6 GPs, min-sample enforcement
│   ├── profile.py               # NEW — bundle write / refuse-before-unpickle load
│   ├── app.py                   # NEW — AppController + session state machine
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py           # NEW — pure error statistics
│   │   ├── protocol.py          # NEW — protocol record
│   │   ├── runner.py            # NEW — target sequence
│   │   └── report.py            # NEW — md + json writer
│   │   # ---- INFRASTRUCTURE: frameworks, devices, filesystem ----
│   ├── tracker.py               # capture thread, fault signal
│   ├── face_mesh.py             # MediaPipe adapter, solvePnP, model cache
│   ├── overlay.py               # GazeOverlay, CalibrationWindow
│   ├── status_window.py         # NEW — messages, actions, counters
│   ├── logging_setup.py         # NEW — handlers, ring buffer, Qt bridge
│   └── tools/
│       ├── __init__.py
│       └── eye_pairing.py       # NEW — FR-33 diagnostic
└── tests/                       # NEW (FR-27)
    ├── conftest.py
    ├── unit/  integration/  regression/  invariants/  arch/
```

### Rules

| Rule | Detail |
|---|---|
| 🔴 One concern per module | A new concern gets a new module, never an append to `overlay.py` (already the largest at 267 lines) |
| 🔴 Layer membership is declared in the module docstring | First line after the summary: `Layer: core` / `application` / `infrastructure` |
| 🔴 Dependency direction | `infrastructure → application → core`. Never the reverse |
| Import ordering | stdlib → third-party → first-party, blank-line separated, alphabetical within group — enforced by `ruff` rule `I`. This is already the de-facto style in all 8 files |
| Relative imports inside the package | `from .gaze import ...` — matches every existing intra-package import |
| Dependency management | `requirements.txt` stays the runtime constraint file with bounds on both sides; dev tooling goes in `pyproject.toml` `[project.optional-dependencies].dev` |

### DO / DON'T

```python
# DO — core module declares its layer and imports nothing outward
"""Frame acceptance gates.

Layer: core
"""
from .gaze import FEATURE_A_EAR, FEATURE_YAW      # core -> core: allowed

# DON'T — a core module reaching for a framework or an outer layer
from PyQt6.QtCore import QObject                   # core must never import Qt
from .tracker import GazeTracker                   # core must never import infrastructure
```

---

## 2. Error Handling Pattern  `[New adoption]`

**Current** (verified): the codebase holds **both extremes with no stated rule**. The consumer swallows everything and prints at frame rate; the equally failure-prone producer loop has no guard at all and dies permanently on the first exception.

```python
# CURRENT — main.py:113-117. Unbounded printing to a stream a windowed app discards.
try:
    pred, var = self.calibrator.predict_with_variance(feat_for_pred)
except Exception as exc:  # predictor rarely but can fail on degenerate input
    print(f"[predict] {exc}")
    return

# CURRENT — tracker.py:149-171. try/finally with NO except: one transient
# MediaPipe error terminates the producer permanently and silently.
try:
    while not self._stop:
        result = mesh.process(frame)          # can raise
        feat = extract_gaze_features(result)  # can raise
finally:
    cap.release()
    mesh.close()
```

**Recommended** ([aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md) → Code Standards → Error Handling): use typed errors, never swallow errors, log with context, user-friendly messages.

**Migration Note**: replace both extremes with the F0–F4 taxonomy from the approved architecture. Lands in phase **M6** for the producer paths and **M2/M5** for the refusal paths. Every `except Exception` that only prints is a review failure from that phase onward. Existing behaviour is preserved where it was already correct — the atomic download's `raise ... from exc` is the model, not the exception.

### The one stated rule

| Category | Definition | Handling |
|---|---|---|
| **F0 Frame-local** | One frame's data is unusable | Drop, count by reason, **no message**. Escalate to F2 if the sustained rate crosses `live.stale_after_ms` |
| **F1 Transient subsystem** | A collaborator failed once and may recover | Bounded retry, counted, rate-limited log. Message only when the bound is exceeded |
| **F2 Session fault** | Cannot continue as-is; recovery possible | Visible message + remediation + action; enter `Faulted`; app stays alive |
| **F3 Precondition** | Cannot start | Visible message with remediation text; offer Retry / Quit |
| **F4 Contract refusal** | A deliberate, correct refusal | Explicit message naming the mismatch. **Never degrade silently** |

### Exception hierarchy

```python
# eye_tracker/errors.py — Layer: core
class EyeTrackerError(Exception):
    """Base for every failure this application raises deliberately.

    Catching this separates our own refusals from genuine programming bugs,
    which is what makes the F4 category distinguishable at runtime.
    """


class ConfigError(EyeTrackerError):
    """F3 — malformed or out-of-range configuration."""


class DetectorUnavailableError(EyeTrackerError):
    """F3 — no usable MediaPipe API, or the model asset could not be obtained."""


class CameraUnavailableError(EyeTrackerError):
    """F3 — no candidate camera produced a usable image."""


class CaptureLostError(EyeTrackerError):
    """F2 — capture failed beyond the configured retry bound."""


class InsufficientCalibrationDataError(EyeTrackerError):
    """F4 — the calibration coverage rule was not met."""


class ProfileRefusedError(EyeTrackerError):
    """F4 — a stored calibration was rejected. Carries ``reason`` and ``remediation``."""
```

🔴 `ProfileRefusedError` and `InsufficientCalibrationDataError` **must** carry a machine-readable `reason` and a human `remediation`, because both are surfaced verbatim to a user who may not be able to use a mouse.

### DO / DON'T

```python
# DO — narrow the type, count it, rate-limit, escalate on persistence
try:
    pred, var = self.calibrator.predict_with_variance(feat_for_pred)
except (ValueError, RuntimeError) as exc:
    self.counters.bump(RejectionReason.PREDICT_ERROR)
    rate_limited(log, "predict_failed").warning("prediction failed", exc_info=exc)
    if self.counters.consecutive(RejectionReason.PREDICT_ERROR) > settings.live.predict_failure_limit:
        raise CaptureLostError("prediction is failing persistently") from exc
    return

# DON'T — swallow everything and print at frame rate to a discarded stream
except Exception as exc:
    print(f"[predict] {exc}")
    return
```

```python
# DO — a producer loop survives one transient fault and surfaces a sustained one
while not self._stop:
    try:
        frame = self._read_frame(cap)
        self.features_ready.emit(extract_gaze_features(mesh.process(frame)))
        failures = 0
    except Exception as exc:                      # broad HERE is deliberate: the loop must not die
        failures += 1
        rate_limited(log, "capture_frame").warning("frame failed", exc_info=exc)
        if failures > settings.camera.read_failure_limit:
            self.fault.emit(Fault.f2("capture_lost", "The camera stopped responding.",
                                     remediation="Reconnect the camera, then press Retry."))
            return

# DON'T — no except at all: one transient error kills the producer forever
try:
    while not self._stop:
        ...
finally:
    cap.release()
```

```python
# DO — a refusal names the mismatch and never degrades
raise ProfileRefusedError(
    reason="feature_semantics_version",
    message="Your saved calibration was created before the head-pose correction.",
    remediation="Run calibration once to create a new profile.",
)

# DON'T — load it anyway and hope. Failure criterion 3 names this the
# highest-severity outcome available in this scope.
if manifest["feature_semantics_version"] != FEATURE_SEMANTICS_VERSION:
    log.warning("version mismatch, loading anyway")
```

🔴 **`raise ... from exc` always.** The one existing raise site already does this ([face_mesh.py:70](eye_tracker/face_mesh.py#L70)); it is the standard.

---

## 3. Logging Pattern  `[New adoption]`

**Current** (measured, not quoted): **10 `print()` sites across 3 modules** — [main.py](main.py) 2, [overlay.py](eye_tracker/overlay.py) 3, [tracker.py](eye_tracker/tracker.py) 5. No levels, no destination control, discarded entirely by a windowed application.

> The analysis documents record "nine sites across four modules". Measured directly against source it is **10 across 3**. This document carries the measured figure.

**Recommended** ([aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md)): log with context; never log secrets.

**Migration Note**: mechanical, phase **M0** (setup) then **M6** (call sites). The existing `[module]` bracket prefixes are already hand-rolled logger names, so each site converts one-for-one. 🔴 After M6, a `print()` anywhere in `eye_tracker/` or `main.py` is a review failure — enforced by ruff rule `T20`.

### Levels

| Level | Use for | Example |
|---|---|---|
| `DEBUG` | Per-frame detail, feature values | gate outcome for one frame |
| `INFO` | Lifecycle and one-off outcomes | camera selected, profile restored, fit completed in 4.1 s |
| `WARNING` | Recovered or degraded, F0/F1 | relaxed sample buffer used for a target, one prediction failure |
| `ERROR` | F2/F3/F4 — user is being told | camera lost, profile refused, coverage rule not met |
| `CRITICAL` | Not used | reserved; nothing in a single-user desktop app qualifies |

### Logger names — the existing convention, kept

`eye_tracker.tracker` · `eye_tracker.face_mesh` · `eye_tracker.calibration` · `eye_tracker.overlay` · `eye_tracker.profile` · `eye_tracker.app` · `eye_tracker.app.predict`

### DO / DON'T

```python
# DO — module-level logger named after the module, lazy % formatting, context
import logging
log = logging.getLogger(__name__)          # -> "eye_tracker.tracker"

log.info("camera selected", extra={"index": idx, "backend": name, "faces": detected})
log.warning("relaxed buffer used for target %d (%d strict / %d total)",
            point_no, len(self._buf), len(self._fallback_buf))

# DON'T — print, or an f-string that formats even when the level is disabled
print(f"[tracker] selected camera index {idx}")
log.debug(f"feature vector {feat}")        # formats the whole 38-vector every frame
```

### What must never be logged  🔴

| Never | Why |
|---|---|
| Camera frames, or any path one was written to | Biometric image data. Nothing in this application persists a frame |
| `pts2d` landmark arrays | 478 points of facial geometry — biometric |
| Blendshape maps | Expression data — biometric |
| Full feature vectors above `DEBUG` | Derived biometrics. At `DEBUG` they go to the in-memory ring buffer only, unless the user explicitly enables file debug logging |
| Absolute paths containing the OS username | Log the resolved directory once at startup, then relative names |

There are no credentials, tokens or API keys anywhere in this application, so the rulebook's secrets rule has nothing to bite on — recorded so a future reviewer does not assume it was overlooked.

### Rate limiting — required, not optional

```python
# DO — 1st, 10th, 100th, then every 1000th, keyed per (logger, code)
rate_limited(log, "predict_failed").warning("prediction failed", exc_info=exc)

# DON'T — the current behaviour: unbounded printing at 30 Hz
print(f"[predict] {exc}")
```

### Thread safety  🔴

Log records originate on the capture thread. The Qt bridge handler is a `QObject` **constructed on the GUI thread** that only **emits a signal** — it must never touch a widget.

```python
# DO — the handler emits; the GUI thread paints
class QtSignalHandler(logging.Handler, QObject):
    record_ready = pyqtSignal(object)
    def __init__(self):
        QObject.__init__(self)
        assert QThread.currentThread() is QApplication.instance().thread()
        logging.Handler.__init__(self)
    def emit(self, record):
        self.record_ready.emit(self.format(record))   # queued to the GUI thread

# DON'T — paint from whatever thread logged
def emit(self, record):
    self.status_window.set_message(record.getMessage())   # cross-thread widget access
```

---

## 4. Persistence & File I/O  `[Current — kept + extended]`

*(Reframed from the workflow's "Database Access" — no database exists and none is introduced.)*

**Current**: exactly one write site, and it is the most careful I/O in the codebase — unique temp name, atomic `replace`, cleanup tolerating `FileNotFoundError`, and `raise ... from exc`.

**Recommended**: the rulebook offers **Repository**, which abstracts *database* access. There is nothing to abstract. Judged not applicable rather than adopted — forcing a repository over two local files would be the rulebook's own **Premature Optimization** anti-pattern.

**Decision**: the existing atomic-write pattern becomes the project standard for **every** file write, and is extended to the calibration profile per DR-7.

### DO / DON'T

```python
# DO — the established pattern, generalised (face_mesh.py:56-71 is the origin)
tmp = target.with_suffix(f"{target.suffix}.{os.getpid()}.tmp")
try:
    with tmp.open("wb") as dst:
        dst.write(payload)
    tmp.replace(target)                  # atomic on POSIX and Windows
except OSError as exc:
    tmp.unlink(missing_ok=True)
    raise ProfileWriteError(f"Could not save the calibration to {target}.") from exc

# DON'T — stream straight to the destination: a crash leaves a valid-looking corrupt file
with target.open("wb") as dst:
    dst.write(payload)
```

### Deserialisation ordering  🔴

```python
# DO — read the manifest and refuse BEFORE unpickling. The manifest is JSON inside
#      a ZIP for exactly this reason: joblib.load executes arbitrary code.
with zipfile.ZipFile(path) as z:
    manifest = json.loads(z.read("manifest.json"))
    _refuse_unless_compatible(manifest)          # raises ProfileRefusedError
    payload = z.read(manifest["payload"]["file"])
    if hashlib.sha256(payload).hexdigest() != manifest["payload"]["sha256"]:
        raise ProfileRefusedError(
            reason="payload_digest",
            message="Your saved calibration file is damaged.",
            remediation="Run calibration once to replace it.",
        )
    calibrator = joblib.load(io.BytesIO(payload))
_verify_witnesses(calibrator, manifest)          # 1e-6 px, FR-17

# DON'T — unpickle first and validate after. By then the payload has already run.
calibrator = joblib.load(path)
if calibrator.semantics_version != FEATURE_SEMANTICS_VERSION:
    raise ...
```

⚠️ A profile is **trusted local input only**. There is deliberately no import-from-path UI. The SHA-256 detects corruption, **not tampering** — an attacker who can rewrite the payload can rewrite the digest beside it. Filesystem ownership is the actual control. Do not describe the digest as a signature.

---

## 5. Internal Contract Format  `[Current — kept]`

*(Reframed from the workflow's "API Response Format" — no HTTP or RPC surface exists.)*

**Current**: a 38-element positional vector whose every index has a named constant, consumed by four modules; Qt signals for all cross-component notification; one adapter normalising two detector backends to a single return shape.

**Recommended**: the rulebook's **Observer** pattern *is* Qt signals, and its **Adapter** pattern *is* `FaceMeshWrapper` — both already implemented idiomatically. Nothing to adopt.

### DO / DON'T

```python
# DO — index the shared contract by name
blink = feat[FEATURE_BLINK_AVG]

# DON'T — a literal offset. Renumbering silently changes meaning in 4 modules.
blink = feat[36]
```

```python
# DO — every backend branch returns the identical shape, so callers stay backend-agnostic
return {"landmarks": ..., "blendshapes": ..., "facial_matrix": ...}

# DON'T — a branch that returns a different shape, pushing the branch into every caller
if self._mode == "tasks":
    return landmarks, blendshapes
return landmarks
```

### Rules for the 38-D contract  🔴

| Rule | Reason |
|---|---|
| 🔴 Index numbering never changes | Failure criterion 6. Values may change; positions may not |
| 🔴 A change of *meaning* bumps `FEATURE_SEMANTICS_VERSION` | FR-18. The layout digest catches accidental renumbering as a second line of defence |
| 🔴 `len(vector) == FEATURE_COUNT` is asserted | The constant exists today and is never used |
| 🔴 Absent optional input becomes `NaN`, never a neutral value | A `solvePnP` failure must not read as a perfectly centred head (DR-16) |
| Signal payloads are fresh, never reused buffers | This is why the codebase has zero locks — see §10 |

---

## 6. Configuration Pattern  `[New adoption]`

**Current**: none. ~40 behavioural constants are literals at their use sites across 5 modules, including **two divergent copies** of the frame gate (TD-1).

**Recommended** ([aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md)): no hardcoded values; environment variables for anything environment-specific.

**Migration Note**: phase **M2**, and it must land **before** the head-pose fix in M3 so the gate re-pairing has one place to happen. 🔴 M2 is behaviour-preserving: golden tests assert every resolved setting equals today's literal **before** M3 changes any of them. The full literal-to-setting inventory is in the approved architecture document.

### Structure

```python
# eye_tracker/config.py — Layer: core
@dataclass(frozen=True, slots=True)
class GateSettings:
    ear_min: float = 0.16
    blink_max: float = 0.55
    squint_max: float = 0.55
    yaw_max: float = 0.45      # re-paired: inherited from today's PITCH-named gate
    pitch_max: float = 0.35    # provisional — nodding has never been gated
    roll_max: float = 0.60     # re-paired: inherited from today's YAW-named gate

    def widened(self, **deltas: float) -> "GateSettings":
        """Return a copy with named ceilings raised — the live envelope."""
        return replace(self, **{k: getattr(self, k) + v for k, v in deltas.items()})
```

Precedence: **defaults → TOML file → environment → CLI flags**. 🔴 An unknown key in the TOML file is an **error**, not a silent ignore — a typo must never leave a default quietly in place.

### DO / DON'T

```python
# DO — one definition; the second envelope is an explicit named deviation
CALIBRATION_GATE = settings.gate
LIVE_GATE = CALIBRATION_GATE.widened(blink=0.03, squint=0.03,
                                     yaw=0.10, pitch=0.10, roll=0.10)

# DON'T — two independent literal blocks. This is TD-1, and they HAVE diverged
# on 4 of 6 thresholds (main.py:95-100 vs overlay.py:182-187).
if blink > 0.58 or abs(feat[FEATURE_YAW]) > 0.70:   # live
    ...
if blink > 0.55 or abs(yaw) > 0.60:                 # calibration
    ...
```

### Tunable vs numerical guard — the boundary, stated  🔴

| Kind | Treatment | Examples |
|---|---|---|
| **Behavioural constant** | Must be a setting | gate thresholds, dwell times, motion thresholds, kernel bounds, dot radius |
| **Numerical guard** | **Stays a literal at the point of construction** | `+ 1e-6` on a divisor, `np.maximum(std*std, 1e-6)`, `max(cutoff, 1e-3)`, `max(dt, 1e-3)`, `mad > 1e-6` |

Success criterion 8 ("no behavioural constant remains a literal at its use site") is read as applying to constants that change behaviour. Epsilons prevent division by zero; making them configurable would invite a user to break the numerics. This is the codebase's own established habit — three independent modules apply it identically.

```python
# DO — guard where the divisor is produced, one site, uniform magnitude
eye_w = float(np.linalg.norm(eye_vec)) + 1e-6

# DON'T — promote a numerical guard to configuration
eye_w = float(np.linalg.norm(eye_vec)) + settings.numerics.epsilon
```

---

## 7. Naming Conventions  `[Current — kept, one scoped exception]`

**Current**: consistent across all seven modules and independently praised in six of the seven deep-dive catalogs.

| Kind | Convention | Example |
|---|---|---|
| Contract constants | `FEATURE_<UPPER_SNAKE>` | `FEATURE_A_UPPER_CLEAR` |
| Landmark constants | `EYE_<A\|B>_<PART>` | `EYE_A_OUTER` |
| Private module constants | `_<UPPER_SNAKE>` | `_MODEL_POINTS` |
| Private classes | `_<PascalCase>` | `_ScreenRegressor`, `_OneEuro1D` |
| Public classes | `<PascalCase>` | `GazeCalibrator` |
| Functions / methods | `<lower_snake>` | `extract_gaze_features` |
| Private functions | `_<lower_snake>` | `_eye_geometry` |
| Qt slots | `_on_<event>` | `_on_feat`, `_on_calib_done` |
| **Qt overrides** | **Qt's own `camelCase`** | `paintEvent`, `keyPressEvent` |
| Signals | `<lower_snake>`, past participle | `features_ready`, `finished` |
| Eye identity | neutral `A` / `B`, never left/right | sidesteps the mirroring ambiguity |

**The rulebook conflict, and its resolution.** [aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md) requires "no single-letter names except loops". [one_euro.py](eye_tracker/one_euro.py) deliberately uses `a`, `a_d`, `tau`, `dx_hat` — and the deep-dive judged this **correct**, because the module cites Casiez, Roussel & Vogel (CHI 2012), so the paper supplies the vocabulary. Renaming would sever the code from its verifiable reference.

⚠️ **Scoped exception**: short mathematical locals are permitted **only inside a function whose docstring cites the source that defines them**. No citation, no short names. This converts a rulebook violation into a rule with a precondition.

### DO / DON'T

```python
# DO — short names, because the citation supplies the vocabulary
def _alpha(cutoff: float, dt: float) -> float:
    """Smoothing coefficient from a cutoff frequency.

    Notation follows Casiez, Roussel & Vogel, CHI 2012, section 3.
    """
    tau = 1.0 / (2.0 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)

# DON'T — short names with no cited source
def _calc(c, d):
    t = 1.0 / (2.0 * math.pi * c)
    return 1.0 / (1.0 + t / d)
```

```python
# DO — preserve Qt's camelCase for framework overrides, snake_case for ours
def paintEvent(self, event): ...        # Qt's contract
def _begin_collect(self): ...           # ours

# DON'T — rename a framework override to match local style. It stops being an override.
def paint_event(self, event): ...       # never called by Qt
```

---

## 8. Code Organisation  `[Current — kept + enforced]`

**Current**: clean acyclic dependencies, verified across all 8 files. Nothing imports upward.

**Recommended**: the clean-architecture rulebook's directory restructure and its `grep`-based validation checklist.

**Decision**: keep the layout, adopt the rulebook's **goal** — the dependency rule — and enforce it with a test instead of a directory shape. An AST test is a stricter check than the rulebook's own `grep` suggestion.

```python
# tests/arch/test_import_direction.py
CORE = {"gaze", "pose", "gates", "config", "errors", "diagnostics", "one_euro"}
FORBIDDEN_IN_CORE = {"PyQt6", "cv2", "sklearn", "mediapipe", "joblib"}

def test_core_imports_no_framework_and_nothing_outward():
    for module in CORE:
        for imported in imports_of(f"eye_tracker/{module}.py"):
            assert imported.split(".")[0] not in FORBIDDEN_IN_CORE
            assert imported not in APPLICATION | INFRASTRUCTURE
```

### DO / DON'T

```python
# DO — infrastructure depends on core; the pure logic is reusable and testable
# eye_tracker/face_mesh.py  (infrastructure)
from .pose import euler_from_rotation_matrix

# DON'T — core reaching outward, which makes the pure module untestable without a camera
# eye_tracker/pose.py  (core)
from .face_mesh import FaceMeshWrapper
```

---

## 9. UI Components / Shared Library  `[Current — kept]`

**Current**: [overlay.py](eye_tracker/overlay.py) holds both widgets (`GazeOverlay`, `CalibrationWindow`); no shared-widget location exists. The target architecture adds a third window, `status_window.py`.

**Recommended** ([aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md) → UI PRIMITIVE CHECK): generic components belong in a shared library, never in a feature folder.

**Assessment**: with three widgets total and no duplicated widget code (step 2a found none), creating a `widgets/` shared subpackage now would be the rulebook's own **Premature Optimization** anti-pattern.

**Decision**: **[Current — kept]** — one module per window, with a stated trigger for revisiting.

| Rule | Detail |
|---|---|
| One module per window | `status_window.py` is its own module, **not** appended to the 267-line `overlay.py` |
| Widget-local helpers stay with their widget | `_representative_feature` stays in `overlay.py` — it has one caller |
| 🔴 **Promotion trigger** | The **third** consumer of any widget helper moves it to `eye_tracker/widgets/`. Not the second — two callers is a coincidence; three is a pattern |
| 🔴 No business logic in a widget | Gating, prediction and sample selection belong in `core`/`application`. A widget paints and collects input |

### DO / DON'T

```python
# DO — the widget asks core for the decision
result = LIVE_GATE.check(feat)
if not result.accepted:
    self.counters.bump(result.reason)
    return

# DON'T — thresholds inlined in a widget, which is how TD-1 came to exist
if ear_a < 0.16 or blink > 0.55 or abs(yaw) > 0.60:
    return
```

---

## 10. Concurrency & Thread Affinity  `[Current — kept, made explicit]`

*Not one of the workflow's categories. Included because it is the most fragile correctness property in the system and the one most easily destroyed by a well-intentioned change — failure criterion 10 exists for it.*

**Current**: correct, and nowhere asserted. Zero locks, because every feature vector is a freshly allocated array published by value; queued signal delivery, because both receivers happen to be constructed on the GUI thread.

### Rules

| Rule | Why |
|---|---|
| 🔴 Publish by value; never emit a reused buffer | The **only** reason this codebase needs no locks |
| 🔴 Assert GUI-thread affinity in every signal receiver's `__init__` | If a receiver were built on the worker thread, Qt would switch to a direct connection and `QPainter` would run on the capture thread. The system would still start and would fail like a rendering bug |
| 🔴 Exactly one worker thread | Adding a second changes the whole concurrency argument |
| 🔴 No shared mutable state across the boundary | Failure criterion 10 |
| Cooperative stop flags use `threading.Event` | States the intent that a bare `bool` only implies |

### DO / DON'T

```python
# DO — a fresh array per frame, and the affinity dependency made loud
def __init__(self):
    super().__init__()
    assert QThread.currentThread() is QApplication.instance().thread(), \
        "receiver must be built on the GUI thread or Qt uses a direct connection"

feat = extract_gaze_features(result)      # new ndarray every call
self.features_ready.emit(feat)

# DON'T — "optimise" the allocation away and silently introduce a data race
self._scratch[:] = extract_gaze_features(result)
self.features_ready.emit(self._scratch)
```

---

## 11. Numerical Guards  `[Current — kept]`

*Not one of the workflow's categories. Included because three independent modules already apply it identically, which makes it a genuine project pattern worth codifying.*

```python
# DO — floor every quantity that could divide or vanish, at the point of construction
eye_w = float(np.linalg.norm(eye_vec)) + 1e-6      # gaze.py:87
var = np.maximum(std * std, 1e-6)                  # calibration.py:250
dt = max(t - self._t, 1e-3)                        # one_euro.py:30

# DON'T — a conditional at each use site, or nothing at all
dx = np.dot(iris_offset, u) / eye_w if eye_w > 0 else 0.0
```

⚠️ Record the side effect where it matters: the `+1e-6` in `eye_h` is why the lid-clearance identity sums to `1 − 3.5e-8` rather than exactly 1. Tests assert `abs=1e-6`, never exact equality.

---

## 12. Annotations & Docstrings  `[New adoption]`

**Current** (measured): **1 of 56** functions carries any annotation; **6 of 65** defs have a docstring; 7 of 7 functional modules have a module docstring.

**Recommended** ([aire-implementation-rulebook.md](SPEC/rulebooks/aire-implementation-rulebook.md) → Documentation): document public classes and methods with params, returns and errors; explain WHY, not WHAT.

**Migration Note**: applies to **new and touched** code only. No repo-wide annotation sweep — that would produce a large diff with no behavioural benefit and would compete with the migration phases for review attention.

| Scope | Standard |
|---|---|
| New modules | Fully annotated, including return types |
| Touched functions | Annotate while you are in there |
| Untouched code | Left alone |
| Public functions and classes | NumPy-style docstring with `Parameters`, `Returns`, `Raises` |
| Private helpers | One-line docstring where the name is not self-evident |
| 🔴 Every module | Docstring whose second line declares `Layer: core \| application \| infrastructure` |

### DO / DON'T

```python
# DO — annotated, NumPy-style, and it documents WHY the wrap exists
def euler_from_rotation_matrix(rmat: np.ndarray) -> tuple[float, float, float]:
    """Return (yaw, pitch, roll) in radians for OpenCV's camera frame.

    Parameters
    ----------
    rmat : ndarray, shape (3, 3)
        Rotation matrix from ``cv2.Rodrigues``.

    Returns
    -------
    tuple of float
        Yaw, pitch and roll. Pitch is centred on 0 for an upright frontal
        face; the raw X rotation rests at ±pi because ``_MODEL_POINTS`` is
        +Y-up/+Z-toward-viewer while the camera frame is +Y-down/+Z-into-scene,
        which would otherwise place a branch cut at the most common head pose.

    Raises
    ------
    ValueError
        If ``rmat`` is not 3x3.
    """

# DON'T — restate the signature in prose, and add nothing a reader could not see
def euler_from_rotation_matrix(rmat):
    """Takes a rotation matrix and returns the euler angles."""
```

---

## 13. Lint & Format Tooling  `[New adoption]`

**Current**: none. No linter, no formatter, no config — while the quality gates require zero lint errors.

**Decision**: **ruff** for both linting and formatting. One tool, config in the `pyproject.toml` that FR-26 requires anyway, so no new file.

**Migration Note**: `line-length = 100` was chosen by measurement, not habit — at 100 only **3 lines** in the entire codebase need touching (2 in `main.py`, 1 in `tracker.py`, both files heavily modified anyway); at 88 it would be 13. The longest existing line is 108.

```toml
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM", "RET", "PTH", "NPY", "T20", "PLR0915", "RUF"]
#         T20 = no print()  (FR-25)   PLR0915 = too many statements (§14)

[tool.ruff.lint.per-file-ignores]
# §14 allowlist — declarative constructions where splitting would fragment a
# single contract. Each entry states its reason; nothing is exempted silently.
"eye_tracker/gaze.py"    = ["PLR0915"]  # extract_gaze_features: one 38-element contract literal
"eye_tracker/overlay.py" = ["PLR0915"]  # Qt widget __init__: flat window-flag/attribute setup
"tests/*"                = ["PLR0915"]  # long AAA test bodies are clearer than helper indirection
```

🔴 CI runs `ruff check` and `ruff format --check`. A warning is a failure, per the implementation rulebook's NO LINT ERRORS rule.

---

## 14. Function & File Length  `[New adoption]`

**Current** (measured): **10 of 56** functions exceed 30 lines. **0 files** exceed 500 lines — the largest is `overlay.py` at 267.

| Lines | Function |
|---|---|
| 95 | `gaze.py::extract_gaze_features` |
| 47 | `tracker.py::_open_capture` |
| 43 | `overlay.py::CalibrationWindow.__init__` |
| 39 | `main.py::_on_feat` |
| 37 | `gaze.py::_eye_geometry` |
| 35 | `face_mesh.py::FaceMeshWrapper.__init__` |
| 34 | `overlay.py::_on_feat`, `tracker.py::_run` |
| 32 | `face_mesh.py::_detect_landmarks`, `overlay.py::_finish_collect` |

**Decision**: target ≤30 lines for new and refactored functions, with an **auditable allowlist** for declarative constructions.

**Migration Note**: applied as code is touched, not as a separate refactor. Most offenders shrink naturally — `_on_feat` moves into `LivePipeline`, `_run`'s body gains extracted helpers, `_open_capture` splits at the probe boundary. The allowlist covers only the cases where splitting would *reduce* safety:

| Allowlisted | Reason |
|---|---|
| `extract_gaze_features` | A single 38-element array literal **is** the contract. Splitting it into partial builders introduces index-mismatch risk between the parts and separates the layout from the constants that name it |
| Qt widget `__init__` | Flat window-flag and attribute setup. Extracting `_setup_flags()` helpers adds indirection without adding meaning |
| Test bodies | An explicit Arrange/Act/Assert body is clearer than helper indirection that hides what is being asserted |

🔴 Every allowlist entry lives in `pyproject.toml` **with its reason as a comment**. Adding one is a review decision, not a convenience.

---

## 15. Testing Patterns  `[New adoption]`

**Current**: none. 0% coverage across 1,295 LOC. No `tests/`, no `conftest.py`, no framework, no test dependency. Per the brownfield rulebook's red-flag rule, all seven modules qualify as "large module with no tests → document as risk".

**Tooling**: pytest + pytest-cov + pytest-qt.

⚠️ **Blocked on open item 6** — `.venv/` has no `Scripts/python.exe` and no `pyvenv.cfg`, so no runner can execute. This blocks migration phase M0 and therefore every test below.

### Layout

```
tests/
├── conftest.py          # offscreen Qt app, synthetic pts2d builder, stub tracker, fitted calibrator
├── unit/                # pose, gaze, gates, config, metrics, one_euro, diagnostics, profile manifest
├── integration/         # calibration state machine, session transitions, tracker with a fake capture
├── regression/          # test_defect_003.py … test_defect_009.py — one module per defect
├── invariants/          # the verified-correct behaviours FR-29 protects
└── arch/                # import-direction test (§8)
```

### Naming — behavioural, not implementational

```python
# DO — the name states the behaviour, so a failure report is self-explanatory
def test_aborting_in_the_inter_target_gap_emits_finished_exactly_once(): ...
def test_each_pose_output_tracks_the_axis_its_name_claims(): ...
def test_loading_a_profile_from_a_different_camera_is_refused(): ...

# DON'T — names that describe the implementation or say nothing
def test_disconnect(): ...
def test_head_pose_2(): ...
```

### Structure — AAA, one behaviour per test

```python
# DO
def test_high_variance_slows_the_step_response():
    f = _OneEuro1D(min_cutoff=1.6, beta=0.06, d_cutoff=1.0)   # Arrange
    f(0.0, t=0.0)
    out = f(500.0, t=1 / 30, cutoff_scale=0.011)              # Act
    assert out < 200.0                                        # Assert

# DON'T — several behaviours in one test; the first failure hides the rest
def test_smoother():
    assert _alpha(1.6, 1/30) == pytest.approx(0.2510, abs=1e-4)
    f = _OneEuro1D(1.6, 0.06); assert f(123.456, t=0.0) == 123.456
    ...
```

### Mocking policy  🔴

| Mock | Never mock |
|---|---|
| The camera (`cv2.VideoCapture`) — inject a factory | `extract_gaze_features` — it is pure and fast |
| The network (model download) | `FrameGate`, `LivePipeline`, `pose` — pure, and the logic under test |
| The clock — **inject** `t`, do not patch `time.monotonic` | `GazeCalibrator` for its own tests — fit 25 synthetic points, it takes seconds |

The implementation rulebook's rule applies literally: **mocks only for external boundaries, never for internal logic**. A stub tracker (`QObject` with one signal) is the whole harness needed to drive the real `CalibrationWindow` headless under `QT_QPA_PLATFORM=offscreen` — proven during the deep-dive verification.

### Regression tests are written failing-first  🔴

```python
# tests/regression/test_defect_004.py
def test_each_pose_output_tracks_the_axis_its_name_claims():
    """Written against the DEFECT, so it fails on pre-fix code and passes after.

    Regression evidence for GitHub #4 — head-pose labels cyclically permuted.
    """
    rest = rot_x(np.pi)
    for axis, idx, name in (("x", 1, "pitch"), ("y", 0, "yaw"), ("z", 2, "roll")):
        base = euler_from_rotation_matrix(rest)
        moved = euler_from_rotation_matrix(rot(axis, np.deg2rad(15)) @ rest)
        assert moved[idx] - base[idx] == pytest.approx(np.deg2rad(15), abs=1e-3), name
```

Every one of the 7 defects gets one such module. FR-28 requires the test to fail against pre-fix code — so it is **written and observed failing before the fix**, and the failing output is pasted into the story's DoD evidence.

### Invariant tests — FR-29

Lock the behaviours the analysis verified as *correct*, so remediation cannot silently regress them: eye-local roll invariance (bit-identical across 40°), the out-of-distribution variance interlock (σ 18–23 px in-distribution vs ~6000 px extrapolating), the smoother's step response (90% in 1 frame at scale 1.0, 6 frames at 0.011), atomic model download, camera selection preferring face detection over brightness.

### Coverage

| Requirement | Value |
|---|---|
| Minimum overall | **≥85%** across `eye_tracker/` and `main.py` (FR-27) |
| New business logic | 100% |
| Pass rate | 100% — 🔴 no `skip`, no `xfail` to reach the gate (failure criterion 7) |
| Excluded | `if __name__ == "__main__":`, `tests/` itself |
| Enforcement | `pytest --cov=eye_tracker --cov=main --cov-fail-under=85` in CI |

The gate is reachable because the pure modules — `pose`, `gates`, `config`, `metrics`, `diagnostics`, `errors`, `one_euro`, `gaze`, `pipeline` — carry the bulk of the line count and need no hardware. `tracker.py` and `face_mesh.py` become testable only once their collaborators are injected rather than constructed inline; that is a design requirement, not a testing preference.

---

## 16. Documentation Standards  `[New adoption]`

| Standard | Rule |
|---|---|
| Comments explain **why** | 🔴 A comment restating the code is noise. The best existing comments state an observed *symptom* — "Tool-style windows hide when the owning app loses focus on macOS" — and that is the bar |
| Platform branches | 🔴 Must record the symptom that motivated them, not just the platform. Already exemplary in `overlay.py`; now mandatory |
| Non-obvious maths | 🔴 Cite the source. `one_euro.py` cites Casiez et al.; `gaze.py` and `calibration.py` contain comparably non-obvious maths with no citation — new maths must not repeat that |
| Provisional values | ⚠️ Anything not derived from evidence is marked provisional **in code**, with what would settle it. The two pitch ceilings are the current instance |
| No commented-out code | 🔴 |
| No `TODO` / `FIXME` | 🔴 Failure criterion 8 |
| Module docstring | 🔴 Summary line + `Layer:` declaration |
| Analysis documents | When a fix invalidates a deep-dive finding, the document is updated **in the same story** — the list is in the approved architecture |

### DO / DON'T

```python
# DO — states the symptom and why the branch exists
# Tool-style windows hide when the owning app loses focus on macOS, which
# would make the overlay disappear as soon as you click elsewhere.
if not _IS_MAC:
    flags |= Qt.WindowType.Tool

# DON'T — restates the code
# set the window flags
self.setWindowFlags(flags)
```

```python
# DO — a provisional value says so, and says what would settle it
# Provisional. Nodding has never been gated, so no tuned value exists to inherit.
# Settle from the FR-24 rejection counters plus a measured seating distance
# (requirements open item 3), which gives the screen's subtended vertical angle.
pitch_max: float = 0.35

# DON'T — an invented number presented as a tuned one
pitch_max: float = 0.35
```

---

## 17. Known Tech Debt — Shared Code

Findings from the mandatory duplicate/misplaced-shared-code scan. 🔴 **These are debt, not patterns to imitate.** New code must not copy their shape.

| ID | Finding | Evidence | Resolution | Phase |
|---|---|---|---|---|
| **TD-1** | Frame gate duplicated as two independent literal blocks — **12 literals, already diverged on 4 of 6 thresholds** | [main.py:95-100](main.py#L95-L100) vs [overlay.py:182-187](eye_tracker/overlay.py#L182-L187) | One `FrameGate` base + named live deviation (§6) | M2 |
| **TD-2** | Landmark indices re-inlined as raw literals while the named constants defining them are imported and **never used** | `_EYE_A_TOP_RING = [159, 160, 161]` at [gaze.py:21-24](eye_tracker/gaze.py#L21-L24) duplicates `EYE_A_TOP = 159` at [face_mesh.py:17-24](eye_tracker/face_mesh.py#L17-L24) | Reuse the named constants so the two files cannot drift | M3 |
| **TD-3** | Screen geometry resolved twice, captured once, never revalidated | [overlay.py:56](eye_tracker/overlay.py#L56), [overlay.py:98](eye_tracker/overlay.py#L98) | One `screen_geometry()` helper | M4 |
| **TD-4** | `print()` as the sole diagnostic channel — **10 sites, 3 modules** | measured | `logging` (§3), enforced by ruff `T20` | M6 |
| **TD-5** | Dead code: `viable`, `FEATURE_COUNT` unused, `GazeCalibrator.predict`, `set_dot_visible` uncalled, `facial_matrix` unread, 4 unused landmark imports, unused `numpy` import in `tracker.py` | 7 deep-dives, verified by search | Remove or wire up; `FEATURE_COUNT` becomes asserted, `set_dot_visible` gets wired (FR-21) | M6 |
| **TD-6** | Model cache path says `Eyee`/`eyee`; the repository is `EyeTracker` | [face_mesh.py:43-46](eye_tracker/face_mesh.py#L43-L46) | New artifacts use `EyeTracker`; the model cache path is **left alone** — renaming forces a re-download and no requirement asks for it | deferred |

No duplicated widgets, hooks or generic helpers were found beyond the above. The package contains no misplaced shared code.

---

## 18. File / Module Boundary Map  *(mandatory)*

This is the authoritative input `aire-brownfield-plan` uses to populate `files_touched` and `shared_files` in `docs/plans/dependency-graph.yml`. Paths are real, taken from deep-dive evidence and the approved architecture — not assumed.

### Concern → owning files

| Concern | FRs | Owning file(s) | Phase |
|---|---|---|---|
| Eye-pairing investigation | FR-33 | `eye_tracker/tools/eye_pairing.py` 🆕 | M0 |
| Packaging & tooling | FR-26 | `pyproject.toml` 🆕 | M0 |
| Logging infrastructure | FR-25 | `eye_tracker/logging_setup.py` 🆕 | M0 |
| Test scaffold | FR-27 | `tests/conftest.py` 🆕, `tests/arch/**` 🆕 | M0 |
| Accuracy measurement | FR-10, FR-11, FR-12 | `eye_tracker/evaluation/{metrics,protocol,runner,report}.py` 🆕 | M1, M8 |
| Configuration | FR-13 | `eye_tracker/config.py` 🆕 | M2 |
| Frame gating | FR-3, FR-4, FR-14, FR-15 | `eye_tracker/gates.py` 🆕 | M2 |
| Head-pose correctness | FR-1, FR-2 | `eye_tracker/pose.py` 🆕, `eye_tracker/face_mesh.py` | M3 |
| Application lifetime & session machine | FR-7, FR-22 | `eye_tracker/app.py` 🆕, `main.py` | M4 |
| Calibration integrity | FR-5, FR-6 | `eye_tracker/overlay.py` | M4 |
| Smoother reset | FR-22 | `eye_tracker/one_euro.py` | M4 |
| Minimum-sample enforcement | FR-8, FR-9 | `eye_tracker/calibration.py` | M5 |
| Live inference & rejection accounting | FR-24 | `eye_tracker/pipeline.py` 🆕, `eye_tracker/diagnostics.py` 🆕 | M6 |
| Failure feedback & recovery UI | FR-20, FR-21, FR-23 | `eye_tracker/status_window.py` 🆕, `eye_tracker/overlay.py` | M6 |
| Capture robustness | FR-30, FR-31, FR-32 | `eye_tracker/tracker.py` | M6 |
| Calibration persistence | FR-16 – FR-19 | `eye_tracker/profile.py` 🆕 | M7 |
| Regression & invariant tests | FR-28, FR-29 | `tests/regression/**`, `tests/invariants/**` 🆕 | per phase |

### `shared_files` — two or more concerns must touch these  🔴

These are the serialisation points. Two stories touching the same entry **cannot run in parallel** without a merge conflict, and the plan workflow must sequence them.

| File | Why it is shared | Concerns touching it |
|---|---|---|
| `pyproject.toml` | Packaging + ruff + pytest + coverage config all live here | every phase |
| `eye_tracker/config.py` | Every concern adds its settings group | M2, M3, M4, M5, M6, M7 |
| `eye_tracker/errors.py` | Every fault-producing concern adds an exception and a code | M4, M5, M6, M7 |
| `eye_tracker/diagnostics.py` | Every rejection reason is registered here | M2, M3, M6 |
| `eye_tracker/gaze.py` | The 38-D contract: semantics version, `NaN` change, `FEATURE_COUNT` assertion | M3, M7 |
| `eye_tracker/app.py` | The session state machine — every lifecycle and UX concern wires in here | M4, M6, M7 |
| `tests/conftest.py` | Every test concern adds fixtures | every phase |
| `requirements.txt` | Dependency declarations | M0, M7 |
| `docs/status.md` | Every workflow writes here (`merge=union` is already configured) | every phase |

### Unavoidable cross-concern files, and why

| File | Why it cannot be split |
|---|---|
| `eye_tracker/app.py` | It is the composition root. Something must know the whole system exists; concentrating that in one file is better than diffusing it. Mitigated by keeping the per-frame logic in `pipeline.py` and the state table small |
| `eye_tracker/gaze.py` | Sole owner of the 38-D contract. Splitting it would give the contract two owners, which is the failure mode failure criterion 6 guards against |
| `eye_tracker/config.py` | A single resolved `Settings` tree is the point. Per-module config files would recreate TD-1 in a new form |

---

## Quality Checklist

Applies to every story. Reviewers check against this document by section number.

- [ ] All new code follows the chosen patterns; each `[New adoption]` section's Migration Note honoured
- [ ] Module docstring present, with the `Layer:` declaration (§1, §12)
- [ ] Dependency direction respected — `tests/arch/` passes (§8)
- [ ] No `print()` anywhere in `eye_tracker/` or `main.py` (§3)
- [ ] No `except Exception` that only logs and returns; F0–F4 category identified for every failure path (§2)
- [ ] Every `raise` uses `from exc` where a cause exists (§2)
- [ ] No behavioural constant left as a literal at its use site; numerical guards left alone (§6)
- [ ] Frame gating goes through `FrameGate` — no inline thresholds (§6, §9)
- [ ] New/touched functions annotated; public API carries a NumPy docstring (§12)
- [ ] `ruff check` and `ruff format --check` clean — zero warnings (§13)
- [ ] Functions ≤30 lines, or covered by an allowlist entry **with its reason** (§14)
- [ ] Tests written with the code, never after; AAA; behavioural names (§15)
- [ ] Defect fixes have a regression test **observed failing** against pre-fix code, output pasted as evidence (§15)
- [ ] Coverage ≥85%; 100% pass; no `skip` or `xfail` used to reach the gate (§15)
- [ ] GUI-thread affinity asserted in any new signal receiver (§10)
- [ ] No frame, landmark array or blendshape map logged or persisted (§3)
- [ ] Provisional values marked provisional in code, with what would settle them (§16)
- [ ] No `TODO`/`FIXME`; no commented-out code (§16)
- [ ] Tech debt in §17 not imitated; any entry resolved in this story struck through
- [ ] Analysis documents updated in the same story when a fix invalidates a finding (§16)
