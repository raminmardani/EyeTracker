# UI/UX Discovery — EyeTracker

**Date**: 2026-08-07
**Author**: UI_UX_DESIGNER
**Status**: Step 01–03 complete
**Sources**: [requirements.md](docs/requirements.md) · [00-system-overview.md](docs/architecture/current/00-system-overview.md) · 7 × `01-*-deep-dive.md` · [02-target-architecture-brownfield.md](docs/architecture/design/02-target-architecture-brownfield.md) · [03-patterns-and-standards-brownfield.md](docs/architecture/design/03-patterns-and-standards-brownfield.md)

> **Reference check**: `SPEC/references/` contains **0 files** — no brand guidelines, no design files, no images. Nothing to align to, and the `[S]`kip gate did not trigger.

---

## 1. Platform & tech constraints

| Constraint | Value | Consequence for design |
|---|---|---|
| Platform | Desktop — Windows / macOS / Linux | No mobile, no tablet, no touch |
| Display | **Single primary display.** Multi-monitor explicitly OUT of scope | No responsive breakpoints. Windows size to `primaryScreen().geometry()` |
| UI toolkit | PyQt6 6.11.0, `QWidget` + `QPainter` | No web design system, no CSS framework, no component library |
| Styling mechanisms available | Qt Style Sheets (QSS), `QPalette`, direct `QPainter` | Currently **direct `QPainter` with hardcoded `QColor` literals** |
| Fonts | Whatever the OS provides — **no `setFont` call exists anywhere** | Cannot ship a web font; must name a fallback stack of system fonts |
| Icons | No web icon set is reachable | Qt standard icons or text-only labels |
| Network in UI path | None | No CDN fonts, no remote assets |
| Auth | **None** — single OS user, no login, no sessions | No auth screens, no permissions UI |
| Test harness | `QT_QPA_PLATFORM=offscreen` proven working | UI states are automatable without a person |

---

## 2. Surface inventory — what there is to design

| Surface | Status | Interaction model | Evidence |
|---|---|---|---|
| `GazeOverlay` | existing, modified | 🔴 **`WindowTransparentForInput` — can never receive mouse or keyboard input.** Output-only | [overlay.py:41-55](eye_tracker/overlay.py#L41-L55) |
| `CalibrationWindow` | existing, modified | Keyboard only. `Esc` handled; **every other key is swallowed** because `super().keyPressEvent` is never called | [overlay.py:235-239](eye_tracker/overlay.py#L235-L239) |
| `StatusWindow` | **NEW** | The **only** surface that can accept input | DR-12 |

**There is no navigation structure.** Three windows, no nav, no routing, no menus. The workflow's navigation question does not apply.

---

## 3. Current visual state — measured from source

| Property | Value | Site |
|---|---|---|
| Calibration background | `RGB(18,18,22)` | [overlay.py:243](eye_tracker/overlay.py#L243) |
| Calibration body text | `RGB(180,180,180)` | [overlay.py:244](eye_tracker/overlay.py#L244) |
| Target outer ring | fill `RGB(50,50,60)`, stroke `RGB(220,220,220)` 2 px, r = 26 | [overlay.py:260-262](eye_tracker/overlay.py#L260-L262) |
| Target inner dot | collecting `RGB(0,210,255)`, idle `RGB(255,170,40)`, stroke white 1 px, r = 10 | [overlay.py:264-267](eye_tracker/overlay.py#L264-L267) |
| Gaze dot | fill `RGBA(255,40,40,210)`, outline `RGBA(255,255,255,230)` 2 px, r = 14 | [overlay.py:76-78](eye_tracker/overlay.py#L76-L78) |
| Typography | OS default family **and** default size — no explicit typography anywhere | no `setFont` call exists |
| Progress indication | text `"(n/25)"` only. No bar, no time estimate | [overlay.py:246](eye_tracker/overlay.py#L246) |
| Empty/waiting state | `"Center your face in the camera to start calibration"` — **no timeout, shown indefinitely** | [overlay.py:250](eye_tracker/overlay.py#L250) |

### Contrast audit (WCAG 2.1 relative-luminance formula, computed not estimated)

| Foreground | Background | Ratio | Verdict |
|---|---|---|---|
| Calibration body text `RGB(180,180,180)` | `RGB(18,18,22)` | **9.01:1** | AA pass / **AAA pass** (normal text) |
| Target ring stroke `RGB(220,220,220)` | `RGB(18,18,22)` | **13.63:1** | AA pass / AAA pass |
| Target ring **fill** `RGB(50,50,60)` | `RGB(18,18,22)` | **1.47:1** | fail — the ring is carried entirely by its stroke |
| Inner dot collecting `RGB(0,210,255)` | ring fill `RGB(50,50,60)` | **7.04:1** | pass |
| Inner dot idle `RGB(255,170,40)` | ring fill `RGB(50,50,60)` | **6.66:1** | pass |
| Gaze dot red `RGB(255,40,40)` | white desktop | **3.76:1** | AA pass (non-text) / AAA fail |
| Gaze dot red `RGB(255,40,40)` | black desktop | **5.59:1** | pass |
| Gaze dot outline white | **white desktop** | **1.00:1** | 🔴 **invisible** |
| Gaze dot outline white | mid-grey desktop | **3.95:1** | AA pass / AAA fail |

**Findings**

1. ✅ The calibration screen's text contrast **already passes AAA**. No change needed — a rare case where the existing choice is better than the standard requires.
2. 🔴 **The gaze dot has no colour pair that works on arbitrary desktop content.** Its white outline vanishes on a light background (1.00:1); the red fill alone then carries it at 3.76:1. A single outline colour cannot solve this — the overlay floats above content it does not control.
3. ⚠️ Two of the three state colours are distinguished **by hue alone** (cyan "collecting" vs amber "idle"). For deuteranopia/protanopia these remain distinguishable, but relying on hue alone for a state signal is fragile. A redundant non-colour cue is needed.

---

## 4. Key user flows extracted from requirements

| # | Flow | Duration | Current feedback | Required |
|---|---|---|---|---|
| 1 | First launch, no profile | camera probe **seconds, unmeasured** → calibration **79–141 s** → fit **multi-second freeze** | **None for probe or fit** | Progress + non-blocking feedback |
| 2 | Launch with a stored profile | near-instant | n/a — feature is new | Confirm restore, enter live directly (FR-16) |
| 3 | Stored profile refused | instant | n/a | Named reason + calibrate action (FR-18, FR-19) |
| 4 | Face lost during live | — | 🔴 dot **freezes**, indistinguishable from steady gaze | Hide within 500 ms, restore within 500 ms (FR-21) |
| 5 | Camera lost mid-session | — | 🔴 silent spin at ~100 Hz forever | Message + retry within 3 s (FR-23) |
| 6 | Recalibrate without restart | — | 🔴 impossible — one-way door | Trigger from live (FR-22) |
| 7 | Too few usable targets | — | 🔴 proceeds silently to an unusable model | Visible refusal, never silent (FR-8) |
| 8 | Evaluation run | minutes | n/a | Operator-facing, not end-user (FR-10) |

**Every one of flows 4–7 is currently a silent failure.** Failure criterion 1 forbids all of them. This is why the UX work exists.

---

## 5. Audience — and the contradiction it creates

Requirements define the audience as **"users who cannot operate a mouse"** (hands-free input / accessibility).

🔴 **Recovery actions therefore cannot depend on a mouse.** FR-20 and FR-23 require an *offered recovery action*; FR-22 requires a recalibration trigger. Buttons alone would be unreachable for the target user. Dwell-click is explicitly OUT of scope this cycle.

**Design consequence**: every action must be reachable by keyboard, with the button as a secondary affordance for a carer, operator or evaluator. **Recorded limitation**: a user who can operate neither mouse nor keyboard cannot self-recover in this cycle. That follows from the deliberate signal-only scope and cannot be solved by UI design; it should be revisited when dwell-click is scoped.

---

## 6. Derived design decisions — with their evidence

Stated rather than asked, because each follows from an approved document. Each is open to correction.

| Decision | Value | Derived from |
|---|---|---|
| Emotional target | **Calm, unambiguous, never alarming** | Accessibility audience; an assistive tool that startles or blames the user is a defect |
| Data density | **Low — spacious, large type** | Same audience; the workflow's High/Medium/Low maps to Low here |
| Responsive target | **Desktop-only, single display** | Multi-monitor explicitly OUT |
| Navigation style | **N/A** | Three windows, no navigation structure exists |
| Icons | **Text-first. No emoji** (patterns doc bans them). Qt standard icons only where universally understood | No web icon set is reachable; text labels also serve screen readers better |
| Loading states | **Determinate** where the total is known (calibration `n/25`), **indeterminate + elapsed** where it is not (camera probe, GP fit) | Probe and fit durations are unmeasured and unbounded |
| Success feedback | **Inline state text in `StatusWindow`**, no toasts | Toast stacks are a web idiom; a persistent single-line state is clearer and needs no dismissal |
| Validation | **N/A** — no forms, no user-entered data | No text input exists anywhere in the application |
| Tables / modals / charts / bulk actions / search | **N/A** | None exist and none is in scope |

---

## 7. User decisions — Step 02

Asked rather than assumed. All four answered 2026-08-07.

| # | Question | Decision |
|---|---|---|
| 1 | Accessibility level | **AAA for windows we own; AA non-text floor for the overlay.** Split is deliberate: AAA is not physically achievable for a dot floating over uncontrolled desktop content |
| 2 | Gaze-dot visibility | **Dual outline** — dark outer ring + light inner ring, so one edge always contrasts |
| 3 | Failure-message presentation | **Persistent banner in `StatusWindow`** — never dismissed, never steals focus during normal running, and reachable without a mouse |
| 4 | Styling mechanism | **Central tokens module**; QSS for `StatusWindow`, `QPainter` reads the same tokens |

### Why the dual outline works — verified, not asserted

Worst-case best-edge contrast across every background type, including the pathological case of the dot over identical red:

| Desktop background | Dark ring | Light ring | Best edge | Verdict |
|---|---|---|---|---|
| White | 21.00:1 | 1.00:1 | **21.00:1** | pass |
| Mid grey | 5.32:1 | 3.95:1 | **5.32:1** | pass |
| Black | 1.00:1 | 21.00:1 | **21.00:1** | pass |
| The same red as the fill | 5.59:1 | 3.76:1 | **5.59:1** | pass |

A single outline colour has a failing case in every scheme. Two rings of opposite polarity have none — the minimum best-edge contrast is 5.32:1, comfortably above the 3:1 non-text floor.

### Emotion → colour mapping

Derived emotional target is **calm, unambiguous, never alarming**, which maps onto the workflow's *Efficient* and *Professional/Trustworthy* rows: **grey-blue neutrals with a cyan accent**.

The existing palette already embodies this — `#121216` surfaces with a `#00D2FF` accent — so the base hues are **kept**, not replaced. Only values that fail measurement are changed.
