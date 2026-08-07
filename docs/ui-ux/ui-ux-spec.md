```yaml
version: 1.0
platform: desktop
tech_stack: [pyqt6, qpainter, qss]
styling: shared_tokens_module

design_tokens:
  colors: {bg: "#121216", bg2: "#1E1E24", bd: "#6E6E7A", fg: "#E4E4E8",
    fg2: "#B4B4B4", accent: "#00D2FF", warn: "#FFAA28", error: "#FF8A8A",
    ok: "#6BE39A", dot: "#FF2828@210", focus: white, dot_rings: [black, white]}
  spacing: {base: 4, scale: [4,8,12,16,24,32,48]}
  type: {family: os_default, unit: pt, scale: [11,13,16,20,28], weights: [400,600]}
  targets: {min: 44, gap: 8}
  icons: none; motion: none

responsive_behavior:
  scaling: {sizes: pt, targets: screen_fraction}
  geom_change_live: fault+recal
  windows:
    GazeOverlay: {input: none, dot_r: 18, dual_ring: 1}
    CalibrationWindow: {fullscreen: 1, input: keyboard}
    StatusWindow: {w: 420, anchor: bottom_right, margin: 24, default: pill_44,
      expand_on: [fault, focus, F1], hide_during: calibration}

ux_logic:
  error_display: persistent_banner
  severity: {F0F1: no_message, F2: problem+retry, F3: cannot_start+retry|quit,
    F4: refused+reason+calibrate}
  success: inline_stateline_5s
  loading: {calibration: determinate, probe: indeterminate+elapsed,
    gp_fit: static_text_flushed_pre_block}
  waiting: first_face_timeout->F3
  density: low
  counters: nonzero_desc_max8
  wording: event_then_action; never_blame_user

component_map:
  atoms: [Text, Action44, StateDot+label, ProgressBar]
  molecules: [Banner, StateLine, CounterTable]
  organisms: [StatusWindow, CalibrationScreen, GazeDot]

user_journey:
  primary: launch -> valid_profile ? live : calibrate25 -> fit -> live
  critical: [refused->calibrate, face_lost->hide<=500ms,
    cam_lost->banner+retry<=3s, targets<min->refuse]

a11y:
  level: {windows: AAA, overlay: AA_non_text}
  focus_ring: white_2pt_offset2
  keys: {tab: [banner, recal, retry, quit], R: recal, T: retry, Q: quit,
    F1: help, Esc: collapse|abort}
  focus_steal: fault_only
  labels: required_all_controls
  announce: QAccessibleEvent
  never_color_alone
  limits: [app_scoped_shortcuts, no_kbd_no_mouse->no_self_recovery]
```
