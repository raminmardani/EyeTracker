# CI Pipeline Generation — AIRE Builds the Project's Own Eval Pipeline

---

## 1. 🔴 Generated per project — never copied from a template

Every project has different package managers, script names, test runners, module paths and service
dependencies. A pasted pipeline that calls `npm run lint` in a repo whose script is called
`lint:ci` fails on the first run, and a pipeline that fails for structural reasons gets disabled by
the team within a week — taking the real gates with it.

**Therefore:**

| Rule | Meaning |
|---|---|
| **Read, never assume** | Every command in the generated YAML is read out of the repo: `package.json` scripts, `Makefile` targets, `pyproject.toml`/`tox.ini`, `pom.xml` plugins, `build.gradle` tasks, the `.evals/config.json` thresholds. |
| **No invented script names** | If the repo has no lint script, generate the direct tool invocation (`npx eslint .`) — never a script name that does not exist. |
| **No invented services** | Only add a `services:` block for a datastore the repo demonstrably needs (a compose file, a test config, a connection string in test setup). |
| **Verify before committing** | Every referenced script/target must be shown to exist. List the verification in the announcement. |
| **Same thresholds as local** | Read from `.evals/config.json`. Never hardcode a number into the YAML that also lives in the config. |

---

## 2. When it runs

| Flow | Generate / refresh the pipeline at |
|---|---|
| **First cycle in a repository** | **STOP CHECKPOINT Step 1.6** — generated and committed **on the cycle branch** with the other STOP CHECKPOINT artifacts (Section 2.1). 🔴 Never pushed to base; it reaches base when the cycle's PR merges. |
| **Every later cycle** | 🔴 **Nothing is regenerated** — inherited from base and used as-is. If any artifact is **missing**, create it on the cycle branch (deterministically) rather than halting: `common/directory-structure.md` — Artifact Ownership. |
| Any flow, thresholds changed | Regenerate the threshold-bearing steps only. Announce the diff. |

**Idempotent.** If `.github/workflows/agentic-eval-pipeline.yml` already exists:
- Same stack, same thresholds → leave it **untouched** and say so.
- Thresholds moved → update only those values, preserve every human edit elsewhere, and show the diff.
- 🔴 **Never overwrite a pipeline a human has edited.** Show the drift and ask.

---

### 2.1 🔴 WHERE THE PIPELINE LIVES — the cycle branch, never pushed to base

**GitHub runs a `pull_request` workflow from the HEAD branch, not the base.** The pipeline therefore
only needs to exist on the branch raising the PR — which is always a cycle branch or something cut
from one.

| PR | Head branch has it because | CI runs |
|---|---|---|
| story → epic | story branches are cut from the epic branch | ✅ |
| ve → epic / bug / enh | cut from the cycle branch | ✅ |
| epic → main | the epic cycle created it | ✅ |
| bug → main | the bug cycle created it on the bug branch | ✅ |
| enh → main | the enhancement cycle created it on the enhancement branch | ✅ |

**Base gets it for free.** `.github/workflows/agentic-eval-pipeline.yml` and `.evals/**` are part of
the cycle's own PR diff, so merging the cycle lands them on base. The next cycle branches from base,
finds them present, and leaves them alone (`common/directory-structure.md` — Artifact Ownership).

🔴 **Do NOT push these files directly to base, and do NOT raise a separate `[CI]` PR for them.** They
ride in with the cycle that created them. There is no bootstrap-on-base step.

#### 2.1.1 Generate at the STOP CHECKPOINT, commit with the cycle

1. Check whether each artifact already exists (on this branch, or inherited from base).
2. **Present → leave it completely alone.** Never regenerate, never diff-and-update.
3. **Missing → generate it deterministically** from its canonical template, and commit it alongside
   the cycle's other STOP CHECKPOINT artifacts.
4. Announce what was created versus inherited, and name the branch-protection check the user may want
   to require (see below).
5. Continue. 🔴 **Never block the cycle on any of this.**

#### 2.1.2 The self-repair job no longer constrains where the workflow lives

The historical reason for seeding base was `anthropics/claude-code-action`, which refuses to run with
elevated permissions unless the workflow file is byte-identical to the default branch's copy:

```
Workflow validation failed. The workflow file must exist and have identical
content to the version on the repository's default branch.
```

🔴 **That constraint no longer applies**: self-repair runs the **Claude Code CLI** from
`.evals/scripts/auto-fix-agent.*` (Section 6), which is an ordinary `run:` step with no such guard. It
works on the very PR that introduces the pipeline. If a team overrides this to use the marketplace
action, that guard returns and they must land the workflow on the default branch first — say so, and
do not let it block the cycle.

#### 2.1.3 Enforcement is a repository setting

Requiring CI to pass before merge is **GitHub branch protection** with the verify job's name as a
required status check. That is configured once on the repository and cannot be carried by any branch.
Name the job in the completion announcement so the user can enable it; 🔴 never attempt to change
repository settings automatically.

---

## 3. Stack detection → real commands

Detect the stack, then resolve each stage's command from what the repo actually provides. Resolve in
order: **repo script → direct tool invocation → `N/A` with a stated reason.**

| Stage need | JS/TS | Python | Java/Kotlin | Go | .NET |
|---|---|---|---|---|---|
| Install | `npm ci` / `pnpm i --frozen-lockfile` / `yarn --immutable` | `pip install -r requirements.txt` / `poetry install` / `uv sync` | `mvn -B -ntp install -DskipTests` / `gradle build -x test` | `go mod download` | `dotnet restore` |
| Lint (D1) | `eslint`/`biome` | `ruff check` | `checkstyle`/`spotless:check` | `golangci-lint run` | `dotnet format --verify-no-changes` |
| Types (D2) | `tsc --noEmit` | `mypy` | compiler | `go vet ./...` | build |
| SAST (D3) | `semgrep --config auto` (stack-agnostic) | + `bandit` | + `spotbugs` | + `gosec` | + `security-scan` |
| Deps (D4) | `npm audit --json` | `pip-audit` | `mvn dependency-check:check` | `osv-scanner` | `dotnet list package --vulnerable` |
| Licences (D5) | `license-checker` | `pip-licenses` | `license-maven-plugin` | `go-licenses` | `nuget-license` |
| Complexity (D6) | eslint `complexity` | `radon cc` | PMD | `gocyclo` | analyzers |
| Secrets (D7) | `gitleaks detect` — **prefer the binary/container over `gitleaks/gitleaks-action`** (Section 4.0.3) | — | — | — | — |
| Unit + coverage | `jest --coverage` / `vitest run --coverage` | `pytest --cov` | `mvn test jacoco:report` | `go test -cover` | `dotnet test --collect:"XPlat Code Coverage"` |
| **Behavioural (Gherkin)** — always invoked via `.evals/behavior/run.sh <tier>` inside Podman | `cucumber-js` | `pytest-bdd` | `mvn verify -Dcucumber` | `godog run` | `reqnroll` |
| E2E | `playwright test` (only when the extension is enabled) | | | | |

🔴 A stage with no resolvable command is emitted as an explicit **skipped step with a `# reason:`
comment**, never silently dropped and never faked with `echo ok`.

### 3.1 🔴 Tool installation — the self-repair job needs the SAME tools as the verify job

The self-repair job runs on a **fresh runner** — it has no tools from the verify job. If the agent
fixes the code but cannot re-run the evals (because semgrep / mypy / the test runner is not
installed), it pushes an unverified commit. That commit fails the next CI run and wastes a retry.

**Rule**: the self-repair job must install the **same runtimes, project dependencies, and eval tools**
as the verify job. Generate the install steps identically in both jobs — or extract them into a
**composite action** / **reusable workflow** so they cannot drift.

**Complete tool checklist** (install in the self-repair job exactly as in the verify job):

| Category | What to install | Why self-repair needs it |
|---|---|---|
| **Language runtimes** | Node (`actions/setup-node`), Python (`actions/setup-python`), Go, Java — whichever the project uses | The fix may need to compile or run tests |
| **Project dependencies** | `npm ci` / `pip install -r requirements.txt` / `mvn install -DskipTests` — the same command the verify job runs | The tests import the project's own packages |
| **Test runners** | `pytest`, `jest`, `vitest`, `pytest-bdd`, `cucumber-js` — whatever the verify job uses | Rule 4 of Section 6.0.1: re-run evals before committing |
| **Static analysis tools** | `semgrep`, `pip-audit` / `npm audit`, `gitleaks`, `mypy` / `tsc`, the linter | Re-running `run-static-evals.*` requires them |
| **Coverage tools** | `pytest-cov`, `c8` / `istanbul`, `jacoco` | Coverage gate re-verification |
| **Behavioural test infra** | `podman`, the Gherkin runner | B1/B2 re-verification when the fix touches behaviour |
| **Claude Code CLI** | `npm i -g @anthropic-ai/claude-code` | The repair agent itself |

🔴 **If a tool fails to install, exit non-zero immediately.** Do not proceed to repair with a partial
toolset — the re-verification step will fail or skip silently, producing an unverified commit.

### 3.2 🔴 Verify job install steps — no gate may run without its tool

The verify job must install every tool it needs BEFORE any gate step runs. Generate the install
section by reading the project's stack (Section 3), then:

1. **Emit setup actions** for every runtime the project uses (`actions/setup-node`,
   `actions/setup-python`, `actions/setup-java`, `actions/setup-go`). Pin the version to the
   project's own `.node-version` / `pyproject.toml [project] requires-python` / `go.mod` go
   directive. If no pin exists, use the latest LTS.
2. **Emit project dependency install** — the exact command the project uses (`npm ci`, `pip install
   -r requirements.txt`, `poetry install`, `mvn -B install -DskipTests`). Read it from the
   project's `package.json` scripts, `Makefile`, `pyproject.toml`, or build file.
3. **Emit eval tool install** — every tool from the Section 3 table that this stack needs. Combine
   related tools into a single step to reduce job time:
   ```yaml
   - name: "Install eval tools"
     run: |
       pip install semgrep pip-audit
       gitleaks_version="8.21.2"
       curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${gitleaks_version}/gitleaks_${gitleaks_version}_linux_x64.tar.gz" | tar xz -C /usr/local/bin gitleaks
       semgrep --version
       gitleaks version
       pip-audit --version
   ```
4. **Verify every tool after installation** — append a version check to each install block. The
   check must exit non-zero if the binary is not in PATH:
   ```yaml
   - name: "Install and verify linter"
     run: |
       npm install -g eslint
       eslint --version || { echo "eslint not found after install"; exit 1; }
   ```

🔴 **No install step may use `|| true` or `continue-on-error: true`.** A failed install must abort
the job immediately. Running gates without their tools produces partial or empty results that look
like passes.

🔴 **Pin tool versions.** An unpinned `pip install semgrep` may install a breaking update between
runs, causing a gate that passed yesterday to fail today for the same code. Pin to a known-working
version and update deliberately.

🔴 **The `curl` install pattern for gitleaks (and similar binaries) must pin the version in the URL
and verify the binary after extraction.** A 404 from a stale URL exits non-zero immediately — the
secret scanner was not installed. Never fall through to the gate with a missing binary.

🔴 **These commands are what `run-static-evals.*` invokes internally — they are NOT pasted into the
workflow as standalone steps.** The YAML calls the script; the script runs the tool twice (base and
HEAD) and diffs. Emitting the raw command as a CI step re-introduces the whole-tree verdict bug
(Section 4.0b).

---

## 4. Pipeline shape — four stages plus self-repair

The generated workflow mirrors `common/eval-framework.md` and the local gate order exactly. **CI does
not introduce new gates and does not relax any.** It is the same contract, re-verified where a human
can see it.

```
on: pull_request → [ <base-branch>, 'epic/**', 'bug/**', 'enh/**' ]   (Section 4.0a)
    push        → [ <base-branch> ]        workflow_dispatch

job: verify-and-evaluate
  ├── Stage 1  Deterministic       .evals/scripts/run-static-evals.sh <base-sha>
  │                                D1 lint · D2 types · D3 SAST(+SonarQube) · D4 deps · D5 licences
  │                                D6 complexity · D7 secrets
  │                                🔴 DELTA-SCOPED vs the base ref — never a whole-tree verdict
  ├── Stage 2  Behavioural         unit tests + coverage ≥ unitTestCoverageMin, then Gherkin
  │                                in Podman — B1 (this unit) · B2 (every other feature file)
  │                                · B3 (whole epic) only on a PR into the base branch
  ├── Stage 3  Semantic            J1 architecture · J2 security (OWASP) vs .evals/rubrics/*
  │                                BLOCKING at the config minimums
  ├── SonarQube               LAST gate step · if: always() · continue-on-error
  │                                one input to the verdict, never a kill switch
  ├── Verdict                 🔴 the ONLY step that fails the job — tallies every
  │                                gate's outcome (Section 4.0c)
  └── Stage 4  Scorecard           if: always() — publish eval-summary to the PR + job summary

  🔴 EVERY gate step: id + continue-on-error. NEVER `|| true` (Section 4.0c).

job: self-repair          (needs: verify-and-evaluate, if: failure())
  └── Claude Code fixes the failure and pushes a commit   — max retryLimitForSelfRepair attempts
```

### 4.0 🔴 VALIDATION GATE — never commit a pipeline that cannot run

A generated workflow that fails to parse is worse than no workflow: every gate it was supposed to
enforce silently does not run, and the PR looks merely "red" rather than "unverified".

**Validate BEFORE committing. A pipeline that fails any check below is not committed — it is fixed.**

#### 4.0.1 The checks, in order

| # | Check | How |
|---|---|---|
| V1 | **YAML parses** | `python -c "import yaml,sys;yaml.safe_load(open('.github/workflows/agentic-eval-pipeline.yml'))"` — or `yq e . <file> >/dev/null`, or any available parser |
| V2 | **Valid GitHub Actions schema** | `actionlint` when available (`command -v actionlint`). It catches expression errors, bad `needs:`, unknown contexts — things a YAML parser cannot see |
| V3 | **Every referenced script/target exists** | For each `npm run X` / `make X` / `mvn X`, confirm X is defined in the repo (Section 1). A command that does not exist fails on the first run |
| V4 | **Every referenced file exists** | `.evals/config.json`, `.evals/rubrics/*`, `.evals/behavior/run.sh`, `sonar-project.properties` when the Sonar steps are active |
| V5 | **Every referenced secret is named in the announcement** | So the user knows what to add. A step reading an unlisted secret is a generation defect |
| V6 | **Every action's required `permissions:` are declared** | Cross-check each `uses:` against Section 4.0.3. A missing scope fails only at runtime, so a parser and `actionlint` both pass a workflow that cannot work — this check is the only thing that catches it before the first run |
| V7 | **Stage 1 is delta-scoped** | 🔴 No bare whole-tree command with `--error`/`--exit-code 1`/`--strict`. Every D1–D7 step either calls `.evals/scripts/run-static-evals.*` or uses the tool's native baseline flag (Section 4.0b). A blunt command passes V1–V6 and still fails every future PR on pre-existing debt |
| V8 | **Step failure is isolated** | Every gate step has `id:` + `continue-on-error: true`, no `\|\| true`, exactly one Verdict step tallies them all, and Sonar is last with `if: always()` (Section 4.0c). A pipeline failing this either aborts on the first failure or cannot fail at all — both pass V1–V7 |
| V9 | **No stub can pass** | 🔴 Prove each generated script can FAIL. Run `run-static-evals` and `run-evals` once against a deliberately broken input (an injected lint error, a rubric criterion set to fail) and confirm a non-zero exit. A script that returns PASS or `N/A` unconditionally is the worst defect this generator produces — it removes a gate while looking healthy (Section 5.0). Also grep the scripts for hardcoded `"status": "PASS"` / `"N/A"` literals not derived from a real result |
| V10 | **Trigger covers every integration branch** | The `pull_request` filter names the resolved base branch AND `epic/**`, `bug/**`, `enh/**` (Section 4.0a). A filter of just `[main]` skips every story PR — they merge with no checks at all, and nothing looks wrong |
| V11 | **`EVAL_KEY` resolves to the evidence key, not the branch name** | The `auto-fix-agent.*` script must find `eval.json` at the same path the verify job wrote it. If `EVAL_KEY` is set to `github.head_ref`, the self-repair job will search the wrong directory, find nothing, and exit 0 — hiding a real failure behind a green job (Section 6.0.1 rule 1) |
| V12 | **Every directory the scripts write to is created first** | Grep every script for file writes and confirm a `mkdir -p` precedes each one. A missing directory aborts the script before it reaches the repair logic (Section 6.0.1 rule 2) |
| V13 | **Self-repair re-runs evals before committing** | The `auto-fix-agent.*` script must invoke `run-static-evals.*` and `run-evals.*` after the fix and before the commit, and exit non-zero if they still fail. A commit that does not re-verify wastes a retry attempt (Section 6.0.1 rule 4) |
| V14 | **No `# GENERATE:` or `<placeholder>` comments remain** | Grep the committed YAML for `GENERATE:`, `TODO:`, `PLACEHOLDER`, and angle-bracket placeholders like `<base-branch>`. Any hit means the generator left unresolved instructions in the file |
| V15 | **Verify job uploads eval artifacts** | The verify job must have an `actions/upload-artifact` step that uploads `eval.json`, `eval-summary.md`, and the `static/` + `judge/` evidence directories. The self-repair job's `actions/download-artifact` depends on this — without the upload, self-repair has no `eval.json` and exits 0 on a real failure (Section 6.0.1 rule 3) |
| V16 | **Every tool is verified after installation** | Each install step in the verify job must be followed by a version check (`semgrep --version`, `gitleaks version`, `mypy --version`, etc.). A tool that installs but cannot run crashes mid-gate. In the generated YAML, combine the install and verify in the same `run:` block |
| V17 | **Evidence round trip** | Run each script once; every artifact the path contract declares must exist at the declared path, and each consumer must read the path it was written to (Section 5.3.4). 🔴 A write/read mismatch passes V1–V16 completely — YAML parses, scripts exist, job goes green — while J1/J2 report `N/A` forever |
| V18 | **Every failing gate reaches the scorecard AND the brief** | Force each gate to fail in turn; confirm it appears in `eval.json`'s `gates` block, in `.evals/_run/failed-gates.txt`, and that `verdict` matches the job result. 🔴 A gate that fails the build while `eval.json` says `PASS` — SonarQube being the observed case — leaves self-repair with nothing to act on (Section 4.0c.3) |
| V19 | **Self-repair never exits 0 without repairing** | Run `auto-fix-agent.*` with its inputs deliberately removed. It must exit **non-zero** naming what was missing — never exit 0 and never reclassify its own missing input as an "infrastructure failure" of the build (Section 6.5) |
| V20 | **No deferred-setup `N/A`** | Grep every generated script and its output for `N/A` reasons containing "yet", "TODO", "not wired", "not bootstrapped", "not installed", "not enabled", "pending". Each is **ERROR**, not `N/A` (`common/eval-framework.md` Section 2.4.2). Also assert the log and `eval.json` agree per gate, and that `overall` discloses `checksRun`/`checksTotal` |
| V21 | **Tool install is retried, with a container fallback** | Every install step works the Section 2.4.1 chain — 3 attempts per rung, ending at an OCI image run through Podman — and **halts** rather than degrading to `N/A`. 🔴 A gate recorded `N/A` for a missing tool without the container rung attempted is a bootstrap failure |

🔴 **If V2's tool is unavailable, say so** and record `actionlint: not available` in the announcement.
Never claim a schema check that did not run.

#### 4.0.1a 🔴 LOCAL DRY-RUN — run the pipeline locally before committing

After V1–V13 pass, **execute the generated scripts locally** against the current branch to confirm
they produce real results, not just that they parse:

1. Run `bash .evals/scripts/run-static-evals.sh "$(git merge-base HEAD origin/<base-branch>)"` and
   confirm it produces a non-empty output with real gate results — not stubs, not all-N/A.
2. Run `bash .evals/scripts/run-evals.sh "$(git merge-base HEAD origin/<base-branch>)"` and confirm
   `eval.json` is written with real `gates` entries and that `eval-summary.md` is produced.
3. If either exits non-zero, **that is the correct signal** — it means the scripts work. Read the
   output to confirm the failure is a real finding, not a missing directory or a wrong path.
4. Confirm `eval.json` lives at the expected evidence path and that `EVAL_KEY` in the workflow
   resolves to the same directory name.

🔴 **Do not commit scripts that have never run.** A script that parses and passes V1–V13 but crashes
on first invocation (missing dependency, wrong path, wrong flag) wastes the team's first CI run and
erodes trust in the pipeline. The local dry-run is what catches that class of defect.

Log the dry-run results in `audit.md` — which scripts ran, their exit codes, and whether the outputs
matched expectations.

#### 4.0.2 YAML rules that prevent the common breakages

These are the failure modes that actually occur when a model writes CI YAML. Follow them while
generating, not only while validating:

1. 🔴 **QUOTE EVERY `name:` VALUE.** A bare colon inside an unquoted scalar is the single most common
   cause of "Invalid workflow file".
   - Correct: `- name: "Stage 1: deterministic gates"`
   - Broken: `- name: Stage 1: deterministic gates`
2. 🔴 **Multi-line commands use a block scalar `|`**, never `>` and never inline. Inside `|`,
   colons, quotes and `#` are literal text and safe.
3. 🔴 **Quote any scalar containing** `: ` · `#` · a leading `*`, `&`, `!`, `%`, `@`, `` ` `` ·
   or a value that could read as a number/bool (`on`, `yes`, `1.10`).
4. 🔴 **`if:` expressions are unquoted GitHub expressions or fully quoted strings — never half.**
   `if: failure() && github.event_name == 'pull_request'`
5. 🔴 **Two-space indentation, spaces only. Never a tab.** A tab anywhere in a YAML file is a
   parse error.
6. 🔴 **No placeholder left in the file.** `<base-branch>`, `<n>`, `<runner>` are for this document —
   the generated file carries real values. Grep the output for `<` followed by a letter before
   committing.
7. **`run: |` bodies keep one consistent indent**; every line of the block indented deeper than the
   `run:` key.

#### 4.0.3 Actions that need a token — wire it, don't ask for it

Some marketplace actions fail with an unhelpful error unless a token is passed in `env:`. **`GITHUB_TOKEN`
is provided automatically by GitHub Actions** — the user never creates it — but it is NOT injected into
a step's environment on its own. 🔴 Wiring it is AIRE's job at generation time, not a user action.

| Action | Needs | Who provides it |
|---|---|---|
| `gitleaks/gitleaks-action@v2` | `GITHUB_TOKEN` in `env:` | Automatic — AIRE wires it |
| `gitleaks/gitleaks-action@v2` on an **organization-owned** repo | `GITLEAKS_LICENSE` secret | 🔴 The user — free for personal and public repos, **paid for org-owned private repos** |
| `SonarSource/sonarqube-scan-action` | `SONAR_TOKEN`, `SONAR_HOST_URL` | The user (Section 4.1.2) |
| `anthropics/claude-code-action@v1` — 🔴 **NOT the default; AIRE uses the CLI (Section 6)** | `id-token: write` (OIDC) + `contents: write` + `pull-requests: write` | Only when the team explicitly chose the action variant. Omitting `id-token: write` fails with *"Could not fetch an OIDC token"*, and the action additionally refuses to run until the workflow matches the default branch |

```yaml
      - name: "D7: secret scan"
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}   # org-owned repos only
```

🔴 **DEFAULT TO THE BINARY, NOT THE ACTION.** The licence requirement turns a free, zero-setup gate
into a blocked pipeline on exactly the repos most likely to need it. Unless the repo *already* uses
`gitleaks-action`, generate the container form instead — no token, no licence, no marketplace
dependency, identical detection:

```yaml
      - name: "D7: secret scan"
        run: |
          podman run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest \
            detect --source /repo --redact --exit-code 1
```

Use the Action only when the repo already depends on it — and then wire `GITHUB_TOKEN`, and surface
the `GITLEAKS_LICENSE` requirement in the setup gate when the repo is org-owned.

**General rule**: any generated step using a marketplace action must have its required `env:` and
`permissions:` resolved from that action's own documentation **before** the file is committed. A step
that fails on its first run for a missing token is a generation defect, caught by V3/V5 in Section 4.0.1.

#### 4.0.4 On failure

Fix and re-validate — up to **3 attempts**, then HALT and report, exactly like every other loop:

```
CI PIPELINE VALIDATION FAILED

  File:  .github/workflows/agentic-eval-pipeline.yml
  Check: [V1 YAML parse | V2 actionlint | V3 missing script | V4 missing file]
  Error: [exact parser output, including the line number]
  Line:  [the offending line, quoted verbatim]

  Attempt 1 - [what changed] -> [result]
  Attempt 2 - [what changed] -> [result]
  Attempt 3 - [what changed] -> [result]

3 retries ended. Please suggest next steps.
The pipeline has NOT been committed. No gate is currently enforced in CI.
```

🔴 **Never commit the file anyway "so the user can fix it".** An invalid workflow in the repo reads as
a broken build rather than an absent one, and it hides that nothing is being enforced.

#### 4.0.5 Confirm it actually ran

Committing a parseable file is not proof it runs. **After the design commit is pushed**, verify the
workflow was accepted:

```bash
gh run list --workflow=agentic-eval-pipeline.yml --limit 1
```

- A run appears (queued, in progress, or completed) → report its URL and status.
- **No run, or status `action_required` / a startup failure** → the file was rejected by GitHub.
  Report it immediately with the reason. Do not treat "pushed" as "working".
- `gh` unavailable → say the verification could not be performed, and tell the user to check the
  Actions tab. Never assume success.

### 4.0a 🔴 TRIGGER — every AIRE integration branch must be covered

AIRE raises PRs into **several** branches, not just the base. A `pull_request` trigger filtered to
`[ main ]` silently skips **every story PR**, because those target the epic branch. The PR then shows
no checks at all and merges ungated — the most dangerous failure in this document, because nothing
appears wrong.

**Every PR AIRE raises, and where it goes:**

| PR | Head | Target | Must trigger CI |
|---|---|---|---|
| Story | `story/<N.M>-<title>` | the **epic** branch | ✅ |
| ve test docs | `ve/<TICKET-ID>-<title>` | epic / bug / enhancement branch | ✅ |
| Epic | `epic/<EPIC-ID>-<title>` | base branch | ✅ |
| Bug | `bug/<TICKET-ID>-<title>` | base branch | ✅ |
| Enhancement | `enh/<TICKET-ID>-<title>` | base branch | ✅ |
| CI bootstrap | `ci/agentic-eval-pipeline` | base branch | ✅ |

So the filter must name the **base branch and every integration-branch pattern**:

```yaml
on:
  pull_request:
    branches:
      - <base-branch>        # resolved from aire-state.md ## Branching, e.g. main
      - 'epic/**'
      - 'bug/**'
      - 'enh/**'
  push:
    branches:
      - <base-branch>        # whole-codebase scan after a merge
  workflow_dispatch:         # manual re-run without a new commit
```

**Rules:**

1. 🔴 **Resolve `<base-branch>` from `aire-state.md` `## Branching`** — never hardcode `main`. Repos
   use `develop`, `master`, `trunk`.
2. 🔴 **Use `'epic/**'`, not a single epic name.** The filter must survive the next cycle without being
   regenerated; a literal `epic/AIPDLC-123-foo` breaks silently on epic 2.
3. **Quote the glob patterns.** `epic/**` unquoted is valid YAML here but quoting is consistent and
   avoids surprises with other patterns.
4. **`push` on the base branch** gives the post-merge whole-codebase scan a place to run (this is where
   an absolute SonarQube analysis belongs, as opposed to the PR's delta view).
5. **`workflow_dispatch`** so a failed run can be retried after fixing a secret, without an empty commit.
6. 🔴 **Never add `pull_request_target`.** It runs with the base branch's secrets against untrusted head
   code — the wrong tool here, and a real security hazard.

**Verify after generating**: list the branch patterns against the table above and confirm every row is
covered. State the resolved base branch by name in the announcement so a wrong value is obvious
immediately.

### 4.0b 🔴 STAGE 1 MUST BE DELTA-SCOPED — never a bare whole-tree command

This is the single most common way a generated pipeline goes wrong, and it disables the gate within a
week.

**The failure**: the local Static Eval Gate runs a tool, then **diffs the result against the baseline
captured before any code was written**, and classifies each finding as new-vs-pre-existing. A finding
that existed at baseline is recorded and ignored. A bare CI command like

```yaml
        run: semgrep --config auto src --error --severity ERROR --severity WARNING   # 🔴 WRONG
```

has no concept of a baseline. `--error` means *"exit 1 if there are ANY findings"* — a blunt verdict on
the whole tree, every run. One pre-existing warning in old code then fails **every future PR**, for
every story, forever, while the local gate correctly reports PASS. Same tool, same finding, opposite
verdict — purely because the verdict logic differs.

🔴 **`scope: "changed-files"` in `.evals/config.json` is binding on CI exactly as it is locally**
(`common/eval-framework.md` Section 2.2). CI re-verifies the same contract; it does not get a
different, stricter one.

🔴 **This applies to the COVERAGE gate too, not only D1–D7.** A whole-module
`pytest --cov-fail-under=90` fails on pre-existing coverage debt on every PR, regardless of what the
PR touched — the same false-blame defect in a different tool. Measure coverage on the **changed files**
and compare against `unitTestCoverageMin`:

```bash
# WRONG - whole module, fails on pre-existing 86% forever
pytest --cov=src/backend --cov-fail-under=90

# RIGHT - full run for correctness, threshold applied to the changed files only
pytest --cov=src/backend --cov-report=xml          # no --cov-fail-under here
.evals/scripts/run-static-evals.sh "$BASE_SHA"     # owns the changed-file coverage verdict
```

Run the **whole** suite (a change can break a test anywhere), but apply the **threshold** only to
lines in changed files. `run-static-evals.*` owns that computation, exactly as it owns the D1–D7 diff.

#### 4.0b.1 The rule: one script owns the diffing, both callers invoke it

Generate **`.evals/scripts/run-static-evals.*`** and have **both** the local gate and CI call it. Never
re-implement the diff logic in YAML — that is precisely how the two drift apart.

```yaml
      - name: "Stage 1: static evals (delta-scoped)"
        run: .evals/scripts/run-static-evals.sh "${{ github.event.pull_request.base.sha }}"
```

The script's contract, identical in both environments:

1. Resolve the **changed file set**: `git diff --name-only <base-sha>...HEAD`.
2. Run D1–D7 against the **base ref** (baseline) and against **HEAD** (post-change).
3. **Diff the finding sets**, matching on `(rule-id, file, message)` — **not on line number**, which
   shifts when unrelated code moves. That line-shift is exactly why the CORS finding at `main.py:12`
   and `main.py:39` must be recognised as the same pre-existing finding.
4. Count only findings that are **NEW versus baseline AND on a changed file** against the thresholds.
5. Emit `eval.json` + `eval-summary.md`, exit non-zero only on a real delta breach.
6. **Report pre-existing findings as non-blocking information** in the PR comment, so debt stays
   visible without failing the build.

#### 4.0b.2 Use each tool's native baseline flag when it has one

Cheaper and more reliable than a two-pass diff. Prefer these:

| Check | Native delta support | Use |
|---|---|---|
| D3 SAST | ✅ semgrep | `semgrep --config auto --baseline-commit <base-sha>` — reports only findings introduced since that commit |
| D7 Secrets | ✅ gitleaks | `gitleaks detect --log-opts "<base-sha>..HEAD"` — scans only the new commits |
| D4 SCA | ⚠️ partial | Diff the advisory ID set between base and head lockfiles |
| D1 Lint · D2 Types · D6 Complexity | ❌ none | Two-pass diff via the script, matched on `(rule, file, message)` |

🔴 **Never substitute "scope the tool to changed files" for a real baseline diff.** Running
`mypy <changed-files>` still fails on a pre-existing error that happens to live in a file this story
touched — which is the same false blame in a smaller box. Changed-file scoping narrows *where* to look;
the baseline diff decides *who is responsible*. Both are required.

#### 4.0b.3 Forbidden in a generated Stage 1 step

- `--error`, `--exit-code 1`, `--strict`, `--max-warnings 0` on a **whole-tree** invocation
- Any tool run against `src/` (or the whole repo) with no base ref and no baseline comparison
- Thresholds hardcoded in the YAML instead of read from `.evals/config.json`

A step matching any of these is a generation defect, caught by **V7** in Section 4.0.1.

### 4.0c 🔴 STEP FAILURE ISOLATION — one gate must never skip the others

Two opposite defects show up in generated pipelines, and both destroy the verdict.

**Defect A — a hard-failing step aborts the job.** GitHub Actions stops a job at the first failed step.
A step with no error tolerance therefore *skips every gate after it*:

```yaml
      - name: "SonarQube quality gate"          # 🔴 WRONG — no tolerance, and not last
        uses: SonarSource/sonarqube-quality-gate-action@v1
```

When Sonar's gate fails, D1–D7, unit tests, Gherkin and J1/J2 never run. Every later step shows
`⊘ skipped`, and the PR reports a failure that says nothing about the code. Sonar becomes an upstream
kill switch instead of one input among many.

**Defect B — `|| true` makes a gate unable to fail.** The reflexive fix for Defect A is worse:

```yaml
      - name: "D3: SAST"
        run: semgrep --config auto src || true    # 🔴 WRONG — the result is destroyed
```

`|| true` discards the exit code entirely. The step is now decorative: it can never fail the job, and
the scorecard cannot report its real result — which breaks the rule that every figure quoted downstream
must match the stored artifact. **A gate that cannot fail is not a gate.**

#### 4.0c.1 The correct pattern: isolate, collect, then decide once

Every gate step **records** its outcome and lets the job continue. Exactly **one** final step decides
the verdict and is the only step allowed to fail the job.

```yaml
      # every gate step: id + continue-on-error, NEVER `|| true`
      - name: "Stage 1: static evals (delta-scoped)"
        id: static
        continue-on-error: true
        run: .evals/scripts/run-static-evals.sh "${{ github.event.pull_request.base.sha }}"

      - name: "Stage 2: unit + coverage"
        id: unit
        continue-on-error: true
        run: <resolved command>

      - name: "Stage 2: behaviour (Gherkin)"
        id: behavior
        continue-on-error: true
        run: .evals/behavior/run.sh <tiers>

      - name: "Stage 3: judge gates J1 + J2"
        id: judge
        continue-on-error: true
        run: .evals/scripts/run-evals.sh

      # SonarQube LAST among the gates, and never able to abort what follows
      - name: "SonarQube quality gate"
        id: sonar
        if: always()
        continue-on-error: true
        uses: SonarSource/sonarqube-quality-gate-action@v1
        timeout-minutes: 5

      # the ONLY step that fails the job
      - name: "Verdict"
        if: always()
        run: |
          fail=0
          for r in "static:${{ steps.static.outcome }}" \
                   "unit:${{ steps.unit.outcome }}" \
                   "behavior:${{ steps.behavior.outcome }}" \
                   "judge:${{ steps.judge.outcome }}" \
                   "sonar:${{ steps.sonar.outcome }}"; do
            name="${r%%:*}"; outcome="${r##*:}"
            echo "$name: $outcome"
            [ "$outcome" = "failure" ] && fail=1
          done
          exit $fail
```

**Rules:**
1. 🔴 **Every gate step has `id:` and `continue-on-error: true`.** Never `|| true`, never
   `continue-on-error` without an `id` (the outcome would be unreadable).
2. 🔴 **Exactly one Verdict step fails the job**, guarded by `if: always()` so it runs even after a
   failed gate.
3. 🔴 **The scorecard publish step is `if: always()`** so results reach the PR on failure — that is
   when they matter most.
4. 🔴 **SonarQube is the LAST gate step**, `if: always()`, `continue-on-error: true`. It is one input
   among many, never a precondition for running the others.
5. **Order gates cheapest-first** — static, unit, behaviour, judge, Sonar — so a fast failure surfaces
   quickly, but *never* let ordering decide what runs. With isolation, everything runs regardless.
6. `continue-on-error: true` on a step whose result is **not** read by the Verdict step is the same
   defect as `|| true`. Every isolated step must appear in the Verdict tally.

#### 4.0c.2 🔴 The Verdict step HANDS the failure to self-repair — it never makes it go looking

The Verdict step already knows exactly which gates failed. **Write that down and pass it on.** Self-repair
must never have to rediscover the failure by hunting for a file, because the file may be absent, at a
different path, or — worse — present and *silent about the thing that actually failed*.

```yaml
      - name: "Verdict"
        id: verdict
        if: always()
        run: |
          mkdir -p .evals/_run
          fail=0
          : > .evals/_run/failed-gates.txt
          for r in "static:${{ steps.static.outcome }}" \
                   "unit:${{ steps.unit.outcome }}" \
                   "behavior:${{ steps.behavior.outcome }}" \
                   "judge:${{ steps.judge.outcome }}" \
                   "sonar:${{ steps.sonar.outcome }}"; do
            name="${r%%:*}"; outcome="${r##*:}"
            echo "$name: $outcome"
            if [ "$outcome" = "failure" ]; then echo "$name" >> .evals/_run/failed-gates.txt; fail=1; fi
          done
          exit $fail

      - name: "Upload failure context"
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: |
            .evals/_run/failed-gates.txt
            .spec/aire-docs/implementation/code/eval-evidence/
```

🔴 **Every step id in the Verdict tally must be able to appear in `failed-gates.txt`.** A gate that can
fail the build but is not in the tally fails it invisibly.

#### 4.0c.3 🔴 A gate that fails the build MUST appear in `eval.json`

Observed in a real run: SonarQube's Quality Gate failed, the Verdict correctly failed the job — and
`eval.json` contained fifteen gates, **none of them SonarQube**. Self-repair then opened the scorecard,
read `"verdict": "PASS"`, and had nothing to repair. The scorecard disagreed with the build.

**The `gates` block is complete or it is wrong.** Every gate the pipeline can fail on:
`D1_lint` … `D7_secrets`, `unitCoverage`, `behaviorB1`, `behaviorB2`, `behaviorB3`, `apiContract`,
`regression`, `J1_architecture`, `J2_security`, **and `sonarqube` whenever it is enabled**.

🔴 **`verdict` is derived from the `gates` block, and the job's result must agree with it.** If the job
failed while `eval.json` says `PASS`, that is a defect in the scorecard, not a quirk to work around.
The generated `run-evals.*` reads the other steps' outputs (Section 5.3.2) rather than omitting what it
did not compute itself.

#### 4.0c.4 Validation

**V8**: every gate step has an `id:` and `continue-on-error: true`; no gate step uses `|| true`,
`|| exit 0` or `; true`; exactly one Verdict step exists and every isolated step's `id` appears in it;
Sonar is the last gate step and carries `if: always()`.

🔴 A pipeline failing V8 either aborts on the first failure (Defect A) or cannot fail at all
(Defect B). Both pass V1–V7, and both make the PR's green or red meaningless.

### 4.1 Stage 1 — SonarQube: generate everything, then ask for the token

SonarQube is **additive** to semgrep and the Security Baseline review, never a replacement. But
"optional" does not mean "left half-built". **Generate every artifact AIRE can generate, then present
the two values it cannot and wait.**

#### 4.1.1 What AIRE generates (always, when SonarQube is not already configured)

| Artifact | Generated from |
|---|---|
| `sonar-project.properties` | `sonar.organization` — 🔴 **left as `YOUR_ORG_NAME` for the user to replace**; AIRE cannot know the SonarQube organization key. Required by SonarQube Cloud, omitted for self-hosted · `sonar.projectKey` / `sonar.projectName` from the git remote or the repo directory name · `sonar.sources` from the resolved code root (`aire-state.md` `## Code Root`, default `src/`) · `sonar.tests` from `tests/` · `sonar.exclusions` for build output, vendor and generated directories · the coverage report path for the detected test runner (`sonar.javascript.lcov.reportPaths`, `sonar.python.coverage.reportPaths`, `sonar.coverage.jacoco.xmlReportPaths`, `sonar.go.coverage.reportPaths`, …) |
| The scan steps in `.github/workflows/agentic-eval-pipeline.yml` | `SonarSource/sonarqube-scan-action` followed by `SonarSource/sonarqube-quality-gate-action`, with `env: SONAR_TOKEN` and `SONAR_HOST_URL` wired to repository secrets. Written **active**, not commented out. 🔴 Both go **LAST among the gate steps**, with `if: always()` and `continue-on-error: true` (Section 4.0c) — Sonar is one input to the verdict, never a kill switch that skips D1–D7, the tests and the judge. |
| `.evals/config.json` | `sonarqube.enabled: true` |

🔴 **Never invent the two secret values, and never write them into a file.** A token belongs in the
repository's secret store and nowhere else — not in `sonar-project.properties`, not in the workflow
YAML, not in `.evals/config.json`, not in an `.env` committed to the repo.

**Already configured?** If `SONAR_TOKEN` + `SONAR_HOST_URL` already exist as repository secrets, or a
`sonar-project.properties` is already present, use what is there as-is, skip the gate below entirely,
and say so. Never overwrite a properties file a human wrote.

#### 4.1.2 The setup gate — present verbatim, then HALT

Emit the block below exactly as written. **Plain text, no emoji, no decoration** — it is a set of
instructions the user will follow in another window, so it has to read as instructions, not as chat.
Substitute the bracketed values with what was actually generated.

```
CI SETUP REQUIRED

AIRE has generated everything it can for this repository:

  Created   .github/workflows/agentic-eval-pipeline.yml
            all gate steps, the verdict step, and the self repair job
  Created   .evals/scripts/auto-fix-agent.sh
            runs the Claude Code CLI to fix failing gates
  Created   sonar-project.properties
            project key [key], sources [sources], tests [tests], coverage report path
            organization left as YOUR_ORG_NAME for you to set, see below
  Updated   .evals/config.json
            sonarqube.enabled = true

Three values cannot be generated because they belong to your accounts, not to
this repository. Add them as GitHub Actions secrets before the pipeline can run:

  CLAUDE_CODE_OAUTH_TOKEN   lets the pipeline fix its own failing gates
  SONAR_TOKEN               authentication token for SonarQube
  SONAR_HOST_URL            address of your SonarQube server

  sonar.organization        not a secret. Set it in sonar-project.properties,
                            currently YOUR_ORG_NAME. See below.

  GITHUB_TOKEN              nothing to do. GitHub provides this automatically and
                            the pipeline already passes it to the secret scanner.

GET YOUR CLAUDE CODE TOKEN

  1. Install Claude Code, if you do not already have it:
       npm install -g @anthropic-ai/claude-code
  2. Sign in once, interactively:
       claude
     Complete the browser prompt, then leave with /exit
  3. Generate a long lived token for CI:
       claude setup-token
  4. Copy the value it prints. It is shown once.
  5. Prefer an API key instead? Create one at https://console.anthropic.com
     under API Keys, and name the secret ANTHROPIC_API_KEY rather than
     CLAUDE_CODE_OAUTH_TOKEN. The pipeline accepts either.

  Without one of these the gates still run and still block the PR.
  Only the automatic self repair job is skipped.

NOW CHOOSE HOW YOU RUN SONARQUBE


OPTION A - SonarQube Cloud. Hosted by Sonar. Free for public repositories.

  1. Open https://sonarcloud.io and sign in with your GitHub account.
  2. Select Analyze new project and choose this repository.
  3. Open My Account, then Security.
  4. Enter a token name and select Generate.
  5. Copy the token value now. It is shown once and cannot be retrieved later.
  6. Your SONAR_HOST_URL is https://sonarcloud.io

OPTION B - SonarQube Community Build. Free, self-hosted, you run the server.

  1. Start the server:
       podman run -d --name sonarqube -p 9000:9000 docker.io/sonarqube:community
  2. Wait about ninety seconds, then open http://localhost:9000
  3. Sign in with username admin and password admin.
  4. Set a new password when prompted.
  5. Open My Account, then Security.
  6. Enter a token name and select Generate. Copy the token value.
  7. Your SONAR_HOST_URL is the address your CI runner can reach this server on.
     http://localhost:9000 will not work from a GitHub hosted runner. Use a
     reachable host name, or run the pipeline on a self hosted runner.

SET YOUR SONARQUBE ORGANIZATION NAME

  1. Open sonar-project.properties in this repository.
  2. Find the line:  sonar.organization=YOUR_ORG_NAME
  3. Replace YOUR_ORG_NAME with your organization key. Find it in SonarQube Cloud
     under My Organizations, or in the URL of your project page.
  4. Self-hosted SonarQube does not use organizations. Delete the line instead.

IF THIS REPOSITORY IS OWNED BY A GITHUB ORGANIZATION

  The pipeline scans for secrets using the gitleaks container, which needs no token
  and no licence. Nothing to do.

  Only if you later switch to the gitleaks-action marketplace action: that action
  requires a GITLEAKS_LICENSE secret on organization owned repositories. It is free
  for personal and public repositories. See https://gitleaks.io for a licence key.

ADD THE SECRETS TO GITHUB

  1. Open this repository on GitHub.
  2. Go to Settings, then Secrets and variables, then Actions.
  3. Select New repository secret.
  4. Name: CLAUDE_CODE_OAUTH_TOKEN
     Value: the token from claude setup-token.
     Select Add secret.
  5. Select New repository secret again.
  6. Name: SONAR_TOKEN
     Value: the token you copied from SonarQube.
     Select Add secret.
  7. Select New repository secret again.
  8. Name: SONAR_HOST_URL
     Value: your server address.
     Select Add secret.

After adding the secrets and setting your organization name, type: proceed

To continue without SonarQube instead, type: skip
Semgrep and the sixteen rule Security Baseline review still run and still block.
```

#### 4.1.3 Handling the answer

| Answer | Action |
|---|---|
| **`proceed`** | Leave the generated artifacts active. Record in `audit.md` that the user confirmed the secrets were added. Do **not** attempt to verify the secret values — they are not readable from here, and a first pipeline run is what proves them. Continue the STOP CHECKPOINT. |
| **`skip`** | Comment out the two scan steps in the workflow with a one-line note naming the secrets that would enable them, set `sonarqube.enabled: false`, and **keep** `sonar-project.properties` so a later `proceed` needs only the secrets. Record the skip and the reason in `audit.md`. Continue. |
| Anything else | Re-present the block once, unchanged. Do not paraphrase it and do not guess at an intent. |

🔴 **This gate blocks the STOP CHECKPOINT, not the whole framework.** It is presented at CI generation
time, immediately before the workflow halts for `dev-implement` anyway, so it costs the user nothing
extra. `skip` is always a valid, first-class answer — never argue with it and never re-ask on a later
run once it is recorded.

🔴 **Never make SonarQube a hard dependency.** A pipeline that cannot run without a server the team has
not provisioned is a pipeline that gets deleted, taking the real gates with it. Security enforcement
must survive its absence: semgrep (deterministic) plus the Security Baseline diff review (LLM) are the
floor; SonarQube raises the ceiling where it exists.

### 4.1b Stage 2 — behavioural tiers, and which PR runs which

Stage 2 runs the **same three tiers** as the local gate (`common/behavior-spec.md` Section 4.4), in the
**same Podman image**, through the **same entry point**. Scope is decided by the PR's target branch:

| PR | Tiers run | Rationale |
|---|---|---|
| **story / bug / enh → integration branch** | **B1 + B2** | Prove this unit works and broke nothing. Fast — one unit's scenarios plus the accumulated suite. |
| **epic / integration → base branch** | **B1 ∪ B2 ∪ B3** | The last gate before the cycle merges. Runs the whole cycle suite plus `.spec/behavior.feature`. |

```yaml
      - name: Build behaviour image
        run: podman build -t aire-behavior:ci -f .evals/behavior/Containerfile .

      - name: Resolve behavioural tier
        id: tier
        run: |
          # B3 only on a PR into the base branch; B1+B2 otherwise
          if [ "${{ github.base_ref }}" = "<base-branch>" ]; then
            echo "tiers=b1 b2 b3" >> "$GITHUB_OUTPUT"
          else
            echo "tiers=b1 b2" >> "$GITHUB_OUTPUT"
          fi

      - name: Behavioural tests (Gherkin)
        run: |
          for t in ${{ steps.tier.outputs.tiers }}; do
            podman run --rm -v "$PWD:/work:Z" -w /work \
              aire-behavior:ci .evals/behavior/run.sh "$t"
          done
```

🔴 **`run.sh <tier>` is the single entry point.** The developer runs `./.evals/behavior/run.sh b1`,
AIRE's local gate runs the same thing, and CI runs the same thing. Tier membership is resolved
**inside** `run.sh` from the `.spec/` layout and the Story Tracker — never duplicated in the YAML, so
the two can never drift apart.

**Services**: when the suite needs a datastore, the generated job creates a **pod** and runs both
containers into it, mirroring Section 4.3's local setup exactly. Only for a datastore the repo demonstrably
needs.

**Podman on GitHub-hosted runners** is preinstalled on the `ubuntu-*` images. Use `podman`
directly — do not fall back to `docker`. Record the podman version in the evidence.

### 4.2 Stage 3 — the judge in CI

Stage 3 invokes `.evals/scripts/run-evals.*` (generated, Section 5) with the PR diff. It reads
`.evals/config.json` and `.evals/rubrics/`, produces `eval.json` + `eval-summary.md`, and **exits
non-zero** when `J1 < llmJudgeArchitectureScoreMin` or `J2 < llmJudgeSecurityScoreMin`, or any
`gates` entry fails. Authentication: `ANTHROPIC_API_KEY` **or** `CLAUDE_CODE_OAUTH_TOKEN` (Section 6).

---

## 5. Generated scripts — `.evals/scripts/`

Generate in the repo's own primary language so the team can read and edit them.

### 5.0 🔴 NO STUBS. A script that cannot fail is not a gate.

The single most damaging thing this generator can produce is a **plausible placeholder** — a script
that runs, prints reassuring output, writes `"status": "N/A"` and exits 0 without doing the work. It
passes every structural check, turns the PR green, and silently removes a gate from the pipeline. That
is strictly worse than not generating the script at all, because the team believes they are covered.

**Three rules, no exceptions:**

1. 🔴 **Never write a script that hardcodes a passing or `N/A` result.** If the script cannot perform
   its check, it **exits non-zero** with the real reason. It never fabricates an outcome.
2. 🔴 **`N/A` must be earned and must be TRUE.** `N/A` is valid only when the check genuinely does not
   apply, and the recorded `reason` must state the actual cause. Writing
   `"reason": "no judge credentials in this run"` while credentials **are** present is a lie in an
   artifact, and it breaks the rule that every figure quoted downstream matches its source.
3. 🔴 **Distinguish `N/A` from `ERROR`.** Missing credentials, a tool that will not install, an API
   that returns 500 — these are `ERROR` (the check should have run and did not), and they **fail the
   job**. Only "this check does not apply to this work unit" is `N/A`.

**Prove it before committing** — see V9 in Section 4.0.1.

### 5.1 The scripts

| Script | Responsibility |
|---|---|
| `run-static-evals.*` | Takes a base ref. Runs D1–D7 on base and HEAD, diffs the finding sets on `(rule-id, file, message)` — never line numbers — counts only NEW findings on changed files against the `.evals/config.json` thresholds, reports pre-existing findings as non-blocking info. **The local Static Eval Gate and CI both call THIS** — the diff logic exists once (Section 4.0b). |
| `run-evals.*` | Computes the **J1/J2 judge gates** (Section 5.2) and merges them with the deterministic results into `eval.json` + `eval-summary.md`. Exits non-zero on any failed gate or sub-minimum score. |
| `auto-fix-agent.*` | Read `.evals/_run/failed-gates.txt` (**primary** — Section 6.5) plus the failing steps' logs; `eval.json` is supplementary and never a precondition. Triage per Section 6.4, build a precise repair brief (which gate, which file:line, which rubric criterion), invoke the Claude Code CLI, verify the fix re-runs green, commit and push. Enforces `retryLimitForSelfRepair`. |

🔴 All three are **committed to the repo**, not fetched at runtime. A CI gate whose logic lives outside
the repo cannot be reviewed and cannot be reproduced locally.

🔴 **Make them runnable.** Set the executable bit in git
(`git update-index --chmod=+x .evals/scripts/<name>`) **and** invoke them with an explicit interpreter
in the workflow (`run: bash .evals/scripts/<name>.sh`). Either alone is fragile: the bit is lost when
someone recreates the file, and a missing interpreter breaks a non-`.sh` script. Doing both survives
`Permission denied`.

### 5.2 🔴 How `run-evals.*` actually scores J1 and J2

**This is the part that gets stubbed if it is not spelled out.** J1/J2 are LLM judgements, so the
script needs a model call — headless, non-interactive, in a runner with no TTY.

**Mechanism**: the same Claude Code CLI the repair job uses (Section 6). Resolve its headless and
permission flags with `claude --help` at generation time — 🔴 never from memory (Section 6.0).

The script must:

1. **Collect the inputs**: the PR diff (`git diff <base-sha>...HEAD`), `.evals/rubrics/architecture-rubric.json`,
   `.evals/rubrics/security-rubric.json`, and the thresholds from `.evals/config.json`.
2. **Invoke the judge once per rubric**, instructing it to score **each criterion independently** and
   return **strict JSON only** — no prose — in this shape:
   ```json
   { "score": 0.91,
     "criteria": [
       { "id": "ARCH-01", "weight": 0.40, "score": 1.0 },
       { "id": "ARCH-02", "weight": 0.35, "score": 0.8,
         "citation": "src/api/billing.ts:88", "note": "direct ORM call in handler" }
     ] }
   ```
3. **Enforce the scoring discipline** from `common/eval-framework.md` Section 4.1 in the prompt: score
   once, never re-roll; every criterion below 1.0 **must** cite `file:line`; score only what the diff
   shows; a criterion the diff cannot exercise is `N/A` and is excluded with remaining weights
   renormalised to 1.0 — never scored 0.
4. **Validate the response**: it must parse as JSON, carry every criterion id from the rubric, and have
   weights summing to 1.0. 🔴 A malformed or unparseable response is an **ERROR**, not `N/A` — retry
   once, then fail the job.
5. **Compare against the thresholds** and write the result into the **`gates`** block of `eval.json`,
   with the per-criterion breakdown, the pinned judge model and the `rubricVersion`.
6. **Exit non-zero** when `J1 < llmJudgeArchitectureScoreMin` or `J2 < llmJudgeSecurityScoreMin`.

**The only legitimate `N/A` for J1** is the `eval-framework.md` Section 3 fallback chain bottoming out —
no `architecture.md`, no prior rubric, nothing derivable from Atlas or the RE artifacts. Record which
link failed. 🔴 Missing credentials is **ERROR**, never `N/A`: the gate should have run.

**If the rubric file is absent**, say so and fail — do not silently pass. A missing rubric means the
STOP CHECKPOINT did not complete, which is a real problem worth surfacing.

---

### 5.3 🔴 THE EVIDENCE PATH CONTRACT — write and read must be the same path

Every script and every workflow step agrees on **one** layout. These paths are **normative**: a script
that invents its own, or reads from a different directory than it wrote to, produces a gate that
silently reports `N/A` forever while looking healthy.

```text
.spec/aire-docs/implementation/code/eval-evidence/<EVAL_KEY>/
├── eval.json                              <- the scorecard.  NOT one level up.
├── eval-summary.md                        <- pasted into the PR body
├── static/
│   ├── baseline/                          <- pre-change tool output
│   └── <tool>-post.<ext>                  <- post-change tool output
└── judge/
    ├── architecture-score.json            <- J1.  Read it from judge/, not from the parent.
    └── security-score.json                 <- J2 (OWASP 2025)
```

**The three mistakes this contract exists to prevent** — all observed in a real generated pipeline:

| Bug | Symptom |
|---|---|
| Judge files written to `<key>/judge/` but read from `<key>/` | J1/J2 **always** `N/A — judge did not run`, even with valid credentials and a working judge |
| `eval.json` written to `<key>/../eval.json` | Self-repair reports *"No eval.json found — nothing to triage"* and repairs nothing |
| A directory written to without `mkdir -p` | `No such file or directory` on the first CI run, where nothing pre-exists |

🔴 **Every script creates every directory it writes to** (enforced by **V12**):
`mkdir -p "$EVIDENCE_DIR/static/baseline" "$EVIDENCE_DIR/judge" .evals/_run`. A local run works only
because earlier runs left the folders behind; CI starts from a clean checkout and does not.

#### 5.3.1 🔴 `EVAL_KEY` is a work-unit slug, never a branch ref

```yaml
  EVAL_KEY: "${{ github.head_ref }}"        # 🔴 WRONG - "story/2-frontend-upgrade-cta"
```

A branch ref **contains a slash**, so `eval-evidence/${EVAL_KEY}` silently becomes a nested
`eval-evidence/story/2-frontend-upgrade-cta/` — a different location from the `eval-evidence/story-2/`
the local gates wrote. Every downstream reader then finds nothing, and reports it as an absence rather
than a mismatch.

**Derive the key from the work unit, and make it filesystem-safe:**

```yaml
      - name: "Resolve EVAL_KEY"
        id: evalkey
        run: |
          # branch: story/2-frontend-... -> key: story-2
          ref="${{ github.head_ref }}"
          key="$(printf '%s' "$ref" | sed -E 's#^(story|bug|enh)/([^-]+).*#\1-\2#')"
          case "$key" in */*|"") echo "EVAL_KEY unresolved from '$ref'" >&2; exit 1 ;; esac
          echo "key=$key" >> "$GITHUB_OUTPUT"
```

🔴 **Fail loudly if the key still contains `/` or is empty.** A malformed key must stop the run, never
fall through to `unknown` — `eval-evidence/unknown/` is how a whole cycle's evidence gets orphaned.
The key CI computes MUST equal the key the local gates used; they address the same directory.

#### 5.3.2 🔴 Never hardcode a gate result the script did not compute

```python
"D1_lint":       {"status": "N/A"},          # 🔴 WRONG - the static script measured it
"unitCoverage":  {"status": "N/A", "reason": "measured by the workflow's own step"},   # 🔴 WRONG
```

A gate is `N/A` only when it genuinely does not apply (Section 5.0). If another step computed it,
**read that step's output and report the real result** — `run-static-evals.*` writes a machine-readable
summary precisely so `run-evals.*` can merge it. Marking five of seven D-gates `N/A` because the
script did not bother to read them turns the scorecard into decoration.

#### 5.3.3 The scorecard is published from the evidence directory

```yaml
      - name: "Stage 4: publish scorecard"
        if: always()
        run: |
          SUMMARY=".spec/aire-docs/implementation/code/eval-evidence/${{ steps.evalkey.outputs.key }}/eval-summary.md"
          if [ -f "$SUMMARY" ]; then cat "$SUMMARY" >> "$GITHUB_STEP_SUMMARY"
          else echo "::error::No eval-summary.md at $SUMMARY - the eval step did not produce one." ; fi
```

🔴 **Never look for `eval-summary.md` at the repo root** — nothing writes it there. And a missing
summary is an **error to surface**, not a neutral "none produced this run" note: it means Stage 3 did
not complete.

#### 5.3.4 Verification before committing — the round trip

**V17**: run each script once and assert that **every artifact the contract declares exists at the
declared path**, then assert each consumer reads the same path it was written to. Concretely: after
`run-evals.*`, `eval.json`, `eval-summary.md` and both `judge/*.json` must exist under
`eval-evidence/<EVAL_KEY>/`, and `eval.json` must contain a real J1/J2 status — not
`"judge did not run"` when credentials were present.

🔴 A write/read path mismatch passes V1–V16 completely: the YAML parses, the scripts exist and are
executable, the job goes green. Only the round trip catches it.

---

## 6. The CI self-repair agent — the CLI, not the marketplace action

🔴 **Run Claude Code through the generated `.evals/scripts/auto-fix-agent.*` script, using the CLI.
Do NOT use `anthropics/claude-code-action`.**

**Why.** The marketplace action runs with elevated permissions, so GitHub enforces that the workflow
file on the PR branch is **byte-identical to the copy on the default branch**:

```
Workflow validation failed. The workflow file must exist and have identical
content to the version on the repository's default branch.
```

That guard is correct and unavoidable — but it means the action **cannot run on the very PR that
introduces or edits the pipeline**, which is exactly the first cycle in every repository. The CLI has
no such guard: it is an ordinary command in an ordinary step, so self-repair works from the first PR,
on any branch, including the one that created the pipeline.

It is also consistent with the rule already stated in Section 5 — CI logic lives in a committed,
reviewable script that can be reproduced locally — and it removes the need for `id-token: write`
entirely, since there is no OIDC exchange.

### 6.0 🔴 Resolve the CLI flags at generation time — never from memory

CI has **no TTY and no human to approve a tool call**. A headless agent run without the correct
permission flags either hangs until the job times out or completes having changed nothing — and both
look identical to "self-repair ran and found nothing to fix", which is the worst possible failure mode.

Before writing `auto-fix-agent.*`, **run `claude --help` and read the current flags** for:

- print / headless mode (no interactive session)
- permission handling (how tool calls are approved without a human)
- allowed tool restriction (limit it to file edits and the test commands)

Write the resolved flags into the script with a comment naming where they came from, e.g.
`# flags resolved from `claude --help`, CLI vX.Y`. 🔴 Never copy flag names from this document or from
memory — they change, and a wrong flag fails silently.

**Scope the permissions.** The runner is ephemeral, so broader permissions are more defensible there
than on a developer machine — but still restrict the agent to editing the repo and running the
project's own test commands. It must never need network write access or credentials beyond the ones
the job already holds.

**Verify the run did something.** After the CLI exits, the script checks `git status --porcelain`.
No changes plus a zero exit code means the agent made no edits — report that explicitly as
"self-repair produced no changes" rather than letting the job look successful.

```yaml
  self-repair:
    needs: verify-and-evaluate
    if: |
      failure() &&
      github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    permissions:
      contents: write          # push the repair commit
      pull-requests: write     # comment the outcome
                               # no id-token needed — the CLI does not use OIDC
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: 0
      - uses: actions/download-artifact@v4
        with: { name: eval-results }

      # ── Install the SAME runtimes and tools as the verify job ──
      # These steps MUST mirror the verify job's setup exactly.
      # Without them, the re-verification after the fix will fail or skip.
      - name: "Set up runtimes"
        # GENERATE: the same setup-node/setup-python/setup-go steps as verify
      - name: "Install project dependencies"
        # GENERATE: the same pip install / npm ci / mvn install as verify
      - name: "Install eval tools"
        # GENERATE: the same semgrep, gitleaks, pip-audit, etc. as verify

      - name: "Install Claude Code CLI"
        run: npm install -g @anthropic-ai/claude-code

      - name: "Autonomous self-repair"
        env:
          # 🔴 Emit ONLY the variable whose secret is actually configured. An unset
          #    secret expands to an EMPTY STRING, and an empty credential is worse than
          #    an absent one: the SDK sees the variable, tries it, and fails with an auth
          #    error instead of falling through to the other mechanism.
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: bash .evals/scripts/auto-fix-agent.sh
```

🔴 **The `# GENERATE:` comments above are NOT placeholders to leave in the committed YAML.** They
are instructions to the pipeline generator: resolve each one to the actual commands for this project's
stack (from Section 3), identical to the verify job's steps. A committed pipeline with `# GENERATE:`
comments fails V14. To keep them in sync, extract the shared install steps into a reusable composite
action or duplicate them verbatim — never paraphrase or abbreviate.

`auto-fix-agent.*` installs the CLI (`npm i -g @anthropic-ai/claude-code`, pinned), triages the
failure per Section 6.4, builds the repair brief from `eval.json` and the logs, and invokes Claude Code
non-interactively with the brief below, then verifies, commits and pushes.

### 6.0.1 🔴 `auto-fix-agent.*` script requirements — the defects that look like success

These are the exact bugs that produce a green self-repair job that repaired nothing. Each one
was hit in production and must be prevented at generation time.

1. **`EVAL_KEY` must resolve to the same key `eval.json` was written under.** The verify job writes
   evidence to `.spec/aire-docs/implementation/code/eval-evidence/<key>/eval.json` where `<key>` is
   `story-N.M`, `bug-<ID>`, or `enhancement-<ID>` — read from the Story Tracker or the ticket ID.
   The self-repair job must find it at the same path. 🔴 **Never derive the key from
   `github.head_ref`** (the branch name) — branch names do not match evidence keys. Instead, pass
   the resolved key as a workflow-level `env:` variable set in the verify job and consumed by
   self-repair, or have `auto-fix-agent.*` discover it by searching for `eval.json` under the
   evidence root.
2. **`mkdir -p` every directory before writing.** The script uses counter files (e.g.
   `.evals/_run/self-repair-attempt`) to track the retry budget. If the directory does not exist,
   the write fails and the script exits before reaching the repair logic — reporting "nothing to
   triage" when the real problem is a missing directory.
3. **"No eval.json found" is not a free pass.** If `eval.json` is absent AND the verify job failed,
   the script must **exit non-zero** with a clear message ("eval.json missing — cannot triage the
   failure; the verify job's evidence was not produced or not uploaded"). Exiting 0 hides a real
   failure behind a green job.
4. **After each repair attempt, re-run the full eval locally** before committing. Run
   `run-static-evals.*` and `run-evals.*` inside the repair job and confirm the failing gate is now
   green. A commit that does not re-verify is guessing, and a push that fails the next CI run wastes
   a retry attempt on nothing.

**The repair brief — non-negotiable rules, passed verbatim:**

```
The agentic eval pipeline failed on this PR.
Read eval.json and the attached logs. Fix ONLY what failed.
Rules (non-negotiable):
  - Never delete, skip or weaken a test to go green.
  - Never suppress a finding (eslint-disable, # nosec, # type: ignore, ignore-lists).
  - Never lower a threshold in .evals/config.json or edit a rubric.
  - Never edit .spec/architecture.md to make the J1 gate pass.
  - Never edit sonar-project.properties or the Quality Gate to pass a Sonar finding.
  - Fix the code. Then re-run the failing stage and prove it green.
Commit with:  fix(ci): self-repair attempt <n> — <gate>
```

**If the team prefers the marketplace action anyway**: it is a valid choice, but generate it with
`id-token: write` added to `permissions:`, and warn plainly that self-repair stays inert until the
workflow file reaches the default branch (Section 2.1).

### 6.1 Obtaining and configuring the token

Include this verbatim in the completion announcement — the pipeline cannot self-repair without it:

```
CI secrets required
   CLAUDE_CODE_OAUTH_TOKEN   run `claude setup-token` locally, then add it at
                             Settings > Secrets and variables > Actions > New repository secret
   ANTHROPIC_API_KEY         alternative to the OAuth token, for both the judge and self-repair
   SONAR_TOKEN + SONAR_HOST_URL   SonarQube; AIRE prompts for these at the Section 4.1.2 setup gate

   Without one of the first two, the gates still run and still block. Only the
   automatic self-repair job is skipped.
```

### 6.2 Retry limit and its relationship to local self-healing

- CI self-repair is capped by **`retryLimitForSelfRepair`** in `.evals/config.json` (default **3**),
  counted as commits tagged `fix(ci): self-repair attempt <n>` on the PR head.
- 🔴 **This is a separate budget from the local SH-LOOP counters.** A local loop that exhausted its 3
  attempts halts locally and never reaches CI; CI's 3 attempts apply to failures that appear only in
  the CI environment.
- **On exhaustion**: stop, post a PR comment naming every unresolved gate, what each attempt changed,
  and why it did not resolve — closing with *"3 retries ended. Please suggest next steps."* Do not
  push further commits. Do not close or merge the PR.
- 🔴 **Never let the self-repair job pass the build.** It repairs and re-runs; the verify job's own
  result is the only thing that turns the PR green.

### 6.3 Safety rails on the repair job

- Skips on **fork PRs** (secrets are unavailable and untrusted code must not run with write scope).
- `permissions:` is the minimum shown — never `write-all`. With the CLI, `id-token` is **not** needed;
  add it only if the team chose the marketplace-action variant.
- Never force-pushes; never touches any branch other than the PR head.
- Every attempt is one commit, so the whole repair history is reviewable in the PR.
- 🔴 Triage before repairing (Section 6.4). An infrastructure failure is never a code defect.

### 6.4 🔴 TRIAGE BEFORE REPAIRING — not every red job is a code defect

The job fails when **any** gate's outcome is `failure` (Section 4.0c), so self-repair is reached from
several very different causes. **Classify first. Repair second.** An agent that starts editing source
because a token expired does real damage.

| Failure | Class | Self-repair |
|---|---|---|
| D1–D7 **new** findings on changed files | Code | ✅ Repair |
| Unit test failure or coverage below the floor | Code | ✅ Repair |
| Behaviour (Gherkin) scenario failing | Code | ✅ Repair |
| API-contract or regression failure | Code | ✅ Repair |
| J1 / J2 below the configured minimum | Code | ✅ Repair the cited criteria |
| **SonarQube Quality Gate failed WITH reported conditions** (e.g. *"C Reliability Rating on New Code"*) | Code | ✅ Repair — these are real findings on new code |
| **SonarQube auth / unreachable / timeout / missing or wrong `sonar.organization`** | Infrastructure | ❌ **Never** — report and stop |
| Workflow-validation failure (Section 2.1) | Infrastructure | ❌ **Never** |
| Missing secret, runner or network error, dependency-install failure | Infrastructure | ❌ **Never** |

**Telling the two SonarQube cases apart**: the quality-gate action reports the **failed conditions**
when it actually evaluated the gate. Conditions present → real findings, repair them. An error *before*
evaluation — `401`/`403`, host unreachable, project not found, the `timeout-minutes` expiring — means
the gate never ran; there is nothing to repair.

🔴 **An infrastructure failure never consumes a `retryLimitForSelfRepair` attempt**, never enters
`eval.json` as a gate result, and never triggers a source edit. Post one clear PR comment naming the
cause and what the user must fix, then stop.

🔴 **Never "fix" a Sonar finding by editing `sonar-project.properties`, changing the Quality Gate,
lowering a condition, or marking an issue Won't Fix.** That is suppression (SH-6) and is forbidden — fix
the code, or report that it cannot be fixed automatically.

---

### 6.5 🔴 SELF-REPAIR'S INPUT CONTRACT — it is GIVEN the failure, it does not hunt for it

**Order of inputs, and what each is allowed to do:**

| Input | Role | If missing |
|---|---|---|
| `.evals/_run/failed-gates.txt` (from the Verdict step) | **PRIMARY.** The authoritative list of what failed. | 🔴 **Pipeline defect.** Report it and exit **non-zero**. The Verdict step must always produce it. |
| The failing steps' **logs** | Primary detail — the actual error text to repair against | Report what is missing; continue with what is available |
| `eval-evidence/<EVAL_KEY>/eval.json` | **SUPPLEMENTARY** context: per-criterion scores, citations | 🔴 Continue anyway. See below. |

🔴 **`eval.json` is NOT a precondition for repairing.** The build failed; that fact is established by
the Verdict step, not by the scorecard. If `eval.json` is absent or unreadable, repair from
`failed-gates.txt` plus the logs — and report the missing scorecard as a **separate finding**.

🔴 **"I could not find my input" is NEVER an infrastructure failure of the build.** Observed in a real
run:

```
No eval.json found at .../eval-evidence/story/2-frontend-.../eval.json — nothing to triage.
Treating as infrastructure failure, not repairing.
```

Three things wrong with that, all forbidden:

1. It **misclassified** a real SonarQube code failure as infrastructure (Section 6.4 triages the
   *failure*, never the agent's own inability to locate a file).
2. It **exited 0**, so a job that should have stayed red reported success.
3. It **stopped**, when `failed-gates.txt` and the step logs both said plainly what had failed.

**The correct behaviour**: read `failed-gates.txt`, see `sonar`, triage it per Section 6.4 (conditions
were reported → code-class), repair the reliability findings, re-run, commit.

🔴 **Self-repair NEVER exits 0 on a job it did not repair.** Exit 0 means "the failure was addressed".
Anything else — could not classify, could not locate its inputs, chose not to act — exits **non-zero**
with the reason, so the PR stays red.

---

## 7. Relationship to the local gates — 🔴 CI adds, it never replaces

| | Local (`dev-implement`) | CI (this pipeline) |
|---|---|---|
| When | Before the PR is raised | On every PR push |
| Gates | D1–D7, unit+coverage, behavioural, API contract, regression, J1, J2 | The same set |
| Self-heal | SH-LOOP-1…7, 3 attempts each | `retryLimitForSelfRepair`, 3 attempts |
| Authority | Blocks the PR from being raised | Blocks the PR from being merged |

🔴 **Nothing in this file changes the local gates or the local self-healing loops.** They keep their
definitions, their order and their budgets. CI is an outer ring: it re-verifies in a clean
environment what was verified on the developer's machine, and it is what branch protection can
actually enforce.

---

## 8. Completion announcement

```
⚙️ CI pipeline generated — .github/workflows/agentic-eval-pipeline.yml
   Stack: <detected>   Package manager: <detected>
   Commands resolved from: <package.json scripts | Makefile | pyproject.toml | pom.xml>
   Stage 1 (deterministic): <n> checks   SonarQube: [configured | awaiting secrets | skipped by user]
   Stage 2 (behavioural):   <runner> + coverage ≥ <unitTestCoverageMin>%
   Stage 3 (semantic):      J1 ≥ <min> · J2 ≥ <min>  — BLOCKING
   Verdict step:            the ONLY step that fails the job — tallies every gate
   Self-repair:             Claude Code CLI, max <retryLimitForSelfRepair> attempts
   Scripts written (executable + invoked with an explicit interpreter):
     .evals/scripts/run-static-evals.<ext>  — D1–D7, delta vs base ref
     .evals/scripts/run-evals.<ext>         — J1/J2 via the CLI, real scores
     .evals/scripts/auto-fix-agent.<ext>    — self-repair
   Trigger:  PRs into <base-branch>, epic/**, bug/**, enh/**  (Section 4.0a)
   Verified: V1 YAML parses | V2 actionlint | V3 scripts exist | V4 files exist
             V5 secrets listed | V6 permissions declared | V7 delta-scoped
             V8 failures isolated | V9 gates proven able to FAIL | V10 branches covered
   🔑 Secrets to add: <list>
   📦 Pushed directly to <base-branch> (<commit>) — self-repair can run from the next PR onward.
      [or] Raised as PR <url> into <base-branch> — merge before dev-implement. Gates enforce either way.
```

Log the same in `audit.md`, including the full list of resolved commands and their source, so a
reviewer can check that nothing was invented.
