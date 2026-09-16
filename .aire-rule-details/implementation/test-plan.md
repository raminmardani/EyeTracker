
# Test Plan (ve — per story, black-box, MANUAL test steps)

**Purpose**: For **ONE story/ticket**, produce the complete **Test Plan artifact set** as
**manual, executable-by-a-human test steps** covering every test plan that applies to that story.

**Owner**: ve. This file is loaded and executed by the **`/ve-implement` skill**
(`.aire-rule-details/agents/ve-implement-agent.md`). It is **NOT** a Implementation-phase stage — it is
neither an epic-level nor a story-level step of the development workflow, and no development
workflow runs it.

**🔴 WRITTEN EARLY, EXECUTED AFTER MERGE — AND NOTHING IS EVER DEPLOYED.** These steps are
*authored* as soon as the design stages finish (no code needed). They are *executed* by the ve
once the story's code is **merged into the epic branch** (epic cycles) or the **base branch**
(bug/enhancement cycles). At that point the code has **not** been deployed to any environment, so
every plan below must assume the ve **checks out the merged branch, builds it, and runs it
locally, using the project's own build documentation** (its README / CONTRIBUTING / Makefile). That
local instance is the system under test. **Do NOT generate build instructions** — the project
already owns them, they are identical for every story, and they trace to no acceptance criterion.
Just state the dependency in the System Under Test block below. Never write a step that depends on
a dev/QA/staging deployment, a shared base URL, or a pre-running service.

**🔴 BLACK-BOX — NEVER READ APPLICATION SOURCE CODE.** ve runs **in parallel with development**:
when this file executes, the story's code may not exist yet, may be half-written, or may sit on
an unmerged branch. Every test step is derived from the story's **Acceptance Criteria** and the
documents listed under Inputs — never from implementation code.

---

## Prerequisites

- A target story/ticket has been resolved (Story ID `N.M` and/or a Tracker ID) by the `/ve-implement` skill.
- **No dependency on the DEV's code, branch, PR, or merge state.** This runs at any time after the
  story exists — typically while the developer is still building it.
- **This file's own git mechanics — cutting the `ve/…` branch, committing, pushing, and raising
  the PR that carries these artifacts — are handled by `ve-implement-agent.md` Step 3 and Step 5, wrapped
  around this file's execution.** This file is the authority for WHAT test content to generate; it
  does not itself run git commands.

---

## Inputs (read these, and ONLY these)

| # | Source | What it gives you |
|---|--------|-------------------|
| 1 | **The tracker story itself** (`getJiraIssue` / `az boards work-item show` / `gh issue view`, per `common/tracker-sync.md` Section 8, when the story has a non-LOCAL Tracker ID) | Authoritative summary, description, **acceptance criteria** |
| 2 | `.spec/aire-docs/planning/user-stories/stories.md` | Story detail + AC (source of truth when there is no non-LOCAL Tracker ID) |
| 3 | `.spec/aire-docs/planning/requirements/requirements.md` | REQ-IDs the story `Covers`, NFR targets |
| 4 | `.spec/aire-docs/planning/requirements/epic-brief.md` | What the epic/ticket is meant to deliver |
| 5 | `.spec/aire-docs/implementation/design/**` (functional / NFR / NFR-design / infrastructure) | Interfaces, endpoints, data shapes, performance & security targets, deployment topology |
| 6 | `.spec/aire-docs/planning/reverse-engineering/**` (if present) | Existing external interfaces, APIs, architecture of the system under test |
| 7 | `.spec/aire-docs/aire-state.md` | `## Story Tracker` (Story ID ↔ Tracker ID ↔ title), `## Tracker`, `## Branching` |

**🔴 Explicitly OUT OF BOUNDS**: application source files, unit tests, diffs, PRs, commits — and
**build configuration too** (`package.json`, `pom.xml`, `Dockerfile`, `docker-compose.yml`, CI
files). This file generates no build instructions, so there is nothing they could be needed for.
If a detail you need is not in the inputs above, write the step with an explicit
`⚠️ TO CONFIRM: [what you need]` marker — never guess it from code, and never read code to fill it.

---

## Output Location (per story)

All artifacts for a story go into their **own folder**, named from the story's **Tracker ID and
title**:

```
.spec/aire-docs/tests/<TICKET-ID>-<title-kebab-case>/
```

Examples:
- `.spec/aire-docs/tests/PROJ-101-user-can-reset-password/`
- `.spec/aire-docs/tests/AT-256-health-check-endpoint/`

If the story has **no non-LOCAL Tracker ID** (local-only story), use the Story ID instead:
`.spec/aire-docs/tests/story-1.2-<story-title-kebab-case>/`.

**🔴 One folder per story — never write another story's artifacts into it, and never overwrite an
existing story folder.** If the folder already exists, this story's Test Plan artifacts have
already been generated: report that and ask whether to **refresh** (regenerate) or **stop**.

---

## Step 1: Resolve the Story and Extract Acceptance Criteria

1. Resolve the story's **Tracker ID**, **title**, and **Story ID** from the `## Story Tracker`.
2. If a non-LOCAL Tracker ID exists, fetch the issue per `common/tracker-sync.md` Section 8 and use its description/AC as
   authoritative. Otherwise use `stories.md`.
3. Extract the **numbered acceptance criteria** list (`AC-1`, `AC-2`, …) and the REQ-IDs the story
   covers. Every test step you write later must trace back to one of these.
4. Record the resolved folder name: `.spec/aire-docs/tests/<TICKET-ID>-<title-kebab>/`.

---

## Step 2: Determine Which Test Plans Apply to THIS Story

Assess the story's AC, requirements, and design artifacts and decide which of the plans below
apply. **Only generate the applicable ones** — mark the rest `N/A` with a one-line reason in the
summary.

| Test Plan | Applies when | Artifact file |
|-----------|--------------|---------------|
| **Integration** | The story touches ≥2 components/services, or a service + datastore/queue/3rd-party | `integration-test-steps.md` |
| **End-to-End (E2E)** | The story completes a user-visible workflow (UI or API journey) | `e2e-test-steps.md` |
| **API** | The story adds/changes an endpoint or its contract-visible behaviour | `api-test-steps.md` |
| **Contract** | Microservices — a consumer/provider schema changes | `contract-test-steps.md` |
| **Security** | Auth/authz, input handling, PII, secrets, or a Security Baseline rule is in scope | `security-test-steps.md` |
| **Performance** | The story or its requirements carry latency / throughput / concurrency / volume targets | `performance-test-steps.md` |
| **Accessibility** | The story delivers or changes UI | `accessibility-test-steps.md` |

Present the applicability decision to ve before writing files:

```markdown
# 🧪 Test Plan — [TICKET-ID] [Story title]

**Acceptance criteria found**: AC-1 … AC-[n]
**Requirements covered**: [REQ-IDs]
**Output folder**: .spec/aire-docs/tests/<TICKET-ID>-<title-kebab>/

| Test Plan | Applies? | Why |
|-----------|----------|-----|
| Integration | ✅ | [reason] |
| E2E | ✅ | [reason] |
| API | ✅ | [reason] |
| Contract | ❌ N/A | [reason] |
| Security | ✅ | [reason] |
| Performance | ❌ N/A | [reason] |
| Accessibility | ❌ N/A | [reason] |

> Proceed with generating the manual test steps for the ✅ plans? (yes / adjust)
```

Wait for ve's answer.

---

## Step 3: Manual Test Case Format (MANDATORY for every generated step)

Every test case in every artifact uses **this exact structure**. These are steps a **human tester
executes by hand** — no code, no test framework, no scripts.

```markdown
### TC-[PLAN]-[nn] — [Short title]

| Field | Value |
|-------|-------|
| **Traces to** | AC-[n] [/ REQ-ID] |
| **Type** | Integration / E2E / API / Contract / Security / Performance / Accessibility |
| **Priority** | P1 (critical path) / P2 / P3 |
| **Preconditions** | [the locally built + running instance described in **System Under Test**, plus data, accounts, feature flags, local services that must be up — NEVER a deployed environment] |
| **Test data** | [exact inputs / payloads / user accounts to use] |

**Steps**
1. [Action the tester performs — concrete and unambiguous]
2. [Action]
3. [Action]

**Expected result**
- [Observable, verifiable outcome — status code, message, screen state, record state]
- [Second expectation, if any]

**Pass/Fail criteria**: [what makes this a PASS; anything else is a FAIL]
**Cleanup**: [how to reset state after the run]
```

Rules for writing the steps:
- **Observable only** — assert on things a tester can SEE from outside the system (HTTP response,
  UI state, email received, row visible in an admin screen, log line in a shipped log).
  Never assert on internal functions, classes, or private state.
- **Negative and edge cases are mandatory** — every AC gets at least one happy-path case and at
  least one negative/boundary case.
- **Traceability is mandatory** — no test case without an `AC-[n]`. No AC without ≥1 test case.
- **Self-contained** — a tester who has never seen this project must be able to run the case.
- Where the AC leaves a detail undefined, write `⚠️ TO CONFIRM: [question for the BA/dev]`
  inline rather than inventing behaviour.

---

## Step 4: Generate Each Applicable Functional/Non-Functional Test Plan

For each ✅ plan from Step 2, create its artifact file in the story folder. Each file opens with a
short purpose + scope block, then lists test cases in the Step 3 format.

**🔴 Every plan below targets the LOCAL instance** described in the **System Under Test** block —
local base URL/port, local datastore, local test data. Do not reference a dev/QA/staging URL, and do
not assume anything is already deployed or running.

**Every generated artifact opens with the same short System Under Test block** (a precondition, not
a build manual):

```markdown
## System Under Test
| Item | Value |
|------|-------|
| Branch | [epic branch, e.g. `epic/PROJ-50-checkout` — base branch for bug/enhancement cycles] |
| This story's merged PR | [PR URL / number] |
| Confirm the story is in the build | `git log --oneline \| grep [TICKET-ID]` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | [from the design artifacts, or ⚠️ TO CONFIRM] |
| Local services that must be up | [datastore, queue, stub — or none] |
| Test data / accounts to seed | [list, or none] |

> If the build or local run fails, that is a **blocker on the dev team** — report it and do not log
> functional failures against a system that never started.
```

- **`integration-test-steps.md`** — cases that exercise a **boundary between two components** from
  the outside: service A's endpoint causing an observable effect that service B, the datastore, a
  queue or a third-party surfaces. Derive the boundaries from the design/reverse-engineering
  artifacts, never from code.
- **`e2e-test-steps.md`** — complete user journeys end to end (`TC-E2E-01: user registers → verifies
  email → logs in → sees dashboard`). One case per journey the AC implies.
- **`api-test-steps.md`** — per endpoint: happy path, each documented error path, auth required/absent,
  bad payload, boundary values. Assert status code, response shape, and headers.
- **`contract-test-steps.md`** — for each consumer/provider pair: required fields, types, optional
  fields, backward-compatibility check against the previously published schema.
- **`security-test-steps.md`** — authentication required, authorization enforced per role, IDOR
  attempt, injection-style inputs rejected, sensitive data absent from responses and logs, security
  headers present, rate limiting. Map each case to the relevant Security Baseline rule where one
  applies.
- **`performance-test-steps.md`** — state the target from requirements/NFR design
  (`p95 < [X]ms at [Y] rps with [Z] concurrent users`), then the manual procedure to measure it and
  the pass threshold. Include the record-the-numbers table.
- **`accessibility-test-steps.md`** — keyboard-only navigation, focus order and visibility, screen
  reader labels, colour contrast, error announcement, zoom to 200%. Reference the WCAG criterion per
  case.

---

## Step 5: Generate `test-plan-summary.md` (always — the story's ve index)

```markdown
# Test Plan Summary — [TICKET-ID] [Story title]

**Story**: [Story ID N.M] — [title]
**Tracker ID**: [TICKET-ID](<site>/browse/TICKET-ID)   (or `—` for a local-only story)
**Generated**: [ISO 8601 timestamp — from a real clock]
**Generated by**: [session email]
**Source of truth**: Acceptance criteria (black-box) — no application source code was read
**AIRE VERSION**: [N]

## Applicable Test Plans
| Test Plan | Artifact | Cases | Status |
|-----------|----------|-------|--------|
| Integration | integration-test-steps.md | [n] | ⬜ Not run |
| E2E | e2e-test-steps.md | [n] | ⬜ Not run |
| API | api-test-steps.md | [n] | ⬜ Not run |
| Contract | — | — | N/A — [reason] |
| Security | security-test-steps.md | [n] | ⬜ Not run |
| Performance | — | — | N/A — [reason] |
| Accessibility | — | — | N/A — [reason] |

## Acceptance Criteria → Test Case Coverage
| AC | Criterion | Test cases | Covered |
|----|-----------|------------|---------|
| AC-1 | [text] | TC-API-01, TC-API-02, TC-SEC-01 | ✅ |
| AC-2 | [text] | TC-E2E-01 | ✅ |

**Coverage check**: [n]/[n] acceptance criteria have at least one test case. ✅ / ❌

## Execution Record (filled in by ve when the story is tested)
| Test case | Run date | Result | Defect raised |
|-----------|----------|--------|---------------|
| TC-API-01 | | ⬜ Pass / Fail | |

## Open Questions
- ⚠️ TO CONFIRM: [each unresolved detail, with who should answer it]
```

**🔴 The AC coverage check is a checkpoint**: if any acceptance criterion has zero test cases, do not
present completion — add the missing cases first.

---

## Step 6: Present Completion

```markdown
# 🔨 Test Plan Ready — [TICKET-ID] [Story title]

📁 **Artifacts**: `.spec/aire-docs/tests/<TICKET-ID>-<title-kebab>/`
🧪 **Test plans generated**: [list] ([n] manual test cases total)
🔗 **Coverage**: [n]/[n] acceptance criteria covered
🚫 **Not applicable**: [list with reasons]


> These are **manual test steps derived from the acceptance criteria** — they can be executed as
> soon as the story is merged to the epic/base branch
```

**🔴 Confirm-first checkpoint — do not finish silently.** Immediately after the message above, ask:

```markdown
❓ **Do you approve this test plan, or do you want to request changes?**

   1) ✅ Approve — accept this as final
   2) 🔁 Request Changes — go back and adjust

[Answer]:
```

- On **Approve** → proceed to **Step 8** (log the run in `audit.md`).
- On **Request Changes** → ask what to adjust (which plan, which case, what's missing), apply the
  change, regenerate the affected artifact(s) and the coverage table, then re-present this same
  Step 7 completion message and checkpoint. Never close the run without landing on this checkpoint first.

---

## Step 7: Log the Run in audit.md

Append (never rewrite) one entry to `.spec/aire-docs/audit.md`:

```markdown
## Test Plan (ve-implement skill)
**Timestamp**: [ISO 8601 — real clock]
**User Email**: [current session email — read live from the session context]
**User Input**: "[complete raw user input]"
**Story**: "[Story ID N.M] — [title] — [PROJ-XXX](<site>/browse/PROJ-XXX) or local Story ID"
**Output folder**: `.spec/aire-docs/tests/<TICKET-ID>-<title-kebab>/`
**ve branch / PR**: "ve/<TICKET-ID>-<title-kebab> → PR <url> into <Epic Branch | Bug Branch | Enhancement Branch>"
**Test plans generated**: "[list of applicable plans, with case counts] — N/A plans: [list with reasons]"
**Coverage**: "[n]/[n] acceptance criteria covered"
**Approve / Request Changes checkpoint**: "[Approved / Request Changes → re-did [what] → re-approved]"
**AI Response**: "[what was generated/changed]"
**Context**: `/ve-implement` skill — Test Plan (`test-plan.md`)

---
```

Write a tracker-linked story as a clickable Markdown link (JIRA/ADO/GITHUB, per `common/tracker-sync.md`),
never bare text. Use the local Story ID for local-only stories.

**🔴 This audit entry is the ONLY framework state this file writes.** It never touches the Story
Tracker, story status, or tracker status — those remain `ve-list-work`'s job.

---

## Critical Rules

- 🔴 **Never read application source code, and never read build configuration either.** All test
  steps come from acceptance criteria, requirements, design artifacts, the tracker story, and
  documented external interfaces. This file does NOT generate build instructions — the project's
  own build docs own that — so there is no reason to open `package.json`, `pom.xml`, a Dockerfile
  or anything similar.
- 🔴 **Manual test steps only.** This file produces human-executable test cases — it does NOT
  generate, run, or reference automated test scripts. It never touches application code. The
  `ve/…` branch, commit, and PR that carry these artifacts are cut/raised by `ve-implement-agent.md` Step 3
  and Step 5, wrapped around this file's execution — this file itself defines content, not git steps.
- 🔴 **One story per run**, into its own `.spec/aire-docs/tests/<TICKET-ID>-<title>/` folder. Never
  overwrite another story's folder; ask before refreshing an existing one.
- 🔴 **Every test case traces to an AC; every AC has ≥1 test case.** The coverage check in the
  summary is a blocking checkpoint.
- 🔴 **Runs in parallel with development.** Never wait for the DEV's code, branch, PR, or merge to
  *author* these steps.
- 🔴 **No deployed environment — ever.** The ve *executes* these steps after the story merges into
  the epic branch (epic cycles) or base branch (bug/enhancement cycles), by **building that branch
  from source and running it locally**. Every precondition, URL, port and command must reflect that
  locally built, locally running instance. Never write a step that assumes a dev/QA/staging
  deployment, a shared base URL, or an already-running service.
- 🔴 **Never generate build instructions.** They are identical for every story, trace to no
  acceptance criterion, and already exist in the project's README/CONTRIBUTING. Each artifact only
  states the **System Under Test** precondition (branch, merged PR, local URL/port, services, test
  data) and defers the build itself to the project's own docs.
- 🔴 **Unknowns are marked `⚠️ TO CONFIRM`**, never invented and never resolved by reading code.
- 🔴 **Never touch the Story Tracker, story status, or tracker status here.** Status changes are the
  `ve-list-work` skill's job (its local Option B).
- 🔴 **Never close the run without the Step 6 Approve / Request Changes checkpoint.** On Request Changes,
  fix the plan, regenerate the coverage table, and re-present the checkpoint — never finish silently.
- 🔴 **Always log the run in `audit.md` (Step 7), append-only**, once the checkpoint is Approved. This is
  the only file this skill writes outside the story's `.spec/aire-docs/tests/` folder.
- 🔴 Timestamps come from a real clock in ISO 8601; the framework version `[N]` is read live from
  the canonical line in `CLAUDE.md`.
