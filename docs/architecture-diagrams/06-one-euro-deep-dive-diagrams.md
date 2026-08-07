# Architecture Diagrams — One Euro Smoothing

**Date**: 2026-08-06
**Source**: [docs/architecture/current/06-one-euro-deep-dive.md](../architecture/current/06-one-euro-deep-dive.md)
**Analyzed By**: ARCHITECT

> Human-readable preview. Contains only the Mermaid diagrams extracted from the deep-dive, for review by BA / product stakeholders without reading the full analysis.

---

## 1. One Filtered Sample

The last stage in the pipeline — this is what determines how the dot's motion actually *feels*. Heavy smoothing when the gaze is still, near-zero latency when it moves.

**Measured**: a 500 px jump reaches 90% of its target in a single frame (0.03 s) under normal conditions, and still within 6 frames (0.20 s) when the predictor is highly uncertain. Note that the caller never passes `t`, so the filter reads the clock itself — a second clock read for a frame the caller has already timestamped.

```mermaid
sequenceDiagram
  participant AC as AppController._on_feat
  participant O2 as OneEuro2D.filter
  participant FX as _OneEuro1D for x
  participant AL as _alpha

  AC->>O2: filter(pred_x, pred_y, variance=fused_var, motion=motion_score)
  Note over O2: t is not supplied — filter calls time.monotonic() itself
  O2->>O2: var = mean of the 2 clamped variance components
  O2->>O2: scale = 1 / (1 + sqrt(var) / 50.0)
  opt motion > 0
    O2->>O2: scale *= min(2.5, 1 + motion / 25)
  end
  O2->>FX: __call__(x, t, cutoff_scale=scale)
  FX->>FX: dt = max(t - last_t, 1e-3)
  FX->>FX: dx_raw = (x - last_filtered_x) / dt
  FX->>AL: _alpha(d_cutoff=1.0, dt)
  AL-->>FX: a_d
  FX->>FX: dx_hat = a_d*dx_raw + (1-a_d)*last_dx_hat
  FX->>FX: cutoff = (min_cutoff + beta*abs(dx_hat)) * cutoff_scale
  FX->>AL: _alpha(max(cutoff, 1e-3), dt)
  AL-->>FX: a
  FX->>FX: x_hat = a*x + (1-a)*last_filtered_x
  FX-->>O2: x_hat
  O2-->>AC: (fx, fy)
```

---

## 2. Three Signals, One Cutoff

Three independent inputs modulate how hard the dot is smoothed. Two of them — the filter's own velocity estimate and the externally supplied motion score — measure essentially the same thing in different units, so **motion adaptivity is applied twice**. Nothing in the code acknowledges the overlap.

The per-axis variance from the predictor is averaged into a single scalar before use, so a confident vertical axis is smoothed as hard as an uncertain horizontal one.

```mermaid
flowchart TB
  A["predictor fused_var<br/>px squared, per axis"] --> B["mean over both axes<br/>then sqrt"]
  B --> C["variance term<br/>1 / (1 + sigma/50)<br/>range 0 to 1"]
  D["motion score from main<br/>feature-units per second"] --> E["motion term<br/>min(2.5, 1 + motion/25)<br/>range 1 to 2.5"]
  C --> F["cutoff_scale = variance term x motion term"]
  E --> F
  G["filter's own velocity<br/>dx_hat, px per second"] --> H["beta x abs(dx_hat)<br/>beta = 0.06"]
  I["min_cutoff = 1.6 Hz"] --> J["base + beta term"]
  H --> J
  J --> K["cutoff = (min_cutoff + beta*abs(dx_hat)) x cutoff_scale"]
  F --> K
  K --> L["alpha = dt / (dt + 1/(2 pi cutoff))"]
  L --> M["x_hat = alpha*x + (1-alpha)*x_prev"]
```
