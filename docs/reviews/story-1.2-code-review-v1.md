# Code Review - Story 1.2: Packaging metadata, tool configuration and a rebuilt development environment

**Date**: 2026-08-09
**Reviewed By**: REVIEWER Agent (AIRE_REVIEWER)
**Review Number**: 1
**Review Mode**: INITIAL_REVIEW
**Status**: ❌ CHANGES REQUESTED

---

## Review Metadata

**Previous Review**: None — `docs/reviews/` did not exist before this run
**Previous Status**: N/A
**Files Changed Since Last Review**: All (initial review)
**Severity Threshold Applied**: All (🔴 🟠 🟡 🟢)
**Branch**: `feat/story-1.2-packaging` — **uncommitted**, working tree only
**Story file**: `docs/plans/stories/epic-1-story-1.2-Packaging-And-Environment.md`
**Self-review under audit**: `docs/stories-implemented/story-1.2-review.md`

**IN scope**: `pyproject.toml`, `docs/development.md`, `tests/arch/test_packaging.py`, plus verification of the story's zero-application-change claim and of the evidence recorded in the self-review.
**OUT of scope**: the 31 pre-existing lint findings in `main.py` / `eye_tracker/**` (owned by CYCLE-2 – CYCLE-4 by design), `tests/conftest.py` and the remaining suite directories (Story 1.3), enforcement of the ≥85% coverage threshold (CYCLE-5, per AC15 and the story's OUT list).

---

## Review Summary

**Components Reviewed**:

| File | Lines | Kind |
|---|---:|---|
| `pyproject.toml` | 149 | New — packaging + ruff lint/format + pytest + coverage config |
| `docs/development.md` | 376 | New — environment rebuild runbook |
| `tests/arch/test_packaging.py` | 37 | New — 2 packaging-invariant tests |
| `docs/plans/dependency-graph.yml` | +10 | Modified — `files_touched` amendment (see ISS-003) |
| `main.py`, `eye_tracker/**` | 0 | **Verified unchanged** |

**Lines of Code**: ~560 lines delivered; **0 new production Python**
**Tests Reviewed**: Yes — 2 tests, both passing
**Coverage**: 0.00% over 651 statements (see *Coverage note* below)

**Overall Assessment**: This is a high-quality, unusually well-evidenced piece of work. Every configuration value is traceable to a measurement, every lint suppression carries a reason and a named removal owner, and three genuine defects in the story's own specification were caught and recorded rather than coded around. The zero-application-change contract holds under independent verification. One finding blocks approval: the permanent FR-26 guard test scans a **cwd-relative** path and therefore reports a green pass having examined zero files when pytest is not invoked from the repository root — a regression guard that can silently stop guarding. Two medium and three low findings follow.

---

## Independent Verification Performed

Per the review rulebook's **VERIFY EVIDENCE** rule, the developer's evidence was **re-executed**, not read. All commands run in the project `.venv` (Python 3.14.6, ruff 0.16.2, pytest 8.4.2).

| # | Command | Result | Matches self-review? |
|---|---|---|---|
| 1 | `ruff check .` | `All checks passed!` — **rc 0** | ✅ |
| 2 | `ruff format --check .` | `2 files already formatted` — **rc 0** | ✅ |
| 3 | `ruff check . --statistics --config 'lint.per-file-ignores={}'` | `Found 31 errors` / 11 rules — T201×10, F401×5, E501×3, E702×3, I001×3, SIM105×2, B905/PLR0915/RUF046/SIM108/SIM117 ×1 | ✅ exact match |
| 4 | `pytest` | 2 passed, **rc 0**, coverage table printed, 2 `CoverageWarning`s as documented | ✅ |
| 5 | `git diff --stat -- main.py eye_tracker/` | **empty** | ✅ AC20 holds |
| 6 | `ruff check . --select PLR0915 --config 'lint.per-file-ignores={}'` | 1 finding: `eye_tracker/overlay.py:86 (31 > 30)` | ✅ |
| 7 | Same at `max-statements=50` | `All checks passed!` — **PLR0915 inert at the default** | ✅ Deviation 2 justified |
| 8 | `ruff check --stdin-filename eye_tracker/newmod.py` with a new `print()` | `T201`, `F401`, `I001` — **rc 1** | ✅ the gate still bites |
| 9 | Same via `--stdin-filename tests/unit/test_new.py` | `T201`, `F401`, `I001` — **rc 1** | ✅ bites in test dirs too |
| 10 | Secrets/PII grep over delivered files | no match, rc 1 | ✅ |
| 11 | `TODO`/`FIXME`/`XXX`/`HACK` grep | no match, rc 1 | ✅ |
| 12 | `grep -rnE "sys\.path\.(append\|insert)" tests/` | no match, rc 1 | ✅ |

**A claim worth recording as cleared, not as a finding.** The `"tests/*"` per-file-ignores key looks like it should fail to match the nested `tests/arch/test_packaging.py`, since many glob implementations stop `*` at a path separator. Tested directly rather than assumed:

```
ruff check tests/ --config 'lint.select=["ANN"]' --config 'lint.per-file-ignores={}'        → 3 errors
ruff check tests/ --config 'lint.select=["ANN"]' --config 'lint.per-file-ignores={"tests/*"=["ANN"]}' → 0 errors
```

Ruff's `*` **does** cross directory separators, so the entry is live for the whole `tests/` tree. No change needed.

---

## Checklist Results

### Correctness
- [x] ✅ Configuration does what it claims — every table verified by execution
- [x] ✅ `packages.find` discovery (not an explicit list) — proven by the self-review's scratch-tree wheel build; the design reason is sound and prevents `pyproject.toml` becoming a cross-story merge point
- [x] ✅ Dependency mirror between `requirements.txt` and `[project].dependencies` is exact — 6/6 floors and ceilings identical
- [x] ⚠️ **Test correctness** — one guard test can pass without scanning anything (**ISS-001**)
- [x] ✅ No race conditions / memory concerns — no runtime code added

### Pattern Adherence
- [x] ✅ `line-length = 100`, `target-version = "py314"` — verbatim per patterns §13
- [x] ✅ `select` list character-identical to patterns §13 (13 entries)
- [x] ✅ `max-statements = 30` — patterns §14 made enforceable rather than nominal
- [x] ✅ Every allowlist entry carries a reason **and** a removal owner (patterns §14 🔴 rule, §16)
- [x] ✅ Dropping patterns §13's `gaze.py = ["PLR0915"]` is correct and evidenced — verification #7 confirms the entry would exempt nothing
- [x] ⚠️ **Coverage exclusions incomplete** vs patterns §15 (**ISS-002**)
- [x] ✅ `Layer:` declaration present on the new test module (patterns §1/§12)

### Testing
- [x] ✅ Tests exist and pass (2/2)
- [x] ✅ TDD evidence is real — RED observed with `ModuleNotFoundError`, then GREEN
- [x] ✅ Test names state behaviour, not implementation (patterns §15)
- [x] ✅ The FR-26 probe correctly uses a **subprocess from `tmp_path`** — the only formulation that can actually detect the failure mode
- [x] ⚠️ The second test's scan root is cwd-relative (**ISS-001**)
- [x] ⚠️ Coverage 0% — accepted, see note

### Documentation
- [x] ✅ `docs/development.md` is complete, dual-shell, and validated by execution
- [x] ✅ Troubleshooting (a)–(d) present; (d) added from a failure actually encountered
- [x] ✅ No commented-out code, no `TODO`/`FIXME`
- [x] ✅ Comments explain **why**, per patterns §16 — the `readme` omission comment is a model example
- [x] ⚠️ One evidence table in the self-review is incomplete (**ISS-003**)

### Security
- [x] ✅ No hardcoded secrets, keys or credentials — independently grepped
- [x] ✅ No PII; no biometric data path introduced (no runtime code at all)
- [x] ✅ `.venv/` gitignored and unstaged — `git check-ignore` confirms `.gitignore:18`
- [x] ✅ N/A: input validation, authN/authZ, injection, XSS — this story adds no request surface, no I/O and no runtime code path. RBAC section correctly records `No role-differentiated access — single actor`

### SOLID / Anti-Monolith / Performance
- [x] ✅ N/A by construction — the deliverable is declarative configuration and one test module. No classes, no coupling, no runtime paths. Deliberately noted rather than silently skipped.

---

## Coverage note — 0% is accepted, and here is why

The framework's nominal gate is ≥85%. This story reports **0.00% over 651 statements** and is still approved on that axis, for reasons that are checkable rather than rhetorical:

- The story adds **zero new production Python** (verified: `git diff --stat -- main.py eye_tracker/` is empty; the only new `.py` is a test module).
- The 651 statements are pre-existing modules the story is **forbidden** to modify (AC20) and forbidden to test (`tests/conftest.py` and the unit/integration/regression/invariants suites are Story 1.3's and later).
- AC15 **requires** `--cov-fail-under` to be absent, and the OUT list explicitly forbids enforcing 85% here. CYCLE-5 is named in-config as the owner.
- Raising the number would have meant writing tests against another story's code — inflating a metric rather than covering behaviour.

What the story *does* prove is the **wiring**: coverage now attaches to `eye_tracker` and `main`, which was impossible before because no interpreter existed. That is the correct deliverable for a wave-1 seed story. Recorded here explicitly so the waiver is auditable rather than silent.

---

## Issues Found

### ISS-001: FR-26 guard test passes vacuously when pytest is not run from the repository root 🟠 High

**Category**: Testing / Correctness
**File**: `tests/arch/test_packaging.py:32`
**Pattern Reference**: `docs/architecture/design/03-patterns-and-standards-brownfield.md` §15 (Testing Patterns); story AC7

**Issue**:
`test_no_test_file_manipulates_sys_path` resolves its scan root from the **process working directory**:

```python
for path in pathlib.Path("tests").rglob("*.py"):
```

When pytest runs from anywhere other than the repository root, `Path("tests")` does not exist, `rglob` yields nothing, `offenders` stays `[]`, and the test **reports PASS having examined zero files**. The story calls this test the permanent guard for AC7 ("also permanently asserted by `tests/arch/test_packaging.py:29`") and the self-review repeats that claim — so a green suite would be read as proof that no `sys.path` hack exists, when in fact nothing was checked.

**Reproduced** (not inferred):

```
$ cd $TEMP/rev12
$ .../.venv/Scripts/python.exe -m pytest ".../tests/arch/test_packaging.py::test_no_test_file_manipulates_sys_path" -o addopts=""
.                                                                        [100%]
1 passed in 0.01s

$ python -c "import pathlib; p=pathlib.Path('tests'); print(p.exists(), list(p.rglob('*.py')))"
False []
```

The first test in the same module is immune to this — it correctly uses `tmp_path` and a subprocess — which makes the asymmetry easy to miss on reading.

The team is already half-aware of the fragility: `docs/development.md:328-330` tells the reader to run pytest from the repository root because "the packaging test also reads `tests/` as a relative path". Documenting a trap is weaker than removing it, and a document cannot protect a CI job that changes its working directory.

**Current Code** (`tests/arch/test_packaging.py:29-36`):

```python
def test_no_test_file_manipulates_sys_path():
    """FR-26: the fragility this story removes must not creep back in."""
    offenders = []
    for path in pathlib.Path("tests").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"sys\.path\.(append|insert)", text):
            offenders.append(str(path))
    assert offenders == [], f"sys.path manipulation found in: {offenders}"
```

**Suggested Fix** — anchor on the module's own location, and fail loudly if the scan found nothing to scan:

```python
TESTS_ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_no_test_file_manipulates_sys_path():
    """FR-26: the fragility this story removes must not creep back in."""
    scanned, offenders = 0, []
    for path in TESTS_ROOT.rglob("*.py"):
        scanned += 1
        if re.search(r"sys\.path\.(append|insert)", path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(TESTS_ROOT)))
    # A guard that scans nothing must fail, not pass: the failure mode this test
    # exists to catch is silence, and an empty scan is indistinguishable from a
    # clean one otherwise.
    assert scanned > 0, f"scanned no test files under {TESTS_ROOT} — guard is inert"
    assert offenders == [], f"sys.path manipulation found in: {offenders}"
```

**Why This Matters**: FR-26's whole purpose is to remove a fragility that is *invisible until it bites*. A guard against it that is itself invisible-when-broken reproduces the exact class of defect the requirement targets. It is also the cheapest possible fix — two lines — and this test is about to be joined by Story 1.4's import-direction test in the same directory, so the anchoring idiom set here will be copied.

---

### ISS-002: coverage does not exclude `if __name__ == "__main__":`, contrary to patterns §15 🟡 Medium

**Category**: Pattern
**File**: `pyproject.toml:147-149`
**Pattern Reference**: `docs/architecture/design/03-patterns-and-standards-brownfield.md` §15, *Coverage* table — `Excluded | if __name__ == "__main__":, tests/ itself`

**Issue**:
The shipped `[tool.coverage.report]` sets only `show_missing` and `skip_covered`. Coverage.py's default `exclude_lines` is `["# pragma: no cover"]` — it does **not** exclude main-guards. `main.py:140` contains `if __name__ == "__main__":`, and `--cov=main` is enabled (`pyproject.toml:141`), so those lines are counted in the denominator of a target the project can never legitimately cover from a test.

Verified: `grep -n "exclude_lines" pyproject.toml` → no output; `grep -n '__main__' main.py` → `140:if __name__ == "__main__":`.

Half the patterns §15 exclusion rule is implemented (`omit = ["tests/*"]`, `pyproject.toml:145`); the other half is missing. No acceptance criterion names it — AC16 asks only for the `tests/*` omit and `show_missing` — which is likely why it slipped.

**Impact today**: none. `--cov-fail-under` is deliberately absent, so nothing fails. **Impact later**: CYCLE-5 switches the ≥85% gate on against a denominator that permanently includes unreachable lines, and whoever hits that will re-derive this from scratch.

**Suggested Fix**:

```toml
[tool.coverage.report]
show_missing = true
skip_covered = false
# patterns §15: the main-guard is not reachable from a test and must not sit in
# the denominator of the >=85% gate CYCLE-5 switches on. main.py:140 is the
# current instance.
exclude_lines = [
  "pragma: no cover",
  "if __name__ == .__main__.:",
]
```

**Why This Matters**: patterns §15 is the authoritative standard this story's "Must Read" list names, and §14's principle applies equally here — a gate is only trustworthy if its denominator is honest. Fixing it now costs three lines; fixing it in CYCLE-5 means debugging a coverage shortfall under deadline.

---

### ISS-003: the "files outside scope" evidence table omits a file the story did modify 🟡 Medium

**Category**: Documentation / Evidence
**File**: `docs/stories-implemented/story-1.2-review.md:323` (Gate 2, check **N16**)

**Issue**:
N16's stated rule is *"Files outside the story's scope must not be touched"*, and its evidence is a pasted `git status --porcelain` listing:

```
 M docs/status.md, ?? .mcp.json, ?? docs/development.md, ?? pyproject.toml, ?? tests/
```

The real working tree also contains ` M docs/plans/dependency-graph.yml`, which **this story modified**. Its diff is self-identifying:

```
+      # AMENDED 2026-08-09 during implementation. TDD requires a test proving the
+      # editable install works ...
+      - tests/arch/test_packaging.py
```

**The amendment itself is correct and well-argued** — adding `tests/arch/test_packaging.py` to `files_touched` keeps the same-wave disjointness check truthful, the comment names the date, the reason and the non-collision with Stories 1.3/1.4, and quietly creating a test file that the graph did not know about would have been the worse choice. This finding is about the **evidence**, not the change: the one check whose entire job is to enumerate every touched file is the check that missed one, and it is signed off ✅ PASS.

**Suggested Fix**: add the row to N16 and to the *Files Changed* table in the self-review:

```
| `docs/plans/dependency-graph.yml` | Modified (+10) | `files_touched` amended to include
  tests/arch/test_packaging.py — TDD requires a test to prove the editable install;
  rationale recorded inline in the graph |
```

**Why This Matters**: the review rulebook makes VERIFY EVIDENCE a 🟡 REQUIRED rule precisely because downstream agents consume these tables as fact. This one is otherwise exemplary — 16 negative-space checks with reproducible commands is far above the norm — which is exactly why the single gap should be closed rather than tolerated.

---

### ISS-004: `__import__("os")` inline where a module-level import belongs 🟢 Low

**Category**: Style / Maintainability
**File**: `tests/arch/test_packaging.py:21`

**Issue**:

```python
env={**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}},
```

`__import__` is the dynamic-import escape hatch; nothing here needs it. The line also reimplements "copy the environment minus one key" the long way. Ruff does not flag it (no `PLC` rule selected), so it will survive unless a human changes it — and this file is the template the other four suite directories will copy from.

**Suggested Fix**:

```python
import os
...
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", "import eye_tracker, main; print('ok')"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
```

Behaviour is identical and the Arrange step becomes readable, which patterns §15 asks of an AAA body.

---

### ISS-005: no `__init__.py` or `conftest.py` under `tests/` — future basename collisions 🟢 Low

**Category**: Maintainability / Testing
**File**: `tests/arch/` (directory)

**Issue**:
`tests/` currently holds exactly one module and no `__init__.py` or `conftest.py`. Under pytest's default `importmode=prepend`, test modules in different directories that share a basename collide with `import file mismatch`. Patterns §15 defines **five** suite directories (`unit/`, `integration/`, `regression/`, `invariants/`, `arch/`), and same-named modules across them — `tests/unit/test_config.py` and `tests/integration/test_config.py` — are a natural naming outcome.

**Suggested Fix**: decide the convention in **Story 1.3**, which owns `tests/conftest.py` and creates the suite tree — either add `__init__.py` to each suite directory, or set `[tool.pytest.ini_options] consider_namespace_packages = true` / `importmode = "importlib"`. Recorded here so 1.3 inherits the decision rather than discovering it.

**Note**: correctly **not** actionable in this story — `tests/conftest.py` and the suite directories are on this story's OUT list.

---

### ISS-006: `ruff>=0.14,<1` does not bound the breaking changes it is meant to bound 🟢 Low

**Category**: Maintainability
**File**: `pyproject.toml:38`

**Issue**:
AC3 asks for "a bounded pin in the style already used by `requirements.txt` (explicit floor, major ceiling)", and `<1` satisfies that literally. But ruff is a **0.x** project: its breaking changes arrive in *minor* bumps, so `<1` bounds nothing in practice. This is not hypothetical — the 0.14 → 0.16 minor bump added Markdown code-fence formatting, which broke AC13 mid-story and forced Deviation 1. The developer's own Lesson 1 identifies the mechanism; the pin was left as the AC specified it.

**Suggested Fix** (for the CYCLE-5 toolchain story, not necessarily now): tighten to `ruff>=0.16,<0.17`, or pin exactly and bump deliberately. Any fresh install today lands on a version whose formatter scope differs from the one the config was written against.

**Why only Low**: the current config already absorbs the known behaviour change with a permanent, documented exclusion, and the AC's wording is what it is. Flagged so the next toolchain bump is a decision rather than a surprise.

---

## Issue Summary

| # | ID | Severity | Category | File | Status |
|---|-----|----------|----------|------|--------|
| 1 | ISS-001 | 🟠 High | Testing / Correctness | `tests/arch/test_packaging.py:32` | Should Fix (blocks approval) |
| 2 | ISS-002 | 🟡 Medium | Pattern | `pyproject.toml:147-149` | Should Fix |
| 3 | ISS-003 | 🟡 Medium | Documentation / Evidence | `docs/stories-implemented/story-1.2-review.md:323` | Should Fix |
| 4 | ISS-004 | 🟢 Low | Style / Maintainability | `tests/arch/test_packaging.py:21` | Optional |
| 5 | ISS-005 | 🟢 Low | Maintainability / Testing | `tests/arch/` | Defer to Story 1.3 |
| 6 | ISS-006 | 🟢 Low | Maintainability | `pyproject.toml:38` | Defer to CYCLE-5 |

**Summary**:
- Blockers (🔴): **0**
- High (🟠): **1**
- Medium (🟡): **2**
- Low (🟢): **3**

---

## What Was Done Well

1. ✅ **Three specification defects caught, not coded around.** `readme = "README.md"` naming a file that does not exist would have made AC5 impossible; the `max-statements` / "30 findings" mismatch would have left patterns §14 enforcing nothing; ruff 0.16's Markdown formatting made AC13 unachievable as written. Each was measured, resolved with the narrower option, and recorded with its counterfactual. This is the difference between following a spec and engineering against one.
2. ✅ **The allowlist is a work list, not a mute button.** All 18 file×rule entries carry a reason *and* a named removal cycle, and the right→left audit — every entry maps to ≥1 real finding — is what justifies dropping patterns §13's inert `gaze.py = ["PLR0915"]`. Independently reproduced: 31 findings, 11 rules, exact distribution match.
3. ✅ **The gate was proven to still fail.** Verifying `ruff check` exits 0 proves nothing on its own; adding a `print()` to a new file and observing `T201` proves the gate is alive. Confirmed here for both an application path and a test path.
4. ✅ **Zero-change proven by blob hash, not by `git diff`.** 8/8 blobs identical to HEAD is a stronger claim than a clean diff and exactly right for a cycle whose rollback contract is "revert; nothing behavioural changed".
5. ✅ **The runbook was validated by executing it** from a renamed `.venv/`, and amended from a failure actually encountered (the misleading `from versions: none` pip error, now Troubleshooting (d)). Documentation validated by reading is not validated.
6. ✅ **The FR-26 probe is formulated correctly.** A subprocess from `tmp_path` with `PYTHONPATH` stripped is the only version of this test that can detect the failure mode; an in-process `import` would have passed against the broken state.
7. ✅ **The 0% coverage figure was reported honestly** with its reasoning, rather than inflated by writing tests against another story's modules.

---

## Approval Status

**Decision**: ❌ CHANGES REQUESTED

**Reason**: Per the review rulebook's verdict table — *"CHANGES REQUESTED | Blockers or high issues exist"* — ISS-001 (🟠 High) must be resolved before approval. No 🔴 Blockers were found; the story's substance is sound and the fix is small.

**Next Steps**:
1. Fix **ISS-001** — anchor the guard test's scan root and assert a non-zero scan count (required).
2. Fix **ISS-002** — add `exclude_lines` for the main-guard per patterns §15 (recommended; cheap now, costly in CYCLE-5).
3. Fix **ISS-003** — add `docs/plans/dependency-graph.yml` to the self-review's N16 and *Files Changed* tables (recommended).
4. ISS-004 optional; **ISS-005 carried to Story 1.3**; **ISS-006 carried to CYCLE-5**.
5. Re-run `ruff check .`, `ruff format --check .` and `pytest`, paste output, and re-request review.

**Carried forward to other owners** (recorded, not absorbed):
- 🚩 **Plan owner** — the deferred one-time global `ruff format` sweep. The story requires this be raised, and it is: decide before CYCLE-2 opens, since that is when the first exclusion comes off. The `*.md` exclusion is separate and permanent.
- ⚠️ **Story 1.3** — ISS-005 (test-package layout), and the two expected `CoverageWarning`s that clear once the suite imports real code.
- ⚠️ **CYCLE-5** — ISS-006 (ruff pin band), and switching on `--cov-fail-under=85` against the denominator ISS-002 corrects.

---

## Sign-Off

**Reviewer**: REVIEWER Agent (AIRE_REVIEWER)
**Date**: 2026-08-09 16:29
**Signature**: Changes Requested — 0 🔴 / 1 🟠 / 2 🟡 / 3 🟢
