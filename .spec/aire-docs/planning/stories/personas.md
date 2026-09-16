# Personas — EVAL-1

## P1 — Aria, hands-free user (accessibility)
Cannot operate a mouse; relies on gaze as her only pointer. She cannot read a terminal — a
`print()` to a discarded stream is invisible to her. When the dot misbehaves she needs the system
itself to say why.
**Cares about**: REQ-F-02 (a nameable reason), REQ-F-03 (diagnostics that survive a windowed app).

## P2 — Devin, maintainer
Fixes defects in the gaze pipeline. Today two threshold blocks have silently diverged and he has no
way to know which gate rejected a frame.
**Cares about**: REQ-F-01 (one definition), REQ-F-02 (attributable rejections).

## P3 — Sam, support engineer
Triages "the dot is sluggish" reports from a log file, without the user's hardware.
**Cares about**: REQ-F-03 (levels + controllable destination), REQ-F-02 (counts by reason).
