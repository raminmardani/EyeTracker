# Project Status

**Last Updated**: 2026-08-07 19:03
**Updated By**: AIRE_PRODUCT_OWNER
**Overall Status**: 🟢 ON TRACK

---

## Project Overview

**Project**: EyeTracker
**Type**: Brownfield
**Start Date**: 2026-08-06
**Target Completion**: TBD
**Active Cycle**: CYCLE-1

---

## Progress Summary

| Step | Status | Owner | Updated | Evidence | Recorded |
|------|--------|-------|---------|----------|----------|
| System Discovery | ✅ Done | AIRE_ARCHITECT | 2026-08-06 | `docs/architecture/current/00-system-overview.md` | 2026-08-06 15:58 |
| Deep-Dive | ✅ Done | AIRE_ARCHITECT | 2026-08-06 | `docs/architecture/current/01-*-deep-dive.md` (7 modules) | 2026-08-06 19:29 |
| Requirements | ✅ Done | AIRE_ANALYST_PM | 2026-08-06 | `docs/requirements.md` | 2026-08-06 20:44 |
| Target Architecture | ✅ Done | AIRE_ARCHITECT | 2026-08-07 | `docs/architecture/design/02-target-architecture-brownfield.md` | 2026-08-07 11:14 |
| Patterns | ✅ Done | AIRE_ARCHITECT | 2026-08-07 | `docs/architecture/design/03-patterns-and-standards-brownfield.md` | 2026-08-07 12:18 |
| Build Cycles | ✅ Done | AIRE_BUILD_CYCLE_PLANNER | 2026-08-07 | `docs/plans/builds/` (5 cycles) + `docs/plans/build-cycles.md` | 2026-08-07 14:58 |
| UI/UX Design | ✅ Done | AIRE_UI_UX_DESIGNER | 2026-08-07 | `docs/ui-ux/ui-ux-spec.md` | 2026-08-07 13:43 |
| Implementation Plan | ✅ Done | AIRE_PRODUCT_OWNER | 2026-08-07 | `docs/plans/implementation-plan.md` + `docs/plans/dependency-graph.yml` + `docs/plans/stories/` — **11 of 11 story files authored**, all 7 waves, every one gate-passed | 2026-08-07 19:03 |
| Review | ⏸️ Not Started | AIRE_REVIEWER | — | — | 2026-08-06 14:57 |
| QA | ⏸️ Not Started | AIRE_QA | — | — | 2026-08-06 14:57 |

---

## Current Step Details

### Implementation Plan — BUILDID: CYCLE-1

**Owner**: AIRE_PRODUCT_OWNER
**Status**: ✅ Done — 11 stories planned, **11 authored**, all 7 waves
**Started**: 2026-08-07
**Completed**: 2026-08-07
**Scope decision**: **CYCLE-1 only** (user choice). Numbering `Epic 1 / Story 1.1`. `team_size: 1` — solo, so the graph's waves describe **dependency order, not concurrency**

**Progress**:
- [x] Prerequisites — requirements, `architecture/current/` (8 files), `architecture/design/` (2 files), `docs/ui-ux/ui-ux-spec.md` and `docs/plans/builds/cycle-1/cycle-plan.md` all verified present ✅
- [x] Reference check — `SPEC/references/` contains **0 files**; stories derive from the approved cycle plan and patterns document ✅
- [x] Phase 1 — Cycle scope, epic decomposition and story boundaries derived from CYCLE-1's scope (M0 + M1) ✅
- [x] Phase 2 — `docs/plans/dependency-graph.yml`: 11 stories, 7 waves, 12 requires-edges, 5 `shared_files`; **user approved graph + shared_files + distribution** ✅
- [x] Phase 3 — `docs/plans/implementation-plan.md`: graph mirror, wave summary, 10 success criteria, 2 epics, 11-story index, quality gates, 7-row risk table, 4 QA Manual Testing Groups ✅
- [x] Phase 4 — **all 11 story files** authored one at a time, each passing a **blocking depth gate** before being presented ✅
- [x] Phase 4 — Stories 2.1 – 2.4 additionally had their code blocks **assembled and executed** — 25, 33 and 20 test cases plus a full end-to-end report render — with every manual break-case run to confirm the suites are calibrated ✅
- [x] Phase 4 — All 11 mermaid Flow Diagrams **rendered to SVG** (mermaid-cli 11, `aria-roledescription="flowchart-v2"`, 0 syntax errors) ✅
- [x] Phase 4 — Graph re-verified after authoring: requires/enables mirrored both ways, every `requires` target in an earlier wave, wave membership matches every story's `wave` field, and `shared_files` discipline holds (`tests/conftest.py` in waves 2/3/5 — never the same wave) ✅
- [x] Phase 4 — GitHub push pass 1: **4 issues created** (#10–#13) for waves 1–2, numbers written back into story files and the graph ✅
- [ ] Phase 4 — Stories **1.4, 1.6 and 2.1 – 2.5 not pushed** to GitHub; `epic:2` / `wave:3`–`wave:7` labels and the Epic 2 milestone not created ⏸️
- [x] Phase 5 — `docs/status.md` updated ✅
- [x] Phase 5 — `docs/status.md` updated ✅

**Epics and story counts**:

| Epic | Title | Stories planned | Story files written | On GitHub |
|---|---|---|---|---|
| 1 | Test & Packaging Foundation | 6 (1.1 – 1.6) | **6 / 6** ✅ | 4 (#10 – #13); 1.4 and 1.6 pending |
| 2 | Accuracy Measurement & Baseline | 5 (2.1 – 2.5) | **5 / 5** ✅ | 0; all 5 pending |
| | **Total** | **11** | **11** ✅ | **4** |

**Wave order** (solo — read as sequence, not parallelism): 1: `1.2` · 2: `1.1`, `1.3`, `1.5` · 3: `1.4`, `1.6`, `2.1` · 4: `2.2` · 5: `2.3` · 6: `2.4` · 7: `2.5`

**Evidence-driven deviations from the workflow's defaults** (each recorded in the plan with its reason):
- 🔴 **FR-33 is Story 1.1 but runs in wave 2, not wave 1.** The requirements name it the designated first story; its unit test cannot execute until Story 1.2 supplies pytest, the packaging metadata and a rebuilt `.venv`. It keeps the number and loses the slot — the alternative was an untestable first story
- **`docs/status.md` is declared in `shared_files` but deliberately absent from every story's `files_touched`** — it is `merge=union` in `.gitattributes` and written by `aire-dev-implement`, not by story work. A seed-wave story for it would have been ceremony
- **`tests/conftest.py` is created in wave 2 (Story 1.3), not by a wave-1 seed story** — safe because it is touched again only in waves 3 and 5, and solo execution removes the write race the seed-wave rule exists to prevent
- **No `dev-<slot>` tags and no per-slot distribution** — `team_size: 1`
- **RBAC section is a sentinel on every story** — `No role-differentiated access — single actor.` Verified across all 8 source files: no auth, no user model, no sessions
- **6 stories, not the format's suggested horizontal split** — every story ends in something runnable or measurable

**Measured findings that changed the stories** (taken from source and executed, not quoted from the analysis documents):
- 🔧 **`PLR0915` is inert at ruff's default 50** — nothing in the codebase trips it, so patterns §14 would have gone unenforced. Set `max-statements = 30`, at which **exactly one function** trips it (`overlay.py:86`), giving the rule a live subject and an auditable allowlist
- 🔧 **"Bit-identical" roll invariance is not bit-identical.** Measured drift up to **8.3e-15** across ±40° of rotation — float64 rounding in the rotation itself. An `==` assertion would fail on correct code; the lock uses `atol=1e-9`, matching the deep-dive's own draft test
- 🔧 **The One Euro step-response figures depend on `main.py:35`'s tuning, not the class defaults.** With `min_cutoff=1.6, beta=0.06` and a 500 px step at 30 fps the deep-dive reproduces exactly (1 / 1 / 6 frames at scales 1.0 / 0.85 / 0.011); with `OneEuro2D()` defaults the same measurement gives 2 frames and never reaches 90% at 0.011
- 🔧 **The variance interlock's absolute σ figures cannot be asserted against synthetic data** — 0.10–0.13 px in-distribution versus the deep-dive's real-data 18–23 px. Locked as a **relationship** (≥1000× inflation, strictly falling scale); the real-data figures are locked exactly and separately in the variance→scale mapping test, where all **7 rows reproduce to 5 dp**
- 🔧 **Story 1.3's session-scope justification was overstated** — the GP fit measures **~0.2 s** for both 9- and 25-row grids, not "multiple seconds". Session scope still correct (~6 s of repetition across the suite) but the stated reason was wrong; story corrected and **GitHub issue #12 re-pushed** to match
- **Exactly one layer violation exists** (`gaze.py` → `face_mesh.py`), so Story 1.4's AST test ships with a one-entry `KNOWN_VIOLATIONS` allowlist rather than a green test asserting nothing
- 🔧 **The textbook pixel→degree formula is wrong away from the screen centre.** Measured on real screen metrics read from this machine: the on-axis shortcut is exact at the centre (agreement 3.5e-14°) but **overstates angular error by 15.59% at a screen corner**. Story 2.1 therefore defines gaze error as the true angle at the eye, and its test suite includes a corner case — because a centre-only test **passes** against the wrong formula (verified by perturbation)
- 🔧 **Aggregating pixels then converting once biases every degree figure by 6.82%**, and the two distributions are not rank-equivalent: in Story 2.1's worked example the worst pixel error (56.5685 px) is **not** the worst angular error (53.6656 px). The degree statistics must be computed independently, not derived from the pixel summary
- 🔧 **The 95th percentile is fragile at the target counts the calibration grid can produce.** Exact thresholds: **n ≤ 21 → p95 interpolates the top two values; 22–41 → the top three**; at 25 targets it rests on order statistics 23 and 24. On a 9-point sample the five numpy methods spanned **20.14 px — 92% of that sample's own mean error**. Story 2.1 reports the method, `n` and a top-k flag rather than refusing, because refusing would block the only baseline the grid can produce
- 🔧 **The calibration grid's `n_points` argument is a ceiling selector, not a count** — `n=1..9` presents 9 targets, `10..16` presents 16, and `17` upward always presents 25 (`n=100` → 25). So FR-11's "target count" cannot be recorded as the argument; Story 2.2 records the **resolved integer coordinates** instead
- 🔴 **FR-8's ≥15-usable rule makes the default nine-target grid impossible to calibrate** — 15 of 9 is unachievable. `main.py:134` passes 25 so the shipped path is viable, but `AppController` **and** `CalibrationWindow` both default to 9, so once FR-8 lands at M5 (CYCLE-3) the default construction always refuses. Flagged for the owners; also "≥60% of *requested*" is ambiguous above 25 (requested 30 presents 25) and must be defined against the **resolved** count
- 🔧 **I was wrong about the grid asymmetry mattering.** The shipped 5×5 y-fractions are uneven (centre row at 0.42; 15 of 25 targets in the upper 42%), and given Story 2.1's 15% cross-screen variation I expected an aggregate bias. Measured: **+0.022%**. The layout must still be pinned exactly, but for *per-target* reproducibility — not because it skews the headline figure
- 🔧 **Repeating the seating distance precisely enough is not humanly achievable.** Measured sensitivity at 600 mm: ±10 mm → **1.69%**, ±25 mm → 4.35%, ±50 mm → 9.09%; holding the angle figure to ≤1% needs **±5.9 mm**. Without a chin rest (out of scope) the degree-based delta carries irreducible seating uncertainty while the **pixel** figure carries none — a second, independent measurement pointing at the same success-criterion-7 question Story 2.1 raised
- 🔧 **A camera index is not an identity and a backend integer is not portable.** `tracker.py` may open a *different* index than requested; and `CAP_V4L2`, `CAP_V4L` and `CAP_VFW` are all **200**, which this build names "Video for Windows". Story 2.2 records the resolved index plus the backend **name**, and the frame size/rate the camera actually granted rather than the ones requested
- 🔴 **The existing calibration code pads a short target with rejected frames** (`overlay.py:200-209` falls back to the ungated buffer and prints a note). Defensible as anti-deadlock for *calibration*; for a *measurement* it swaps bad data for missing data and biases the headline number favourably. Story 2.3 forbids it: a target short of samples is **unusable**, with its dominant rejection reason recorded
- 🔧 **The live and calibration gates diverge on 4 of 5 thresholds** (TD-1, read from both files): blink and squint `0.55` vs `0.58`, |yaw| `0.60` vs `0.70`, |pitch| `0.45` vs `0.55`. The evaluation uses the **live** values because the live experience is what is measured; FR-14/FR-15 unify them at M2, which changes frame acceptance between the two sessions and must be stated in the report
- 🔧 **Small target jumps settle *slower* than large ones** — the opposite of the obvious guess. At `cutoff_scale` 0.011 a 422 px adjacent-column jump needs **113 frames** to settle within 1 px while a 1689 px row-wrap needs **12**, because One Euro's adaptive term raises the cutoff with the derivative. So a settling allowance tuned by watching the biggest jump would be tuned against the easiest case. In distribution (`scale ≈ 0.85`) settling is **2 frames** against a 27-frame dwell
- 🔴 **`.gitignore` was silently becoming `gitignore`.** `git status --porcelain` puts a space before an unstaged path, so a full `.strip()` on the command output ate it and `line[3:]` truncated the filename — wrong for exactly the dotfiles a reader checks first. Found by *rendering a report against this repository*, not by reading the code
- 🔧 **Screen physical size cannot be auto-detected, and the layering rule enforces that.** Under `QT_QPA_PLATFORM=offscreen` this machine reports a **fabricated 203.2 × 203.2 mm square screen at exactly 100.0 DPI**; on the real desktop, `DISPLAY6` has `devicePixelRatio` 1.25, so logical and device pixels differ by 25% and mixing them is a silent 20% error in degrees. `evaluation/` is APPLICATION-layer, so an auto-detecting `import PyQt6` would fail Story 1.4's test — in the same wave

**Two scope corrections made during authoring, recorded rather than absorbed**:
- 🔴 **Story 2.5's `files_touched` was unbuildable** — it listed only `docs/evaluation/baseline-pre-fix.md`. Story 2.3's runner is APPLICATION layer and therefore owns no window (Story 1.4's import test enforces it), and no other story presented targets on screen, so the session had nowhere to draw. `dependency-graph.yml` and the plan index were amended to add `eye_tracker/tools/evaluate_session.py` and its test — `tools/` is INFRASTRUCTURE, so PyQt6 is permitted there, and `tools/__init__.py` already exists from Story 1.1
- 🔴 **The protocol had nowhere to record which signal was scored.** The plan's own risk log requires Story 2.3 to record that choice "in the protocol", and the first draft of Story 2.2 had no field for it — so a session scoring the raw calibrator output would have been reported **comparable** to one scoring the smoothed signal the user sees. `SignalRecord` was added to Story 2.2 and re-verified by execution. It also carries the smoother tuning, because when the smoothed signal is scored `min_cutoff`/`beta` change the recorded number — and Story 1.6 records that **FR-13 moves exactly those constants in CYCLE-2**

**Defects the depth gate and prototyping caught before the stories shipped**:
- A **cross-story break in Story 1.4**: `tools/eye_pairing.py` resolved to no layer, so the import test would have failed the moment Story 1.1 landed. Fixed with an explicit `_layer_key()`
- A pytest **`ScopeMismatch`** in Story 1.3 — a session-scoped fixture cannot request a function-scoped one; `synthetic_pts2d` and `mesh_result` became session-scoped
- `reset_rate_limits()` used but never defined in Story 1.5, found by symbol cross-reference (the gate only parses syntax)
- "Six suite directories" — the architecture defines **five**; corrected in the graph, the plan and the story
- **Story 2.2's JSON round trip is normalising, not identity-preserving** — `to_dict` resolves an implicit `eye_px=None` into the explicit screen centre, so `from_dict(to_dict(p)) == p` **fails** with only `viewing` differing. Correct behaviour (a record must not say "the default"), but a DEV hitting that failure blind would most likely write `None` into the record and lose an assumption worth 5.4% at a corner. Now `normalised()` plus AC 18a
- **Story 2.3's dwell-boundary assertion was off by one frame** — accumulating `t += 1/30` twenty-seven times gives `0.8999999999999999`, below the 900 ms boundary, while `27/30` does not. The runner was right; the *test helper* drifted. Fixed with absolute timestamps, plus a note forbidding an epsilon inside `submit`
- **Story 1.2 had no idempotent-repeat row** — caught by re-running the depth gate over all 11 stories at the end, after the gate had been tightened since 1.2 was written. The setup sequence must be safely repeatable, and now says so

**Items referred back to their owners rather than absorbed**: the "bit-identical" wording in `01-gaze-deep-dive.md`; the tuning-dependent figures in `06-one-euro-deep-dive.md`; and patterns §8's "nothing imports upward", which is true of the dependency *cycle* check but not of layers.

---

### Build Cycles

**Owner**: AIRE_BUILD_CYCLE_PLANNER
**Status**: ✅ Done
**Started**: 2026-08-07
**Completed**: 2026-08-07
**Approach**: Cycles derived directly from the architecture's **M0 – M8 migration graph**. Boundaries placed on hard dependency edges so the two evidence-forced orderings cannot be violated by accident

**Progress**:
- [x] Prerequisites — requirements, `architecture/current/` (8 files), `architecture/design/` (2 files) all verified present; `docs/plans/builds/` empty so **no carry-forward items** ✅
- [x] Reference check — `SPEC/references/` contains **0 files**; `SPEC/references/builds/` empty, so cycles are derived from `requirements.md` rather than from supplied build files ✅
- [x] Phase 1 — Requirements, architecture and patterns loaded; 33 FRs extracted; sequencing constraints and cross-cycle integration points noted ✅
- [x] Phase 1d — Tier categorisation: Tier 4 (Integrations) and Tier 5 (NFR/Polish) both **deliberately empty**, each with its reason ✅
- [x] Phase 2 — 5-cycle structure proposed without questions first, per the workflow rule; **user confirmed as proposed** ✅
- [x] Phase 3 — 5 × `cycle-plan.md` generated, each with scope, 4-half-day workshop plan, acceptance criteria, open items, prerequisites, `shared_files` and rollback ✅
- [x] Phase 4 — `docs/plans/build-cycles.md` written: cycle map, dependency map, FR and defect traceability, **14-item risk log**, deviations ✅
- [x] Phase 4 — Dependency diagram **rendered to SVG** (mermaid-cli 11, `aria-roledescription="flowchart-v2"`, 0 real error markers, 5/5 nodes and 3/3 edge labels present) ✅
- [x] Phase 4.5 — GitHub Release Plan executed: `TBD` placeholder **replaced** with 5 Release options; 5 draft releases created; option IDs written back into every cycle plan ✅
- [x] Phase 5 — `docs/status.md` updated ✅

**Cycle structure** (strictly sequential — every boundary sits on a hard dependency edge):

| Cycle | Phases | FRs | Expected Outcome |
|---|---|---|---|
| CYCLE-1 | M0 + M1 | 10, 11, 25*, 26, 27*, 29*, **33** | Green suite + **signed pre-fix accuracy baseline** |
| CYCLE-2 | M2 + M3 | 1, 2, 3, 4, 13, 14, 15, 18* | Correct axes, no discontinuity, **pitch gated for the first time**, one gate definition |
| CYCLE-3 | M4 + M5 | 5, 6, 7, 8, 9, 22 | Abort emits **exactly once**; **recalibrate without restarting**; visible refusal on too-few targets |
| CYCLE-4 | M6 | 20, 21, 23, 24, 25, 30, 31, 32 | **Every failure path visible within 3 s** with a recovery action; dot hides within 500 ms |
| CYCLE-5 | M7 + M8 | 12, 16, 17, 18, 19, 27, 29 | Profile restore with the version gate; **delta with a 95% CI** — programme sign-off |

\* partial in that cycle. **FR-27, FR-28 and FR-29 span every cycle** — Tier 5 was left deliberately empty because the Core Rule *Tests with Code — never postpone tests* forbids a testing tier.

**Why the boundaries are where they are** (both orderings come from evidence, not preference):
- 🔴 **The baseline must precede the head-pose fix** (FR-12). Cycle 1 ends with it; Cycle 2 begins the fix. If the fix landed first the pre-fix baseline would be unrecoverable without checking out an old commit and re-running a human protocol, and success criterion 7 — "accuracy must not regress" — would become **unverifiable**.
- 🔴 **Persistence must be last** (FR-18). A bundle written before the head-pose semantics settled would be refused by its own version gate the moment Cycle 2 shipped. Failure criterion 3 names a silently-loaded stale profile as the **highest-severity outcome available in this scope**.

**Findings recorded during planning**:
- 🔴 **Two of the five Day-4s are human-gated, not build steps.** Cycle 1 and Cycle 5 both need a person, a webcam, controlled lighting and a measured seating distance. Neither can be completed by an agent and neither can be compressed. If the evaluation protocol (open item 3) is unsettled by Cycle 1 Day 3, **the whole programme slips** — Cycle 2 cannot start without the baseline
- 🔴 **A cross-cycle dependency the migration graph does not show**: Cycle 2 ships the two provisional pitch ceilings (0.35 / 0.45 rad — the only invented numbers in the design), but the FR-24 rejection counters that would settle them do not arrive until **Cycle 4**. Cycle 5 carries the task to revisit them
- ⚠️ **A gap between Cycles 3 and 4**: Cycle 3 lands `setQuitOnLastWindowClosed(False)`, but the user-facing Quit control is in `StatusWindow`, which lands in Cycle 4. Cycle 3 therefore ships a tested programmatic exit path, and Cycle 4 must not slip independently — the migration plan treats M4's items as one unit of work
- ⚠️ **Cycle 4 has the largest `shared_files` surface** — `app.py`, `errors.py`, `diagnostics.py`, `config.py` and `conftest.py` all touched by multiple concerns. `aire-brownfield-plan` must **sequence** rather than parallelise stories touching these
- ✅ **`aire-ui-ux-design` having run first turned out to be load-bearing**, not merely advisable: Cycle 4 builds `StatusWindow` and consumes the approved spec directly, so no design run sits on the critical path

**Evidence-driven deviations from the workflow's defaults** (each recorded with its reason):
- **Vertical slices reframed, not abandoned** — this is a single-process desktop application with **no frontend/backend axis to slice along**. The intent is held instead: every cycle ends in something a stakeholder can observe. Cycle 1's observable is a measurement rather than a feature, which is the honest description of it
- **Tier 5 (NFR/Polish) deliberately empty** — a testing tier would violate the Core Rule *Tests with Code*
- **Tier 4 (Integrations) empty** — both integration points (webcam in, one-time model download out) already work
- **No dates invented** — Target Completion is `TBD` (open item 1). Cycles are sequenced by dependency and sized to the 4-half-day structure, ready to be dated

**GitHub integration verified, not assumed**:
- `TBD` placeholder **replaced** (not appended to — `singleSelectOptions` replaces the whole list). Verified beforehand that all 8 project items had `Release` unset, so **nothing lost an assignment**
- 🔧 **The workflow's own example mutation would have failed**: `UpdateProjectV2FieldInput` no longer accepts `projectId`. Sent `fieldId` + `singleSelectOptions` only
- 5 draft releases created; **0 git tags pushed** — verified, because a draft creates no tag until published. Draft URLs therefore carry `untagged-…` and change on publish
- 🔧 `gh` was **not on `PATH`** during this run and had to be invoked as `C:\Program Files\GitHub CLI\gh.exe`. It was **added to the User `PATH` on 2026-08-07**, so new shells resolve `gh` directly — note that already-running processes keep the old in-memory `PATH` until restarted

---

### UI/UX Design

**Owner**: AIRE_UI_UX_DESIGNER
**Status**: ✅ Done
**Started**: 2026-08-07
**Completed**: 2026-08-07
**Scope**: 3 surfaces — `StatusWindow` (new), `CalibrationWindow` and `GazeOverlay` (both existing, modified)

**Progress**:
- [x] Before Starting — brownfield detected; requirements, 7 deep-dives, target architecture and patterns all verified present ✅
- [x] Reference check — `SPEC/references/` contains **0 files**, so the approved-designs `[S]`kip gate did not trigger ✅
- [x] Step 01 — Context read; `docs/ui-ux/01-discovery.md` written, incl. a **measured contrast audit of every existing colour** ✅
- [x] Step 02 — 4 design questions asked and answered; 9 further items derived from approved documents with their evidence recorded ✅
- [x] Step 03 — Decisions documented; **checkpoint** `docs/ui-ux/03-inspiration.md` ✅
- [x] Step 04 — Design tokens created; every colour verified by computation, not estimated ✅
- [x] Step 05 — **Gate 1 approved** ✅
- [x] Steps 06–07 — Component hierarchy, layout, DPI strategy, focus and keyboard model ✅
- [x] Step 08 — **Checkpoint** `docs/ui-ux/08-visual-foundation.md`; **Gate 2 approved** ✅
- [x] Steps 09–10 — Component→feature map and UX patterns ✅
- [x] Step 11 — **Gate 3 approved** ✅
- [x] Step 12 — Accessibility sub-gate: all 6 items defined; `docs/ui-ux/ui-ux-spec.md` generated ✅
- [x] Step 13 — `docs/status.md` updated ✅

**User decisions** (4 asked, not assumed):

| Question | Decision |
|---|---|
| Accessibility level | **AAA** for owned windows; **AA non-text** floor for the overlay |
| Gaze-dot visibility | **Dual outline** — dark outer ring + light inner ring |
| Failure presentation | **Persistent banner** in `StatusWindow` |
| Styling mechanism | **Central tokens module**, shared by QSS and `QPainter` |

**Measured findings — contrast audit of the existing palette**:
- ✅ Calibration body text already measures **9.01:1 — passes AAA**. No change needed
- 🔴 **The gaze dot's white outline measures 1.00:1 on a white desktop — invisible.** No single outline colour works over uncontrolled content. The dual outline was verified to give a best-edge contrast of **≥5.32:1 on any background**, including the pathological red-on-red case
- 🔴 `#4CAF50` — the **workflow's own default success green** — measures 5.97:1 here and **fails AAA**. Replaced with `#6BE39A` (10.33:1)
- 🔴 The natural error red `#FF5C5C` measures 5.48:1 and fails AAA. Replaced with `#FF8A8A` (7.31:1)
- 🔴 The focus ring is **white, not accent**: `#00D2FF` reaches only 2.79:1 against the border it sits beside, under the 3:1 floor. White gives 5.03:1
- ⚠️ Target ring **fill** is 1.47:1 against the background — the ring is carried entirely by its stroke

**Evidence-driven deviations from the workflow's defaults** (each recorded with its reason):
- **Elevation is 3 levels, not the Material 0/1/2/4/8/16** — Qt provides no portable drop shadow, and shadows on a frameless translucent always-on-top window are compositor-dependent. Depth comes from tone + border
- **44 pt touch targets, not the desktop 32 pt minimum** — justified by an audience that may have motor impairment
- **No responsive breakpoints or column grid** — single primary display; multi-monitor is out of scope
- **Sizes in points, not pixels** — points scale with the OS DPI setting; pixels do not
- **Explicit typography is itself a fix**: there is no `setFont` call anywhere today, so all text renders at the OS default (~9 pt), including the full-screen calibration instruction

**Three UX decisions that fall out of the architecture**:
- 🔴 **The GP fit must show static text, never a spinner.** DR-14 deliberately leaves the fit on the GUI thread, so an animated spinner would freeze mid-spin — and a frozen spinner reads as a hang. The label must also be painted and flushed *before* the blocking call or it never renders
- 🔴 **Focus-stealing rule**: `StatusWindow` raises and activates itself **only** on a transition into `Faulted`, never during normal running — the in-scope way to make keyboard recovery reachable at the moment it is needed
- 🔴 **A mid-session screen-geometry change must invalidate the *active* calibration**, not just stored ones, because screen geometry is part of the profile key. Both windows currently capture geometry once and never revalidate. ⚠️ **New scope, stated by no FR** — falls out of proposed FR-19a, still awaiting ratification

**Recorded limitations** (not solved, and not presented as solved):
- Qt shortcuts are application-scoped, so `R`/`T`/`Q` do not fire while `StatusWindow` lacks focus. A global hotkey needs platform-specific hooking, which is out of scope
- 🔴 **A user who can operate neither mouse nor keyboard cannot self-recover this cycle.** FR-20/FR-23 require an offered recovery action; the audience is defined as users who cannot use a mouse; dwell-click is explicitly out of scope. This is a consequence of the signal-only scope and cannot be solved by UI design — revisit when dwell-click is scoped
- Any always-visible window permanently occupies screen area a gaze user might want to look at. Held to ~420 × 44 pt via the collapsed pill

**Spec compliance**: `ui-ux-spec.md` measured at **681 tokens** (cl100k) / **686** (o200k) against the <700 limit, using `tiktoken` rather than an estimate — a character-based estimate had put the first draft at 1,103. 0 prose lines, 0 emoji, all 9 template sections present.

---

### Patterns & Standards

**Owner**: AIRE_ARCHITECT
**Status**: ✅ Done
**Started**: 2026-08-07
**Completed**: 2026-08-07
**Approach**: 45 catalogued patterns compared against the rulebooks; every pattern marked `[Current — kept]` or `[New adoption]` with DO/DON'T examples

**Progress**:
- [x] Prerequisites — requirements, system overview, 7 deep-dives and the approved target architecture all verified present ✅
- [x] Reference check — `SPEC/references/` + `builds/` + `devops/` contain **0 files** ✅
- [x] Phase 1 — Pattern catalogs extracted from all 7 deep-dives; code standards re-measured directly against source ✅
- [x] Phase 2a — **Duplicate / misplaced shared-code scan: 6 tech-debt items found (TD-1 – TD-6)**, each with evidence and a resolution phase ✅
- [x] Phase 2 — Recommended patterns loaded from `aire-design-patterns.md`, `aire-implementation-rulebook.md`, `aire-clean-architecture.md` ✅
- [x] Phase 3 — All 8 workflow categories compared and decided; 2 reframed as N/A; 4 open decisions taken by the user ✅
- [x] Phase 4 — Project structure and code structure defined (target layout, import ordering, dependency management) ✅
- [x] Phase 5 — Coding patterns documented with DO/DON'T for every pattern ✅
- [x] Phase 6 — Testing patterns: layout, naming, AAA, mocking policy, failing-first regression rule, coverage gate ✅
- [x] Phase 7 — Documentation standards ✅
- [x] Phase 7.5 — **File/Module Boundary Map** with the `shared_files` list for `docs/plans/dependency-graph.yml` ✅
- [x] Phase 8 — `docs/architecture/design/03-patterns-and-standards-brownfield.md` written; 29/29 Python examples and the TOML config **parse-verified** ✅
- [x] Phase 9 — `docs/status.md` updated ✅

**Pattern decisions** (16 sections; 4 genuinely open choices taken by the user, the rest constrained by approved requirements or already compliant):

| # | Category | Decision | Migration |
|---|---|---|---|
| 1 | Project Structure | [Current — kept + extended] | No |
| 2 | Error Handling | **[New adoption]** — F0–F4 taxonomy + `EyeTrackerError` hierarchy | Medium |
| 3 | Logging | **[New adoption]** — `logging`, bracket prefixes → logger names | Low |
| 4 | Persistence & File I/O *(reframed from Database Access — N/A)* | [Current — kept + extended] | No |
| 5 | Internal Contract Format *(reframed from API Response Format — N/A)* | [Current — kept] | No |
| 6 | Configuration | **[New adoption]** — dataclasses + TOML | Medium |
| 7 | Naming Conventions | [Current — kept, one scoped exception] | No |
| 8 | Code Organisation | [Current — kept + **enforced** by AST test] | No |
| 9 | UI Components / Shared Library | [Current — kept] | No |
| 10 | Concurrency & Thread Affinity | [Current — kept, made explicit] | No |
| 11 | Numerical Guards | [Current — kept] | No |
| 12 | Annotations & Docstrings | **[New adoption]** — new/touched code, NumPy on public API | No |
| 13 | Lint & Format Tooling | **[New adoption]** — ruff, `line-length = 100` | Low |
| 14 | Function & File Length | **[New adoption]** — ≤30 with an auditable allowlist | Low |
| 15 | Testing | **[New adoption]** — none exists today | High |
| 16 | Documentation | **[New adoption]** | No |

**User decisions taken this run**: ruff for lint+format · annotate new/touched code with NumPy docstrings on the public API · package base `EyeTrackerError` with typed subclasses · enforce ≤30 lines with a documented allowlist.

**Measured findings** (taken from source, not from the analysis documents):
- **10 of 56 functions exceed the 30-line rule** — worst: `extract_gaze_features` 95, `_open_capture` 47, `CalibrationWindow.__init__` 43. **0 files exceed 500 lines** (largest: `overlay.py` at 267)
- **1 of 56 functions carries any type annotation**; **6 of 65 defs have a docstring**; 7 of 7 functional modules have a module docstring
- 🔧 **Correction to the analysis documents**: they record "nine `print` sites across four modules". Measured directly it is **10 sites across 3 modules** (`main.py` 2, `overlay.py` 3, `tracker.py` 5). The patterns document carries the measured figure and the FR-25 inventory is one larger than recorded
- `line-length = 100` chosen by measurement — 3 lines need touching at 100 versus 13 at 88; longest existing line is 108

**Known tech debt recorded** (TD-1 – TD-6, flagged as debt **not** patterns to imitate): duplicated gate thresholds (12 literals, diverged on 4 of 6) · landmark indices re-inlined while their named constants go unused · screen geometry resolved twice · `print()` as sole diagnostics · 7 dead-code items · stale `Eyee` cache-path identity. No duplicated widgets or misplaced generic helpers were found.

**Key standards established beyond the workflow's category list**: the one stated rule for drop-frame versus surface (F0–F4) that the deep-dives said the project lacked · the **tunable versus numerical-guard boundary**, so success criterion 8 does not turn epsilons into configuration · concurrency and GUI-thread affinity as asserted invariants rather than accidents · short mathematical locals permitted **only** where the function's docstring cites the source defining them.

---

### Target Architecture

**Owner**: AIRE_ARCHITECT
**Status**: ✅ Done
**Started**: 2026-08-07
**Completed**: 2026-08-07
**Approach**: Existing architecture style extended, not replaced. Additive-First throughout — 1 deliberate breaking contract change, explicitly flagged

**Progress**:
- [x] Prerequisites — system overview, 7 deep-dives and `docs/requirements.md` all verified present ✅
- [x] STEP 0 — Reference check: `SPEC/references/` + `builds/` + `devops/` contain **0 files**; nothing required `aire read`; no approved material constrains the design ✅
- [x] Phase 0 — Context loaded: overview + 7 deep-dives + requirements + **all 8 application source files re-read** (1,295 LOC) so the design cites current code, not the analysis alone ✅
- [x] Phase 0 — Impact analysis presented: all 7 modules Modified, 15 new components, 3 sequencing findings ✅
- [x] Phase 1 — Delta analysis, technology selection (**no new runtime dependency**), architecture-style decision ✅
- [x] Phase 2 — Target context, component architecture, data architecture, contract changes, security design ✅
- [x] Phase 2 — Roles & Permissions Matrix reconciled: **no new roles**, no matrix update required ✅
- [x] Phase 3 — Error handling (one stated rule, 5 categories) and observability designed ✅
- [x] Phase 3 — `docs/architecture/design/02-target-architecture-brownfield.md` written: delta table, 17 decision records, migration plan, full FR traceability ✅
- [x] Phase 3 — `docs/architecture-diagrams/02-target-architecture-diagrams-brownfield.md` written; **8/8 diagrams rendered to SVG** (mermaid-cli 11.16.0, 0 error markers), 8/8 blocks SHA-256-identical to source ✅
- [x] Phase 3 — User approval obtained ✅
- [x] Phase 4 — `docs/status.md` updated ✅

**Decisions recorded** (4 supplied by the user, 13 derived and each carrying ≥2 alternatives):

| Decision | Value |
|---|---|
| Head-pose source (DR-1) | Fix inside `solvePnP` — rebind axes, unwrap pitch. `facial_matrix` deferred as a measured experiment |
| Configuration layer (DR-2) | Frozen dataclasses + optional TOML via stdlib `tomllib` |
| Calibration profile key (DR-3) | One auto slot per capture fingerprint + semantics version; auto-save, auto-restore |
| Profile restore gate (DR-4) | Refuse on **any** mismatch |
| Controller location (DR-5) | `AppController` → `eye_tracker/app.py`; `main.py` becomes a shim (FR-27 coverage) |
| Live path (DR-6) | Extracted as a pure `LivePipeline` — the main testability lever |
| Profile format (DR-7) | ZIP of `manifest.json` + `model.joblib`, atomic temp-then-replace |
| Serialisation (DR-8) | `joblib` (already transitive via scikit-learn); `skops` recorded as the long-term direction |
| `finished` payload (DR-9) | `CalibrationResult` dataclass — **the one deliberate breaking change** |
| Layering (DR-10) | Enforced by an AST import-direction test, not a directory restructure |
| Calibration window (DR-11) | Single-use, `WA_DeleteOnClose` — removes the bug class by lifetime |
| New UI surface (DR-12) | `StatusWindow` — derived from FR-20 – FR-24, not added |
| Smoother (DR-13) | `OneEuro2D.reset()` — additive, required by FR-22 |
| App lifetime (DR-14) | `setQuitOnLastWindowClosed(False)` now; **GP fit deliberately not threaded** — no FR requires it |
| Camera viability (DR-15) | `viable` removed, intent enforced as a configured F3 precondition |
| Silent fallbacks (DR-16) | Head-pose failure → `NaN` not zeros; absent blendshapes → F3 fault |
| Test tooling (DR-17) | pytest + pytest-cov + pytest-qt |

**Key design outcomes**:
- 🔴 **FR-3's trap closed with recorded provenance.** Each gate threshold is re-bound to the physical axis it was actually tuned for: yaw inherits 0.45/0.55 from today's `PITCH`-named gate, roll inherits 0.60/0.70 from today's `YAW`-named gate. Keeping the numbers against corrected names would have retuned both envelopes in opposite directions.
- 🔴 **Migration order is evidence-forced, not preferred.** The evaluation harness (M1) must precede the head-pose fix (M3) because FR-12 requires a pre-fix baseline; persistence (M7) must come last because FR-18's gate is only meaningful once semantics stabilise.
- 🔴 **FR-8 surfaced a structural finding.** A "samples > input dimensions" rule is unsatisfiable at any achievable target count — the binocular Y subset has 25 columns and the grid yields at most 25 targets. The minimum is therefore set on a coverage basis (≥15 usable, ≥3 rows, ≥3 columns, ≥60% of requested), which is also the better guard given row-major collection.
- **Persistence is refuse-before-unpickle by construction.** The manifest is JSON inside a ZIP specifically so every mismatch check completes before deserialisation; three witness vectors make FR-17's 1e-6 px identity a runtime invariant, not only a test.
- **Only 2 invented numbers in the whole design** — the provisional pitch ceilings (0.35 / 0.45 rad), both marked provisional and traceable to open item 3.

**Requirements reconciliation — 8 items flagged for the requirements owner** (recorded in the document, none silently absorbed): proposed FR-19a (screen geometry belongs in the profile key); DR-16's two observability changes traced to failure criterion 1 rather than a numbered FR; `one_euro.py` moving from IMPACT to Modified; the `finished` payload change; `calibration:delete-own` having no FR; `StatusWindow` as a new UI surface; the two provisional pitch ceilings; and the unanswered question of what `pose_quality` is *supposed* to do.

**Coverage**: 33/33 FRs traced to a named design element · 16/16 success criteria · 10/10 failure criteria · **0 application source changes**.

---

### Requirements

**Owner**: AIRE_ANALYST_PM
**Status**: ✅ Done
**Started**: 2026-08-06
**Completed**: 2026-08-06
**Path**: PATH L (local definition), with the 7 GitHub defects folded in as a remediation workstream

**Progress**:
- [x] Prerequisites — system overview + 7 deep-dive documents verified present ✅
- [x] STEP 0 — Reference check: `SPEC/references/` contains **0 files**; no PRD, designs, specs or build documents; nothing required `aire read` ✅
- [x] STEP 1 — Source selected: PATH L (GitHub Projects is the configured tracker; the repo's only issues are the 7 defects, no feature stories existed) ✅
- [x] L.1 — Architecture summary presented from the verified analysis ✅
- [x] L.2 / L.3 — 8 product decisions collected across two question rounds ✅
- [x] L.4 — `docs/requirements.md` generated: 33 functional requirements across 9 themes, 16 measurable success criteria, 10 failure criteria, full defect traceability ✅
- [x] L.5 — `docs/status.md` updated ✅

**Decisions recorded** (none inferred — all supplied by the user):

| Decision | Value |
|---|---|
| Product intent | Hands-free input / accessibility |
| Primary objective | Improve gaze accuracy |
| Interaction scope | Signal + baseline only — no dwell-click, scroll or pointer control this cycle |
| Accuracy target | Establish a baseline first; no numeric target invented |
| Foundations IN | Automated test suite, configuration layer, calibration persistence |
| Foundations OUT | Multi-monitor support |
| Defects IN | All 7 (#3–#9) |
| Eye-pairing risk | Specced as the first story (FR-33), not assumed |
| Failure UX | Visible error + guided recovery |

**Key requirement outcomes**:
- **Theme A (head-pose correctness) is a prerequisite, not parallel work.** Accuracy cannot be measured or trusted while defects #4 and #5 stand — the axes are mislabelled and feature 10 jumps 6.21 rad at the neutral head position.
- 🔴 **FR-18 exists because two IN-scope choices collide.** Theme A changes what head-pose features *mean*; Theme E makes calibrations outlive the process. Without a feature-semantics version on saved calibrations, a pre-fix profile would load silently into a post-fix system and produce confidently wrong predictions with no error and no attribution path. Highest-severity latent hazard in this scope. Persistence must not ship before the semantics stabilise.
- **Accuracy is expressed as measurement, not a number** — success criteria require a documented protocol, a baseline recorded against a commit SHA, and a post-fix delta with a 95% CI. "Must not regress" is the bar.
- **FR-3 guards a specific trap**: renaming the head-pose axes without re-pairing the gate thresholds silently retunes the physical envelope, because those numbers were tuned against whichever axis was actually being measured.
- **Roles: single actor.** Verified across all 8 source files — no auth, no user model, no sessions. Calibration profiles are per-machine files, explicitly **not** an access-control mechanism.

**Open items** (recorded, not invented — none blocks architecture): target completion date; target deployment hardware (cameras / OS versions for accessibility users); evaluation protocol specifics; the eye-pairing answer (FR-33); the calibration profile key; and the `.venv/` rebuild, which currently blocks any test runner.

---

### Deep-Dive

**Owner**: AIRE_ARCHITECT
**Status**: ✅ Done
**Started**: 2026-08-06
**Completed**: 2026-08-06
**Scope**: Full system — all 7 functional modules (1,295 LOC, 8 files including the empty package marker)

**Progress**:
- [x] Prerequisites — agent, rulebook, system overview verified; `SPEC/references/` re-checked (empty, 0 reference docs) ✅
- [x] Phase 1 — Module analysis: all 7 modules, components, interfaces, internal/external dependencies ✅
- [x] Phase 2 — Flow analysis: 19 Mermaid diagrams (7 sequence, 4 state, 8 flow) ✅
- [x] Phase 3 — Data analysis: 38-D feature contract fully specified; no database exists (documented as N/A, no ER diagram applicable) ✅
- [x] Phase 4 — Pattern extraction: 45 patterns catalogued across 7 modules, every one with a file-cited code example and DO/DON'T ✅
- [x] Phase 5 — 7 deep-dive documents written ✅
- [x] Phase 6 — 7 diagram preview files written; 38/38 Mermaid blocks structurally validated, every diagram byte-equal between source and preview ✅
- [x] Phase 7 — `docs/status.md` updated ✅

**Verification performed** (synthetic inputs only; no webcam, no repository file modified):
- 4 verification scripts executed against the installed libraries — Python 3.14.6, numpy 2.5.1, scikit-learn 1.9.0, OpenCV 4.14.0.94, PyQt6 6.11.0
- **25 checks executed** across modules `01`, `02`, `03`, `05`, `06` — including a headless offscreen-Qt harness that drove the real `CalibrationWindow` with a stub tracker
- Modules `04` and `07` rest on source reading and cross-file search (no execution possible without a webcam); each claim is individually sourced in its Verification Record
- Every unverified claim is marked ⚠️ and carries a defined test procedure — no finding is asserted without either execution or a citation

**Key findings** (detail in the per-module documents):
- 🔴 **Head-pose angle labels are cyclically permuted** — verified by projecting a synthetic head and rotating each camera axis 15°. `FEATURE_YAW` measures roll, `FEATURE_PITCH` measures yaw, `FEATURE_ROLL` measures pitch. Consequence: the frame-rejection gates act on the wrong axes and **nodding is never gated at all**. See `03-face-mesh-deep-dive.md`
- 🔴 **`FEATURE_ROLL` is discontinuous at the neutral head position** — rests at ±π and swings 6.21 rad across a 4° nod. Present in all 6 GP feature subsets. Leading hypothesis for the kernel length-scale saturation. See `03`
- 🔴 **Aborting calibration can emit `finished` twice** — reproduced headless: 2 fits, 2 overlays, 2 signal connections, with the second arriving ~107 s later in the shipped configuration. Cause: 3 of 5 scheduled transitions use uncancellable static timers. See `05`
- 🟡 **App-exit constraint** — reproduced: the application survives calibration only because the overlay is shown synchronously before the calibration window closes. Threading the blocking GP fit (the obvious fix for the frozen UI) makes the app exit silently unless `setQuitOnLastWindowClosed(False)` lands first. Sequencing constraint for the target architecture. See `05`, `07`
- 🟡 **`pose_quality` cannot move the predicted gaze point** — verified: it is a common factor across all fusion weights and cancels exactly. It only changes smoothing strength. See `02`
- 🟡 **11 of 38 features are exactly linearly determined** (numerical rank 27) — 8 intentional aggregates plus 3 unintended: the two lid-clearance pairs each sum to 1.0, and `INTEROCULAR` is a constant multiple of `FACE_SCALE`. Redundant columns are fed to the same isotropic kernel; the binocular subsets are 28–29% redundant. See `01`, `02`
- 🟡 **4 of 6 GP kernels saturate the RBF length-scale ceiling** on clean synthetic data, putting them in the near-linear regime — the models are not behaving as the flexible nonparametric regressors the design implies. See `02`
- 🟡 **Dead code confirmed by search**: `viable` camera thresholds (documented as live configuration in the system overview — **that entry is superseded by `04`**), `FEATURE_COUNT`, `GazeCalibrator.predict`, `GazeOverlay.set_dot_visible`, `facial_matrix`, 4 unused landmark imports, unused `numpy` import in `tracker.py`
- ✅ **Confirmed strengths**: eye-local geometry is exactly roll-invariant (bit-identical across 40° of rotation); the uncertainty channel genuinely works as an out-of-distribution interlock (σ 18–23 px in-distribution vs ~6000 px extrapolating); the atomic model-download pattern is correct; camera selection by actual face detection is well designed
- 🔴 Zero automated tests remains the dominant risk — every numerical finding above was reachable by a test that does not exist. `01`, `03` and `06` need no hardware at all

**Environment note for downstream workflows**: `.venv/` currently has no `Scripts/python.exe` and no `pyvenv.cfg`, so it cannot be activated. The libraries are present in `.venv/Lib/site-packages` and were reached via `PYTHONPATH` with system Python 3.14.6. This differs from the rebuilt-environment state recorded in `00-system-overview.md` and will block any test runner until resolved.

---

## Build Cycles

| Cycle | BUILDID | Scope | Stories | Status | Start | End | Recorded |
|-------|---------|-------|---------|--------|-------|-----|----------|
| Cycle 1 | CYCLE-1 | Foundations & Measurement Baseline — packaging, test scaffold, logging infra, `.venv` rebuild, FR-33 eye-pairing, evaluation harness + **pre-fix baseline** (M0 + M1) | 0/11 | ⏸️ Not Started | — | — | 2026-08-07 17:38 |
| Cycle 2 | CYCLE-2 | Configuration & Head-Pose Truth — config layer, single gate definition, axis correction, de-discontinuation, pitch gating, semantics v2 (M2 + M3) | 0/— | ⏸️ Not Started | — | — | 2026-08-07 14:58 |
| Cycle 3 | CYCLE-3 | Calibration Integrity & Recalibration — owned lifetime, cancellable machine, idempotent completion, recalibrate without restart, minimum-usable enforcement (M4 + M5) | 0/— | ⏸️ Not Started | — | — | 2026-08-07 14:58 |
| Cycle 4 | CYCLE-4 | No Silent Failures — `StatusWindow`, rejection accounting, `print()` → logging, dot hiding, capture robustness, `viable` enforced (M6) | 0/— | ⏸️ Not Started | — | — | 2026-08-07 14:58 |
| Cycle 5 | CYCLE-5 | Persistence & Accuracy Delta — versioned profile bundle, refuse-before-unpickle, post-fix delta with 95% CI, ≥85% coverage close-out (M7 + M8) | 0/— | ⏸️ Not Started | — | — | 2026-08-07 14:58 |

_Stories `X/N` column is advisory after parallel merges; compute from Story Tracker._
_Cycles 2–5 show `0/—` because story decomposition was scoped to **CYCLE-1 only**; each needs its own `aire-brownfield-plan` run before its `N` is known._

---

## Story Tracker

| BUILDID | Story | Title | Start | End | Recorded |
|---------|-------|-------|-------|-----|----------|
| CYCLE-1 | 1.1 | Eye-pairing investigation — do landmark and blendshape signals describe the same eye | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 1.2 | Packaging metadata, tool configuration and a rebuilt development environment | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 1.3 | Test scaffold — offscreen Qt harness, synthetic fixtures and the five suite directories | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 1.4 | Dependency-direction enforcement — an AST import test replacing a directory restructure | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 1.5 | Structured logging infrastructure with the bracket convention preserved as logger names | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 1.6 | Invariant locks for the three verified-correct behaviours reachable without hardware | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 2.1 | Gaze-error metrics reported in both degrees of visual angle and screen pixels | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 2.2 | Evaluation protocol — target layout, session parameters and the reproducibility record | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 2.3 | Evaluation runner — present known targets, collect predictions, emit a measurement set | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 2.4 | Baseline report generation stamped with the commit SHA it was measured against | — | — | 2026-08-07 17:38 |
| CYCLE-1 | 2.5 | Record the pre-fix accuracy baseline under the documented protocol | — | — | 2026-08-07 17:38 |

**Authoring state** — ✅ **all 11 stories have story files**, so `aire-dev-implement` can be run for any story in any wave. What remains is the GitHub push pass, not authoring.

| Story | Story file | GitHub issue | Wave |
|---|---|---|---|
| 1.2 | ✅ `epic-1-story-1.2-Packaging-And-Environment.md` | [#10](https://github.com/raminmardani/EyeTracker/issues/10) | 1 |
| 1.1 | ✅ `epic-1-story-1.1-Eye-Pairing-Investigation.md` | [#11](https://github.com/raminmardani/EyeTracker/issues/11) | 2 |
| 1.3 | ✅ `epic-1-story-1.3-Test-Scaffold.md` | [#12](https://github.com/raminmardani/EyeTracker/issues/12) | 2 |
| 1.5 | ✅ `epic-1-story-1.5-Logging-Infrastructure.md` | [#13](https://github.com/raminmardani/EyeTracker/issues/13) | 2 |
| 1.4 | ✅ `epic-1-story-1.4-Import-Direction-Enforcement.md` | ⏸️ not pushed | 3 |
| 1.6 | ✅ `epic-1-story-1.6-Invariant-Locks.md` | ⏸️ not pushed | 3 |
| 2.1 | ✅ `epic-2-story-2.1-Error-Metrics.md` | ⏸️ not pushed | 3 |
| 2.2 | ✅ `epic-2-story-2.2-Evaluation-Protocol.md` | ⏸️ not pushed | 4 |
| 2.3 | ✅ `epic-2-story-2.3-Evaluation-Runner.md` | ⏸️ not pushed | 5 |
| 2.4 | ✅ `epic-2-story-2.4-Baseline-Report.md` | ⏸️ not pushed | 6 |
| 2.5 | ✅ `epic-2-story-2.5-Record-Baseline.md` | ⏸️ not pushed | 7 |

⚠️ Issues **#10 and #12** have been edited locally since they were pushed — 1.2 gained an idempotent-repeat row (its absence was caught by a later tightening of the depth gate) and 1.3's fit-cost figure was corrected. Both GitHub bodies are **stale** and must be refreshed in the push pass.

---

## Enhancement Tracker

| Enhancement | Story ID | Title | Related-Story | Tracker | Start | End | Recorded |
|-------------|----------|-------|---------------|---------|-------|-----|----------|
| — | — | (none) | — | — | — | — | 2026-08-06 14:57 |

---

## Change Requests

| CR ID | Status | Scheduled Cycle | Summary | Drafted | Applied | Recorded |
|-------|--------|-----------------|---------|---------|---------|----------|
| — | — | — | (none) | — | — | 2026-08-06 14:57 |

---

## Quality Metrics

| Metric | Target | Current | Status | Recorded |
|--------|--------|---------|--------|----------|
| Unit Test Coverage | ≥85% | —% | ⏸️ | 2026-08-06 14:57 |
| Integration Tests | 100% pass | — | ⏸️ | 2026-08-06 14:57 |
| Code Review | All stories | 0/11 | ⏸️ | 2026-08-07 17:38 |
| Documentation | All stories | 0/11 | ⏸️ | 2026-08-07 17:38 |

---

## Completed Steps

- [x] **Project Kickoff**: Done — 2026-08-06
  - Evidence: `docs/status.md`
- [x] **System Discovery**: Done — 2026-08-06
  - Evidence: `docs/architecture/current/00-system-overview.md`
  - Diagrams: `docs/architecture-diagrams/00-system-overview-diagrams.md` (3 diagrams, all validated)
  - Coverage: 8/8 application source files read; 9/9 dependency versions verified; 0 code changes made
- [x] **Deep-Dive**: Done — 2026-08-06 (full system, 7 of 7 modules)
  - Evidence:
    - `docs/architecture/current/01-gaze-deep-dive.md` — 38-D feature contract, eye-local geometry, redundancy analysis
    - `docs/architecture/current/02-calibration-deep-dive.md` — 6 GPs, feature subsets, quality weighting, variance fusion
    - `docs/architecture/current/03-face-mesh-deep-dive.md` — MediaPipe adapter, model cache, head-pose axis mislabelling
    - `docs/architecture/current/04-tracker-deep-dive.md` — capture thread, camera discovery, signal contract
    - `docs/architecture/current/05-overlay-deep-dive.md` — calibration state machine, sample selection, UI lifecycle
    - `docs/architecture/current/06-one-euro-deep-dive.md` — smoothing, measured response, variance coupling
    - `docs/architecture/current/07-main-deep-dive.md` — orchestration, live pipeline, gate divergence
  - Diagrams: `docs/architecture-diagrams/0{1..7}-*-deep-dive-diagrams.md` — 19 diagrams, 38/38 Mermaid blocks validated
  - Coverage: 7/7 modules; 45 patterns catalogued, all with file-cited code examples; 25 checks executed across 5 modules; unverified claims marked ⚠️ with defined test procedures; **0 code changes made**
- [x] **Defects Raised**: Done — 2026-08-06 (7 defects)
  - Evidence: GitHub Issues [#3–#9](https://github.com/raminmardani/EyeTracker/issues), all added to Project 4
  - Labels: `bug` + `severity:high` (#3–#6), `severity:medium` (#7, #8), `severity:low` (#9). Priority left unset for the PO
  - Cross-references: #4↔#5 (head pose) and #3↔#6 (Esc-abort path), each stating why they are separate tickets
- [x] **Requirements**: Done — 2026-08-06
  - Evidence: `docs/requirements.md` — 33 FRs across 9 themes, 16 measurable success criteria, 10 failure criteria
  - Path: L (local definition) with all 7 defects folded in and fully traced
  - Reference check: `SPEC/references/` empty — 0 approved documents constrain this specification
- [x] **Target Architecture**: Done — 2026-08-07 (user-approved)
  - Evidence: `docs/architecture/design/02-target-architecture-brownfield.md`
  - Diagrams: `docs/architecture-diagrams/02-target-architecture-diagrams-brownfield.md` — 8 diagrams, **8/8 rendered to SVG** with mermaid-cli 11.16.0 and 0 error markers; 8/8 blocks SHA-256-identical to source
  - Approach: existing layered-pipeline monolith **extended, not replaced**; logical layers enforced by an AST import-direction test rather than a directory restructure
  - Scope: 7 modules Modified, 15 new components, 5 new local artifacts, **no database introduced**, **no new runtime dependency** (`joblib` is a declaration of an existing transitive dependency)
  - Decisions: 17 records, each with ≥2 alternatives; 4 confirmed by the user (head-pose source, config mechanism, profile key, restore gate)
  - Contracts: 1 deliberate breaking change (`CalibrationWindow.finished` → `CalibrationResult`, single internal consumer), explicitly flagged; all others additive
  - Security: profile deserialisation identified as the only new code-execution surface; refuse-before-unpickle ordering, payload digest, and post-unpickle witness verification designed; `skops` considered and deferred with rationale
  - Roles: reconciled against the canonical matrix — **no new roles, no matrix update required**
  - Coverage: 33/33 FRs, 16/16 success criteria, 10/10 failure criteria; 8 requirements-reconciliation items flagged rather than absorbed
  - **0 application source changes** — `main.py`, `eye_tracker/` and `requirements.txt` verified byte-identical
- [x] **Patterns & Standards**: Done — 2026-08-07 (all 11 pattern decisions user-approved)
  - Evidence: `docs/architecture/design/03-patterns-and-standards-brownfield.md` — 16 pattern sections, 1,023 lines
  - Every pattern marked `[Current — kept]` or `[New adoption]`; every `[New adoption]` carries a Migration Note naming its phase
  - DO / DON'T examples for all 16 sections — **29/29 Python examples and the TOML config parse-verified**
  - Comparison basis stated per category: `aire-design-patterns.md` is a JavaScript GoF reference with no logging/config/naming guidance, so those categories draw on `aire-implementation-rulebook.md` and `aire-clean-architecture.md` instead of attributing recommendations to a rulebook that does not make them
  - 2 workflow categories reframed rather than left empty: Database Access → Persistence & File I/O (no database exists), API Response Format → Internal Contract Format (no HTTP/RPC surface)
  - **File/Module Boundary Map** delivered with a 9-entry `shared_files` list — the authoritative input for `files_touched` / `shared_files` in `docs/plans/dependency-graph.yml`
  - Tech debt: TD-1 – TD-6 recorded as debt, not patterns; no duplicated widgets or misplaced generic helpers found
  - **0 application source changes** — analysis and documentation only
- [x] **UI/UX Design**: Done — 2026-08-07 (3 approval gates passed)
  - Evidence: `docs/ui-ux/ui-ux-spec.md` — **681 tokens** (cl100k) / 686 (o200k), under the <700 limit, verified with `tiktoken`
  - Checkpoints: `docs/ui-ux/03-inspiration.md`, `docs/ui-ux/08-visual-foundation.md` · Audit trail: `docs/ui-ux/01-discovery.md`
  - Surfaces designed: `StatusWindow` (new), `CalibrationWindow` and `GazeOverlay` (existing, modified)
  - **Every colour token verified by computing WCAG relative luminance** — not estimated. 3 defaults rejected for failing AAA, including the workflow's own success green
  - Gaze-dot dual outline verified to hold **≥5.32:1 best-edge contrast on any background**, replacing an outline that measures 1.00:1 on a white desktop
  - Platform-aware deviations recorded with reasons: 3-level elevation (no portable Qt drop shadow), 44 pt targets, points not pixels, no breakpoints or grid
  - Accessibility: AAA for owned windows, AA non-text floor for the overlay; keyboard-first with a focus-on-fault rule; 2 limitations recorded rather than glossed
  - **0 application source changes** — design documentation only
- [x] **Build Cycles**: Done — 2026-08-07 (5 cycles, structure user-confirmed as proposed)
  - Evidence:
    - `docs/plans/build-cycles.md` — cycle map, dependency map, FR + defect traceability, 14-item risk log, deviations
    - `docs/plans/builds/cycle-1/cycle-plan.md` — Foundations & Measurement Baseline (M0 + M1)
    - `docs/plans/builds/cycle-2/cycle-plan.md` — Configuration & Head-Pose Truth (M2 + M3)
    - `docs/plans/builds/cycle-3/cycle-plan.md` — Calibration Integrity & Recalibration (M4 + M5)
    - `docs/plans/builds/cycle-4/cycle-plan.md` — No Silent Failures (M6)
    - `docs/plans/builds/cycle-5/cycle-plan.md` — Persistence & Accuracy Delta (M7 + M8)
  - Approach: cycles derived from the architecture's M0 – M8 migration graph, with boundaries placed on hard dependency edges so **neither evidence-forced ordering can be violated by accident** — baseline before the head-pose fix (FR-12), persistence last (FR-18)
  - Coverage: **33/33 FRs** mapped to a cycle · **7/7 defects** mapped · 16/16 success criteria and 10/10 failure criteria reachable
  - Each cycle plan carries: scope with owning files, deferred items **with reasons**, a 4-half-day workshop plan, acceptance criteria traced to numbered success criteria, open items with owners, prerequisites, its `shared_files` list, and a rollback statement
  - Diagram: dependency map **rendered to SVG** with mermaid-cli 11 — `aria-roledescription="flowchart-v2"`, 0 real error markers, 5/5 nodes and 3/3 dotted edge labels present
  - GitHub: `TBD` placeholder **replaced** with 5 Release options on field `PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc`; verified beforehand that all 8 project items had `Release` unset so nothing lost an assignment; 5 draft releases created with **0 git tags pushed**; option IDs written back into every cycle plan
  - Deviations recorded with reasons: vertical slices reframed (no frontend/backend axis exists); Tier 4 and Tier 5 deliberately empty; no dates invented (open item 1)
  - **0 application source changes** — planning documentation only
- [x] **Implementation Plan (CYCLE-1)**: Done — 2026-08-07 (**11 of 11** stories written, all 7 waves, every one gate-passed)
  - Evidence:
    - `docs/plans/implementation-plan.md` — graph mirror, wave summary, workload distribution, `shared_files`, 10 success criteria, 2 epics, 11-story index, quality gates, 7-row risk table, 4 QA Manual Testing Groups
    - `docs/plans/dependency-graph.yml` — 11 stories, 7 waves, 12 requires-edges, 5 `shared_files`, `team_size: 1`, `buildid: CYCLE-1`
    - `docs/plans/stories/` — **11 story files**: 1.1 – 1.6 (Epic 1) and 2.1 – 2.5 (Epic 2)
  - Scope: **CYCLE-1 only** by user choice; numbering `Epic 1 / Story 1.1`; `team_size: 1` so waves are dependency order, not concurrency
  - Graph integrity verified, not assumed: **12 mermaid edges = 12 YAML requires-edges**; diagram rendered with mermaid-cli 11 (`aria-roledescription="flowchart-v2"`, 0 syntax errors); no cycles; every `requires` target exists; `shared_files` cross-checked against every story's `files_touched`
  - Every story passed a **blocking depth gate** before being presented — section completeness, header-vs-graph mirror, single-actor RBAC consistency, QA-branch correctness, response-table depth, AC mirroring, and `ast.parse` / `tomllib.loads` on every embedded code block
  - The gate and hand-prototyping caught **7 real defects** in draft stories, including a cross-story break in 1.4 that would have failed the moment 1.1 landed, and a pytest `ScopeMismatch` in 1.3
  - GitHub: **4 issues created** — [#10](https://github.com/raminmardani/EyeTracker/issues/10) (1.2), [#11](https://github.com/raminmardani/EyeTracker/issues/11) (1.1), [#12](https://github.com/raminmardani/EyeTracker/issues/12) (1.3), [#13](https://github.com/raminmardani/EyeTracker/issues/13) (1.5) — each labelled `story` + `epic:1` + `cycle:1` + `wave:N`, milestoned, added to Project 4, `Release = CYCLE-1` (option `cd228d8a`), with issue numbers written back into both the story files and the graph
  - Bodies pushed via `--body-file` after inline heredocs were found to silently truncate at 30–48 KB; every issue verified post-create for required-section parity, not assumed
  - 🔧 The workflow's own GitHub parity check asserts `## QA-observable behaviour` unconditionally while also instructing that the section be omitted when **QA Candidate = No** — made conditional, otherwise 3 of 4 pushes would have "failed" correctly-built issues
  - Stories 2.1 – 2.4 had their code blocks **assembled and executed** before shipping, against real `numpy` 2.5.1, the real `eye_tracker/gaze.py` feature indices and this repository's real git state: **25**, **33** and **20** test cases pass, plus a full end-to-end report render through all four modules. Every manual perturbation was run to confirm the suites are calibrated rather than merely green
  - **Execution found three real defects** the depth gate could not: 2.2's normalising JSON round trip (now AC 18a), 2.3's off-by-one dwell boundary under accumulated time (now AC 20a), and 2.4 truncating `.gitignore` to `gitignore` via `strip()` on porcelain output (now AC 8a)
  - **Two scope corrections** recorded rather than absorbed: Story 2.5's `files_touched` was unbuildable (no story presented targets on screen) and Story 2.2 had nowhere to record the scored signal
  - All 11 Flow Diagrams **rendered to SVG** with mermaid-cli 11 — `aria-roledescription="flowchart-v2"`, 0 syntax errors
  - Graph re-verified after authoring: `requires`/`enables` mirrored both ways, every dependency in an earlier wave, wave membership matching every story's `wave` field, and `shared_files` discipline holding
  - **Not delivered**: GitHub issues for **1.4, 1.6 and 2.1 – 2.5**; the `epic:2` and `wave:3`–`wave:7` labels and the Epic 2 milestone; refreshed bodies for the locally-edited **#10** and **#12**
  - **0 application source changes** — planning documentation only

---

## Upcoming

1. **`aire-dev-implement 1.2`** *(next)* — the only wave-1 story and the sole entry point: nothing else in the graph can run before it. It rebuilds `.venv/`, so it is also **the fix for blocker B-1**, and it lands the packaging metadata, ruff/pytest/coverage configuration and the `max-statements = 30` setting that every later story's quality gate depends on. Issue [#10](https://github.com/raminmardani/EyeTracker/issues/10)
2. **Second GitHub push pass** — create the `epic:2` and `wave:3` – `wave:7` labels and the Epic 2 milestone, then push stories **1.4**, **1.6** and **2.1 – 2.5**, writing each issue number back into the story file and `dependency-graph.yml`. ⚠️ Also **refresh #10 and #12**, whose bodies are stale after local edits. The push script and its guardrails are already written and proven against 4 issues
3. **Two architecture-owner items surfaced while authoring Epic 2**: (a) 🔴 **FR-8's ≥15-usable rule makes the default nine-target grid impossible to calibrate** — `main.py` passes 25 so the shipped path is fine, but `AppController` and `CalibrationWindow` both default to 9, so once FR-8 lands at M5 the default construction always refuses; and "≥60% of *requested*" must be defined against the **resolved** count, since requesting 30 presents 25. (b) The `main.py:87-126` live-chain **duplication** in Story 2.5's session tool, which must be deleted when DR-6 extracts `LivePipeline` at M6
4. **Requirements owner ratification — 11 items**, up from 9. The 9 previously flagged (chiefly proposed **FR-19a**, screen geometry in the profile key), plus two surfaced by cycle planning:
   - 🔴 **The FR-8 coverage-rule substitution.** FR-8's stated basis — "justified against the largest feature subset (currently 25 inputs)" — is **arithmetically unsatisfiable**: the binocular Y subset has 25 columns and the grid yields at most 25 targets. The architecture substitutes `≥15 usable AND ≥3 rows AND ≥3 cols AND ≥60% of requested`. Needed by **Cycle 3 Day 4**
   - The `CalibrationWindow.finished` → `CalibrationResult` breaking contract change. Needed by **Cycle 3 Day 2**
5. 🔴 **Settle the evaluation protocol** (open item 3) — seating distance, lighting, target count, session count. Needed by **Cycle 1 Day 3** or Day 4's baseline is not reproducible, FR-11 fails, and Cycle 5's delta has no valid comparison basis
6. **Schedule the two human-gated days.** Cycle 1 Day 4 and Cycle 5 Day 4 both need a person, a webcam and controlled lighting. Neither is a build step, neither can be compressed, and both must use the **identical** protocol or success criterion 7 is unverifiable
7. **Supply a target completion date** (open item 1) — the cycles are sequenced by dependency and ready to be dated. With 5 cycles and only 3 existing sprints, more iterations are needed on the GitHub project
8. **Revisit when dwell-click is scoped** — recovery actions currently require mouse or keyboard input from an audience defined as unable to use a mouse. Recorded as a limitation of the signal-only scope, not a UI defect. **Cycle 5's delta report is the evidence that decision was waiting for**, since the signal-only scope was justified by "binding actions to an unmeasured signal is unsafe"

---

## Blockers

| ID | Description | Owner | Opened | Status | Recorded |
|----|-------------|-------|--------|--------|----------|
| B-1 | 🔴 **`.venv/` has no `Scripts/python.exe` and no `pyvenv.cfg`** — it cannot be activated, so no test runner can execute. Blocks **implementation**, not planning. **Now owned by Story 1.2** (issue #10), the single wave-1 story — clearing it is the first act of implementation. Requirements open item 6 | Dev | 2026-08-06 | 🔴 Blocked | 2026-08-07 17:38 |
| B-2 | ⚠️ **Evaluation protocol unspecified** — seating distance, lighting, target count and session count are undefined, so Cycle 1's baseline would not be reproducible and Cycle 5's delta would have no valid comparison basis. Requirements open item 3. **Story 2.2 is written to record this protocol, not to invent it** — it needs the answer as an input | Requirements owner | 2026-08-06 | 🔴 Blocked | 2026-08-07 17:38 |
| B-3 | ✅ **RESOLVED 2026-08-07** — all 11 story files now exist and pass the depth gate. Story authoring is no longer a gate on anything; what remains is the GitHub push pass, which blocks tracker visibility rather than implementation | Product owner | 2026-08-07 | ✅ Done | 2026-08-07 19:03 |

> Neither open blocker gates the **next** action. B-1 is cleared *by* the next action — Story 1.2 rebuilds `.venv/`. **B-3 is resolved**: all 11 stories exist, so dev can implement any wave in dependency order.
>
> 🔧 **B-2 now has exactly one bite, and it is enforced in code.** Stories 2.2 and 2.4 were built so the block is *visible*: every owner-supplied protocol value is a machine-detectable placeholder (`unresolved_placeholders()`), and every report prints the sections still blank. Story 2.5's tool then **refuses to record a baseline while any placeholder remains** — checked before the window opens, so a doomed 72-second session is never performed on a person. B-2 blocks the CYCLE-1 *baseline*, and nothing else. Overall Status remains 🟢 ON TRACK on that basis; it turns 🔴 if wave 7 is reached with B-2 still open, because the cycle's stated outcome is the baseline.

---

## Agent Activity

| Agent | Last Action | Status | Updated | Recorded |
|-------|------------|--------|---------|----------|
| AIRE_INITIALIZER | GitHub Projects tracking bootstrapped | Idle | 2026-08-06 | 2026-08-06 18:25 |
| AIRE_ARCHITECT | Patterns & standards approved — 16 sections, 6 tech-debt items, boundary map delivered | Idle | 2026-08-07 | 2026-08-07 12:18 |
| AIRE_QA | Raised 7 defects to GitHub Issues (#3–#9), all added to Project 4 | Idle | 2026-08-06 | 2026-08-06 19:52 |
| AIRE_ANALYST_PM | Requirements complete — 33 FRs, 16 success criteria, 7/7 defects traced | Idle | 2026-08-06 | 2026-08-06 20:44 |
| AIRE_UI_UX_DESIGNER | UI/UX spec approved — 3 gates passed, 681 tokens, contrast audit complete | Idle | 2026-08-07 | 2026-08-07 13:43 |
| AIRE_BUILD_CYCLE_PLANNER | Build cycles complete — 5 cycles, 33/33 FRs mapped, GitHub Release options created, 14 risks logged | Idle | 2026-08-07 | 2026-08-07 14:58 |
| AIRE_PRODUCT_OWNER | Implementation plan complete — **11/11 stories authored** across 7 waves, all gate-passed, 4 pushed as #10–#13; 3 execution-found defects and 2 scope corrections recorded | Idle | 2026-08-07 | 2026-08-07 19:03 |
| AIRE_DEV | — | Standby | — | 2026-08-06 14:57 |
| AIRE_REVIEWER | — | Standby | — | 2026-08-06 14:57 |

---

## Project Tracking

**Tracking**: GitHub Projects
**Repo**: https://github.com/raminmardani/EyeTracker
**Project**: https://github.com/users/raminmardani/projects/4
**Project Number**: 4
**Project Node ID**: PVT_kwHOA3gd_c4Bfno8
**Priority Field ID**: PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZY
**Story Points Field ID**: PVTF_lAHOA3gd_c4Bfno8zhZ5RZU
**Sprint Field ID**: PVTIF_lAHOA3gd_c4Bfno8zhZ5R4I
**Release Field ID**: PVTSSF_lAHOA3gd_c4Bfno8zhZ5RZc
**Status Field ID**: PVTSSF_lAHOA3gd_c4Bfno8zhZ5Qpg

**Notes for downstream workflows**:
- Owner is a **user account**, not an org — use `--owner raminmardani` and note that project URLs are `/users/…`, not `/orgs/…`.
- **Release** now holds **5 options, one per build cycle** — the `TBD` placeholder was replaced on 2026-08-07 (`gh project field-create` rejects an empty option list for `SINGLE_SELECT`, and `singleSelectOptions` replaces the whole list rather than appending). CYCLE-1's option ID is `cd228d8a`; the other four are recorded in each `docs/plans/builds/cycle-N/cycle-plan.md`.
- **Story issues use `--body-file`, never an inline body.** Inline heredocs were observed to silently truncate bodies at 30–48 KB, producing an issue that looks created but is missing sections. Verify required-section parity after every create.
- **Labels that exist**: `story`, `epic:1`, `cycle:1`, `wave:1`, `wave:2`. `epic:2` and `wave:3` – `wave:7` **do not exist yet** and must be created before pushing stories 1.4, 1.6 or 2.1 – 2.5. Milestone `Epic 1: Test & Packaging Foundation` exists; the Epic 2 milestone does not.
- **Pass milestones by title, not by number** — `gh issue create --milestone` takes the title string.
- **Sprint** iterations already exist: Sprint 1 (2026-08-06), Sprint 2 (2026-08-20), Sprint 3 (2026-09-03), 14 days each.
- Branch protection on `main` was **deliberately skipped** (solo repo — a required approving review would block self-merges). Re-run Step I of `aire-project-kickoff` if collaborators are added.
- `UpdateProjectV2FieldInput` no longer accepts `projectId` — pass only `fieldId` and `singleSelectOptions`. `iterationConfiguration` requires a non-empty `iterations` array with `title`, `startDate`, `duration`.
