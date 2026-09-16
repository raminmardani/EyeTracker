# Evaluation Framework

## Purpose
This file defines everything that decides whether generated code is good enough to ship:

1. **The Static Eval Gate (D1–D7)** — deterministic, zero-token, blocking, scoped to changed files.
2. **The Judge Gates (J1, J2)** — LLM-as-a-Judge scores, **BLOCKING**, computed inside the automatic
   Code Review and self-healed.
3. **The scorecard** — `eval.json` + `eval-summary.md`, the evidence every downstream claim must match.

The same contract runs in **two places**: locally inside the implement workflows, and again in **CI**
on the Pull Request (`common/ci-pipeline-generation.md`). CI re-verifies; it never relaxes.

## Enforcement Mode — automatic, silent, blocking
- D1–D7 and J1/J2 run INSIDE existing steps. They add **no approval gate and no new stage**.
- A gate failure is fixed by the AI **in the same run** under the invoking workflow's
  **Self-Healing Retry Policy** — 3 attempts per loop, then HALT with the Retry-Limit Report.
- Every outcome is logged in `.spec/aire-docs/audit.md` per the invoking workflow's audit format.

---

## 1. Config resolution
Read `.evals/config.json` at the workspace ROOT. **If it does not exist, create it from the template
below** (announce it, log it in audit.md) and proceed — 🔴 never block on a missing config, and never
halt a cycle because base was not bootstrapped (`common/directory-structure.md` — Artifact Ownership).

🔴 **CREATION IS DETERMINISTIC.** Emit the template's keys in exactly the order shown, two-space
indent, trailing newline, LF endings, and **no timestamp, run id, hostname or absolute path anywhere**.
Two independent runs against the same repo must produce byte-identical files — that is what lets two
concurrent cycles both create it without conflicting. The same requirement applies to
`security-rubric.json`, `.evals/scripts/**` and `.evals/behavior/**`.

🔴 **If it already exists, use it AS-IS** — never regenerate, never reorder, never add a key that a
newer template introduced. The repo's own file wins.

```json
{
  "evalFrameworkVersion": "1.0.0",
  "scope": "changed-files",
  "retryLimitForSelfRepair": 3,
  "thresholds": {
    "lintErrorsAllowedDelta": 0,
    "typeErrorsAllowed": 0,
    "semgrepFindingsAllowed": { "critical": 0, "high": 0, "medium": 5 },
    "dependencyVulnerabilitiesAllowed": { "critical": 0, "high": 0 },
    "disallowedLicenses": ["GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL-1.0"],
    "maxCyclomaticComplexity": 12,
    "secretFindingsAllowed": 0,
    "unitTestCoverageMin": 90.0,
    "behaviorScenarioPassRateMin": 100.0,
    "llmJudgeArchitectureScoreMin": 0.85,
    "llmJudgeSecurityScoreMin": 0.85,
    "securityVulnerabilitiesAllowed": 0
  },
  "behavior": {
    "containerRuntime": "podman",
    "image": "aire-behavior:local",
    "containerfile": ".evals/behavior/Containerfile",
    "entrypoint": ".evals/behavior/run.sh",
    "_comment": "Same image + command locally and in CI. A missing runtime degrades to native execution, recorded, never blocking."
  },
  "sonarqube": {
    "enabled": false,
    "_comment": "Set true when CI generation creates sonar-project.properties and the user answers proceed at the setup gate. Additive to semgrep, never a replacement."
  },
  "judge": { "model": "<resolved session model id>", "rubricVersion": "<architecture.md version>" }
}
```

- `scope: "changed-files"` is **mandatory behaviour, not a preference**: every threshold applies ONLY
  to files this work unit changed. Repo-wide absolutes are unachievable on brownfield code and cause
  the gate to be disabled.
- `thresholds` is the **single source** for every number the gates enforce — the ≥90% coverage figure,
  the complexity cap, and the two judge minimums. Where a rule file states a number, that number is
  read from here.
- `retryLimitForSelfRepair` is the **CI** self-repair budget. The local budget is the
  Self-Healing Retry Policy's 3 attempts per SH-LOOP, defined in each implement workflow.
- 🔴 **`thresholds` is the ONLY place a number lives.** Rule files, diagrams, PR bodies and
  completion messages reference the KEY (`unitTestCoverageMin`), never the literal value. A number
  restated in a second file drifts the moment one of them changes, and then two rules disagree
  about what passes. **Diagrams and worked examples may show the current value** (a flowchart
  reading `coverage < unitTestCoverageMin` is unreadable) — they illustrate, they do not enforce.
  Any rule that DECIDES pass/fail must reference the key.
- 🔴 **Lowering a threshold to pass a gate is forbidden** (SH-6). Thresholds change only as a
  deliberate, announced, audited decision — never inside a remediation attempt.

---

## 2. The Static Eval Gate — D1–D7

| # | Check | Blocking condition | Tooling by stack (use what the repo already has) |
|---|---|---|---|
| D1 | Lint | new errors on changed files > `lintErrorsAllowedDelta` | ESLint / Ruff / Checkstyle / golangci-lint / dotnet format |
| D2 | Type check | errors > `typeErrorsAllowed` | `tsc --noEmit` / mypy / compiler / `go vet` |
| D3 | Static security scan | findings above `semgrepFindingsAllowed` by severity, **or** a failed SonarQube Quality Gate when enabled | `semgrep --config auto` (always) · the stack's SAST (bandit, gosec, SpotBugs) · **SonarQube** when configured |
| D4 | Dependency vulnerabilities | above `dependencyVulnerabilitiesAllowed` | `npm audit --json` / `pip-audit` / `osv-scanner` / `mvn dependency-check` |
| D5 | Licence scan | any dependency matching `disallowedLicenses` | `license-checker` / `pip-licenses` / `go-licenses` |
| D6 | Cyclomatic complexity | any CHANGED function > `maxCyclomaticComplexity` | ESLint `complexity` / radon / PMD / gocyclo |
| D7 | Secret scan (diff only) | findings > `secretFindingsAllowed` | `gitleaks detect` / `git secrets`, else a regex sweep of the diff |

### 2.1 Security: three layers, deliberately overlapping

D3 is the deterministic layer. It does **not** stand alone:

| Layer | What it catches | Blocking |
|---|---|---|
| **semgrep + stack SAST** (D3) | Known-dangerous code shapes — injection, disabled verification, weak crypto | ✅ always |
| **SonarQube** (D3, when configured) | The above plus the project's own Quality Gate: security hotspots, reliability, duplication | ✅ when `sonarqube.enabled` |
| **Security Baseline review** (Code Review Phase 2.5) | The 16 SECURITY-NN rules judged semantically against the diff — design-level flaws no pattern matcher sees (missing authorisation, broken access control, PII in logs) | ✅ 🔴/🟠 on the changed surface |

🔴 **SonarQube is additive and optional; the other two are not.** A repo with no SonarQube server is
still fully gated. AIRE nonetheless generates `sonar-project.properties` and the wired scan steps up
front, then asks the user for the two values only they can supply — see
`common/ci-pipeline-generation.md` Section 4.1.

### 2.2 Baseline → diff mechanics (this is what makes the gate usable)
The gate is evaluated on the **delta**, exactly like the regression gate:

1. **BASELINE** — at the branch checkpoint, **before any code is generated**, run D1–D7 and save the
   raw output to `<evidence-dir>/static/baseline/`. Pre-existing findings are recorded and then
   **ignored forever** — they define "already broken". Do not fix them, do not block on them.
2. **POST-CHANGE** — after the Full Regression gate, re-run D1–D7 and save to `<evidence-dir>/static/`.
3. **DIFF** — only findings that are **NEW versus the baseline, on files this work unit changed**,
   count against the thresholds. Fix them in the same run, re-run, re-diff, until the diff is clean —
   bounded by that loop's 3-attempt budget.

🔴 **Match findings on `(rule-id, file, message)` — NEVER on line number.** Unrelated edits shift
line numbers, so a pre-existing finding that moves from `main.py:12` to `main.py:39` is the SAME
finding. Matching on position re-blames old debt on whoever touched the file.

🔴 **CI RUNS THE SAME DIFF, NOT A STRICTER CHECK.** `scope: "changed-files"` binds the pipeline
exactly as it binds the local gate. Both invoke the SAME script — `.evals/scripts/run-static-evals.*`
(`common/ci-pipeline-generation.md` Section 4.0b) — so the diff logic exists in one place and cannot
drift. A CI step that runs a tool bare over the whole tree (`semgrep … --error`, `mypy src/`) has no
baseline, fails on pre-existing debt, and contradicts this section. That is a generation defect, not a
stricter policy.

🔴 **Changed-file scoping is NOT a substitute for the baseline diff.** Running a tool only on changed
files still fails on a pre-existing finding that happens to live in one of them. Scoping narrows
*where to look*; the baseline diff decides *who is responsible*. Both are required.

🔴 **Never suppress a finding to pass the gate** — no blanket `eslint-disable`, no `# nosec`,
no `# type: ignore`, no adding a package to an ignore list, no widening `disallowedLicenses`, no
marking a SonarQube issue "won't fix". That is the exact analogue of deleting a failing test to go
green and is equally forbidden. Fix the code.

### 2.3 🔧 Tooling Bootstrap (MANDATORY — runs BEFORE the baseline, never after)

🔴 **REUSE THE PROJECT'S EXISTING ENVIRONMENT. NEVER CREATE A SECOND ONE.** Before installing
anything or creating a virtual environment, search the repo for one that already exists and use it:

| Look for | Typical locations |
|---|---|
| Python venv | `.venv/`, `venv/`, `<code-root>/.venv/`, `$VIRTUAL_ENV`, `poetry env info -p`, `pipenv --venv` |
| Node modules | `node_modules/`, workspace roots named in `package.json` `workspaces` |
| Other | `.tool-versions`, `.nvmrc`, `Makefile` targets, a devcontainer, an existing `Containerfile` |

🔴 **Search the code root as well as the repo root.** A monorepo commonly keeps its environment at
`src/backend/.venv`, not at the top level. Creating `.venv-<story>` beside it wastes minutes,
installs a divergent tool set, and means the gates measure a different environment than the developer
does — which is how a gate passes locally and fails in CI.

Create a new environment **only** when the search finds none. Announce which environment was reused or
created, and record it in the evidence manifest.

**A check with no config in the repo is not "N/A" — it is "not set up yet".** Before the BASELINE
run, detect what is missing and **create the missing configuration**, so the gate has something real
to measure.

🔴 **ORDERING IS NOT OPTIONAL — bootstrap → baseline → generate code → post-change → diff.**
If a config were created *after* the baseline, the two runs would be measured under **different
rules**, and every finding the new config surfaces on pre-existing code would be attributed to this
work unit. The diff would be garbage and the gate would block on debt it did not create.

**Per check, resolve in this order:**

1. **Config present** (`eslint.config.*`, `.eslintrc*`, `ruff.toml`, `pyproject.toml [tool.*]`,
   `tsconfig.json`, `.gitleaks.toml`, `checkstyle.xml`, `.golangci.yml`, `sonar-project.properties`,
   a `package.json` lint/type script, …) → 🔴 **USE IT AS-IS.** The repo's own standards win. Never
   override, never "upgrade", never add rules to it.
2. **Config missing, tool standard for the detected stack** → **create a minimal config** (table
   below), invoke the tool through the stack's own runner (`npx`, `pipx run`, `go run`, the build
   plugin), and announce what was created.
3. **Genuinely no tool for this stack / offline / no package manager** → record `"status": "N/A"` in
   `eval.json` with the reason and **surface it to the user**. 🔴 **Never a silent skip.**

**What to create when it's missing** — the *recommended* preset, never the strictest:

| Check | Create if missing (stack-appropriate) |
|---|---|
| D1 Lint | `eslint.config.js` extending the recommended set · `ruff.toml` with the default rules · `.golangci.yml` with default linters · `checkstyle.xml` from the standard preset |
| D2 Type check | `tsconfig.json` with `strict` **off** unless the repo already types strictly · `mypy.ini` at default |
| D3 SAST | rely on `semgrep --config auto`; write `.semgrepignore` only for genuine build/vendor dirs. SonarQube: only when its secrets exist |
| D4 SCA | none needed — works off the lockfile |
| D5 Licence | the `disallowedLicenses` list already in `.evals/config.json` |
| D6 Complexity | enable the linter's own complexity rule at `maxCyclomaticComplexity` |
| D7 Secrets | `.gitleaks.toml` from the tool's default ruleset |
| **Behavioural runner** | the stack's Cucumber-family runner + a minimal config — see `common/behavior-spec.md` Section 4.2 |

🔴 **Recommended presets, NOT strict/all.** Turning on every rule in a brownfield repo produces a
baseline with thousands of findings and buries the handful this work unit actually introduced.

🔴 **Never write a config that pre-suppresses findings** — no seeded `ignorePatterns` beyond real
build output, no `rules: { …: "off" }` for a rule the preset enables, no `--exclude` of the source
tree. Bootstrapping makes the check *runnable*, never *passable*.

**Record it**: every config created (path + tool + preset) goes in `eval.json` under `"bootstrap"`, in
`eval-summary.md`, and in `audit.md`. **Announce it** — it adds files to the user's repo.

**Idempotent**: on later work units the configs exist, so rule 1 applies and nothing is recreated.

### 2.4 🔴 Tool Installation — every gate must have its tool BEFORE the baseline runs

A config without its tool is useless. Before the baseline capture, confirm every tool required by
D1–D7, the test runners, the coverage reporter, the behavioural runner, and the judge is installed
and invocable. 🔴 A missing tool is **not** `N/A` — it is incomplete setup, which is an **ERROR**
(Section 2.5.2 defines exactly which `N/A` reasons are legitimate).

#### 2.4.1 🔴 INSTALL IS RETRIED UNTIL IT SUCCEEDS — the gate waits for its tool, never skips it

A gate without its tool does not become inapplicable; it becomes **unmeasured**. So bootstrap does not
"try once and record N/A" — it works through a fallback chain, with a retry budget, and **stops the run**
if it cannot get there. Identical locally and in CI.

**Per tool, in order. Move to the next rung only when the current one fails:**

| # | Rung | Example |
|---|---|---|
| 1 | **Already present** — PATH, `node_modules/.bin`, the project venv | `command -v semgrep` |
| 2 | **Project package manager** | `npm i -D eslint` · `pip install semgrep` · `go install` |
| 3 | **Alternative installer** | `pipx run` · `npx --yes` · `brew` · the vendor's install script |
| 4 | 🔴 **OCI image via Podman** — the rung that makes "unavailable" almost impossible | `podman run --rm -v "$PWD:/src:Z" -w /src docker.io/semgrep/semgrep semgrep --config auto` |
| 5 | **ERROR — stop the run** | only after 1–4 have all been attempted and recorded |

**Retry budget**: each rung gets **3 attempts** with backoff before moving to the next. Most install
failures in CI are transient — a registry timeout, a rate limit, a mirror hiccup — and a single failed
attempt must never be allowed to disable a gate for the whole run.

**Verify after every successful install** (V16): run the tool's version command and require exit 0. A
binary that installs but cannot execute (wrong architecture, missing shared object) is worse than one
that is absent, because it crashes mid-gate and leaves a partial `eval.json`.

🔴 **Rung 4 is not optional.** Podman is already required for the behaviour gate, so a container image
is always available as a route. Every D1–D7 tool ships one — `semgrep/semgrep`,
`zricethezav/gitleaks`, `aquasec/trivy`, `returntocorp/…`, plus the language base images for the rest.
**Recording `N/A` without having tried the container route is a bootstrap failure, not an N/A.**

**When the whole chain is exhausted:**

```
TOOL BOOTSTRAP FAILED — <tool> for <gate>

  Rung 1 already present ....... not found
  Rung 2 <pkg manager cmd> ..... failed 3/3 — <last error>
  Rung 3 <alt installer cmd> ... failed 3/3 — <last error>
  Rung 4 podman <image> ........ failed 3/3 — <last error>

<gate> cannot be measured. This is an ERROR, not N/A.
The run stops here — a gate that never ran must not be reported as passing or inapplicable.
```

🔴 **Then HALT.** Do not continue to the baseline, do not record `N/A`, do not proceed to code
generation. An unmeasured gate silently removes a check from every later comparison in the cycle.

🔴 **In CI this must never happen.** The generated workflow installs and verifies every tool it uses
(V16), and the runner has a package manager, network and Podman. `"<tool> not installed"` inside a CI
run is a **pipeline defect to fix**, never a result to accept.

**Complete tool table — install what the detected stack needs, BOTH locally AND in CI:**

| Gate / Purpose | JS/TS | Python | Java/Kotlin | Go | .NET |
|---|---|---|---|---|---|
| **D1 Lint** | `eslint` or `biome` | `ruff` | `checkstyle` / `spotless` | `golangci-lint` | `dotnet format` (built-in) |
| **D2 Type check** | `typescript` (`tsc`) | `mypy` | compiler (built-in) | `go vet` (built-in) | compiler (built-in) |
| **D3 SAST** | `semgrep` (always) | `semgrep` + `bandit` | `semgrep` + `spotbugs` | `semgrep` + `gosec` | `semgrep` + `security-scan` |
| **D4 SCA** | `npm audit` (built-in) | `pip-audit` | `mvn dependency-check` / `osv-scanner` | `osv-scanner` | `dotnet list package --vulnerable` |
| **D5 Licence** | `license-checker` | `pip-licenses` | `license-maven-plugin` | `go-licenses` | `nuget-license` |
| **D6 Complexity** | eslint `complexity` rule | `radon` | PMD | `gocyclo` | roslyn analyzers |
| **D7 Secrets** | `gitleaks` (binary or container) | `gitleaks` | `gitleaks` | `gitleaks` | `gitleaks` |
| **Unit tests** | `jest` / `vitest` | `pytest` | `mvn test` / `gradle test` | `go test` | `dotnet test` |
| **Coverage** | `c8` / `istanbul` / vitest built-in | `pytest-cov` | `jacoco` | `-coverprofile` (built-in) | `XPlat Code Coverage` |
| **Behavioural (Gherkin)** | `cucumber-js` | `pytest-bdd` (🔴 not `behave` — see `common/behavior-spec.md` Section 4.1) | `cucumber-jvm` | `godog` | `reqnroll` |
| **Container runtime** | `podman` | same | same | same | same |
| **J1/J2 judge** | Claude Code CLI (`@anthropic-ai/claude-code`) | same | same | same | same |

🔴 **Verify each tool is callable after installation.** Run a version/help command (e.g.
`semgrep --version`, `gitleaks version`, `mypy --version`) and confirm a zero exit code. A tool that
installed but cannot execute (wrong platform binary, missing shared library) is worse than a missing
tool — it crashes mid-gate and produces a partial `eval.json`.

🔴 **Install BEFORE the baseline, not between baseline and post-change.** A tool installed after the
baseline means the baseline was measured without it and the diff is invalid — same ordering rule as
config bootstrap (Section 2.3).

🔴 **The CI pipeline must install the SAME tools.** See `ci-pipeline-generation.md` Section 3.1 for the
CI-specific installation requirements. A tool present locally but absent in CI produces a gate that
passes locally and fails (or silently skips) in CI — the worst drift.

**Record it**: list every tool installed (name + version) in `eval.json` under `"toolchain"` and in
`audit.md`. A gate result without its tool version is not reproducible.

---

### 2.5 🔴 `N/A` DISCIPLINE — a closed list, and "yet" is never on it

`N/A` removes a gate from the verdict. It is therefore the easiest way to make a pipeline look green
while measuring nothing, and it must be spent from a **closed list of reasons**.

#### 2.5.1 The ONLY legitimate reasons for `N/A`

| # | Reason | Example |
|---|---|---|
| 1 | The check **cannot apply to this stack** | D2 type check on plain JavaScript with no type checker in the ecosystem |
| 2 | The check **does not apply to this work unit** | `apiContract` when the plan has no API-layer step; `behaviorB3` when this is not the last work unit |
| 3 | The tool **genuinely does not exist** for this stack — 🔴 valid ONLY after the full Section 2.4.1 chain, **including the Podman image rung**, has been attempted and recorded | a licence scanner for a niche language, with all four rungs shown as tried |

Each must name the **concrete fact** that makes it inapplicable — the stack, the plan step, the tracker
state. `"reason": "project is plain JavaScript; no type checker applies"` is a reason.

#### 2.5.2 🔴 FORBIDDEN reasons — every one of these is `ERROR`, and ERROR fails the job

Anything meaning *"the work to make this check run has not been done"* is **incomplete setup, not an
inapplicable check**. Observed verbatim in a real run, all forbidden:

- ✗ `"no baseline diff configured yet"`
- ✗ `"scanner not fully wired yet"`
- ✗ `"no licence scanner bootstrapped yet"`
- ✗ `"complexity rule not enabled yet"`
- ✗ `"gitleaks not installed"`
- ✗ anything containing **"yet"**, "TODO", "not wired", "not bootstrapped", "not implemented",
  "pending", "future"

🔴 **The word "yet" is the tell.** It admits the check *should* run and doesn't. Section 2.3 exists
precisely to make it run: create the missing config **before** the baseline, then measure. Deferring
that work and recording `N/A` converts a mandatory gate into decoration.

**Specifically, these are never `N/A`:**

| Check | Why it must run |
|---|---|
| D4 SCA | `npm audit` / `pip-audit` / `osv-scanner` need **no config** — they read the lockfile |
| D5 Licence | The `disallowedLicenses` list is already in `.evals/config.json` |
| D6 Complexity | Enable the linter's own complexity rule at `maxCyclomaticComplexity` (Section 2.3) |
| D7 Secrets | `gitleaks` installs with one command; in CI the install step is generated (V16) |
| D1 Lint | Bootstrap the recommended preset (Section 2.3) |

🔴 **A missing tool in CI is a pipeline defect, not an `N/A`.** The generated workflow installs and
verifies every tool it uses (V16). `"gitleaks not installed"` inside a CI run means the install step is
missing — fix the pipeline; do not record the gate as inapplicable.

#### 2.5.3 🔴 The log and the artifact must say the same thing

Observed in the same run: the log printed `gitleaks not installed — D7 recorded N/A` while `eval.json`
recorded `"D7_secrets": {"status": "PASS", "findings": 0}`.

That is the most dangerous defect in this document: **the artifact claims a passing gate that never
ran**, and the artifact is what the scorecard, the PR body and every downstream reader trust. Whatever
a script prints about a gate MUST equal what it writes for that gate. When they disagree, the run is
invalid — fix the script, never reconcile by hand.

#### 2.5.4 🔴 `overall` must disclose coverage

`"overall": "PASS"` with five of seven checks `N/A` is not a pass; it is two checks passing. Report it
honestly:

```json
{ "overall": "PASS", "checksRun": 2, "checksTotal": 7,
  "checksNA": ["D1_lint", "D2_typecheck", "D4_sca", "D5_license", "D6_complexity"] }
```

and in the summary line: `Static Eval: PASS (2 of 7 checks ran — 5 N/A, see reasons)`.
🔴 Never print a bare `PASS` that implies full coverage, and never append a softener like
*"N/A checks await tool bootstrap"* — under 2.4.2 that sentence is itself the admission that the run
should have failed.

---

## 3. Rubric derivation (for J1)

🔴 `architecture-rubric.json` is derived **mechanically from
`.spec/architecture.md` Section 10 Verifiable Constraints** — one constraint, one criterion, same
weights, same wording. Never hand-written, never generic, never borrowed.

The full contract lives in **`implementation/architecture-doc.md` Section 3–Section 4**. Summary:

- **Derive** at the STOP CHECKPOINT, immediately after `architecture.md` is written, before the design
  commit. Write to `.evals/rubrics/architecture-rubric.json` with `rubricVersion` **equal to the
  `architecture.md` version**. Commit both together.
- **Regenerate** whenever `architecture.md` changes, bumping both versions.
- 🔴 **Never hand-edit the rubric** — edit Section 10 and regenerate. A hand-edited rubric cannot be traced
  to an approved decision, and J1 is blocking.

**Fallback chain** (bug/enhancement flows skip most design stages, so there is often nothing to
derive from). Resolve in order and record which link was used in `eval.json`:

1. This cycle's `architecture.md` Section 10.
2. A versioned rubric already committed at `.evals/rubrics/architecture-rubric.json` from a prior
   cycle — usable only if the reverse-engineering artifacts still describe the same architecture.
3. Derive from **Atlas** existing-system truth (`common/helix-atlas-integration.md`) or, if Atlas is
   unavailable, from `.spec/aire-docs/planning/reverse-engineering/`.
4. **J1 = `N/A`**, with the reason recorded. **When J1 is `N/A` it does not block** — an absent
   rubric must never fail a work unit.

🔴 **Never score J1 against an absent, generic, or unrelated rubric.** An ungrounded architecture
score that blocks a PR is worse than no score at all.

`security-rubric.json` (for J2) is derived from the **OWASP Top 10:2025** and the project's own
security context. Generated at the STOP CHECKPOINT alongside the architecture rubric. Map the
OWASP Top 10:2025 categories applicable to the detected stack:

| ID | OWASP 2025 | Category |
|---|---|---|
| A01 | Broken Access Control | Endpoints, resource ownership, RBAC |
| A02 | Security Misconfiguration | CORS, headers, debug modes, defaults |
| A03 | Software Supply Chain Failures | Dependencies, build integrity, CI/CD |
| A04 | Cryptographic Failures | Secrets, TLS, hashing, key management |
| A05 | Injection | SQL, NoSQL, OS command, LDAP, template |
| A06 | Insecure Design | Threat modelling gaps, missing controls |
| A07 | Authentication Failures | Passwords, sessions, brute-force, MFA |
| A08 | Software or Data Integrity Failures | Deserialization, unsigned updates |
| A09 | Security Logging and Alerting Failures | Audit trails, sensitive data in logs |
| A10 | Mishandling of Exceptional Conditions | Error disclosure, uncaught exceptions |

Each criterion's `prompt` states the exact code pattern that scores 0 in a diff.
Weights sum to 1.0, biased toward the categories the stack is most exposed to.
Exclude categories the stack genuinely cannot exercise.
Create or regenerate it whenever the stack or the security context changes.

---

## 4. Judge gates — J1 and J2 (🔴 BLOCKING)

Computed **once per Code Review pass, inside the automatic Code Review, and nowhere else** — from the
work unit's diff plus the rubrics.

| # | Score | Blocking minimum | What it covers |
|---|---|---|---|
| J1 | Architecture conformance | `llmJudgeArchitectureScoreMin` (0.85) | Weighted score over the `architecture.md` Section 10 criteria — transaction boundaries, layering, module boundaries, secret/PII handling |
| J2 | Security (OWASP 2025) | `llmJudgeSecurityScoreMin` (0.85) | OWASP Top 10:2025 categories applicable to the stack — broken access control, security misconfiguration, supply chain failures, cryptographic failures, injection, insecure design, authentication failures, data integrity failures, logging failures, mishandling of exceptional conditions |

Each score is `0.0`–`1.0`, written with its **per-criterion breakdown** to
`<evidence-dir>/judge/architecture-score.json` and `<evidence-dir>/judge/security-score.json`.

Record the **pinned judge model** and the **`rubricVersion`** with every score. A score without both
is not comparable across runs, because changing either silently re-scores every work unit.

### 4.1 Scoring procedure

1. Score **once** per review pass. One score, one verdict — no averaging, no re-rolls to get a better
   number. 🔴 Re-scoring the same diff until it passes is result-shopping and is forbidden.
2. Score **each criterion independently** against its `prompt`, then compute the weighted total.
3. **Every criterion scoring below 1.0 must cite `file:line` and state what violates it.** A low score
   with no citation is not actionable and cannot be remediated — treat an uncited criterion score as
   a defect in the judging pass and re-run that criterion.
4. **Score only what the diff shows.** Never mark a criterion down for code this work unit did not
   touch — that is the same delta principle as Section 2.2.
5. A criterion that this work unit's diff cannot exercise scores **`N/A` and is excluded from the
   weighted total**, with the remaining weights renormalised to 1.0. 🔴 Never score an inapplicable
   criterion 0.

### 4.2 🔁 JUDGE GATE SELF-HEAL — SH-LOOP-6

**Verification that must pass**: `J1 ≥ llmJudgeArchitectureScoreMin` **and**
`J2 ≥ llmJudgeSecurityScoreMin` (a score of `N/A` passes).

1. **Below minimum** → self-heal. Remediation targets **the specific criteria that scored below 1.0**,
   worst weighted-loss first, using their cited `file:line`. Fix the code so the constraint holds.
2. Re-run the affected gates the fix touched (unit tests, regression) in the same attempt, then
   re-score in the next Code Review pass.
3. 🔁 **This is SH-LOOP-6 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT
   and emit the Retry-Limit Report**, naming each failing criterion, its weight, its citation, and
   what the three attempts changed.
4. 🔴 **Forbidden ways to pass this gate** (all are SH-6 violations):
   - editing `.spec/architecture.md` Section 10 to weaken or delete a constraint,
   - editing `.evals/rubrics/architecture-rubric.json` directly,
   - lowering `llmJudgeArchitectureScoreMin` / `llmJudgeSecurityScoreMin`,
   - re-scoring until a run happens to clear the bar,
   - marking a genuinely applicable criterion `N/A`.

   The architecture document changes only when the **design decision** changed — never because a score
   did not clear. See `implementation/architecture-doc.md` Section 5.

### 4.3 Why blocking, and what that costs

LLM scores vary run to run. Blocking on them is a deliberate trade: an architecture violation that a
linter cannot see — a transaction split across two commits, a raw query in a controller, a token in a
log line — is exactly the class of defect that survives every deterministic gate and reaches
production. J1 is the only gate that catches it.

The variance is contained by the design of the rubric, not by softening the gate:
- criteria are **binary and citable** (`score 0 if X appears in the diff`), not aesthetic judgements;
- criteria are **derived from an approved document**, so the bar is one a human already agreed to;
- a criterion the diff cannot exercise is `N/A`, so a work unit is never judged on absent code;
- the 3-attempt cap means a genuinely borderline score surfaces to a human rather than looping.

🔴 If a criterion proves unjudgeable in practice — it fires inconsistently on equivalent code — the
fix is to **rewrite the constraint in `architecture.md` Section 10 to be checkable**, as an announced,
audited amendment. Not to remove the gate.

---

## 5. Gate inventory — what blocks, and where it is enforced

| Gate | Local loop | CI stage | Blocks |
|---|---|---|---|
| D1–D7 static | SH-LOOP-4 | 1 | ✅ |
| Unit tests + coverage | SH-LOOP-1 | 2 | ✅ |
| Behavioural **B1** — this unit | SH-LOOP-7 | 2 | ✅ |
| Behavioural **B2** — cumulative (every other feature file) | SH-LOOP-7 | 2 | ✅ |
| Behavioural **B3** — epic scope (last work unit only) | SH-LOOP-8 | 2 (epic PR) | ✅ |
| API & contract | SH-LOOP-2 | 2 | ✅ (when applicable) |
| Full regression | SH-LOOP-3 | 2 | ✅ |
| J1 architecture | SH-LOOP-6 | 3 | ✅ (unless `N/A`) |
| J2 security (OWASP) | SH-LOOP-6 | 3 | ✅ |
| Code review findings (🔴/🟠) | SH-LOOP-5 | — | ✅ |

`verdict` is `PASS` only when **every** gate is `PASS` or `N/A`. There is no weighted composite — one
gate's failure is never offset by another's success.

---

## 6. Evidence and output

`<evidence-dir>` = `.spec/aire-docs/implementation/code/eval-evidence/<key>/`, where `<key>` is:
- `story-[N.M]` — epic flow (`dev-implement`)
- `bug-[TICKET-ID]` — bug flow (`bug-fix-implement`)
- `enhancement-[TICKET-ID]` — enhancement flow (`enhancement-implement`)

```text
<evidence-dir>/
├── eval.json            # machine-readable scorecard
├── eval-summary.md      # human-readable scorecard (goes into the PR body)
├── static/              # post-change raw tool output (lint, typecheck, sast, sca, license, complexity, secrets)
│   └── baseline/        # the pre-change run of the same tools
└── judge/               # architecture-score.json, security-score.json (with per-criterion breakdown)
```

### 6.1 `eval.json` (example format)

```json
{
  "key": "story-1.2", "trackerId": "PROJ-102",
  "evalFrameworkVersion": "1.0.0", "rubricVersion": "1.2.0",
  "judgeModel": "<pinned model id>", "scope": "changed-files", "changedFiles": 7,
  "bootstrap": {
    "created": [
      { "check": "D1_lint", "path": "eslint.config.js", "tool": "eslint", "preset": "recommended" }
    ],
    "reused": [
      { "check": "D2_typecheck", "path": "tsconfig.json", "note": "repo's own config, used as-is" }
    ]
  },
  "gates": {
    "D1_lint":        { "status": "PASS", "newFindings": 0 },
    "D2_typecheck":   { "status": "PASS", "errors": 0 },
    "D3_sast":        { "status": "PASS", "new": { "critical": 0, "high": 0, "medium": 2 },
                        "sonarqube": { "enabled": true, "qualityGate": "PASS" } },
    "D4_sca":         { "status": "PASS", "new": { "critical": 0, "high": 0 } },
    "D5_license":     { "status": "PASS", "violations": [] },
    "D6_complexity":  { "status": "PASS", "maxChanged": 9, "threshold": 12 },
    "D7_secrets":     { "status": "PASS", "findings": 0 },
    "unitCoverage":   { "status": "PASS", "value": 93.4, "threshold": 90.0 },
    "behaviorB1":    { "status": "PASS", "scenarios": "12/12", "acsCovered": "5/5",
                        "containerised": true, "image": "aire-behavior:local@sha256:…" },
    "behaviorB2":    { "status": "PASS", "scenarios": "48/48", "featureFiles": 4 },
    "behaviorB3":    { "status": "N/A",  "reason": "not the last work unit — 2 stories still open (1.4, 1.5)" },
    "apiContract":    { "status": "PASS", "endpoints": 3 },
    "regression":     { "status": "PASS", "newFailures": 0 },
    "J1_architecture":{ "status": "PASS", "score": 0.91, "min": 0.85,
                        "rubricSource": "architecture.md#10",
                        "criteria": [
                          { "id": "ARCH-01", "weight": 0.40, "score": 1.0 },
                          { "id": "ARCH-02", "weight": 0.35, "score": 0.8,
                            "citation": "src/api/billing.ts:88", "note": "direct ORM call in handler" },
                          { "id": "ARCH-03", "weight": 0.25, "score": 1.0 }
                        ] },
    "J2_security":        { "status": "PASS", "score": 0.92, "min": 0.85,
                        "criteria": [
                          { "id": "SEC-01", "owasp": "A01:2025", "weight": 0.20, "score": 1.0 },
                          { "id": "SEC-02", "owasp": "A05:2025", "weight": 0.20, "score": 0.8,
                            "citation": "src/api/users.ts:44", "note": "unsanitised input in query builder" },
                          { "id": "SEC-03", "owasp": "A04:2025", "weight": 0.15, "score": 1.0 },
                          { "id": "SEC-04", "owasp": "A07:2025", "weight": 0.15, "score": 1.0 },
                          { "id": "SEC-05", "owasp": "A02:2025", "weight": 0.15, "score": 0.9,
                            "citation": "src/config/cors.ts:12", "note": "wildcard origin in non-dev env" },
                          { "id": "SEC-06", "owasp": "A09:2025", "weight": 0.15, "score": 1.0 }
                        ] }
  },
  "selfHealing": {
    "SH-LOOP-1": { "attempts": 1, "budget": 3 },
    "SH-LOOP-6": { "attempts": 0, "budget": 3 },
    "SH-LOOP-7": { "attempts": 0, "budget": 3 },
    "SH-LOOP-8": { "attempts": 0, "budget": 3 }
  },
  "verdict": "PASS"
}
```

🔴 `J1_architecture` and `J2_security` live under **`gates`**, not a separate `scores` block —
they decide the verdict like every other gate.

### 6.2 `eval-summary.md` — the scorecard that travels into the PR body (example format)

**Format is fixed.** One table, one row per gate, in gate-inventory order (Section 5). This is the artifact
the PR body, the tracker comment and the completion message all quote — every figure they state must
match this table exactly.

```markdown
### 🎯 Eval Scorecard — Story 1.2 · **PASS**

| Gate | Result | Threshold | Status |
|---|---|---|---|
| D1 Lint | 0 new findings | ≤ 0 delta | ✅ PASS |
| D2 Type check | 0 errors | 0 | ✅ PASS |
| D3 Static security | 0C / 0H / 2M · SonarQube gate PASS | 0C / 0H / ≤5M | ✅ PASS |
| D4 Dependencies | 0C / 0H | 0C / 0H | ✅ PASS |
| D5 Licences | 0 violations | none disallowed | ✅ PASS |
| D6 Complexity | max 9 | ≤ 12 | ✅ PASS |
| D7 Secrets | 0 findings | 0 | ✅ PASS |
| Unit coverage | 93.4% | ≥ 90.0% | ✅ PASS |
| Behavioural B1 (this story) | 12/12 scenarios · 5/5 ACs · podman | 100% | ✅ PASS |
| Behavioural B2 (cumulative) | 48/48 scenarios · 4 feature files | 100% | ✅ PASS |
| Behavioural B3 (epic scope) | not the last story — 1.4, 1.5 still open | last unit only | ⚪ N/A |
| API & contract | 3/3 endpoints | all applicable | ✅ PASS |
| Regression | 0 new failures | 0 | ✅ PASS |
| J1 Architecture | 0.91 | ≥ 0.85 | ✅ PASS |
| J2 Security (OWASP 2025) | 0.92 | ≥ 0.85 | ✅ PASS |

**Verdict**: PASS · judge `<model>` · rubric v1.2.0 (from `architecture.md` v1.2.0)
**Self-healing**: SH-LOOP-1 1/3 · all other loops 0/3


```

**Formatting rules:**
- Status is exactly one of `✅ PASS`, `❌ FAIL`, `⚪ N/A` — an `N/A` row **must** carry its reason in
  the Result column.
- A `FAIL` row is never omitted or softened; the table shows the failing state that halted the run.
- The J1 breakdown is always present when J1 was scored, including on a PASS. A criterion that scored
  below 1.0 without a citation is a defect (Section 4.1 rule 3).
- The J2 security breakdown is always present when J2 was scored, including its OWASP category per criterion.
- Bootstrap additions, when any occurred, are appended as a short `**Bootstrapped**:` line.

🔴 **Every figure quoted downstream** — completion message, Code Review report, PR body, tracker
comment — **MUST match this table.** A mismatch is a gate failure. The artifact is the source of
truth; the claim is not.

---

## 7. Where this file is invoked

| Flow | Bootstrap + baseline D1–D7 | Static Eval Gate | J1 + J2 | Rubric derivation |
|---|---|---|---|---|
| `dev-implement` | Step 1.5 Item 4.6 | Step 6.6 | Section A Auto Code Review (blocking) | STOP CHECKPOINT, from `architecture.md` Section 10 |
| `bug-fix-implement` | Step 3 Item 5 | Step 7.5 | Step 8a (blocking) | Fallback chain Section 3 |
| `enhancement-implement` | Step 10 | Step 14.5 | Step 15a (blocking) | Fallback chain Section 3 |
| `code-review` standalone | — | — | Recomputed and reported for the scope reviewed | — |
| **CI pipeline** | — (runs on a clean checkout) | Stage 1 | Stage 3 (blocking) | — (reads the committed rubric) |

The bootstrap (Section 2.3) always runs **in the same step as the baseline**, immediately before it, in all
three local flows — never as a separate stage and never after code generation.

`ticket-implement` is a router and invokes nothing directly.

---

## 8. Failure policy

| Situation | Behaviour |
|---|---|
| A D-gate fails on a NEW finding | Fix in the same run under SH-LOOP-4, re-run, re-diff. No user prompt. |
| A D-gate finding exists at baseline | Recorded, ignored, never blocking — **locally AND in CI**. Reported as non-blocking information so the debt stays visible. |
| CI fails on a finding the local gate passed | 🔴 A generation defect in the pipeline, not a real regression. The CI step is running the tool without a baseline. Fix it to call `run-static-evals.*` (`ci-pipeline-generation.md` Section 4.0b) — never "fix" pre-existing debt to appease a blunt CI command, and never lower a threshold. |
| **J1 or J2 below its minimum** | **Blocks.** Remediate the cited criteria under SH-LOOP-6, re-score on the next review pass. On 3 exhausted attempts: HALT with the Retry-Limit Report. |
| **J1 is `N/A`** (no derivable rubric) | Does **not** block. Recorded with the reason and the fallback-chain link that bottomed out. |
| A criterion scores low with no citation | Defect in the judging pass — re-run that criterion. Never remediate an uncited score. |
| A **B1 or B2** scenario fails | Fix the code under SH-LOOP-7 (3 attempts). Never edit or skip the scenario. A B2 failure is still THIS unit's problem — it turned that scenario red. |
| A **B3** scenario fails | Fix under SH-LOOP-8 — its own separate 3-attempt budget, because an epic-scope failure is usually an integration gap between units, not a bug inside one. |
| B3 would run but other work units are still open | `N/A — deferred`, naming the open units. 🔴 Never reported as a pass. |
| Podman is not installed | The ONE case where a behaviour tier may run natively. Record `"containerised": false, "reason": "podman not installed"` — that exact reason — and mark the tier `PASS (unverified parity)`. 🔴 Never fall back to the Docker CLI. 🔴 Any other justification for skipping the container ("no browser needed", "backend only", "faster natively") is a **gate violation**, not a pass (`common/behavior-spec.md` Section 5.1). 🔴 In CI this must never occur. |
| The auto-remediate loop keeps finding issues | Loops under SH-LOOP-5, max 3 rounds, then HALT. |
| A check has no config in the repo | **Not `N/A` — bootstrap it** (Section 2.3) before the baseline, announce it, commit it. |
| A check's config already exists | Use it as-is. Never override, upgrade, or add rules. |
| A tool is missing | 🔴 **Install it** — work the Section 2.4.1 chain (present → package manager → alternative installer → **Podman image**), 3 attempts per rung. Never record `N/A` before the container rung has been tried. |
| The whole install chain is exhausted | 🔴 **ERROR — HALT the run** with the per-rung report. Not `N/A`, not a pass. An unmeasured gate silently drops a check from every later comparison in the cycle. |
| A check is recorded `N/A` because its setup was deferred ("not configured **yet**", "scanner not wired", "gitleaks not installed") | 🔴 **ERROR, and the job fails.** This is incomplete bootstrap, not an inapplicable check (Section 2.5.2). Run Section 2.3, then measure. |
| A script's log and its `eval.json` disagree about a gate | 🔴 The run is **invalid**. The artifact claiming a gate that never ran is the worst failure mode here — fix the script, never reconcile by hand (Section 2.5.3). |
| `overall: PASS` while several checks are `N/A` | Report `checksRun` / `checksTotal` and list the `N/A` checks. A bare `PASS` implying full coverage is forbidden (Section 2.5.4). |
| SonarQube not yet configured | CI generation creates `sonar-project.properties` and the active scan steps, then presents the plain-text setup gate (`ci-pipeline-generation.md` Section 4.1.2) and waits for `proceed` or `skip`. On `skip` the steps are commented out and `sonarqube.enabled` is set false; semgrep + the Security Baseline review still enforce D3. Not a failure either way. |
| A SonarQube token or host URL would be written to a file | 🔴 Forbidden. Secrets live in the repository secret store only — never in `sonar-project.properties`, the workflow YAML, `.evals/config.json`, or a committed `.env`. |
| A bootstrapped config would land AFTER the baseline | 🔴 Ordering violation. Bootstrap first, then baseline. |
| A downstream number disagrees with the artifact | Gate failure. The artifact wins. |
| Someone suppresses a finding, lowers a threshold, or edits a rubric/architecture doc to pass | 🔴 SH-6 violation. Treated as a gate failure and called out explicitly in the output and audit.md. |
