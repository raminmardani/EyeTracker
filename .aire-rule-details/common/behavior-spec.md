# Behavior Specs — Gherkin, and Where It Lives

**Purpose**: the executable behavioural contract the code must satisfy. Two levels, nothing else.

**Load this file when**: writing a `.feature` file, or running the behavioural test gate.

---

## 1. Two files, two levels. That is the whole structure.

```text
.spec/
├── architecture.md                                  # ONCE per cycle — the system design
├── behavior.feature                                 # ONCE per cycle — cross-story journeys
└── aire-docs/
    └── implementation/
        └── code/
            └── behavior/
                ├── story-1.1.feature                # one file per work unit
                ├── story-1.2.feature
                ├── bug-PROJ-123.feature
                └── enh-PROJ-456.feature
```

| File | Scope | Written when | Tagged with |
|---|---|---|---|
| `.spec/architecture.md` | Whole cycle | End of the design stages (STOP CHECKPOINT) | — |
| `.spec/behavior.feature` | Whole cycle | End of the design stages (STOP CHECKPOINT) | `@REQ-<id>` |
| `.spec/aire-docs/implementation/code/behavior/<work-unit>.feature` | One work unit | Before that unit's code is generated | `@AC-<n>` |

🔴 **`architecture.md` is written ONCE for the whole cycle — never per story.** A story does not get its
own architecture document. If a story needs architectural context, it reads the relevant section of
`.spec/architecture.md` directly.

🔴 **No other per-story spec files.** No `01-requirements.md`, no `02-architecture.md`, no
`04-constraints.md`, no per-story knowledge graph. That information already exists and is already
authoritative elsewhere — copying it per story only creates something that can drift:

| The agent needs | It reads |
|---|---|
| Acceptance criteria | the tracker item, and `.spec/aire-docs/planning/user-stories/stories.md` |
| Requirements text | `.spec/aire-docs/planning/requirements/requirements.md` (via the story's `Covers` REQ-IDs) |
| Architecture and its constraints | `.spec/architecture.md` |
| Thresholds and quality floor | `.evals/config.json` |
| Security rules | the Security Baseline extension |
| Existing-system truth | `.spec/aire-docs/planning/reverse-engineering/` (from Atlas — `helix-atlas-integration.md`) |

---

## 2. Writing the work-unit feature file

Written **before** the implementation — it is the contract, not a description of what got built.

1. **One `Scenario` per acceptance criterion, minimum.** An AC with several distinct outcomes gets a
   scenario per outcome. Every AC must appear.
2. **Tag every scenario with its AC**: `@AC-1`. The gate reports coverage by tag, and an AC with no
   scenario fails the gate.
3. **Name scenarios after the behaviour**, not the mechanism: `Successful prorated upgrade`, not
   `Test upgrade function`.
4. **Cover the failure paths.** Every error condition the acceptance criteria or the API contract name
   gets its own scenario. Happy paths only does not pass this gate.
5. **`Background:`** holds shared preconditions — fixture data, authenticated actor, system state.
6. **Steps describe business behaviour, never implementation**:
   - Yes: `Then the user's plan should be "PRO"`
   - No: `Then subscriptionRepository.update should have been called`
7. **Concrete, checkable values**: `Then a prorated charge of $10.00 is calculated`, not
   `Then the charge is correct`.
For example format given below:
```gherkin
Feature: Mid-Cycle Subscription Upgrade

  Background:
    Given a user "A" exists with ID "usr_123"
    And "A" has an active "STANDARD" subscription at $20/month
    And 15 days remain in the 30-day billing cycle

  @AC-1
  Scenario: Successful prorated upgrade
    When "A" requests an upgrade to "PRO" at $40/month
    Then a prorated charge of $10.00 is calculated
    And "A"'s plan becomes "PRO"
    And the response is 200 with proratedCharge 1000

  @AC-3
  Scenario: Payment declined during upgrade
    Given "A" has an expired card on file
    When "A" requests an upgrade to "PRO"
    Then "A"'s plan remains "STANDARD"
    And the response is 402 Payment Required
```

## 3. Writing the cycle-level `.spec/behavior.feature`

Holds the journeys that **span** work units — the ones no single story owns and that only become
testable once several exist. Tagged `@REQ-<id>` against `requirements.md`.
Example format given below:
```gherkin
Feature: Subscription lifecycle — end to end

  @REQ-014 @REQ-021
  Scenario: A standard subscriber upgrades, is billed, and sees the new plan
    Given a new user signs up on the "STANDARD" plan          # story 1.1
    When they upgrade to "PRO" mid-cycle                       # story 1.3
    Then the prorated charge is taken                          # story 1.3
    And the billing history shows both entries                 # story 1.4
    And the portal displays "Pro Plan"                         # story 1.5
```

🔴 **Not a copy of the per-story scenarios.** If it only restates what individual stories already
cover, it is adding nothing — write the genuine cross-unit journeys, or record explicitly that the
requirement has none.

---

## 4. Step definitions and runner configuration

Step definitions live in **`tests/behavior/steps/`**. Feature files live under `.spec/`. They are in
different trees **on purpose**: a `.feature` file is an authored specification, a step definition is
source code, and `.spec/` never holds source.

### 4.1 🔴 The runner MUST support explicit feature and step paths

Some BDD runners locate step definitions by **walking up from the feature file** looking for an
adjacent `steps/` directory. That discovery model is incompatible with this layout — it can never
reach `tests/behavior/steps/` from a feature under `.spec/`.

🔴 **Choose a runner that accepts explicit paths. Never work around a runner's discovery model by
scattering bridge folders across the repo** — a `steps/` directory at the workspace root, a re-export
shim, or a copy of the feature files is a symptom of the wrong runner, not a solution. Nothing outside
`src/`, `tests/`, `.spec/` and `.evals/` may be created (`common/directory-structure.md`).

| Stack | Runner | Why it works | Configure with |
|---|---|---|---|
| Python | **`pytest-bdd`** — 🔴 use this, not `behave` | `scenarios()` takes an arbitrary feature path; steps live in the test module or `conftest.py` | `scenarios("<relative path to .feature>")` in `tests/behavior/test_<unit>.py` |
| JS / TS | `@cucumber/cucumber` | `--import` / `--require` accept globs | `paths` + `import` in `cucumber.cjs` |
| Java / Kotlin | Cucumber-JVM | `features` and `glue` are independent options | `@CucumberOptions(features=…, glue=…)` |
| Go | `godog` | Steps are registered in Go test code; features passed as paths | `godog.Options{Paths: […]}` |
| .NET | Reqnroll | Feature files are project items with a configurable path | `reqnroll.json` |

🔴 **Do not use `behave`.** It resolves `steps/` relative to the feature directory, which would force
step code inside `.spec/`. `pytest-bdd` covers the same Gherkin surface with no adjacency requirement,
and reuses the project's existing pytest setup.

**Python reference shape:**

```python
# tests/behavior/test_story_1_1.py
from pytest_bdd import scenarios
scenarios("../../.spec/aire-docs/implementation/code/behavior/story-1.1.feature")
```
```python
# tests/behavior/steps/billing_steps.py   — imported via conftest.py
from pytest_bdd import given, when, then
```

### 4.2 Binding rules

- Bind the Gherkin vocabulary to `src/` through the application's **public surface** — HTTP endpoint,
  service method, CLI. Never reach into internals.
- Reuse steps across features. A vocabulary that drifts per feature is a maintenance failure.
- Keep the runner's config file in the repo root if its tooling requires it (`cucumber.cjs`,
  `pytest.ini`); keep everything else under `.evals/behavior/`.

Bootstrap the runner if the repo has none, per `common/eval-framework.md` Section 2.3 — minimal
recommended config, announced, committed with the work unit.

---

## 5. 📦 Sandboxed execution — Podman, always

🔴 **EVERY behaviour tier — B1, B2 and B3 — runs inside a Podman container. There is no
"this tier does not need it" case.** The container is not a convenience for browser tests; it is what
makes the result *mean* something: an isolated runtime, a clean test database, the same image locally
and in CI. A scenario that passes on a developer's machine and fails in the pipeline is worse than no
scenario, because nobody trusts any result afterwards.

```text
.evals/behavior/
├── Containerfile          # runtime + project deps + the Gherkin runner
└── run.sh                 # THE entry point — developer, AIRE, and CI all call this
```

### 5.1 🔴 The ONLY permitted exception

Containerisation may be skipped **if and only if Podman is not installed on the machine**, proven by
an actual check:

```bash
command -v podman || echo "PODMAN NOT INSTALLED"
```

🔴 **Nothing else is a valid reason. Never reason your way out of the container.** All of the
following are FORBIDDEN justifications, and a run recorded with any of them is a **gate violation**,
not a passing tier:

- ✗ "this tier only exercises backend code, no browser needed"
- ✗ "the suite runs through TestClient, so no service is required"
- ✗ "no new dependency was introduced by this story"
- ✗ "it is faster natively"
- ✗ "the container adds no value for these scenarios"

The point is **environment parity**, not browser support. A backend suite is exactly the case where a
native run diverges — host Python version, a stale local venv, an OS package the runner lacks, a
database that happens to be running locally. Those are the failures the container exists to catch.

**When Podman genuinely is absent**: run natively, record
`"containerised": false, "reason": "podman not installed"` — that **exact** reason, nothing
invented — surface it loudly in the output, and mark the tier **`PASS (unverified parity)`** rather
than plain `PASS`. 🔴 **In CI this must never happen**: GitHub-hosted `ubuntu-*` runners ship with Podman, so
`containerised: false` in a CI run is a pipeline defect to fix, not a result to accept.

🔴 **PODMAN ONLY — never fall back to the Docker CLI.** If Podman is missing, that is the Section 5.1
exception (run natively, recorded); it is **not** a cue to try `docker`. One runtime keeps the image,
the flags and the rootless behaviour identical everywhere.
*(A `docker.io/...` prefix inside an image reference is the Docker Hub **registry hostname**, which
Podman pulls from normally. It is not the Docker CLI and is fine to use.)*

### 5.2 Building the image

- **Reuse before creating.** An existing `Containerfile`, `Dockerfile`, devcontainer or compose file
  that builds a working test environment wins — Podman builds a `Dockerfile` unchanged. Only generate
  one when nothing is reusable.
- **Build**: `podman build -t aire-behavior:local -f .evals/behavior/Containerfile .`

🔴 **THE IMAGE MUST BE PROVEN TO BUILD BEFORE THE GATE IS DECLARED READY.** Run the build at
bootstrap and treat a non-zero exit as a **blocking ERROR**, quoting the real build output. Never
continue to `podman run` with an image that was not built: the run then treats `aire-behavior:local`
as a **remote** reference and fails with a confusing registry 404/denied, hiding the actual cause.

🔴 **The Containerfile must `COPY` every file its install step transitively needs.** Dependency
manifests reference each other — `requirements-dev.txt` containing `-r requirements.txt`,
`package.json` needing `package-lock.json`, a `pyproject.toml` needing its lock file. Copying only the
file named on the `RUN` line makes the build fail inside the container on a path that exists perfectly
well on the host.

  - **Before writing the COPY lines**, open each manifest and follow its includes one level at a time
    until nothing new is referenced. Copy every file in that closure.
  - Verify by building. A green build is the only acceptable evidence — reading the Containerfile is
    not.

```dockerfile
# WRONG - requirements-dev.txt does `-r requirements.txt`, which was never copied
COPY src/backend/requirements-dev.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt

# RIGHT - copy the whole closure, preserving the relative layout the manifest expects
COPY src/backend/requirements.txt src/backend/requirements-dev.txt /tmp/deps/
RUN pip install --no-cache-dir -r /tmp/deps/requirements-dev.txt
```

### 5.3 The pod: app + its data stores

Behaviour scenarios exercise real behaviour, so they need the real dependencies — **a test database,
not a mock**. Run the suite and its stores in a **pod** so they resolve each other by name:

```bash
podman pod create --name aire-beh -p 8000:8000

# every datastore the repo demonstrably needs, ephemeral, seeded fresh per run
podman run -d --pod aire-beh --name beh-db \
  -e POSTGRES_PASSWORD=test -e POSTGRES_DB=test docker.io/library/postgres:16

podman run --rm --pod aire-beh -v "$PWD:/work:Z" -w /work \
  -e DATABASE_URL=postgresql://postgres:test@127.0.0.1/test \
  aire-behavior:local .evals/behavior/run.sh <tier>

podman pod rm -f aire-beh          # always torn down, pass or fail
```

- 🔴 **Only a store the repo demonstrably needs** — evidenced by a compose file, a test config, or a
  connection string in test setup. Never invent one.
- 🔴 **Ephemeral and seeded per run.** Never point a behaviour run at a developer's local database or
  any shared environment: a scenario that mutates shared state makes every later run
  non-reproducible.
- **Tear the pod down on every exit path**, including failure.
- **Rootless-safe**: `:Z` on mounts for SELinux hosts; never require `--privileged`.

### 5.4 Evidence must prove the sandbox

The `evidence-manifest.md` for every tier records the **image reference and digest**, the exact
`podman` command, the pod members, and `containerised: true`. 🔴 A tier whose evidence cannot show
which image produced it has not demonstrated parity, whatever its scenarios reported.

🔴 **`run.sh <tier>` resolves tier membership itself** from the `.spec/` layout and the Story Tracker.
Never duplicate that logic in CI YAML — that is how local and CI drift apart.

---

## 6. 🥒 THE BEHAVIOUR GATE — three tiers

Widening scope. Each tier runs only once the previous is green.

| Tier | Runs | Proves | Loop |
|---|---|---|---|
| **B1** | This work unit's `<work-unit>.feature` | I built what was asked | SH-LOOP-7 |
| **B2** | Every **other** `.feature` file in `code/behavior/` | I broke nobody else's behaviour | SH-LOOP-7 |
| **B3** | B1 ∪ B2 **+ `.spec/behavior.feature`** | The requirement works end to end | SH-LOOP-8 |

```
Story 1.1 done → B1: 1.1        B2: (prior cycles)
Story 1.2 done → B1: 1.2        B2: 1.1
Story 1.5 done → B1: 1.5        B2: 1.1–1.4     B3: all + .spec/behavior.feature   ← last unit only
```

**Bug and enhancement cycles** use the same tiers — B1 is the fix's scenarios, B2 the entire existing
suite (the tier that matters most there: it proves the change broke nothing), B3 adds
`.spec/behavior.feature`. Since there is one work unit, B3 runs on it — record that, do not pretend it
was skipped.

### 6.1 Detecting the last work unit

🔴 **The trigger is PR MERGE STATE, never the tracker status label.** These are two different facts and
they lag each other: a story's PR merges during `dev-implement`, but its status only becomes
`🧪 Ready for Testing` later, when ve signs it off with `ve-list-work`. Keying B3 on the label means a
merged-but-not-yet-signed-off story reads as "still open", B3 defers forever, and the epic gate never
runs on any cycle.

**At B2-green time, for every OTHER work unit in this cycle, resolve its PR merge state:**

1. Read the `## Story Tracker` in `aire-state.md` for each unit's `PR` and `Merged` columns.
2. **Verify live** — `gh pr view <n> --json state,mergedAt` — do not trust a stale `Merged` column.
3. A unit counts as **done** when its PR is `MERGED`. Its tracker status is irrelevant here:
   `🔵 In Development` with a merged PR is **done** for this purpose.

**This is the last work unit → RUN B3** when every other unit's PR is merged. That includes the common
case you will hit most: *the final story, with all previous stories implemented and their PRs merged,
still sitting at `🔵 In Development` awaiting ve sign-off.* 🔴 **B3 runs.** Do not defer it because a
status label has not moved yet.

**Only defer B3** when a unit genuinely has **no merged PR** — no PR raised, or one still open. Record
`B3: N/A — deferred, <n> units with unmerged PRs (<list with PR state>)`, naming each unit and the
actual state you observed. 🔴 Never report a deferred B3 as a pass, and never defer on a status label
alone.

**Single-unit cycles** (bug, enhancement, or a one-story epic): there are no other units, so the
condition is satisfied immediately and **B3 runs on that unit**. Record that it ran on a single-unit
cycle — do not present it as skipped.

**Concurrency**: two developers finishing together may both see "all others merged" and both run B3.
Harmless — the same suite runs twice. Note it; do not add locking.

### 6.2 Verification and evidence

**Verification**: every scenario passes; for B1 every `@AC-<n>` in the story is executed; for B3 every
`@REQ-<id>` the cycle covers is executed.

**Evidence** per tier → `.spec/aire-docs/implementation/code/behavior-test-evidence/<key>/<b1|b2|b3>/`:
`behavior-test-run.log`, the **mandatory machine-readable** `behavior-test-report.*`, and an
`evidence-manifest.md` with the image ref + digest, the exact command, whether it ran containerised,
the tier's file set, and every scenario with its tag and result. 🔴 `containerised` must be `true` — anything else is only valid under the Section 5.1 exception, with its exact reason. A raw log alone does not satisfy it.

### 6.3 Failure handling

- **B1 / B2 fail** → 🔁 **SH-LOOP-7**, 3 attempts, then SH-4 (HALT + Retry-Limit Report).
- **B3 fails** → 🔁 **SH-LOOP-8**, its own 3 attempts. An epic-scope failure is usually an integration
  gap *between* units, so it must not inherit a budget already spent on one story's retries.
- 🔴 **Fix the code, never the scenario.** A scenario changes only when the AC or requirement it
  encodes genuinely changed — and then the AC, `requirements.md` and the tracker item are amended
  together and the reconciliation is logged. Deleting, skipping or `@ignore`-ing a scenario to go green
  is the exact analogue of deleting a failing unit test and is equally forbidden (SH-6).
- 🔴 **A B2 failure is THIS unit's problem.** "That scenario belongs to another story" is not a
  defence — this unit turned it red, so this unit fixes it.

**N/A**: B1 only for a unit with no externally observable behaviour (pure build-config or docs change);
a unit with acceptance criteria is never N/A. B2 only when no other feature file exists. Record why.
