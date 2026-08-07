# Checkpoint — Steps 04–08 (Design System & Visual Foundation)

**Date**: 2026-08-07 · **Author**: UI_UX_DESIGNER · **Resume point for**: Steps 09–12
**Gate 05**: approved 2026-08-07

---

## Design tokens (locked at gate 05)

```
colors:
  surface          #121216   kept
  surface_raised   #1E1E24   new
  border           #6E6E7A   new   3.30:1 on raised   (>=3 UI boundary)
  text_primary     #E4E4E8   new  13.08:1
  text_secondary   #B4B4B4   kept  8.00:1
  accent           #00D2FF   kept  9.21:1
  warn             #FFAA28   kept  8.71:1
  error            #FF8A8A   new   7.31:1   (#FF5C5C rejected at 5.48:1)
  success          #6BE39A   new  10.33:1   (#4CAF50 rejected at 5.97:1)
  focus_ring       #FFFFFF   new  16.58:1 vs surface / 5.03:1 vs border
  dot_fill         #FF2828 alpha 210   kept
  dot_ring_outer   #000000   new
  dot_ring_inner   #FFFFFF   new   best edge >=5.32:1 on any background
spacing: base 4; scale 4 8 12 16 24 32 48
type:   family OS-default fallback stack; sizes pt 11 13 16 20 28; weights 400 600
elevation: e0 flat | e1 raised+1px border | e2 raised+border+3px accent left edge
targets: min 44px, spacing >=8px
icons:  none required; text labels; Qt standard icons optional, never emoji
```

---

## Component hierarchy

| Tier | Component | Qt realisation |
|---|---|---|
| **Atom** | `Text` | `QLabel` styled from tokens; role = caption / body / subtitle / title / display |
| **Atom** | `Action` | `QPushButton`, min 44 px, white 2 px focus ring at 2 px offset |
| **Atom** | `StateIndicator` | 12 px dot **plus a text label** — never colour alone |
| **Atom** | `ProgressBar` | `QProgressBar`, determinate or indeterminate |
| **Molecule** | `Banner` | severity tone (e1/e2) + message + remediation + inline `Action` |
| **Molecule** | `StateLine` | `StateIndicator` + state name + detail text |
| **Molecule** | `CounterTable` | two-column reason → count, `body` size, `text_secondary` |
| **Organism** | `StatusWindow` | `StateLine` + `Banner` + `CounterTable` + action row |
| **Organism** | `CalibrationScreen` | instruction (`display`) + target + `ProgressBar` + hint |
| **Organism** | `GazeDot` | dual-outline dot, output only |

---

## Layout

The workflow's 12/8/4-column grid is **N/A** — no multi-column layout exists. Layout is a single vertical stack per window.

### `StatusWindow`

| Property | Value |
|---|---|
| Width | 420 pt fixed; height content-driven |
| Anchor | Bottom-right of primary screen, 24 pt margin |
| Default state in Live | **Collapsed pill** — `StateLine` only, ~44 pt tall |
| Expands when | A fault occurs, or the window takes focus, or the user presses `F1` |
| Collapses when | Fault is cleared and focus is lost |
| Hidden during | Calibration — the full-screen calibration window owns the display |

⚠️ **Trade-off recorded**: any always-visible window permanently occupies screen area that the user might want to look at, which for a gaze-input tool is real cost. The collapsed pill keeps that cost to ~420 × 44 pt in one corner, and expansion is instantaneous so the 3-second message rule still holds.

### `CalibrationScreen`

| Region | Content | Token |
|---|---|---|
| Top, 24 pt inset, centred | Instruction | `display` 28 pt, `text_primary` |
| Centre | Target — outer ring r 26, inner dot r 10 | ring stroke `text_secondary`, inner `accent` when collecting / `warn` when idle |
| Bottom, 24 pt inset | `ProgressBar` determinate `n/total` + text label | `accent` on `surface_raised` |
| Bottom, below bar | Hint — "Esc to abort" | `caption` 11 pt, `text_secondary` |

Progress today is the text `"(n/25)"` only. A determinate bar is added because the ritual runs 79–141 s.

### `GazeDot`

Radius 14 fill, 2 pt light inner ring, 2 pt dark outer ring → 18 pt overall. Hidden, not frozen, when the signal is lost or stale.

---

## Resolution & DPI strategy

Replaces the workflow's responsive-breakpoint model, which does not apply to a single-display desktop app.

| Concern | Strategy |
|---|---|
| DPI variation | All sizes in **points**, so Qt scales them with the OS DPI setting. No pixel constants |
| Resolution variation | Calibration targets stay **fractions of screen geometry** (already the case). `StatusWindow` stays a fixed logical width |
| 🔴 Geometry change mid-session | Both windows currently capture `primaryScreen().geometry()` once and never revalidate. Connect to `primaryScreenChanged` / `geometryChanged`; on change **while Live**, show a fault banner and offer Recalibrate — because screen geometry is part of the calibration profile key, so a resolution change invalidates the **active** calibration exactly as it invalidates a stored one |
| Multi-monitor | OUT of scope. Predictions stay clipped to the primary display |

---

## Focus & keyboard model

The product's audience cannot rely on a mouse, so this section is load-bearing rather than a checklist item.

| Surface | Focus policy |
|---|---|
| `GazeOverlay` | **Never focusable** — `WindowTransparentForInput` |
| `CalibrationWindow` | Keyboard only. `Esc` aborts; 🔴 now calls `super().keyPressEvent` so other keys propagate instead of being swallowed |
| `StatusWindow` | `Qt::StrongFocus`; the only interactive surface |

**Tab order**: banner action (when present) → Recalibrate → Retry (when present) → Quit.

**Shortcuts** (require `StatusWindow` focus): `R` recalibrate · `T` retry · `Q` quit · `F1` shortcut list · `Esc` collapse the expanded banner (**not** quit).

🔴 **Focus-stealing rule**: `StatusWindow` calls `raise_()` + `activateWindow()` **only** on a transition into `Faulted` (F2/F3/F4) — never during normal running. This is what makes the shortcuts reachable at the one moment they are needed, without stealing focus while the user works.

⚠️ **Recorded limitation**: Qt shortcuts are application-scoped, so they do not fire while `StatusWindow` lacks focus. A genuinely global hotkey needs platform-specific hooking, which is out of scope. The focus-on-fault rule is the in-scope mitigation, not a full solution.

---

## Accessibility foundation

| Requirement | Implementation |
|---|---|
| Contrast | AAA (7:1 text / 4.5:1 large) in owned windows; AA non-text (3:1) floor for the overlay |
| Focus visibility | White 2 pt ring at 2 pt offset — 5.03:1 against the border, 16.58:1 against the surface |
| Never colour alone | Every state carries a text label beside its indicator; every severity carries a word, not just a tone |
| Screen reader | `accessibleName` + `accessibleDescription` on all controls; state and banner changes raise a `QAccessibleEvent` — Qt's equivalent of a live region |
| Motion | No animation. Nothing blinks, pulses or auto-dismisses |
| Target size | 44 pt minimum, 8 pt spacing |
