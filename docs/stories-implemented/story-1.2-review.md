# Story 1.2 Self-Review

**Date**: 2026-08-09
**Story**: Packaging metadata, tool configuration and a rebuilt development environment
**Developer**: DEV Agent (STORY-AGENT)
**Branch**: `feat/story-1.2-packaging`
**Story file**: `docs/plans/stories/epic-1-story-1.2-Packaging-And-Environment.md`

---

## What Was Implemented

- **`.venv/` rebuilt from scratch** (requirements open item 6 closed). The previous tree had
  `Lib/site-packages` and stale dependency console scripts but **no `python.exe` and no
  `pyvenv.cfg`** — not a virtual environment at all. Renamed to `.venv.broken`, recreated with
  `C:\Python314\python.exe -m venv .venv`, proven, then the old tree was deleted.
- **`pyproject.toml` created** — the single substantive artifact. Carries packaging metadata
  (`[build-system]`, `[project]`, `dev` extra, `py-modules`, `packages.find`), ruff lint config
  with a fully-owned per-file-ignores allowlist, ruff format scoping, pytest config and coverage
  config.
- **FR-26 satisfied**: `eye_tracker` and `main` import from any directory with `PYTHONPATH`
  cleared, via an editable install — no `sys.path` hack, no per-machine environment variable.
- **FR-27 wired (not enforced)**: coverage runs over both `eye_tracker` **and** `main`;
  `--cov-fail-under` is deliberately absent with CYCLE-5 named as its owner.
- **`docs/development.md` created** — the end-to-end rebuild runbook, Windows + POSIX, with a
  four-part verification block and four troubleshooting entries. Validated by execution, not by
  reading.
- **`tests/arch/test_packaging.py` created** — two tests guarding the FR-26 invariant against a
  future `sys.path` shortcut.
- **Zero application source modification.** `main.py` and all seven files under `eye_tracker/`
  are byte-identical to their pre-story state (blob-hash verified, not just `git diff`).

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `pyproject.toml` | New | Packaging metadata + ruff lint/format + pytest + coverage config (149 lines) |
| `docs/development.md` | New | Environment rebuild runbook: prerequisites, Windows/POSIX commands, verification block, troubleshooting |
| `tests/arch/test_packaging.py` | New | Two packaging-invariant tests (FR-26 import probe; no-`sys.path`-manipulation guard) |
| `.venv/` | Rebuilt | Not version-controlled. Now contains `Scripts/python.exe` + `pyvenv.cfg` and all 6 runtime deps + 4 dev tools |
| `requirements.txt` | **Unchanged** | AC22 — byte-identical, blob `79ec83e3…` before and after |
| `main.py`, `eye_tracker/**` | **Unchanged** | AC20 — byte-identical, all 8 blob hashes match HEAD |
| `.gitignore` | **Unchanged** | AC21 is a verification, not a change — `.venv/` already covered at line 18 |

## Patterns Applied

| Pattern | Where Applied | Notes |
|---------|---------------|-------|
| **Lint & Format Tooling** (patterns §13) | `pyproject.toml:54-59` | ruff for both; `line-length = 100`, `target-version = "py314"`, the 13-entry `select` list verbatim |
| **Function & File Length** (patterns §14) | `pyproject.toml:61-65, 84-85` | `max-statements = 30` so `PLR0915` actually bites; the one function it catches (`CalibrationWindow.__init__`) is the exact Qt-widget-`__init__` case §14 allowlists, with its reason in the comment |
| **Documentation Standards** (patterns §16) | `pyproject.toml:67-107, 109-133` | Every suppression states a reason **and** names the cycle that removes it. Every deferral says what would settle it |
| **Bounded dependency declarations** (patterns §1) | `pyproject.toml:24-39` | Explicit floor + major ceiling + reason comment. `dev` extra follows the identical convention; dev tooling stays out of `requirements.txt` |
| **Layer declaration** (patterns §1) | `tests/arch/test_packaging.py:1-4` | Module docstring declares `Layer: test`. No layer declaration was added to any existing module — §12 applies to new and touched code, and nothing existing was touched |
| **Behavioural test naming** (patterns §15) | `tests/arch/test_packaging.py:12,29` | `test_eye_tracker_and_main_import_without_path_manipulation`, `test_no_test_file_manipulates_sys_path` — names state behaviour, AAA structure, one behaviour each |
| **Error class / logging convention** | *Deliberately not applied* | This story adds no runtime code path; no `EyeTrackerError` subclass and no logger were introduced |

## Testing Summary

- **Unit Tests**: 2 written, 2 passing (architecture/packaging invariants)
- **Integration Tests**: 0 — this story adds no runtime collaboration to integrate
- **Total**: **2 passed / 2 total, 100% pass rate**
- **Coverage**: **0.00%** over 651 statements

### On the coverage figure — read this before treating it as a failure

**0% is the correct and honest number.** This story adds **zero new production Python**. Its
deliverables are one TOML file, one Markdown runbook and one test module. The 651 statements in
the coverage table are the *pre-existing* application modules, which this story is forbidden from
touching (AC20) and forbidden from testing (`tests/conftest.py` and the unit/integration/
regression/invariants suites are explicitly Story 1.3's and later). There is no new production
line for a test to cover.

Inflating this number would have required writing tests against legacy modules that belong to
other stories — which would have imported them, changed the coverage denominator, and produced a
figure that measured someone else's work. The ≥85% gate is FR-27's, and the story explicitly
defers its enforcement to CYCLE-5 (`pyproject.toml:137-140`).

What this story *does* prove about coverage is the **wiring**: the table below shows coverage
successfully attaching to `eye_tracker` (7 modules discovered and measured) — which was impossible
before this story, because no test runner could be invoked at all.

**Test Output** (`pytest`, from the repository root, in the rebuilt `.venv`):

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-8.4.2, pluggy-1.6.0
PyQt6 6.11.0 -- Qt runtime 6.11.1 -- Qt compiled 6.11.0
rootdir: C:\Users\ramin.mardani\Documents\EyeTracker
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0, qt-4.5.0
collected 2 items

tests\arch\test_packaging.py ..                                          [100%]

=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.6-final-0 _______________

Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
eye_tracker\__init__.py          0      0   100%
eye_tracker\calibration.py      84     84     0%   2-257
eye_tracker\face_mesh.py       108    108     0%   2-184
eye_tracker\gaze.py            104    104     0%   2-173
eye_tracker\one_euro.py         45     45     0%   6-63
eye_tracker\overlay.py         185    185     0%   2-267
eye_tracker\tracker.py         125    125     0%   2-171
----------------------------------------------------------
TOTAL                          651    651     0%
============================== 2 passed in 2.45s ==============================
EXIT=0
```

### TDD evidence — the test was written first and observed failing

Before `pyproject.toml` existed, with only `pytest` installed:

```
    result = subprocess.run(
        [sys.executable, "-c", "import eye_tracker, main; print('ok')"],
        cwd=tmp_path,
        env={**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}},
        ...
    )
>       assert result.returncode == 0, result.stderr
E       AssertionError: Traceback (most recent call last):
E           File "<string>", line 1, in <module>
E             import eye_tracker, main; print('ok')
E         ModuleNotFoundError: No module named 'eye_tracker'
E
E       assert 1 == 0

tests\arch\test_packaging.py:25: AssertionError
=========================== short test summary info ===========================
FAILED tests/arch/test_packaging.py::test_eye_tracker_and_main_import_without_path_manipulation
========================= 1 failed, 1 passed in 0.19s =========================
EXIT=1
```

This is precisely the "Same import **before** the editable install" row of the story's
system-response table, observed rather than assumed. RED → implement → GREEN.

---

## DoD Evidence

### Gate 1 — Spec Echo

#### 1a. Acceptance Criteria — 23 rows for 23 AC (AC 1–22 plus AC 4a)

| AC | Requirement | Proof |
|----|-------------|-------|
| 1 | `[build-system]` with `setuptools>=77` and `wheel` | `pyproject.toml:1-3` — `requires = ["setuptools>=77", "wheel"]`, `build-backend = "setuptools.build_meta"`. Proven functional: `Building editable for eye-tracker (pyproject.toml): finished with status 'done'` |
| 2 | `[project]` name / version / `requires-python` / mirrored deps | `pyproject.toml:6` `name = "eye-tracker"`, `:7` `version = "0.1.0"`, `:18` `requires-python = ">=3.14"`, `:24-31` deps. Mirror verified pin-by-pin in **Gate 3 table A** — all 6 floors and 6 ceilings identical to `requirements.txt` |
| 3 | `dev` extra: pytest, pytest-cov, pytest-qt, ruff, each bounded | `pyproject.toml:33-39`. Installed: `pytest-8.4.2 pytest-cov-7.1.0 pytest-qt-4.5.0 ruff-0.16.2` — every one inside its declared band (**Gate 3 table B**) |
| 4 | `py-modules = ["main"]` + `packages.find include = ["eye_tracker*"]` (discovery, not a list) | `pyproject.toml:44` and `:52`. Both proven by the built wheel in **AC 4a** below |
| 4a | `import eye_tracker.tools, eye_tracker.evaluation` fails now, must succeed later with **no pyproject change** | **Fails now** (expected): `ModuleNotFoundError: No module named 'eye_tracker.tools'`, exit 1. **Will succeed later**, proven constructively: the *unmodified shipped* `pyproject.toml` was copied to a scratch tree containing the two future subpackages and built — wheel contents: `eye_tracker/__init__.py`, `eye_tracker/evaluation/__init__.py`, `eye_tracker/tools/__init__.py`, `main.py`. The glob covers them; an explicit `packages = ["eye_tracker"]` would not |
| 5 | `pip install -e ".[dev]"` succeeds in a fresh `.venv/` | `Successfully installed colorama-0.4.6 coverage-7.15.4 eye-tracker-0.1.0 iniconfig-2.3.0 pluggy-1.6.0 pygments-2.20.0 pytest-8.4.2 pytest-cov-7.1.0 pytest-qt-4.5.0 ruff-0.16.2 typing_extensions-4.16.0` — run inside the venv created during the AC19 walkthrough. Idempotent repeat also exit 0 |
| 6 | `import eye_tracker, main` from a non-root cwd, `PYTHONPATH` unset | `cd /tmp && env -u PYTHONPATH python -c "import eye_tracker, main; print('FR-26 OK', eye_tracker.__file__)"` → `FR-26 OK C:\Users\ramin.mardani\Documents\EyeTracker\eye_tracker\__init__.py`, exit 0. Also asserted in a subprocess by `tests/arch/test_packaging.py:12` |
| 7 | No `sys.path` manipulation in any test file or `conftest.py` | `grep -rnE "sys\.path\.(append\|insert)" tests/` → **no output, rc=1**. `find tests -name conftest.py` → empty (none exists). Also permanently asserted by `tests/arch/test_packaging.py:29` |
| 8 | `line-length = 100`, `target-version = "py314"` | `pyproject.toml:55` and `:56`, verbatim per patterns §13 (`03-patterns-and-standards-brownfield.md:746-748`) |
| 9 | `select` is exactly the 13-entry patterns §13 list | `pyproject.toml:59` — `["E","F","W","I","B","UP","SIM","RET","PTH","NPY","T20","PLR0915","RUF"]`. Character-identical to `03-patterns-and-standards-brownfield.md:751` |
| 10 | `max-statements = 30` | `pyproject.toml:65`, with the reason at `:62-64`. Measured effect proven in **Gate 3 table D**: 50 → 30 findings/10 rules (PLR0915 inert); 30 → 31 findings/11 rules (PLR0915 fires once, `overlay.py:86`) |
| 11 | One `per-file-ignores` entry per pre-existing finding class, each with a reason + named removal owner | `pyproject.toml:67-107`. All 17 rule-entries carry both. 1:1 correspondence with the 31 real findings verified in **Gate 3 table C** — no unowned suppression and **no inert entry** |
| 12 | `ruff check .` exits 0 | `All checks passed!` — `rc=0` (ruff 0.16.2) |
| 13 | `ruff format --check` exits 0 for its configured paths | `ruff format --check .` → `2 files already formatted`, `rc=0`, run from the repo root. See **Deviation 1** for the `*.md` exclusion this required |
| 14 | `testpaths`, `qt_api = "pyqt6"`, `addopts` with coverage over both targets + term-missing | `pyproject.toml:135` `testpaths = ["tests"]`, `:136` `qt_api = "pyqt6"` (DR-17), `:141` `addopts = "--cov=eye_tracker --cov=main --cov-report=term-missing"`. Confirmed live: pytest header shows `configfile: pyproject.toml`, `testpaths: tests`, `plugins: cov-7.1.0, qt-4.5.0` |
| 15 | `--cov-fail-under` **absent**, with a comment naming CYCLE-5 | `grep -nE "^[^#]*cov-fail-under" pyproject.toml` → **no output, rc=1** (present only inside the explanatory comment). Owner named at `pyproject.toml:139-140`: "switched on in CYCLE-5 (Story for FR-27 close-out)" |
| 16 | `[tool.coverage.run]` omits `tests/*`; `[tool.coverage.report]` shows missing lines | `pyproject.toml:145` `omit = ["tests/*"]`, `:148` `show_missing = true`. Confirmed live: the coverage table has a populated `Missing` column and lists no `tests\` row |
| 17 | `.venv/` has `Scripts/python.exe` **and** `pyvenv.cfg`; 6 runtime deps import | `ls .venv/Scripts/python.exe .venv/pyvenv.cfg` → both listed. `python -c "import cv2, mediapipe, numpy, sklearn, PyQt6; print('ok')"` → `ok`. `sys.prefix` → `C:\Users\ramin.mardani\Documents\EyeTracker\.venv` |
| 18 | `docs/development.md` documents prerequisites, Windows+POSIX commands, verification, interpreter-failure recovery | `docs/development.md` — §1 prerequisites incl. the verified 3.14.6 (`:17-40`), §2 create with both shells (`:42-89`), §3 activate + `sys.prefix` (`:91-125`), §4 install (`:127-152`), §5 four-part verification (`:154-247`), §7 cleanup (`:260-280`), Troubleshooting (a)-(d) (`:282-375`). Interpreter-failure recovery is (a) at `:284` |
| 19 | The guide is verified **by executing it** | Full transcript in **Gate 1c** below. `.venv` renamed to `.venv.proven`, the document followed verbatim from the top, environment rebuilt, all four §5 checks green. No step required knowledge absent from the document |
| 20 | 🔴 Zero application source modification | `git diff --stat -- main.py eye_tracker/` → **empty**. `git diff HEAD --stat` → **empty**. Stronger: all 8 blob hashes identical to HEAD (**Gate 2 check N1**) |
| 21 | `.venv/` not staged, still gitignored | `git status --porcelain \| grep -c "\.venv"` → **0**. `git check-ignore -v .venv/pyvenv.cfg` → `.gitignore:18:.venv/` |
| 22 | `requirements.txt` unchanged; dev tooling in the extra, not here | `git diff --stat -- requirements.txt` → empty. HEAD blob `79ec83e3a5efbdb66de7769d25b25149ec41a06f` == worktree blob `79ec83e3a5efbdb66de7769d25b25149ec41a06f`. `pytest`/`ruff` appear only in `pyproject.toml:33-39` |

**AC row count = 23. Story AC count = 23 (1–22 plus 4a). Gate 1a PASSES.**

#### 1b. Numbered Steps — 9 rows for 9 Steps

| Step | Requirement | Proof |
|------|-------------|-------|
| 1 | Verify base interpreter; **rename** (not create over) `.venv`; confirm both artifacts; confirm `sys.prefix` | `python --version` → `Python 3.14.6`; `C:/Python314/python.exe --version` → `Python 3.14.6`. `mv .venv .venv.broken` → `renamed ok`. `python -m venv .venv` → rc 0. Both `.venv/Scripts/python.exe` and `.venv/pyvenv.cfg` listed; `pyvenv.cfg` contents show `home = C:\Python314`, `version = 3.14.6`. `sys.prefix` → inside `.venv` |
| 2 | Write `pyproject.toml` packaging tables, mirroring `requirements.txt` | `pyproject.toml:1-52`. Mirror verified pin-by-pin in **Gate 3 table A**. Comments explaining `requires-python`, opencv major alignment and the `packages.find` glob are retained at `:9-17`, `:20-23`, `:47-51` |
| 3 | Ruff config + measurement-derived per-file-ignores; drop the inert `gaze.py PLR0915`; prove the gate still bites | `pyproject.toml:54-107`. `gaze.py` entry is `["F401","SIM108"]` (`:92-97`) — **no PLR0915**, because it exempts nothing (**Gate 3 table D**). Gate-bites probe: `printf 'print("probe")\n' > _probe.py; ruff check _probe.py` → `T201 \`print\` found ... Found 1 error.` **exit 1**; `_probe.py` then removed (`ls _probe.py` → No such file) |
| 4 | pytest + coverage config; threshold deliberately absent | `pyproject.toml:134-149`. `--cov-fail-under` absent (AC15 evidence). CYCLE-5 named at `:139-140` |
| 5 | Scope the formatter; record the deferral; flag the sweep alternative to the plan owner | `pyproject.toml:109-133`. All 7 legacy `.py` excluded plus `*.md` (**Deviation 1**). Deferral reason recorded at `:110-114`; the `*.md` rationale, marked **Permanent**, at `:116-122`. Plan-owner flag raised in **Next Steps** below. Sweep verifiably *not* performed: `ruff format --check main.py eye_tracker/ --config 'format.exclude=[]'` → `7 files would be reformatted, 1 file already formatted` |
| 6 | `pip install --upgrade pip`; `-r requirements.txt`; `-e ".[dev]"`; FR-26 probe from non-root; repeatable | `Successfully installed pip-26.2.1`; all 6 runtime pins + transitives installed; editable install rc 0. FR-26 probe → `FR-26 OK …\eye_tracker\__init__.py`. **Idempotent repeat**: second `pip install -e ".[dev]"` → `Successfully installed eye-tracker-0.1.0`, rc 0 |
| 7 | Write `docs/development.md` with all 8 named contents + troubleshooting (a)(b)(c) | Written; per-section citations in AC18 above. Troubleshooting (a) `:284`, (b) `:317`, (c) `:331`, plus (d) `:360` added from a real encountered failure (**Challenge 2**) |
| 8 | Prove the guide by executing it from a renamed `.venv/` | **Gate 1c** transcript. `mv .venv .venv.proven` → `ls -d .venv` → *No such file or directory*, then the guide followed verbatim to a working environment |
| 9 | Assert zero source modification; assert nothing under `.venv` staged; remove `.venv.broken` / `.venv.proven` | `git diff --stat -- main.py eye_tracker/` empty; `git status --porcelain \| grep -c "\.venv"` → `0`; `rm -rf .venv.broken .venv.proven` → `ls -d .venv*` returns **only** `.venv`. Order respected: `.venv.broken` was deleted only *after* the replacement passed every check |

#### 1c. AC19 / Step 8 — the executed walk-through transcript

```
$ mv .venv .venv.proven
working env set aside as .venv.proven
$ ls -d .venv
ls: cannot access '.venv': No such file or directory

=== GUIDE §1: prerequisites ===
$ python --version
Python 3.14.6

=== GUIDE §2: create (Git Bash variant, verbatim) ===
$ [ -d .venv ] && mv .venv .venv.broken ; python -m venv .venv
venv rc=0
$ ls .venv/Scripts/python.exe .venv/pyvenv.cfg
.venv/Scripts/python.exe
.venv/pyvenv.cfg

=== GUIDE §3: activate + sys.prefix check (verbatim) ===
$ source .venv/Scripts/activate
$ python -c "import sys; print(sys.prefix); print(sys.version)"
C:\Users\ramin.mardani\Documents\EyeTracker\.venv
3.14.6 (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)]

=== GUIDE §4: install (verbatim) ===
$ python -m pip install --upgrade pip
Successfully installed pip-26.2.1
$ python -m pip install -r requirements.txt
Successfully installed PyQt6-6.11.0 PyQt6-Qt6-6.11.1 PyQt6-sip-13.12.0 absl-py-2.5.0
certifi-2026.7.22 cffi-2.1.1 contourpy-1.3.3 cycler-0.12.1 flatbuffers-25.12.19
fonttools-4.63.0 joblib-1.5.3 kiwisolver-1.5.0 matplotlib-3.11.1 mediapipe-0.10.35
narwhals-2.24.0 numpy-2.5.2 opencv-contrib-python-4.14.0.94 opencv-python-4.14.0.94
packaging-26.3 pillow-12.3.0 pycparser-3.0 pyparsing-3.3.2 python-dateutil-2.9.0.post0
scikit-learn-1.9.0 scipy-1.18.0 six-1.17.0 sounddevice-0.5.5 threadpoolctl-3.6.0
$ python -m pip install -e ".[dev]"
Successfully installed colorama-0.4.6 coverage-7.15.4 eye-tracker-0.1.0 iniconfig-2.3.0
pluggy-1.6.0 pygments-2.20.0 pytest-8.4.2 pytest-cov-7.1.0 pytest-qt-4.5.0 ruff-0.16.2
typing_extensions-4.16.0

=== GUIDE 5.1 ===
$ python -c "import cv2, mediapipe, numpy, sklearn, PyQt6; print('ok')"
ok

=== GUIDE 5.2 (Git Bash variant, verbatim) ===
$ cd /tmp && env -u PYTHONPATH python -c "import eye_tracker, main; print('import OK', eye_tracker.__file__)"
import OK C:\Users\ramin.mardani\Documents\EyeTracker\eye_tracker\__init__.py

=== GUIDE 5.3 ===
$ ruff check .
All checks passed!
ruff check rc=0
$ ruff format --check .
2 files already formatted
ruff format rc=0

=== GUIDE 5.4 ===
$ pytest
TOTAL                          651    651     0%
============================== 2 passed in 2.12s ==============================
pytest rc=0
```

**No step required knowledge that is not in the document.** The document was amended once
*before* this run, adding Troubleshooting (d), after a real transient-network failure during the
first install attempt (**Challenge 2**) — so the runbook covers a failure mode that was actually
encountered rather than an imagined one.

#### 1d. Manual verification matrix — all 12 commands

| # | Command | Expected | Actual | ✓ |
|---|---------|----------|--------|---|
| 1 | `python --version` | `3.14.x` | `Python 3.14.6` | ✅ |
| 2 | `ls .venv/Scripts/python.exe .venv/pyvenv.cfg` | both present | both listed | ✅ |
| 3 | `python -c "import sys; print(sys.prefix)"` | path inside `.venv` | `C:\Users\ramin.mardani\Documents\EyeTracker\.venv` | ✅ |
| 4 | `python -c "import cv2, mediapipe, numpy, sklearn, PyQt6; print('ok')"` | `ok` | `ok` | ✅ |
| 5 | `cd /tmp && PYTHONPATH= python -c "import eye_tracker, main"` | exit 0 | `FR-26 OK`, exit 0 | ✅ |
| 6 | `ruff check .` | `All checks passed!`, exit 0 | `All checks passed!` rc=0 | ✅ |
| 7 | `ruff check _probe.py` (new file with `print()`) | **exit 1**, `T201` | `T201 \`print\` found … Found 1 error.` **exit 1** | ✅ |
| 8 | `ruff format --check` | exit 0 | `2 files already formatted` rc=0 | ✅ |
| 9 | `pytest` | exit 5 before 1.3, **or** exit 0 with `tests/arch/test_packaging.py` collected | exit 0, `test_packaging.py` collected, **2 passed**. Exit-5 branch separately verified: `pytest --override-ini="testpaths=<empty dir>"` → `no tests ran`, **rc=5** | ✅ |
| 10 | `git diff --stat -- main.py eye_tracker/` | empty | empty | ✅ |
| 11 | `python main.py` | app starts, behaves as before | Launched bounded (25 s) under `QT_QPA_PLATFORM=offscreen` so it could not seize the display: **exit 124** = still alive when the timer fired ⇒ `QApplication.exec()` entered and held the event loop, no crash, no stderr. Behavioural identity is guaranteed structurally by AC20 byte-identity, not inferred from the run | ✅ |
| 12 | Full `docs/development.md` walk-through from a renamed `.venv/` | working environment | Transcript in **Gate 1c**, all checks green | ✅ |

#### 1e. Reference requirements

| Reference | Requirement | Proof |
|-----------|-------------|-------|
| `docs/requirements.md:148` | **FR-26** — packaging metadata so `eye_tracker` imports from a test dir without `PYTHONPATH` manipulation | `pyproject.toml` exists; AC6 probe green; AC7 grep clean; guarded permanently by `tests/arch/test_packaging.py` |
| `docs/requirements.md:149` | **FR-27** — suite must reach ≥85% across `eye_tracker/` **and** `main.py` | *Wired, not met, correctly.* Both targets are in `--cov` (`pyproject.toml:141`) and `[tool.coverage.run] source` (`:144`). The threshold is CYCLE-5's (`:139-140`); this story's scope is the precondition |
| `docs/requirements.md:314` | **Open item 6** — `.venv/` rebuild; no test runner can execute | **Closed.** `pytest` executes and collects (`rc=0`, 2 passed). `.venv/Scripts/python.exe` + `pyvenv.cfg` both present |
| `docs/requirements.md:211` | Technical constraint — Python 3.14.6 + bounded set; opencv-contrib major-aligned with opencv-python | `requires-python = ">=3.14"` (`:18`); both opencv packages `>=4.8,<5` (`:25-26`); resolved identically: `opencv-python-4.14.0.94` and `opencv-contrib-python-4.14.0.94` |
| `docs/requirements.md:210` | Tests location `tests/` — blocked on FR-26 | `tests/arch/test_packaging.py` now exists and runs. `testpaths = ["tests"]` (`:135`) |
| `docs/requirements.md:215` | Environment must be rebuilt before FR-27 can run | Rebuilt and proven twice (initial + AC19 walkthrough) |
| `02-target-architecture…:909-911` | **DR-5** — `main.py` becomes a shim; the `conftest.py` `sys.path` hack is explicitly rejected | Shim extraction is **CYCLE-3, correctly not done here** (AC20 forbids it). What this story lands is `py-modules = ["main"]` (`:44`), which makes `main.py` importable and measurable meanwhile. The rejected hack is absent and permanently guarded (AC7) |
| `02-target-architecture…:962-964` | **DR-17** — pytest + pytest-cov + pytest-qt; hence `qt_api` | All three in the `dev` extra (`:35-37`); `qt_api = "pyqt6"` (`:136`). Live confirmation: `plugins: cov-7.1.0, qt-4.5.0` and `PyQt6 6.11.0 -- Qt runtime 6.11.1` in the pytest header |
| `03-patterns…:73` (§1) | Target layout names `pyproject.toml` as NEW for packaging/ruff/pytest/coverage | All four concerns live in the one file (`:1-149`) |
| `03-patterns…:119` (§1) | `requirements.txt` stays the runtime constraint file; dev tooling goes in `[project.optional-dependencies].dev` | `requirements.txt` byte-identical (AC22); dev tooling only at `pyproject.toml:33-39` |
| `03-patterns…:745-760` (§13) | ruff for lint+format, config in pyproject, `line-length=100`, `target-version="py314"`, the exact select list, `tests/* = ["PLR0915"]` | `pyproject.toml:54-59`, `:107`. **One documented departure**: the §13 `gaze.py = ["PLR0915"]` entry is dropped as inert — see **Deviation 2** |
| `03-patterns…:762` (§13) | 🔴 CI runs both `ruff check` and `ruff format --check`; a warning is a failure | Both run, both exit 0, **zero warnings emitted by either** |
| `03-patterns…:791` (§14) | 🔴 Every allowlist entry lives in `pyproject.toml` **with its reason as a comment** | All 17 rule-entries at `:67-107` carry a reason **and** a named removal owner. Zero silent exemptions (**Gate 3 table C**) |
| `03-patterns…:877-885` (§15) | Coverage ≥85% across both targets, enforced by `--cov-fail-under=85` in CI | Deliberately **not** switched on here — the story's AC15 and OUT list both require its absence, with CYCLE-5 named. Recorded, not silent |
| `03-patterns…:891-901` (§16) | A provisional/temporary value says so and says what would settle or remove it | Every suppression and every format exclusion names its removing cycle, or is explicitly marked **Permanent** with the reason (`overlay.py PLR0915` at `:84-85`; `*.md` at `:116-122`) |
| `03-patterns…:980,987` (§18) | `pyproject.toml` and `requirements.txt` are `shared_files` serialisation points | Honoured: this story ran alone against both. `requirements.txt` was treated as read-only |
| `SPEC/references/` | 0 files | Confirmed 0 files — no PRD or design reference constrains this story |

---

### Gate 2 — Negative-Space Check

Every "must NOT" / out-of-scope rule, with a reproducible check and its real output.

| # | Rule that must NOT be violated | Reproducible check | Actual output | Verdict |
|---|-------------------------------|--------------------|---------------|---------|
| **N1** | 🔴 **Zero behavioural change** — `main.py` + `eye_tracker/**` byte-identical | `git diff --stat -- main.py eye_tracker/` ; `git diff HEAD --stat -- main.py eye_tracker/` ; per-file `git rev-parse HEAD:$f` vs `git hash-object $f` | Both diffs **empty**. Hash comparison: `IDENTICAL main.py`, `IDENTICAL eye_tracker/__init__.py`, `IDENTICAL eye_tracker/calibration.py`, `IDENTICAL eye_tracker/face_mesh.py`, `IDENTICAL eye_tracker/gaze.py`, `IDENTICAL eye_tracker/one_euro.py`, `IDENTICAL eye_tracker/overlay.py`, `IDENTICAL eye_tracker/tracker.py` — **8/8** | ✅ PASS |
| **N2** | `requirements.txt` must not be edited; dev tooling must not go in it | `git diff --stat -- requirements.txt` ; blob comparison | Diff empty. HEAD `79ec83e3a5efbdb66de7769d25b25149ec41a06f` == worktree `79ec83e3a5efbdb66de7769d25b25149ec41a06f` | ✅ PASS |
| **N3** | ❌ Fixing any of the legacy lint findings | `ruff check . --statistics --config 'lint.per-file-ignores={}'` — the findings must **still all be there** | `Found 31 errors.` across 11 rules, identical distribution to the pre-story measurement (T201×10, F401×5, E501×3, E702×3, I001×3, SIM105×2, B905, PLR0915, RUF046, SIM108, SIM117 ×1) | ✅ PASS — none fixed |
| **N4** | ❌ A global `ruff format` sweep | `ruff format --check main.py eye_tracker/ --config 'format.exclude=[]'` — legacy files must **still be unformatted** | `7 files would be reformatted, 1 file already formatted` | ✅ PASS — no sweep |
| **N5** | ❌ Enforcing `--cov-fail-under=85` | `grep -nE "^[^#]*cov-fail-under" pyproject.toml` | **no output, rc=1** (appears only inside the explanatory comment at `:137`) | ✅ PASS |
| **N6** | ❌ Migrating the 10 `print()` call sites | `ruff check . --statistics --config 'lint.per-file-ignores={}'` T201 count must still be 10 | `10  T201  [ ] print` | ✅ PASS — all 10 intact |
| **N7** | ❌ Adding module docstrings / `Layer:` to existing modules; `eye_tracker/__init__.py` must stay 0 bytes | `wc -c eye_tracker/__init__.py` ; N1 hash check | `0 eye_tracker/__init__.py`; blob identical to HEAD | ✅ PASS |
| **N8** | ❌ `tests/conftest.py` and the other suite directories (Story 1.3's) | `find tests -name conftest.py` ; `find tests -type f` | conftest: **empty**. Tree: `tests/arch/test_packaging.py` **only** | ✅ PASS |
| **N9** | ❌ Declaring `joblib` | `grep -n joblib pyproject.toml requirements.txt` | no match (it arrives transitively — `joblib-1.5.3` appears in the install log via scikit-learn) | ✅ PASS |
| **N10** | ❌ Removing `.venv.broken` before the new env is proven | Ordering of the session: `.venv.broken` was removed only in Step 9, after AC17/AC19 passed | `rm -rf .venv.broken .venv.proven` ran last; `ls -d .venv*` → `.venv` only | ✅ PASS |
| **N11** | 🔴 **No `sys.path` manipulation** in tests/conftest | `grep -rnE "sys\.path\.(append\|insert)" tests/` | **no output, rc=1**; also permanently asserted by a passing test | ✅ PASS |
| **N12** | 🔴 **No `TODO`/`FIXME`** in delivered code | `grep -rniE "TODO\|FIXME\|XXX\|HACK" pyproject.toml docs/development.md tests/` | **no output, rc=1** | ✅ PASS |
| **N13** | 🔴 **Zero secrets** | `grep -rniE "(api[_-]?key\|secret\|token\|passwd\|password\|credential\|BEGIN .*PRIVATE KEY\|AKIA[0-9A-Z]{16}\|ghp_[A-Za-z0-9]{20,})" pyproject.toml docs/development.md tests/` | **no output, rc=1** | ✅ PASS |
| **N14** | 🔴 **Privacy gate** — no camera frame, `pts2d`, blendshape map or feature vector logged/persisted above DEBUG | This story adds **no runtime code path and no logging call at all**. `grep -rniE "logging\|logger\|print\(\|pts2d\|blendshape" pyproject.toml tests/` finds only the T201/`print` *rule names* in the lint config, never a call site. N1 proves no existing logging site changed | ✅ PASS — no biometric data path introduced |
| **N15** | `.venv/` must not be staged or tracked | `git status --porcelain \| grep -c "\.venv"` ; `git check-ignore -v .venv/pyvenv.cfg` | `0` ; `.gitignore:18:.venv/	.venv/pyvenv.cfg` | ✅ PASS |
| **N16** | Files outside the story's scope must not be touched | `git status --porcelain` | ` M docs/status.md` (pre-existing before this run; **untouched by this story** — orchestrator-owned), `?? .mcp.json` (pre-existing), `?? docs/development.md`, `?? pyproject.toml`, `?? tests/` | ✅ PASS |

---

### Gate 3 — Contract Consistency

#### Table A — `requirements.txt` (runtime truth) ↔ `pyproject.toml [project].dependencies`

Both sides listed element-by-element. AC2 requires **same floors, same ceilings**.

| # | `requirements.txt` | `pyproject.toml:24-31` | Match | Resolved in `.venv` |
|---|---|---|---|---|
| 1 | `opencv-python>=4.8,<5` (:10) | `"opencv-python>=4.8,<5"` | ✅ identical | `opencv-python-4.14.0.94` ✅ in band |
| 2 | `opencv-contrib-python>=4.8,<5` (:15) | `"opencv-contrib-python>=4.8,<5"` | ✅ identical | `opencv-contrib-python-4.14.0.94` ✅ in band, **major-aligned with #1** as the constraint demands |
| 3 | `mediapipe>=0.10.30,<1.0` (:17) | `"mediapipe>=0.10.30,<1.0"` | ✅ identical | `mediapipe-0.10.35` ✅ in band |
| 4 | `numpy>=2.3,<3` (:18) | `"numpy>=2.3,<3"` | ✅ identical | `numpy-2.5.2` ✅ in band |
| 5 | `scikit-learn>=1.3,<2` (:19) | `"scikit-learn>=1.3,<2"` | ✅ identical | `scikit-learn-1.9.0` ✅ in band |
| 6 | `PyQt6>=6.5,<7` (:20) | `"PyQt6>=6.5,<7"` | ✅ identical | `PyQt6-6.11.0` ✅ in band |
| — | `scipy` — commented as removed, transitive via scikit-learn (:22-23) | **absent** — correct | ✅ consistent | `scipy-1.18.0` arrives transitively, as documented |
| — | — | `joblib` **absent** on both sides (OUT: CYCLE-5) | ✅ consistent | `joblib-1.5.3` transitive via scikit-learn |

**6 declared / 6 mirrored / 6 resolved in band. No drift, no silent default, one dependency truth.**

#### Table B — declared `dev` extra ↔ actually installed version

| Declared (`pyproject.toml:34-39`) | Installed | In band? |
|---|---|---|
| `pytest>=8.0,<9` | `pytest-8.4.2` | ✅ |
| `pytest-cov>=5.0,<8` | `pytest-cov-7.1.0` | ✅ |
| `pytest-qt>=4.4,<5` | `pytest-qt-4.5.0` | ✅ |
| `ruff>=0.14,<1` | `ruff-0.16.2` | ✅ — and note this band is exactly why the `*.md` formatter behaviour of Deviation 1 must be handled: any fresh install lands on 0.16.x |
| `setuptools>=77` (build-system, `:2`) | build backend resolved and built the editable wheel successfully | ✅ |

#### Table C — every `per-file-ignores` entry ↔ every real ruff finding (1:1, both directions)

Left: the 31 findings the shipped config actually produces, from
`ruff check . --config 'lint.per-file-ignores={}' --output-format concise`.
Right: the allowlist entry that covers each.

| File | Rule | Findings | Allowlist entry | Reason + removal owner present? |
|---|---|---:|---|---|
| `main.py` | `I001` | 1 | `:76` | ✅ "unsorted imports. Removed: CYCLE-3 (DR-5)" |
| `main.py` | `T201` | 2 | `:74` | ✅ "2 print sites (56, 116). Removed: CYCLE-4 (FR-25…)" |
| `main.py` | `E501` | 2 | `:75` | ✅ "2 long lines… Removed: CYCLE-3 when main.py becomes a shim (DR-5)" |
| `eye_tracker/overlay.py` | `T201` | 3 | `:79` | ✅ CYCLE-4 (FR-25) |
| `eye_tracker/overlay.py` | `E702` | 3 | `:80` | ✅ CYCLE-3 (FR-5/FR-6 rewrite) |
| `eye_tracker/overlay.py` | `I001` | 1 | `:81` | ✅ CYCLE-3 |
| `eye_tracker/overlay.py` | `RUF046` | 1 | `:82` | ✅ CYCLE-3 |
| `eye_tracker/overlay.py` | `SIM105` | 1 | `:83` | ✅ CYCLE-3 |
| `eye_tracker/overlay.py` | `PLR0915` | 1 | `:84-85` | ✅ "CalibrationWindow.__init__ (86): 31 statements… **Permanent, per §14**" |
| `eye_tracker/tracker.py` | `T201` | 5 | `:88` | ✅ CYCLE-4 (FR-25) |
| `eye_tracker/tracker.py` | `E501` | 1 | `:89` | ✅ CYCLE-4 (FR-30/FR-31) |
| `eye_tracker/tracker.py` | `F401` | 1 | `:90` | ✅ CYCLE-4 |
| `eye_tracker/gaze.py` | `F401` | 4 | `:93-95` | ✅ TD-2, CYCLE-2 (FR-1/FR-2) |
| `eye_tracker/gaze.py` | `SIM108` | 1 | `:96` | ✅ CYCLE-2 |
| `eye_tracker/face_mesh.py` | `SIM117` | 1 | `:99-100` | ✅ FR-29 atomic-download pattern, CYCLE-2 |
| `eye_tracker/face_mesh.py` | `SIM105` | 1 | `:101` | ✅ CYCLE-2 |
| `eye_tracker/calibration.py` | `I001` | 1 | `:104` | ✅ CYCLE-3 (FR-8/FR-9) |
| `eye_tracker/calibration.py` | `B905` | 1 | `:105` | ✅ CYCLE-3 |
| **Total** | **11 rules** | **31** | **18 file×rule entries** | **18/18 owned** |

- **Left → right (no unsuppressed finding):** `ruff check .` → `All checks passed!` rc=0.
- **Right → left (no *inert* entry):** every entry above maps to ≥1 real finding. This is exactly
  why patterns §13's `gaze.py = ["PLR0915"]` was **dropped** — it would have been an entry
  exempting nothing, i.e. the silent exemption §14 forbids (**Deviation 2**).
- Plus `"tests/*" = ["PLR0915"]` (`:107`) — forward-looking, per patterns §13 verbatim; the only
  intentionally pre-emptive entry, and it is quoted from the patterns document rather than invented.

#### Table D — the `max-statements` ↔ finding-count reconciliation (both measured)

The story prose says "30 findings"; AC10 mandates `max-statements = 30`. These are two different
numbers and had to be reconciled rather than assumed. Measured, both directions:

| `lint.pylint.max-statements` | Findings | Rules | Difference |
|---|---:|---:|---|
| `50` (ruff default) | **30** | 10 | `PLR0915` fires on **nothing** — the rule is unenforced and patterns §14 goes unimplemented |
| **`30` (shipped, `:65`)** | **31** | 11 | the single extra is `PLR0915` at `eye_tracker/overlay.py:86` (31 statements > 30) |

**Resolution: `max-statements = 30`, allowlist covering all 31.** AC10 is explicit and normative;
the "30" in the story's stakeholder prose is the count at ruff's *default*, which the story's own
Step 3 explains is the setting it rejects. Critically, the story's supplied per-file-ignores block
**already contains** `overlay.py → PLR0915` with a reason — so the story's config and its allowlist
were internally consistent all along at 31; only the round-number prose lagged. Choosing 50 would
have made the arithmetic match the prose while leaving the §14 length rule enforcing nothing —
the opposite of the intent. Verified end state: `ruff check .` → `All checks passed!`, rc=0,
zero warnings.

#### Table E — `pyproject.toml` config ↔ `docs/development.md` documented procedure

Every command the runbook tells a developer to run, against what the config actually does.

| Documented command (`docs/development.md`) | Config that backs it | Documented expectation | Observed |
|---|---|---|---|
| `python --version` → 3.14.6 (`:21`) | `requires-python = ">=3.14"` (`:18`) | `3.14.x` | `Python 3.14.6` ✅ |
| `python -m venv .venv` after **rename** (`:59` PowerShell, `:66` Bash) | n/a — this is the open-item-6 recovery | both artifacts appear | both appeared ✅ |
| `sys.prefix` inside `.venv` (`:114`) | n/a | path inside `.venv` | matched ✅ |
| `pip install -r requirements.txt` (`:131`) | runtime pins mirrored in Table A | 6 pins resolve | resolved ✅ |
| `pip install -e ".[dev]"` (`:132`) | `[build-system]` + `dev` extra | exit 0, repeatable | exit 0 twice ✅ |
| FR-26 probe from `$TEMP` / `/tmp` (`:176` PowerShell, `:185` Bash) | `py-modules` + `packages.find` | `import OK` + a path **in the working tree** | `…\EyeTracker\eye_tracker\__init__.py` ✅ (working tree, confirming editable) |
| `ruff check .` (`:198`) | `[tool.ruff.lint]` + allowlist | `All checks passed!` | matched, rc=0 ✅ |
| `ruff format --check .` (`:199`) | `[tool.ruff.format] exclude` incl. `*.md` | `N files already formatted`, exit 0 | `2 files already formatted`, rc=0 ✅ |
| `ruff check . --statistics --config 'lint.per-file-ignores={}'` (`:214`) — documented so the suppressions are auditable | the allowlist | shows what is suppressed | showed all 31 ✅ |
| `pytest` (`:227`) | `[tool.pytest.ini_options]` | collects, passes, prints coverage table | 2 passed, table printed, rc=0 ✅ |
| Doc states 31 findings are suppressed (`:208`) | 31 measured (Table D) | consistency | ✅ the doc states the measured number, not the prose number |
| Doc predicts two `CoverageWarning`s (`:238-245`) | `--cov=main` with no test importing `main` yet | warnings appear, exit status unaffected | both appeared, rc=0 ✅ |
| Troubleshooting (b): `pytest` → exit **5** (`:317`) | `testpaths = ["tests"]` | rc 5 on empty collection | **verified**: `pytest --override-ini="testpaths=<empty dir>"` → `no tests ran`, **rc=5** ✅ |
| Troubleshooting (c): numpy resolution failure ⇒ interpreter < 3.14 (`:331`) | `numpy>=2.3` floor | explains cause | consistent with `requirements.txt:7-8` and `pyproject.toml:12-14` ✅ |
| Troubleshooting (d): wheel download timeout (`:360`) | n/a | re-run with `--retries 10 --timeout 60` | **observed and recovered from during this build** ✅ |

#### Table F — `[tool.ruff.format].exclude` ↔ what the formatter must and must not touch

| Excluded path | Why | Removal owner | Still genuinely unformatted? |
|---|---|---|---|
| `main.py`, `calibration.py`, `face_mesh.py`, `gaze.py`, `one_euro.py`, `overlay.py`, `tracker.py` | A sweep would rewrite 7 of 8 files in a cycle whose rollback contract is "revert; nothing behavioural changed" | the cycle named in the matching lint entry | ✅ `--config 'format.exclude=[]'` → `7 files would be reformatted` |
| `*.md` | ruff ≥0.16 formats Python fences **inside Markdown** — 20+ files under `docs/` incl. the story specs themselves | **Permanent** (documented as such) | ✅ counterfactual without it → `20 files would be reformatted`, exit 1 |
| *(everything else — i.e. files this story creates)* | must **be** formatted | n/a | ✅ `2 files already formatted`, exit 0 |

---

## Challenges Encountered

| Challenge | Resolution | Notes |
|-----------|------------|-------|
| **`ruff format --check .` fails on Markdown, not Python** — ruff 0.16.2 formats Python code fences inside `*.md`; the story's 7-entry exclude list left 20 `docs/**/*.md` files failing, so **AC13 could not pass as written** | Added `"*.md"` to `[tool.ruff.format].exclude` — the narrowest fix, scoped to the *formatter only*, leaving `ruff check` untouched. Counterfactual measured both ways | **Deviation 1** |
| **Transient network failure** — the first `pip install -e ".[dev]"` died with `Could not find a version that satisfies the requirement setuptools>=77 (from versions: none)`, which reads like a missing package but is actually an unreachable index | Re-ran with `--retries 10 --timeout 60`; succeeded. Then **added it to the runbook** as Troubleshooting (d), because the error text actively misleads | The AC19 walkthrough later ran clean first-try, so the doc covers a failure a developer will hit but did not need itself |
| **`readme = "README.md"` in the story's TOML block, but no `README.md` exists** in the repository — setuptools hard-fails the build on a `readme` key naming an absent file, so `pip install -e .` (AC5) would have been impossible | Omitted the `readme` key and recorded why in a comment at `pyproject.toml:9-12`. Creating `README.md` was rejected: it is outside `files_touched`. No AC references `readme` | **Deviation 3** |
| **Reconciling "30 findings" with `max-statements = 30`** — the two produce different counts | Measured both settings, chose 30 per the normative AC10, shipped an allowlist matching all 31 | **Deviation 4**, full evidence in Gate 3 Table D |
| **Verifying "the app still starts" without seizing the user's display** or hanging the run | Ran bounded under `QT_QPA_PLATFORM=offscreen` with a 25 s timer; exit 124 proves the event loop was entered and held. Behavioural identity itself rests on AC20 byte-identity, which is stronger than any smoke run | — |

## Deviations from Plan

**1. `"*.md"` added to `[tool.ruff.format].exclude` (not in the story's Step 5 list).**
*Reason*: ruff ≥0.16 formats Python code blocks embedded in Markdown. Without this,
`ruff format --check .` exits 1 with `20 files would be reformatted` — all under `docs/`, including
the architecture documents and the story specifications themselves. AC13's intent is that *Python
code* is formatted; a code formatter rewriting the snippets inside a specification would corrupt
the spec it carries. This is the narrowest available fix: it is scoped to `[tool.ruff.format]`
only, so `ruff check` behaviour is entirely unchanged (and ruff's linter never scanned `.md`
anyway). Marked **Permanent** in the config, with the reason, per patterns §16.
*Verification*: with it → `2 files already formatted`, exit 0. Without it → `20 files would be
reformatted, 27 files already formatted`, exit 1.

**2. Patterns §13's `"eye_tracker/gaze.py" = ["PLR0915"]` entry dropped.**
*Reason*: the story's Step 3(a) directs this, and measurement confirms it — at
`max-statements = 30`, `PLR0915` produces exactly one finding repo-wide, at `eye_tracker/overlay.py:86`.
A `gaze.py` entry would exempt nothing. Keeping an inert suppression is precisely the silent
exemption patterns §14 forbids. `overlay.py`'s entry is kept and marked permanent.
*Verification*: Gate 3 Table C — right→left direction shows no inert entry.

**3. `readme = "README.md"` omitted from `[project]` (present in the story's literal TOML block).**
*Reason*: the repository has no `README.md` (`git ls-files | grep -i readme` → nothing). setuptools
fails the build when the `readme` key names a nonexistent file, which would have made AC5
(`pip install -e ".[dev]"` succeeds) unachievable. Creating a `README.md` was rejected as outside
this story's `files_touched`. No acceptance criterion mentions `readme`; AC2 enumerates name,
version, `requires-python` and dependencies only. A comment at `pyproject.toml:9-12` records the
omission and states the condition for adding it back.

**4. `max-statements` / finding-count reconciliation: shipped 30 with a 31-entry-covering allowlist.**
*Reason*: AC10 is normative and explicit (`max-statements = 30`); the "30 findings" figure in the
story's stakeholder prose is the count at ruff's *default* 50, which Step 3(a) explicitly rejects
as leaving `PLR0915` inert. Choosing 50 would have made the round number match while leaving
patterns §14 unenforced — the story's stated failure mode. The story's own supplied
per-file-ignores block already includes `overlay.py → PLR0915`, so the *config* was consistent at
31 from the outset; only the prose lagged. Shipped the consistent pair.
*Verification*: Gate 3 Table D (both settings measured), and `ruff check .` → `All checks passed!`,
rc=0, zero warnings.

**5. Coverage is 0%, against the framework's nominal ≥85% quality gate.**
*Reason*: not a shortfall to remediate — this story adds **zero new production Python**. The 651
statements measured are pre-existing modules this story is forbidden to modify (AC20) and whose
tests belong to Story 1.3 and later. `--cov-fail-under` is deliberately absent per AC15, with
CYCLE-5 named as the owner that switches the threshold on. Reported honestly rather than inflated
by writing tests against another story's code. Full reasoning under *Testing Summary*.

## Lessons Learned

1. **A tool's default file-type scope is part of its contract, and it drifts.** `ruff format` growing
   Markdown support turned a passing configuration into a failing one without any project change.
   The `dev` extra's `ruff>=0.14,<1` band means every fresh install lands on the new behaviour —
   so the exclusion is not a workaround for one machine, it is part of the config's correctness.
   Worth remembering when the CYCLE-5 story revisits the toolchain.
2. **Two numbers in a spec that were derived under different settings will silently disagree.** The
   "30 findings" prose and `max-statements = 30` looked like the same number and were not. The only
   safe move was to measure both configurations and ship the pair that is internally consistent —
   and to write down which was chosen and why, so the next reader does not re-derive it blind.
3. **A literal config block in a story is a draft, not a fact.** `readme = "README.md"` would have
   made the story's own AC5 unachievable. Copying it verbatim would have produced a green-looking
   review and a broken install.
4. **Suppression with a named owner is a genuinely different artifact from suppression.** Writing 18
   entries each naming its removing cycle took real effort, but the config now doubles as a work
   list, and the right→left audit (no *inert* entry) is only possible because each entry claims
   specific findings.
5. **"Validated by execution" catches what review cannot.** The runbook read fine before it was run;
   running it surfaced a misleading pip error that now has its own troubleshooting entry.
6. **Byte-identity beats a smoke test for a zero-change claim.** `git diff` plus 8 matching blob
   hashes proves "behaves exactly as before" more strongly than any launch of the application could.

## Next Steps

- [x] All 23 acceptance criteria met and evidenced
- [x] All 9 numbered Steps executed and evidenced
- [x] All 12 manual verification commands run with output pasted
- [x] DoD Gates 1, 2 and 3 passed
- [x] `ruff check .` and `ruff format --check .` both exit 0, zero warnings
- [x] Full suite green: 2/2 passing
- [x] Zero application source modification proven by blob hash
- [ ] Ready for code review
- [ ] Ready for Unit test validation
- **Unblocks**: Stories 1.1, 1.3 and 1.5 — a working interpreter, an importable package and a
  runnable test suite now exist.
- 🚩 **Flag to the plan owner (Step 5 requires this be raised, not buried).** A one-time global
  `ruff format` sweep is a defensible alternative to the 7-file exclusion list and would delete it
  entirely. It is **deferred, not rejected**. The trade: absorb one large mechanical diff now
  (7 files, behaviour-neutral, destroys `git blame` locality repo-wide) versus seven small ones
  spread across CYCLE-2 to CYCLE-4. It was deferred here because CYCLE-1's rollback contract is
  "revert; nothing behavioural changed", which a whole-codebase rewrite sits badly with. Decide
  before CYCLE-2 opens, since that is when the first exclusion would come off.
  *(Note: the `*.md` exclusion is separate and permanent — a sweep would not remove it.)*
- ⚠️ **For Story 1.3**: `pytest` currently emits two `CoverageWarning`s — `Module main was never
  imported` and `No data was collected`. Both are accurate (no test imports the application yet)
  and both clear as soon as the suite covers real code. They do not affect exit status and are not
  lint warnings. Documented at `docs/development.md:238-245` so they are not mistaken for a defect.
- ⚠️ **For whoever adds a `README.md`**: add `readme = "README.md"` back to `[project]` in the same
  change. The comment at `pyproject.toml:9-12` records the dependency.
