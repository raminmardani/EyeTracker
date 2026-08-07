# Architecture Diagrams — UI Windows & Calibration State Machine

**Date**: 2026-08-06
**Source**: [docs/architecture/current/05-overlay-deep-dive.md](../architecture/current/05-overlay-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. The Calibration State Machine

The transition marked **Banking → Dwelling** is where a reproduced defect lives. It is scheduled by a static timer that the teardown path cannot cancel, so pressing Esc during that 250 ms window leaves the closed window still running — and it eventually reports completion a **second** time.

In the shipped configuration that second report arrives roughly 107 seconds after the user thought they had cancelled, triggering a second multi-second freeze and a duplicated overlay.

```mermaid
stateDiagram-v2
  [*] --> WaitingForFace : __init__ connects features_ready, shows window
  WaitingForFace --> WaitingForFace : feat is None or non-finite — ignored
  WaitingForFace --> Dwelling : first finite feat sets _started, singleShot 250ms
  Dwelling --> Collecting : _dwell_timer fires after 900ms
  Collecting --> Collecting : gated feat appended to _buf, all finite to _fallback_buf
  Collecting --> Banking : _buf reaches samples_per_point
  Collecting --> Banking : _collect_timer fires after 4500ms
  Banking --> Dwelling : idx++, singleShot 250ms, more targets remain
  Banking --> Emitting : idx reaches len(points)
  Emitting --> [*] : _disconnect, finished.emit(X, Y), close()
  Dwelling --> Aborting : Esc
  Collecting --> Aborting : Esc
  WaitingForFace --> Aborting : Esc
  Aborting --> [*] : _disconnect, finished.emit(partial X, Y), close()
```

---

## 2. Per-Target Cycle and Sample Selection

Two buffers are filled in parallel: a strict one that applies six quality gates, and a permissive one that accepts every finite frame. If the gates prove too tight for a given camera or user, calibration **degrades in quality instead of hanging** — a deliberate and well-commented anti-deadlock measure.

The gap is the last fallback branch, which accepts any non-empty buffer. A target can therefore be represented by a single raw frame, and nothing in the emitted data records which targets were degraded.

```mermaid
sequenceDiagram
  participant TR as GazeTracker
  participant CW as CalibrationWindow
  participant RF as _representative_feature

  CW->>CW: _advance — repaint target idx, start dwell timer 900ms
  Note over CW: dwell gives the user time to saccade to the new dot
  CW->>CW: _begin_collect — clear both buffers, collecting=True, start 4500ms timeout
  loop every frame while collecting
    TR-->>CW: features_ready(feat)
    CW->>CW: drop if None or non-finite
    CW->>CW: _fallback_buf.append(feat) — unconditional
    CW->>CW: apply 6 accept gates
    alt frame passes all gates
      CW->>CW: _buf.append(feat)
      opt _buf reached samples_per_point
        CW->>CW: _finish_collect early
      end
    end
  end
  CW->>CW: _finish_collect — collecting=False, stop timeout
  alt len(_buf) >= min_samples_per_point
    CW->>RF: _representative_feature(_buf) — strict
  else len(_fallback_buf) >= min_samples_per_point
    CW->>RF: _representative_feature(_fallback_buf) — print "relaxed fallback"
  else _fallback_buf non-empty
    CW->>RF: _representative_feature(_fallback_buf) — print "low sample count"
  else
    CW->>CW: print "no usable samples, skipping" — target contributes nothing
  end
  RF-->>CW: one 38-vector
  CW->>CW: X.append(vector), Y.append(target pixel), idx++
  CW->>CW: singleShot 250ms to _advance
```

---

## 3. Representative Sample Selection

Outlier-resistant selection: normalise each of the 38 dimensions by its median absolute deviation, rank samples by distance from the centre, discard the worst 30%, then take the median of what remains. Resilient to blinks and saccades mid-collection.

One caveat: the `max(8, ...)` floor means that for buffers of 8 or fewer samples, **no trimming happens at all** — precisely the degraded targets that most need it.

```mermaid
flowchart TB
  A["samples: n x 38"] --> B{"n <= 4 ?"}
  B -->|yes| C["return per-dimension median"]
  B -->|no| D["center = per-dimension median"]
  D --> E["mad = median of abs deviation, per dimension"]
  E --> F["scale = mad where mad > 1e-6, else 1.0"]
  F --> G["dist_i = RMS over 38 dims of (x_i - center)/scale"]
  G --> H["keep = min(n, max(8, round(0.7n)))"]
  H --> I["chosen = the keep samples with smallest dist"]
  I --> J["return per-dimension median of chosen"]
```
