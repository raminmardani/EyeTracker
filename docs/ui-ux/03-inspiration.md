# Checkpoint — Steps 01–03 (Discovery & Direction)

**Date**: 2026-08-07 · **Author**: UI_UX_DESIGNER · **Resume point for**: Steps 04–08

---

## Direction

| Dimension | Value | Source |
|---|---|---|
| Emotional target | Calm, unambiguous, never alarming | Derived — accessibility audience |
| Colour mapping | Grey-blue neutrals + cyan accent | Workflow *Efficient* / *Professional* rows |
| Base hues | **Kept from existing code** — only measured failures change | `#121216` / `#00D2FF` already in source |
| Density | Low — spacious, large type | Derived — audience |
| Platform | Desktop, single primary display | Multi-monitor OUT of scope |
| Toolkit | PyQt6 `QWidget` + `QPainter` | No web design system applies |
| Accessibility | **AAA** for owned windows · **AA non-text** floor for the overlay | User decision, Step 02 Q1 |
| Dot visibility | Dual outline, dark outer + light inner | User decision, Step 02 Q2 |
| Failure presentation | Persistent banner in `StatusWindow` | User decision, Step 02 Q3 |
| Styling | Central tokens module; QSS + `QPainter` both read it | User decision, Step 02 Q4 |
| Icons | Text-first. No emoji. Qt standard icons only where universally understood | Derived — patterns doc bans emoji; text serves screen readers |

## Inspiration

**None supplied and none sought.** `SPEC/references/` is empty; no app or site was named as a reference. Direction is derived from the audience and from measurement of the existing palette, not from an external product.

The one external convention deliberately borrowed is the **dual-polarity outline used by OS cursors and overlay reticles** — chosen because it is the only technique that survives an uncontrolled background, verified by measurement rather than adopted on reputation.

## Surfaces in scope

| Surface | Role | Can accept input? |
|---|---|---|
| `GazeOverlay` | Output only — the gaze dot | **Never** — `WindowTransparentForInput` |
| `CalibrationWindow` | Full-screen target sequence | Keyboard only |
| `StatusWindow` **NEW** | State, messages, recovery actions, counters | **Yes — the only one** |

## Carried constraint

🔴 Recovery actions must be **keyboard-reachable**. The audience is defined as users who cannot operate a mouse, and FR-20/FR-23 require an offered recovery action. A user who can operate neither mouse nor keyboard cannot self-recover in this cycle — a consequence of the signal-only scope, recorded not solved.
