# Development environment setup

How to get from a fresh clone of this repository to an environment in which the
application runs, the linter runs and the test suite runs.

Follow it top to bottom. Every command below is one you type; every "Expect"
line is what you should see. If a step does not produce its expected output,
stop and read [Troubleshooting](#troubleshooting) rather than continuing — a
later step will otherwise fail in a way that does not name the real cause.

The whole sequence is **safely repeatable**. If you get part way through and
something fails, fix it and re-run from the top; no step needs you to remember
which of the earlier ones already ran.

---

## 1. Prerequisites

| Requirement | Value | Check |
|---|---|---|
| CPython | **3.14.6** — the only version this codebase has been verified against | `python --version` |
| Network access | Required. The MediaPipe, PyQt6, OpenCV and SciPy wheels total several hundred MB | — |
| Disk | ~1.5 GB free for the virtual environment | — |
| A webcam | Only to *run* the application. Not needed to install, lint or test | — |

```bash
python --version
```

Expect `Python 3.14.6` (any `3.14.x` is acceptable).

`pyproject.toml` declares `requires-python = ">=3.14"`. That floor is not
stylistic: `numpy>=2.3` is required because **no numpy 1.x wheel is published
for CPython 3.14**, and on an older interpreter pip resolves the dependency set
to a numpy that does not exist. See [Troubleshooting (c)](#c-pip-cannot-resolve-numpy).

If `python` on your `PATH` is not 3.14, call the interpreter by its full path in
every command below — on Windows that is typically `C:\Python314\python.exe`.

---

## 2. Create the virtual environment

> 🔴 **Do not create over an existing `.venv/`.** `python -m venv` does not clean
> the directory it is given. It will leave stale console scripts from the previous
> environment in `Scripts/` (or `bin/`) and can exit 0 while producing a tree that
> is not a usable environment. This repository has already been in exactly that
> state once: a `.venv/` holding dependency console scripts and `Lib/site-packages`
> but with **no interpreter and no `pyvenv.cfg`**. Without `pyvenv.cfg`, Python's
> site machinery cannot locate the base installation, `sys.prefix` is never
> redirected, and the directory is not a virtual environment at all.
>
> **Rename first, delete only once the new environment is proven.** The rename
> costs nothing and keeps a rollback available.

**Windows (PowerShell):**

```powershell
if (Test-Path .venv) { Rename-Item .venv .venv.broken }
python -m venv .venv
```

**Windows (Git Bash) / POSIX (Linux, macOS):**

```bash
[ -d .venv ] && mv .venv .venv.broken
python -m venv .venv
```

### Verify the environment actually exists

Both files must be present. If either is missing, stop — see
[Troubleshooting (a)](#a-pyvenvcfg-or-the-interpreter-is-missing-after-creation).

**Windows:**

```powershell
Test-Path .venv\Scripts\python.exe, .venv\pyvenv.cfg
```

**POSIX:**

```bash
ls .venv/bin/python .venv/pyvenv.cfg
```

Expect both to exist (`True`/`True` on Windows).

---

## 3. Activate, and confirm the activation took effect

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Git Bash):**

```bash
source .venv/Scripts/activate
```

**POSIX:**

```bash
source .venv/bin/activate
```

Then — this check is not optional:

```bash
python -c "import sys; print(sys.prefix); print(sys.version)"
```

Expect `sys.prefix` to be a path **inside** this repository's `.venv`, e.g.
`C:\Users\you\Documents\EyeTracker\.venv`, and the version to be `3.14.6`.

If `sys.prefix` points at the system installation, activation did not take
effect. Do not continue: every `pip install` below would install into the system
interpreter, and the failure would only surface much later as packages that are
importable outside the environment and missing inside it.

---

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

- `requirements.txt` is the **runtime** constraint file — the six libraries the
  application itself imports, each with an explicit floor and a major ceiling.
- The `dev` extra in `pyproject.toml` carries the **tooling** — pytest,
  pytest-cov, pytest-qt and ruff. Developer tools are deliberately kept out of
  `requirements.txt` so that installing the application for normal use does not
  drag the toolchain along with it.
- `-e` (editable) is what makes `eye_tracker` and `main` importable from
  anywhere without setting `PYTHONPATH`. It is not a convenience — it is the
  mechanism behind the check in section 5.

Re-running any of these three commands is safe. A second
`python -m pip install -e ".[dev]"` exits 0, reports already-satisfied
requirements as such, and rebuilds the editable link in place.

If a download stalls or times out, see
[Troubleshooting (d)](#d-a-wheel-download-times-out).

---

## 5. Verify the environment

Four checks. Run all four.

### 5.1 The six runtime dependencies import

```bash
python -c "import cv2, mediapipe, numpy, sklearn, PyQt6; print('ok')"
```

Expect `ok`.

### 5.2 The project imports from outside the repository root

This is the check that proves the packaging metadata is doing its job. Running
it **from the repository root proves nothing**, because the root is on
`sys.path` implicitly — you must run it from somewhere else, with `PYTHONPATH`
cleared.

**Windows (PowerShell):**

```powershell
Push-Location $env:TEMP
$env:PYTHONPATH = ''
python -c "import eye_tracker, main; print('import OK', eye_tracker.__file__)"
Pop-Location
```

**Windows (Git Bash) / POSIX:**

```bash
cd /tmp && env -u PYTHONPATH python -c "import eye_tracker, main; print('import OK', eye_tracker.__file__)" ; cd -
```

Expect `import OK` followed by the path to `eye_tracker/__init__.py` **inside
this repository** (not inside `site-packages` — an editable install points back
at your working tree).

If this fails with `ModuleNotFoundError: No module named 'eye_tracker'`, the
editable install in section 4 did not complete. Re-run it.

### 5.3 The linter and formatter are clean

```bash
ruff check .
ruff format --check .
```

Expect `All checks passed!` and `N files already formatted`. Both must exit 0 —
in CI a warning is a failure.

Two things are worth knowing before you are surprised by them:

- **Pre-existing findings are suppressed, not absent.** The application modules
  predate the linter and carry 31 findings. Each one is switched off individually
  in `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`, with a comment
  giving the reason and naming the cycle that removes it. The gate's job today is
  to block *new* violations. To see what is currently suppressed:

  ```bash
  ruff check . --statistics --config 'lint.per-file-ignores={}'
  ```

- **The formatter is scoped.** `[tool.ruff.format]` excludes the seven legacy
  application modules — each is formatted by the cycle that next modifies it,
  rather than in one sweep that would collide with every later diff. It also
  excludes `*.md`, because ruff formats Python code fences inside Markdown and
  would otherwise rewrite the code samples embedded in the architecture and story
  documents under `docs/`.

### 5.4 The test suite runs

```bash
pytest
```

Expect a session that collects from `tests/`, passes, and prints a coverage
table for `eye_tracker` and `main`.

Coverage is **measured and reported but not enforced**. `--cov-fail-under` is
deliberately absent from `pyproject.toml`; the ≥85% threshold is switched on in
CYCLE-5, once the suite exists to meet it. A gate that fails on day one is a gate
people learn to bypass.

You will currently also see two `CoverageWarning`s — `Module main was never
imported` and `No data was collected`. Both are accurate and expected: no test
imports the application yet. They disappear as soon as the suite covers real
code. They are warnings from coverage, not lint failures, and they do not affect
the exit status.

If `pytest` exits **5** rather than 0, see
[Troubleshooting (b)](#b-pytest-exits-5-instead-of-0).

---

## 6. Run the application

```bash
python main.py
```

A calibration window opens fullscreen; follow the targets. A webcam is required.
To exit during calibration, press `Esc`.

---

## 7. Remove the old environment

Only once every check in section 5 has passed:

**Windows (PowerShell):**

```powershell
Remove-Item -Recurse -Force .venv.broken
```

**POSIX / Git Bash:**

```bash
rm -rf .venv.broken
```

`.venv/` is covered by `.gitignore` and must never be committed — the repository
previously tracked a 752 MB macOS-built environment of 14,251 files. Recreate it
locally instead.

---

## Troubleshooting

### (a) `pyvenv.cfg` or the interpreter is missing after creation

**Symptom.** `python -m venv .venv` exits 0, but `.venv/pyvenv.cfg` does not
exist, or `.venv/Scripts/python.exe` (`.venv/bin/python` on POSIX) does not.
Activation appears to work but `sys.prefix` still points at the system install.

**Cause.** Almost always `venv` was run *over* a directory that already existed.
`venv` does not clean its target, and a partially-populated tree can survive
looking plausible: the console scripts of the previous environment are still in
`Scripts/`, and `Lib/site-packages` is still full, so nothing looks obviously
broken until a test runner cannot be invoked.

**Fix.**

```bash
# POSIX / Git Bash
mv .venv .venv.broken            # keep it until the replacement is proven
python -m venv .venv
ls .venv/bin/python .venv/pyvenv.cfg
```

```powershell
# PowerShell
Rename-Item .venv .venv.broken
python -m venv .venv
Test-Path .venv\Scripts\python.exe, .venv\pyvenv.cfg
```

If it still fails on a genuinely empty target, the base interpreter's `venv`
module is broken or `ensurepip` is unavailable — reinstall CPython 3.14.6, or
create the environment with `python -m venv --without-pip .venv` and bootstrap
pip manually.

### (b) `pytest` exits 5 instead of 0

**Symptom.** `pytest` prints `no tests ran` and the shell reports exit code 5.

**Cause.** This is pytest's `NO_TESTS_COLLECTED` code, not a failure. It means
`testpaths = ["tests"]` matched no test module. It is the expected result on any
checkout where the test suite has not landed yet, and it is called out here
because an exit code that is neither 0 nor 1 reads like a crash.

**Fix.** None needed if `tests/` is genuinely empty. If you expected tests to be
collected, check that you are running `pytest` **from the repository root** —
`testpaths` is resolved relative to the rootdir, and the packaging test also
reads `tests/` as a relative path.

### (c) pip cannot resolve `numpy`

**Symptom.** `pip install -r requirements.txt` fails with a resolution error on
`numpy>=2.3` — "could not find a version that satisfies the requirement", or a
long backtracking search that ends in failure.

**Cause.** The base interpreter is **older than 3.14**. The `>=2.3` floor exists
because no numpy 1.x wheel is published for CPython 3.14; on an older
interpreter, pip is being asked for a combination that has no solution.

**Fix.** Check what actually created the environment:

```bash
python -c "import sys; print(sys.version)"
cat .venv/pyvenv.cfg          # `version` and `home` name the base interpreter
```

If it is not 3.14.x, delete the environment and recreate it with the 3.14
interpreter by full path:

```bash
rm -rf .venv
C:/Python314/python.exe -m venv .venv          # Windows
/usr/local/bin/python3.14 -m venv .venv        # POSIX, adjust the path
```

`requires-python = ">=3.14"` in `pyproject.toml` makes this cause explicit at
install time rather than leaving it as a wheel-resolution puzzle.

### (d) A wheel download times out

**Symptom.** `Connection timed out while downloading`, or
`Could not find a version that satisfies the requirement setuptools>=77 (from
versions: none)` during the build-dependency step of `pip install -e ".[dev]"`.

**Cause.** Transient network failure. The `from versions: none` wording is
misleading — it means pip could not reach the index at all, not that the package
does not exist.

**Fix.** Re-run the same command with longer patience. It resumes from the pip
cache and is safe to repeat:

```bash
python -m pip install --retries 10 --timeout 60 -e ".[dev]"
```
