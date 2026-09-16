# 🔧 WORKFLOW: `bug-fix-implement` (Bug/Defect — Code Fix)

**Purpose**: Implement the fix for the defect prepared by `bug-fix`. Normally entered from `bug-fix` Step 9's **ve Handoff Break** — the user answers `yes` there and this workflow runs in the same session (the keyword is only typed to resume a session that answered `no` or ended after analysis). Sibling of `dev-implement`, but: it works **directly on the existing bug branch** (no story selection, no doability gate, no story branch), it runs a **baseline regression pass before touching code**, a **full-repo regression gate after the fix**, and its PR targets the **base branch** with the **`[BUG]`** prefix — after which the archive runs automatically.

## MANDATORY: Rule Details Loading

May be invoked standalone in a fresh session. Resolve `.aire-rule-details/` and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- `common/branching-strategy.md` — **Bug Branch Model** section
- `implementation/code-generation.md` (planning/generation/coverage mechanics — story selection and story-branch steps do NOT apply here). 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- `workflows/code-review.md` (auto-run after the fix) and `workflows/remediate.md` (on the Remediate path)
- `common/eval-framework.md` — the Static Eval Gate D1–D7 (baseline at Step 3, gate at Step 7.5) and the J1/J2 judge scores (Step 8a). Evidence key for this flow: `bug-[TICKET-ID]`

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `implementation/code-review.md` / `implementation/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).

Skills used **as-is — NEVER edit them**: **`pr-generator`** (pass target branch = the **Base Branch**; PR type `[BUG]`), **`pr-review`** (AUTO MODE after the PR), and **`archive-epic`** in **bug mode** (🔴 **NEVER auto-invoked by this workflow — the operator runs it manually** after all ve work has landed on the bug branch; see Step 12).

## MANDATORY: Audit Entry Format

Every audit.md entry in this workflow carries the `**TRACKER ITEM**:` field (the defect ticket as a tracker hyperlink, or the local ID for LOCAL) — same format as `bug-fix.md` — AND the `**AIRE VERSION**:` field, exactly as `dev-implement` does:

```markdown
**AIRE VERSION**: "[Framework version [N] read from the "AIRE Framework Version" line in CLAUDE.md — do not hardcode]"
```

The version is read **at runtime** from the canonical "AIRE Framework Version" line in `CLAUDE.md` — it records which framework version the bug fix was developed with. Never omit it and never hardcode a literal number. Append-only, ISO 8601 timestamps, complete raw user input.

## 🤖 THIS WORKFLOW IS FULLY AUTOMATIC — IT HAS NO APPROVAL GATES

**Entering this workflow (the `yes` at `bug-fix` Step 9's ve Handoff Break, or typing
`bug-fix-implement` to resume) is the ONLY user decision.** Everything after it — the fix plan, the
code, the unit-test/coverage gate, the regression gates, the automated Code Review, **the
remediation of any findings it reports**, the commit, the push, the `[BUG]` PR and the PR review —
runs **without a single approval prompt**.

- ❌ There is **NO GATE 2** (fix-plan approval). The plan is built, announced and executed.
- ❌ There is **NO GATE 3** (review decision). A review with findings is **remediated automatically**,
  then re-reviewed, **looping until the verdict is clean** — never an Approve/Remediate question.
- ❌ There is **NO GATE 1** either — that was the epic flow's story-set approval, which no longer
  exists anywhere in the framework.
- 🔴 **Never write the word "GATE" into an audit heading from this workflow.** Plan and review
  outcomes are logged as auto-approved decisions under plain headings.
- The stage approvals inside `bug-fix.md` (requirements, the single story) belong to that file and
  are unchanged.
- 🔁 **Automatic does not mean unbounded.** Every self-healing loop in this workflow is capped at
  **3 remediation attempts** by the **Self-Healing Retry Policy (SH-1 … SH-7)** below. When a loop
  exhausts its budget the run **HALTS at that gate**, emits the Retry-Limit Report, and asks the user
  for next steps. A failing gate is never passed, skipped, weakened, or carried forward.

---

## 🔁 SELF-HEALING RETRY POLICY (SH-1 … SH-7) — BINDING ON EVERY AUTOMATIC LOOP IN THIS WORKFLOW

Any gate in this workflow that detects a failure and fixes it without user input is a **self-healing
loop**. Every such loop is bounded by the rules below. **These rules override any wording elsewhere in
this file that describes a loop as uncapped, unbounded, or repeating "until clean" with no limit.**

**Governed loops — each has its own independent attempt counter:**

| ID | Loop | Defined in | Verification that must pass to exit the loop |
|---|---|---|---|
| **SH-LOOP-1** | Unit Test & Coverage | Step 6 | All unit tests green **and** coverage on new/changed code ≥ 90% |
| **SH-LOOP-7** | Behavioural B1 + B2 (Gherkin) | Step 6.2 | The fix's scenarios pass with every AC tag executed, AND the entire existing behaviour suite stays green |
| **SH-LOOP-8** | Behavioural B3 (epic scope) | Step 6.2 | The full suite + the ticket's end-to-end journey pass |
| **SH-LOOP-2** | API & Contract Testing | Step 6.5 | Every applicable checklist item passes on every touched endpoint |
| **SH-LOOP-3** | Full Regression | Step 7 | Zero NEW failures versus the Step 3 baseline |
| **SH-LOOP-4** | Static Eval D1–D7 | Step 7.5 | Zero NEW findings above the `.evals/config.json` thresholds on changed files |
| **SH-LOOP-6** | Judge Gates J1 + J2 | Step 8a Item 2.5 | `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin` (`N/A` passes) |
| **SH-LOOP-5** | Auto-Remediate (code review + security findings) | Step 8c | Review verdict clean — zero 🔴 and zero 🟠 |

**SH-1 — Attempt budget.** Each loop is allowed a **maximum of 3 remediation attempts**. One attempt
is one complete `fix → re-verify` cycle. The initial verification run that first detects the failure
is **not** an attempt (it is attempt 0). Attempts are numbered 1, 2, 3.

**SH-2 — Counters are per-loop, independent, and never silently reset.** Maintain a separate counter
per SH-LOOP ID. A counter is never shared between loops, never reset by another loop's success, and
never reset by advancing to a later gate. When a later loop's remediation forces re-entry into an
earlier loop (for example Step 8c re-running the Step 7 regression comparison), that re-entry **continues the earlier loop's existing
counter** — it does not grant a fresh budget of 3. The only reset is the one the user grants
explicitly under SH-4 step 5.

**SH-3 — Every attempt is recorded.** Before an attempt, log to `audit.md` and to that loop's evidence
manifest: the loop ID, the attempt number (`n of 3`), the exact failures being addressed, the
identified root cause, and the planned fix. After the attempt, log the files changed, the exact
verification command re-run, and its result. An unrecorded attempt is a process violation.

**SH-4 — Exhaustion halts the workflow.** When attempt 3 completes and the loop's verification still
fails, the loop is **exhausted**. Immediately:
1. Stop the loop. Do **not** begin a 4th attempt.
2. Stop the workflow at this gate. Do **not** advance to the next gate, do **not** commit, do **not**
   push, do **not** raise or update a PR, and do **not** change the local Story Tracker or the
   external tracker. The ticket stays `🔵 In Development` on its bug branch. The attempted fixes stay in the working tree for inspection.
3. Emit the **Retry-Limit Report** below as the run's final output.
4. Append the same content to `audit.md` under the heading
   `## Self-Healing Retry Limit Reached — [SH-LOOP-ID] (Bug [TICKET-ID])`, carrying the standard
   `**TRACKER ITEM**:` and `**Epic Link**:` fields.
5. **HALT and await user direction.** Do not resume, re-attempt, reroute, or skip the gate on your own
   initiative. Only an explicit user instruction resumes the run, and only options A and B of the
   report grant a fresh 3-attempt budget — for that one loop, and only after the user's input has
   been applied.

**SH-5 — A stall ends the budget early.** If an attempt produces **no code change at all** AND
re-verification returns output **identical** to the previous verification, the loop cannot make
progress. Treat it as exhausted under SH-4 immediately, regardless of attempts remaining, and state in
the report that the budget ended early on a stall rather than on attempt 3.

**SH-6 — Forbidden shortcuts, on every attempt.** No attempt may produce a pass by weakening the
check. Explicitly forbidden: deleting, skipping, `xfail`-ing or weakening a failing test; suppressing a
finding (`eslint-disable`, `# nosec`, `# type: ignore`, ignore-list entries); lowering a threshold or
widening an allow-list in `.evals/config.json`; deleting a finding from a review report; narrowing a
gate's declared scope. Reaching SH-4 honestly is the required outcome; passing the gate dishonestly is
not an outcome at all.

**SH-7 — Diagnose before spending an attempt.** An attempt that repeats a previous attempt's change,
or applies a speculative fix with no stated root cause, wastes budget. State the root cause in the
attempt log before making the change. If the root cause cannot be established from the available
evidence, stop and report under SH-4 rather than spending an attempt on a guess.

### Retry-Limit Report — emit VERBATIM, substituting every bracketed value

```
🛑 SELF-HEALING RETRY LIMIT REACHED — [loop name] ([SH-LOOP-ID])
   Work unit: Bug [TICKET-ID] — [ticket title]
   Branch:    [bug branch]

   3 of 3 automatic retry attempts have been used and this gate is still failing.
   The workflow has STOPPED at this gate. Nothing was committed, pushed, or raised as a PR, and no
   tracker status was changed.

─────────────────────────────────────────────────────────────────────
WHAT IS STILL FAILING
   Gate:         [step number and gate name]
   Verification: [exact command executed]
   Outcome:      [pass/fail counts, measured coverage %, or finding counts]
   Outstanding:
     • [failure/finding 1 — identifier, file:line, message]
     • [failure/finding 2 — identifier, file:line, message]

WHAT WAS ATTEMPTED
   Attempt 1 — root cause: [diagnosis] → change: [files / summary] → result: [outcome]
   Attempt 2 — root cause: [diagnosis] → change: [files / summary] → result: [outcome]
   Attempt 3 — root cause: [diagnosis] → change: [files / summary] → result: [outcome]

WHY AUTOMATIC REMEDIATION DID NOT RESOLVE IT
   [Specific technical diagnosis — the constraint, contradiction, missing dependency, environment
    limitation, or ambiguous requirement that blocks an automatic fix. Never "unclear" or "complex".]

EVIDENCE
   [paths to the run logs, reports and evidence manifests produced by all 3 attempts]
─────────────────────────────────────────────────────────────────────

3 retries ended. Please suggest next steps. Available options:
   A) 🔧 Provide guidance — describe the intended fix or the correct expected behavior. The gate
      re-runs with a fresh 3-attempt budget for [SH-LOOP-ID] once that input is applied.
   B) 🧭 Correct the requirement — if an acceptance criterion, contract or threshold is itself
      wrong, state the correction; it is applied to the source artifact first, then the gate re-runs
      with a fresh 3-attempt budget for [SH-LOOP-ID].
   C) 🙋 Take it over manually — fix it in the working tree, then re-invoke `bug-fix-implement` for
      this work unit to resume from this gate.
   D) 🗂️ Raise a defect and stop — log the blocker via `/raise-defect` and leave the work unit
      `🔵 In Development` for a later session.

[Answer]:
```

🔴 **Log the user's raw response in `audit.md`** under
`## Self-Healing Retry Limit — User Direction ([SH-LOOP-ID])`. A new budget is granted for the named
loop ONLY, and ONLY under option A or B; every other loop keeps the counter it already held.

---

## Step 1 — Preconditions

1. Read `.spec/aire-docs/aire-state.md`. Require `## Tracker` with `Workflow Type: bug` + `Parent Ticket`, and `## Branching` with `Bug Branch`. If missing, STOP: tell the user to run `ticket-implement <TICKET-ID>` first — this workflow only implements a prepared fix.
2. Verify the state records `Design complete — awaiting bug-fix-implement` (or later). If Planning is incomplete, STOP and say which stage is pending.
3. **Switch to the bug branch**: `git fetch origin`, checkout the recorded Bug Branch, `git pull --ff-only` if it has an upstream. Confirm with `git branch --show-current`. 🔴 All work happens on this ONE branch — never cut another branch.
4. Read `.spec/aire-docs/planning/impact-analysis.md` and `bug-brief.md` — they drive the plan.

## Step 2 — Ticket → 🔵 In Development (automatic)

Running `bug-fix-implement` IS the claim. Without asking, dispatch on `## Tracker` → `Type` per `common/tracker-sync.md` Section 4/Section 5/Section 9:
1. Story Tracker (single row): Status → `🔵 In Development`, Start + Recorded timestamps set.
2. Transition the ticket to the tracker's "In Development" state/label (non-LOCAL): **JIRA** — resolve the actual transition via `getTransitionsForJiraIssue` → `transitionJiraIssue` (Bug and Story issue types can have different workflows; never hardcode the state name); **ADO** — `az boards work-item update --state "Active"`; **GITHUB** — swap the status label to `status:in-development`. **Verify it landed**, announce it, log in audit.md. **LOCAL**: no external call — this step is a no-op beyond the Story Tracker update above.
2.2. **👤 Assign the ticket to the operator (automatic — same claim)**: the developer who typed `bug-fix-implement` claims the fix, so set them as the assignee without asking, per `common/tracker-sync.md` Section 5 — read the session **email** LIVE from the session context (the same one stamped as `**User Email**:` in audit.md), then **JIRA**: resolve via `lookupJiraAccountId` + `editJiraIssue`; **ADO**: `az boards work-item update --assigned-to "<session-email>"` directly; **GITHUB**: a cached GitHub username (ask once per session if not yet recorded) + `gh issue edit --add-assignee`; **LOCAL**: no assignee concept, skip. **Verify** (non-LOCAL) by fetching the issue back. If the identity resolves to no (or ambiguous) account, leave the assignee unchanged, warn the user, and continue — assignment failure is NON-blocking. Announce and log in audit.md.
2.5. **Add the AIRE version label to the ticket** (mirrors dev-implement's version stamping — the defect ticket was raised by ve, not by the framework, so it doesn't carry the label yet), dispatching on `## Tracker` → `Type` per `common/tracker-sync.md` Section 9: **JIRA** — label `aire-v[N]` via the Atlassian MCP; **ADO** — add `aire-v[N]` to `System.Tags`; **GITHUB** — `gh issue edit --add-label aire-v[N]`; **LOCAL** — note the version directly on the local bug entry, no external call. `[N]` is the FULL framework version (including the minor, e.g. `1.0` → `aire-v1.0` — never the major only, never `aire-v1`), read **at runtime** from the "AIRE Framework Version" line in `CLAUDE.md` (never hardcoded). If the label is already present, skip. Verify (non-LOCAL), announce, log in audit.md.
3. 🔴 Skip all Parent-Epic sync steps — `## Tracker` records `Parent Epic: none` in the bug flow.

## Step 3 — 🧪 BASELINE Regression Run (BEFORE any change)

**Purpose**: know what was already broken so post-fix failures are attributed correctly — a fix must never be blamed for (or silently hide) pre-existing failures.

1. Discover and run the **entire repo's unit test suite** (all modules) with no code changes made yet.
2. Record the baseline in `.spec/aire-docs/implementation/code/bug-<TICKET-ID>-summary.md`:
   ```markdown
   ## Baseline Regression (pre-fix)
   - Command(s): [exact commands]
   - Result: [X passed / Y failed / Z skipped]
   - Pre-existing failures: [list each failing test, or "none"]
   ```
3. Pre-existing failures are **logged, not fixed** — they are out of scope UNLESS a failing test is itself the defect under fix (note it if so). Log the baseline in audit.md.
4. If the repo has no test suite at all, record that explicitly — the post-fix regression gate then covers only the new tests.
5. **🔎 BASELINE STATIC EVAL RUN (MANDATORY, AUTOMATIC — same moment, before any change)**: run the **Static Eval Gate checks D1–D7** per `common/eval-framework.md` Section 2 (lint, type check, SAST, dependency vulnerabilities, licences, complexity, secrets) and save the raw output to `.spec/aire-docs/implementation/code/eval-evidence/bug-<TICKET-ID>/static/baseline/`. Exactly like the regression baseline: **every finding is pre-existing debt, not this fix's** — logged, not fixed, never blocking. It exists only so Step 7.5 can tell this fix's findings apart. Log the baseline in audit.md.
   - **🔧 BOOTSTRAP FIRST (eval-framework.md Section 2.3, MANDATORY — same step, immediately BEFORE the baseline run)**: for every check with **no config in the repo**, create the minimal *recommended* config (eslint/ruff/golangci, tsconfig/mypy, `.gitleaks.toml`, the linter's complexity rule at the `.evals/config.json` threshold) so the check is actually runnable. **A check whose config exists is used AS-IS** — the repo's own standards win, never overridden. Announce every file created and log it (`bootstrap` block of `eval.json`) — it adds files to the user's repo, so it is never silent; those files commit with the fix. 🔴 **AND INSTALL THE TOOLS — retried, never skipped (Section 2.4.1)**: for every gate, work the chain *already present → package manager → alternative installer → **OCI image via Podman***, 3 attempts per rung, verifying each install with a version command. Recording a gate `N/A` for a missing tool **before the Podman rung has been tried** is a bootstrap failure, not an `N/A`. If the whole chain is exhausted, **HALT with the per-rung report** — never continue with an unmeasured gate, and never phrase deferred setup as `N/A` ("not wired yet", "not installed", "not enabled yet" — all ERROR, Section 2.5.2).
     - 🔴 **ORDER MATTERS**: bootstrap → baseline → fix → Step 7.5 → diff. A config created AFTER the baseline would make both runs measure under **different rules**, blaming this fix for findings on pre-existing code.
     - 🔴 Recommended presets, never strict/all, and **never a config that pre-suppresses findings**.
   - 🔴 A check is recorded `N/A` **only after the full Section 2.4.1 install chain — including the Podman image rung — has been attempted and recorded**, and only for a reason on the Section 2.5.1 closed list (inapplicable to this stack / to this work unit / no such tool exists). If the chain is exhausted, that is an **ERROR: HALT** with the per-rung report — never `N/A`, never silently skipped, and never phrased as deferred work ("not wired yet", "not installed", "not enabled yet").

## Step 4 — Fix Plan (🤖 announced, not gated)

1. Build the fix plan from `impact-analysis.md` + the design artifacts, using `code-generation.md`'s Part 1 planning format (checkboxed steps), ending with the mandatory Unit Test & Coverage step, the API & Contract Testing Gate (Step 6.5, when the fix touches an API endpoint), and the Full Regression Gate (Step 7). **🧾 TRACE THREAD (bug variant, `common/requirements-traceability.md` Rule 7)**: tag every plan step with the `bug-brief.md` expected-behavior statement(s) and `impact-analysis.md` entry it addresses, and self-check that every expected-behavior statement and every impact-analysis touch point appears in ≥1 step before presenting the plan.
2. **Re-validate the impact analysis against current code.** If the plan must touch files NOT in the impact analysis: add them to `impact-analysis.md` and **re-run the Defect Provenance Analyst (`agents/defect-provenance-analyst.md`, per bug-fix Step 5b) on the newly implicated defective lines** — same line-level procedure (trace each defective line to its introducing commit); if any is AI-generated and the ticket isn't labeled yet, offer the `ai-generated-defect` label (confirm-first, verified, logged). Also run **bug-fix Step 5c** on any newly resolved originating ticket keys — create the "is caused by" link automatically (no confirmation), skipping keys already linked, verified and logged.
3. **🤖 Announce the plan and proceed — NO approval gate**:
   1. **Log the finalized plan** in `.spec/aire-docs/audit.md` (ISO 8601 timestamp) under a **plain heading** — e.g. `## Fix Plan — Finalized (auto-approved, no gate) (Bug [JIRA-ID])` — with the plan path, the step count and the trace summary. **The word "GATE" must NOT appear in the heading.**
   2. Present the plan as an **announcement** (NOT a question):
      ```
      📋 Fix plan ready for Bug [JIRA-ID] — [N] steps.
      Plan: .spec/aire-docs/implementation/plans/bug-[JIRA-ID]-fix-plan.md
      ➡️ Generating the fix now (Step 5).
      ```
   3. **Do NOT wait for a response** — go straight to Step 5. If the user volunteers a change to the plan, apply it, update the plan document, announce the revision, log it, and continue (an interrupt, not a gate).

## Step 4.5 — 🥒 Write the Behaviour Spec (MANDATORY — before any code)

Write `.spec/aire-docs/implementation/code/behavior/bug-<TICKET-ID>.feature` per `common/behavior-spec.md` Section 2 — one Gherkin scenario per acceptance criterion, `@AC-n` tagged, failure paths included (for a bug, including the scenario that reproduces the defect). Authored **BEFORE** the implementation: it is the contract, not a description of what was built.

🔴 **That is the ONLY spec file this work unit gets.** No per-unit requirements, architecture, constraints or knowledge-graph document. The agent reads the tracker item for acceptance criteria, `requirements.md` for the covered REQ-IDs, `.spec/architecture.md` for design constraints, and `.evals/config.json` for thresholds — copying any of that per unit only creates something that can drift.

Announce the file path and the scenario/AC counts. Log both in audit.md.

## Step 5 — Generate the Fix

Execute the announced plan step by step on the bug branch, marking each checkbox `[x]` in the same interaction it completes. **📁 All application code goes into `src/`** (or the recorded `## Code Root` — `common/directory-structure.md`), test code into `tests/`, and nothing into `.spec/`. **🛡️ PLAN FIDELITY**: implement EXACTLY the announced plan — no unplanned files, features, refactors, or scope drift; keep the fix consistent with the impact analysis and design docs the plan was grounded in. If mid-coding you discover the plan must change, **revise the plan document, announce the revision (what changed and why) in your output and in audit.md, and continue** — never apply a deviation silently, and never ask for approval. Write code to the workspace root per the existing project structure. Log progress in audit.md.

## Step 6 — Unit Tests + Coverage Gate (threshold from `.evals/config.json`)

1. Write unit test(s) that **reproduce the defect** — they must exercise the exact failure scenario from the bug-brief (ideally shown to fail against the pre-fix logic) — plus tests covering all new/changed code.
2. RUN them; fix failures; measure coverage on the new/changed code; iterate in the SAME run until **≥90%**. 🔁 **This is SH-LOOP-1 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT, emit the Retry-Limit Report, and do NOT proceed below the threshold.**
3. Capture evidence (tests X/X passing + measured %) in `bug-<TICKET-ID>-summary.md` and audit.md.

## Step 6.2 — 🥒 Behavioural Test Gate (Gherkin — three tiers)

Execute the tiered behavioural gate defined in `common/behavior-spec.md` Section 4.4. Implement the step definitions in `tests/behavior/steps/`, bound to the application's **public surface** (endpoint / service method / CLI) — never to internals — then run the tiers **in order**:

1. **B1 — Unit scope**: this work unit's own `.spec/aire-docs/implementation/code/behavior/bug-<TICKET-ID>.feature`. **Verification**: every scenario passes AND every `@AC-n` tag is executed.
2. **B2 — Cumulative scope**: every **other** feature file already in the repo — earlier work units in this cycle plus everything from prior cycles. **Verification**: all green. 🔴 A B2 failure is THIS unit's problem — it turned that scenario red, so it fixes it. "That scenario belongs to another story" is not a defence.
3. **B3 — Epic scope** (🔴 **last work unit of the cycle ONLY**): B1 ∪ B2 **plus** the cross-unit journeys in `.spec/behavior.feature`, tagged `@REQ-<id>`. 🔴 Detect "last" from **PR MERGE STATE, never the tracker status label** (`common/behavior-spec.md` Section 6.1): for every OTHER work unit read its PR from the Story Tracker and verify live with `gh pr view <n> --json state`. **All others merged → this is the last unit → RUN B3** — including the normal case where those units are still `🔵 In Development` awaiting ve sign-off, because the label lags the merge. Defer ONLY when a unit has no merged PR, recording `B3: N/A — deferred, <n> units with unmerged PRs (<list with PR state>)`. 🔴 Never defer on a status label alone, and never report a deferred B3 as a pass.

**Execution** — 🔴 **every tier runs in a Podman pod** (`common/behavior-spec.md` Section 5): the image built from `.evals/behavior/Containerfile`, plus a fresh ephemeral **test database** where the repo needs one, invoked through `.evals/behavior/run.sh <tier>` — the same image and command a developer runs locally, so a CI-only failure is impossible by construction. 🔴 **The ONLY permitted native run is Podman not being installed** (proven by `command -v podman`), recorded as `"containerised": false, "reason": "podman not installed"`. 🔴 "No browser needed", "backend only", "no new dependency" and "faster natively" are **forbidden justifications** — a tier recorded that way is a gate violation, not a pass. Never fall back to the Docker CLI. A tier runs only once the previous is green.

**Evidence** — per tier, to `.spec/aire-docs/implementation/code/behavior-test-evidence/bug-<TICKET-ID>/<b1|b2|b3>/`: `behavior-test-run.log`, the **mandatory machine-readable** `behavior-test-report.*`, and an `evidence-manifest.md` recording the image ref + digest, the exact command, whether it ran containerised, the tier's feature-file set, and every scenario with its tag and result. A raw log alone does NOT satisfy the gate.

**Self-healing** — 🔁 **B1/B2 failures → SH-LOOP-7; B3 failures → SH-LOOP-8, its own separate 3-attempt budget** (an epic-scope failure is usually an integration gap between units, not a bug inside one, so arriving at the epic gate with the story budget already spent must not halt the cycle). Both capped at 3 attempts; on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report.

🔴 **Fix the code, never the scenario.** A scenario changes only when the AC or requirement it encodes genuinely changed — and then the AC, `requirements.md` and the tracker item are amended together and the reconciliation is logged. Deleting, skipping or `@ignore`-ing a scenario to go green is forbidden (SH-6).

**N/A** — B1 is N/A only for a work unit with no externally observable behaviour (pure build-config or docs change); a unit with acceptance criteria is never N/A. B2 is N/A only when the repo genuinely contains no other feature file. Record the reason explicitly.

## Step 6.5 — 🔌 API & Contract Testing Gate (MANDATORY WHEN APPLICABLE)

**Applicability (automatic, no question asked)**: applies when the fix plan (Step 4) touches an API endpoint/route/controller/handler — i.e. the defect is in, or the fix changes, API-visible behavior. **If the fix plan touches no API layer, this gate is N/A** — record that explicitly in `bug-<TICKET-ID>-summary.md` and proceed to Step 7.

1. Generate automated tests against the actual affected endpoint(s) — via the stack's standard integration-test mechanism (in-process test client or a spun-up test server) — that reproduce the defect at the API level where applicable, plus the full checklist for every endpoint the fix touches:
   - **Functional / happy path** — the documented correct behavior once fixed
   - **Response Code Validation** — correct HTTP status code for every documented success and failure path
   - **Authorization Testing (role-based access)** — unauthenticated → `401`; authenticated with insufficient role → `403`; correct role → success (N/A only for a genuinely public endpoint)
   - **Error Response Validation** — standard error envelope/format and correct error code for each documented error condition
   - **Request Validation** — required fields, data types, and enum constraints on the request payload are enforced (N/A only for an endpoint with no request body)
   - **Response Contract Validation** — the response payload matches its declared schema/contract (required fields, types, enum values)
2. RUN them; fix failures; iterate in the SAME run until every applicable checklist item passes. 🔁 **This is SH-LOOP-2 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.**
3. Capture evidence to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-1.1/` (`api-contract-test-run.log`, the **mandatory machine-readable** `api-contract-test-report.*` — invoke the runner with its report-emitting flag/plugin, e.g. `pytest --junitxml=...` / `jest --json --outputFile=...`; a raw log alone does NOT satisfy the gate unless the runner genuinely has no such capability (documented, surfaced exception) — and `evidence-manifest.md` with the per-endpoint checklist) and reference it in `bug-<TICKET-ID>-summary.md` + audit.md. This gate is separate from and does not replace ve's `/ve-implement` MANUAL API/Contract test steps.

## Step 7 — 🧪 FULL Regression Gate (after the fix)

1. Re-run the **entire repo's unit test suite** (all existing tests + the new bug tests, including any new API & Contract tests from Step 6.5).
2. **Compare against the Step 3 baseline**:
   - **New failures** (passing at baseline, failing now) → caused by the fix. 🔴 BLOCKING: fix them and re-run until zero new failures. 🔁 **This is SH-LOOP-3 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.**
   - **Pre-existing failures** (already failing at baseline) → not blocking; list them as pre-existing.
3. Append the complete outcome to `bug-<TICKET-ID>-summary.md`:
   ```markdown
   ## Full Regression (post-fix)
   - Command(s): [exact commands]
   - Result: [X passed / Y failed / Z skipped]
   - New failures caused by the fix: [none — required to proceed]
   - Pre-existing failures (unchanged from baseline): [list or "none"]
   - New bug tests: [N] — all passing | Coverage on changed code: [NN]%
   ```
4. Log the full comparison in audit.md. Do NOT proceed with new failures outstanding.

## Step 7.5 — 🔎 STATIC EVAL GATE — D1–D7 (MANDATORY, AUTOMATIC — after Step 7, before Code Review)

Re-run D1–D7 per `common/eval-framework.md` Section 2, save to `eval-evidence/bug-<TICKET-ID>/static/`, and **diff against the Step 3 Item 5 baseline**. Only findings **NEW versus the baseline, on files this fix changed**, count. **No user prompt — fix and continue.**

1. **NEW findings above the `.evals/config.json` thresholds** → caused by this fix, so **this fix resolves them in THIS SAME run**, then re-run and re-diff until the diff is clean. 🔴 BLOCKING. 🔁 **This is SH-LOOP-4 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.**
2. 🔴 **NEVER suppress a finding to pass the gate** — no blanket `eslint-disable`, no `# nosec`, no `# type: ignore`, no ignore-list entry, no widening `disallowedLicenses`. That is the exact analogue of deleting a failing test to go green and is equally forbidden. **Fix the code.**
3. **Findings already present at baseline** → pre-existing, listed not blocking.
4. Write `eval.json` + `eval-summary.md` (eval-framework.md Section 6) and append the gate outcome to `bug-<TICKET-ID>-summary.md`. Log in audit.md. Do NOT proceed with new findings outstanding.

## Step 8 — AUTO Code Review → 🤖 Verdict Routing + Auto-Remediate Loop

Mirrors dev-implement Sections A–C, bug-scoped. The Code Review runs **automatically**, and so does everything that follows from it — the user is asked nothing.

### 8a. AUTO Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Bug [TICKET-ID] (ISO 8601 timestamp).
2. Auto-run `workflows/code-review.md` scoped to this fix (read-only — it MUST NOT edit source) → versioned report `.spec/aire-docs/implementation/reviews/bug-<TICKET-ID>-code-review-v[X].md`. Pass in the Step 6/7/7.5 evidence — the review MUST NOT re-run the tests, re-measure coverage, or re-run the D1–D7 checks; it cites the stored evidence.
2.4. **🛡️ AUTOMATED SECURITY REVIEW (MANDATORY, automatic — inside this review pass)**: the review's **Phase 2.5** runs the `agents/code-security-review-agent.md` procedure against this fix's diff (all 16 Security Baseline rules, scoped to the changed files + the attack surface they reach) and writes `.spec/aire-docs/code-security-reviews/security-review-YYYY-MM-DD.md`. Its **🔴/🟠 findings on the changed surface become real `SEC-ISS-XXX` findings** — routed by 8b and **auto-remediated by 8c (SH-LOOP-5) until clean, within its 3-round budget**, exactly like AC findings. 🟡/🔵 and pre-existing violations on untouched lines are **advisory only** (`/raise-defect` for those). 🔴 Never suppress instead of fixing; never widen the scan to the whole repo.
2.5. **⚖️ JUDGE GATES J1 + J2 — 🔴 BLOCKING (MANDATORY, automatic — computed HERE and nowhere else)**: compute the two judge scores per `common/eval-framework.md` Section 4 from this work unit's diff — **J1** against `.evals/rubrics/architecture-rubric.json` (derived from `.spec/architecture.md` Section 10; apply the Section 3 **fallback chain**: this cycle's rubric → a prior cycle's committed rubric → derived from Atlas / the reverse-engineering artifacts → **`N/A` with the reason**; this flow skips most design stages, so `N/A` is a normal outcome and is never scored against a borrowed rubric) and **J2** against `security-rubric.json`. Write them with their **per-criterion breakdown** to `eval-evidence/bug-<TICKET-ID>/judge/`, merge into the **`gates`** block of `eval.json`, refresh `eval-summary.md`, report both in the review report.
   - **Scoring discipline** (Section 4.1): score **once** per review pass — never re-roll for a better number; every criterion below 1.0 **MUST cite `file:line`**; score only what the diff shows; a criterion this diff cannot exercise is `N/A`, excluded, remaining weights renormalised to 1.0 — never scored 0.
   - **🔁 Gate**: `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin` from `.evals/config.json`. `J1 = N/A` passes. **Below minimum → SH-LOOP-6**: remediate the cited criteria worst-weighted-loss first, re-run whatever gates the fix touched, re-score on the next review pass. **Capped at 3 attempts; on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report.**
   - 🔴 **Forbidden ways to pass** (SH-6): editing `architecture.md` Section 10, editing the rubric JSON, lowering either minimum, re-scoring until it clears, or marking an applicable criterion `N/A`.
3. **MANDATORY — audit the complete review log**: the `**TRACKER ITEM**:` field, report path, verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High). Do not summarize away findings.
4. Proceed to **8b**.

### 8b. 🤖 Review Verdict Routing (AUTOMATIC — no question, no gate)

The review's own verdict decides what happens next. **Do NOT present an A/B choice and do NOT wait for the user.** Announce the verdict, then route:
   ```
   🔍 Automated Code Review complete for Bug [JIRA-ID].
      Report: .spec/aire-docs/implementation/reviews/bug-[JIRA-ID]-code-review-v[X].md
      Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]
   ➡️ [Proceeding to commit + [BUG] PR. | Findings found — remediating them automatically now (round [n]).]
   ```
1. **Verdict clean (zero 🔴 and zero 🟠)** → go to **Step 9 (Commit, Push & Raise the `[BUG]` PR)**.
2. **Any 🔴 or 🟠 finding** → go to **8c (SH-LOOP-5)**. The framework fixes its own findings within a budget of **3 remediation rounds**; it hands them back to the user only when that budget is exhausted (SH-4), and then it HALTS instead of raising the `[BUG]` PR.
3. **MANDATORY**: log the routing decision in audit.md under a plain heading (`## Review Verdict — Clean, Proceeding to PR (Bug [JIRA-ID])` or `## Review Verdict — Findings, Auto-Remediating (Bug [JIRA-ID])`) with the full findings list by severity. **No "GATE" in the heading, and no user response to record.**

### 8c. 🤖 Auto-Remediate Loop — SH-LOOP-5 (AUTOMATIC — max 3 rounds)

**Entered whenever the review verdict reports findings. Every round is automatic — no prompts at any point. The loop is bounded by the Self-Healing Retry Policy: one round = one attempt, maximum 3.**
1. **Check the SH-LOOP-5 counter BEFORE starting a round.** If 3 attempts have already been spent, do not start another — go directly to step 7 (Exhaustion).
2. **Log** in audit.md that automatic remediation round `[n] of 3` is starting for Bug [TICKET-ID], naming the review report being remediated, the findings in scope, and the identified root cause of each (SH-3, SH-7).
3. Run `workflows/remediate.md` scoped to that report (fix → unit test → green). 🤖 **Its scope-confirmation prompt is SKIPPED** — every 🔴/🟠 finding is in scope and nothing is deferred. **Re-run the FULL repo suite if the remediation touched non-test code**, comparing against the Step 3 baseline again — only NEW failures block, and they are fixed in the same round. If the remediation touched API-layer code that Step 6.5 covered, also re-run the affected endpoint(s)' API & Contract tests and keep them green. Per SH-2, these re-entries **continue** the SH-LOOP-3 / SH-LOOP-2 counters — they do not reset them.
4. **MANDATORY — audit the complete remediate log**: the round number (`[n] of 3`), which findings were fixed (by severity), files changed, unit-test evidence, regression comparison. Record the complete log, not a summary.
5. **Re-review automatically**: return to **8a** (produces the next report version `v[X+1]`), then **8b** again.
6. **Loop control**:
   - **Verdict clean** → the loop exits successfully → **Step 9 (Commit, Push & Raise the `[BUG]` PR)**.
   - **Findings remain AND attempts spent < 3** → increment the counter and return to step 1.
   - **Findings remain AND attempts spent = 3** → **exhausted** → step 7.
   - **Stall (SH-5)** — a round produced **no code change at all** AND the next review returned an **identical** finding set → the loop cannot progress. Treat as exhausted immediately, regardless of attempts remaining → step 7, noting the early end.
7. **🛑 Exhaustion (SH-4) — HALT, do not raise the `[BUG]` PR.** When the budget is exhausted (3 rounds, or an SH-5 stall):
   - Do **not** run a 4th round, do **not** commit, do **not** push, do **not** raise a PR, and do **not** change the local Story Tracker or the external tracker. The ticket stays `🔵 In Development` and the remediation work stays in the working tree.
   - Emit the **Retry-Limit Report** (Self-Healing Retry Policy, above) with `[loop name]` = `Auto-Remediate (code review + security findings)` and `[SH-LOOP-ID]` = `SH-LOOP-5`, listing every unresolved finding with its ID, severity, file:line, and the reason automatic remediation failed on it.
   - Append the same content to audit.md under `## Self-Healing Retry Limit Reached — SH-LOOP-5 (Bug [TICKET-ID])`.
   - **HALT and wait for the user's direction.** 🔴 Never silence a finding by deleting it from the report, never weaken the review scope to manufacture a clean verdict, and never let an exhausted loop pass unreported.

### 8d. Status
The ticket stays `🔵 In Development` throughout review and remediation.

## Step 9 — Commit, Push & Raise the `[BUG]` PR — 🤖 FULLY AUTOMATIC

🔴 **A clean review verdict is the ONLY thing that triggers this step.** An exhausted SH-LOOP-5 (8c.7) does NOT reach it — that path HALTS at the gate and waits for the user. The commit, push,
PR creation, labels, tracker update (Step 10) and auto PR review (Step 11) run **automatically with
no prompts**. Announce each action; never ask whether to do it.

1. Verify the active branch is the Bug Branch (switch automatically and announce if not). Stage and commit the fix (code + tests + updated docs). The commit message MUST carry an `AIRE-Version:` trailer as the framework signature — exactly as dev-implement Section D does — where `[N]` is read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` (do not hardcode a number):
   ```
   git add <fix files>
   git commit -m "[BUG][TICKET-ID] <concise fix summary>" -m "AIRE-Version: [N]"
   ```
   The `AIRE-Version: [N]` trailer goes on its own line at the end of the message body (alongside any existing trailers). Record the hash in audit.md.
2. Invoke **`pr-generator`** (as-is) **in WORKFLOW mode**, passing **target branch = the Base Branch** from `## Branching`. The PR title carries the **`[BUG]`** prefix; the skill applies the `ai-generated` and `aire-v[N]` labels (plus the `AIRE Framework: v[N]` line in the PR body). 🤖 **Its Phase 5 confirmation is SKIPPED — this workflow has no gates; invoking it is the authorization.** It announces the draft and raises the PR without asking. Never re-ask about pushing or opening the `[BUG]` PR.
3. Record the PR URL in `## Branching` (`Bug PR: <url>`) and the full outcome in audit.md — including the labels applied (`ai-generated` + `aire-v[N]`).

## Step 10 — Tracker Update (NO Ready-for-Testing transition)

1. Story Tracker: keep Status = `🔵 In Development`; set **End** = today and **Recorded** = now; note the PR URL.
2. 🔴 **Do NOT transition the ticket to "Ready for Testing"** (or any further state) — the ticket stays In Development after the PR. Add a **comment** on the ticket (automatic) linking the PR with evidence (tests passing, coverage %, regression clean vs baseline), dispatching on `## Tracker` → `Type` per `common/tracker-sync.md` Section 10: JIRA `addCommentToJiraIssue`, ADO `az boards work-item update --discussion`, GITHUB `gh issue comment`, LOCAL a note appended to the local bug entry (no external call).
3. Log in audit.md (with the TRACKER ITEM field).

## Step 11 — AUTO PR Review

Invoke the **`pr-review`** skill (as-is) in **AUTO MODE** against the just-raised PR: it posts a plain COMMENT review (summary + inline comments) automatically — no prompt, never a formal APPROVE/REQUEST_CHANGES. Record the outcome in audit.md.

## Step 12 — Archive Handoff (MANUAL)

🔴 **RE-READ FIRST.** Before writing any part of this step's output, `Read` this Step 12 section from the file again. Do NOT reconstruct it from memory or from earlier in this session's context — "I already read this file at Step 1" does not satisfy this.

### The ordering invariant

| # | Action | Relative to the archive |
|---|--------|-------------------------|
| 1 | `ve/...` PR(s) merge into `<bug-branch>` | BEFORE |
| 2 | `ve-list-work` Option C amendments pushed to `<bug-branch>` | BEFORE |
| 3 | `ve-list-work` Option B sign-off → ticket `🧪 Ready for Testing` | BEFORE |
| 4 | **`archive-epic`** (bug mode) | ⬅ **THE ARCHIVE** |
| 5 | **`[BUG]` PR merges into `<base-branch>`** | AFTER |
| 6 | `stitch-delta` on `<base-branch>` | AFTER |

🔴 **`archive-epic` runs at row 4 — BEFORE the `[BUG]` PR merges (row 5).** Its cycle-close commit must reside in the still-OPEN `[BUG]` PR; that is the ONLY path by which the RE delta reaches `<base-branch>` for `stitch-delta`.

**TWO DIFFERENT PRs appear here — never write "the PR" unqualified:**
- the **`ve/...` PR** → merges into `<bug-branch>`. The archive **waits for this one**.
- the **`[BUG]` PR** → merges into `<base-branch>`. The archive **must precede this one**.

"Wait until all ve work has landed" means rows 1–3 **only** — never row 5.

**🔴 BANNED OUTPUT — each inverts the invariant. Never emit them, in any wording:**
- "archive runs post-merge" / "it runs post-merge only"
- "when the `[BUG]` PR merges, run `archive-epic`"
- "DO NOT invoke `archive-epic` manually now"
- any instruction for the developer to transition the tracker ticket in this step

Do NOT invoke `archive-epic`, do NOT ask whether to invoke it, and do NOT add an options menu or any competing next-steps block. The block below is the entire output of this step.

### Emit this message VERBATIM (placeholders substituted)

The ONLY permitted modification is substituting `<url>`, `<bug-branch>`, `<base-branch>`, `[TICKET-ID]`, `<slug>` with real values from `## Branching` / the Step 9 PR. **Never ship an unsubstituted placeholder**; never add, remove, reorder, reword, or summarise a line:

```
✅ Bug fix complete — [BUG] PR: <url> (ticket [TICKET-ID] remains 🔵 In Development).
   📦 The cycle archive was deliberately NOT run — it is yours to run, at step 4️⃣ below.

➡️ NEXT ACTIONS (in this order):
   1️⃣  Wait until the ve `ve/...` PR(s) for [TICKET-ID] have MERGED into `<bug-branch>`
       (the ve PR into the bug branch — NOT the [BUG] PR into `<base-branch>`)
   2️⃣  On `<bug-branch>`: `git checkout <bug-branch> && git pull --ff-only`
       (pulls the merged `.spec/aire-docs/tests/<TICKET-ID>-.../` docs in so the archive captures them)
   3️⃣  ve: use the skill ve-list-work — on `<bug-branch>`, NOT on `<base-branch>`
       • Option C to amend a test plan (commit + push to `<bug-branch>` so the archive captures it)
       • Option B to sign off — promotes ticket [TICKET-ID] 🔵 In Development → 🧪 Ready for Testing
       (Sign-off happens HERE, before the archive.)
       🎭 Where the Playwright Test Automation extension is enabled, ve-list-work's own output
          will point you at `/playwright-implement [TICKET-ID]` once manual steps exist — run it here,
          on `<bug-branch>`, same as an epic cycle.
   4️⃣  Use the skill archive-epic  on bug branch (bug mode → `aire-archives/bugs/<TICKET-ID>-<slug>/`)
       🔴 MUST happen while the [BUG] PR is still OPEN — its cycle-close commit rides that
          open PR, which is how the RE delta reaches `<base-branch>`.
   5️⃣  ONLY NOW merge the [BUG] PR into `<base-branch>`: <url>
   6️⃣  Switch to `<base-branch>` and pull the latest
   7️⃣  Use the skill stitch-delta (applies this bug's RE delta to the root docs — final action;
       the ONLY base-branch step)

🔴 ORDER IS LOAD-BEARING: archive-epic (4️⃣) runs BEFORE the [BUG] PR merges (5️⃣).
   Merging first breaks stitch-delta and forces a manual recovery PR.
🔴 Use the skill names EXACTLY as shown — do not describe what you want in your own words.
   Any other phrasing is not a framework trigger and the workflow will not advance.
```
---

## Critical Rules
- EVERY audit entry carries the `**JIRA TICKET**:` field AND the `**AIRE VERSION**:` field (version read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` — never hardcoded).
- 🔴 **NO GATES AT ALL** — the fix plan is announced and executed (no GATE 2), and the review verdict routes the run automatically (no GATE 3). Never present a plan-approval or Approve-&-continue/Remediate prompt, and never write "GATE" into an audit heading from this workflow.
- 🔴 **THE FRAMEWORK FIXES ITS OWN FINDINGS, WITHIN A BOUNDED BUDGET** — any 🔴/🟠 finding triggers the auto-remediate loop (8c, **SH-LOOP-5**): remediate → regression → re-review, looping until the verdict is clean **or the 3-attempt budget is exhausted**. On exhaustion (3 rounds, or an SH-5 stall — no code change + identical findings) the run **HALTS at the gate**: no commit, no push, no `[BUG]` PR, no tracker change; the Retry-Limit Report is emitted to the user and to audit.md, and the run waits for user direction.
- 🔴 Mid-coding plan deviations are applied only after the plan document is revised and the change announced + logged — never silently, and never via an approval prompt.
- Version stamping mirrors dev-implement: the `aire-v[N]` label on the Jira ticket (Step 2.5), the `AIRE-Version: [N]` trailer on the fix commit (Step 9), and the `aire-v[N]` label on the `[BUG]` PR (via pr-generator) — all substituted live from CLAUDE.md.
- ONE branch — work on the recorded Bug Branch only; never create story branches; never commit to the base branch.
- ALWAYS run the BASELINE regression BEFORE any change, and the FULL regression AFTER the fix; only NEW failures (vs baseline) block; log both runs' complete output in `bug-<TICKET-ID>-summary.md`.
- 🔴 ALWAYS BOOTSTRAP missing tool configs BEFORE the baseline static run (Step 3 Item 5, `common/eval-framework.md` Section 2.2) — a check with no config is **set up**, not marked N/A; an existing config is used **as-is**. Bootstrap → baseline → fix → gate → diff: a config created after the baseline blames this fix for pre-existing findings. Announce every file created.
- 🔴 ALWAYS run the BASELINE static eval checks D1–D7 before any change (Step 3 Item 5) and the STATIC EVAL GATE after the regression gate (Step 7.5); only findings NEW vs baseline on changed files block, and this fix resolves them in the same run. **NEVER suppress a finding to pass the gate** — that is the analogue of deleting a failing test. Baseline findings are pre-existing debt: logged, ignored. See `common/eval-framework.md`.
- 🔴 The J1/J2 judge scores are computed ONCE in Step 8a and are **output only** — never a gate, never a review finding, never fed to remediation, never re-scored, never in the `verdict`. J1 = `N/A` is a normal outcome for a bug fix that skipped the design stages and has no derivable rubric.
- 🔴 The 8c auto-remediate loop (**SH-LOOP-5**) is **capped at 3 rounds** by the Self-Healing Retry Policy and is otherwise **unchanged by the eval layer** — it receives no eval input and gains no other stop condition. The J1/J2 judge scores never enter it.
- Unit tests must include at least one test reproducing the defect; coverage on new/changed code ≥90%.
- 🔴 **API & Contract Testing Gate (Step 6.5) is MANDATORY WHEN the fix touches an API endpoint** — applicability is plan-derived and automatic, never asked. Generate automated tests against the real endpoint(s), RUN them, and iterate until every applicable checklist item (functional, response-code validation, role-based authorization 401/403, error-response validation, request validation, response contract/schema validation) passes, in the SAME run, BEFORE the Full Regression Gate (Step 7). This is **SH-LOOP-2**, capped at **3 remediation attempts**; on exhaustion apply SH-4 (HALT + Retry-Limit Report). N/A (with a stated reason) when the fix touches no API layer. Capture proof artifacts to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-1.1/`. This gate does NOT replace ve's `/ve-implement` MANUAL API/Contract test steps.
- NEVER commit/push/raise the PR while the review verdict is unclean. An exhausted SH-LOOP-5 (8c.7) HALTS the run — it does NOT proceed to the PR. PR via `pr-generator` only, target = Base Branch, `[BUG]` prefix, `ai-generated` label. **The whole chain is automatic and prompt-free** — pr-generator runs in workflow mode with Phase 5 skipped; asking whether to push or open the PR is a defect.
- The ticket stays `🔵 In Development` after the PR — NEVER transition it to Ready for Testing yourself; that is ve's, via `ve-list-work` Option B run **on the bug branch, before `archive-epic` and before the `[BUG]` PR merges** (not post-merge on the base branch — after the archive's workspace reset there is no Story Tracker left to promote). No Parent-Epic sync exists in this flow.
- **NEVER run Build & Test in this workflow.** Test Plan is not a Implementation step at any level — it belongs to ve and is run separately, per ticket, via the **`/ve-implement`** skill (black-box, from the ticket's acceptance criteria, into `.spec/aire-docs/tests/<TICKET-ID>-<title>/`). Do not load `implementation/test-plan.md` here and do not write anything under `.spec/aire-docs/implementation/build-and-test/`.
- At Step 2, ALWAYS assign the ticket to the operator who invoked `bug-fix-implement` per `common/tracker-sync.md` Section 5 (automatic, verified where applicable, logged). Unresolvable identity → leave unassigned, warn, continue — assignment failure never blocks the fix. LOCAL has no assignee concept.
- 🔴 After the PR: AUTO `pr-review` (comment-only), then **STOP — the archive is MANUAL**. NEVER invoke `archive-epic` from this workflow. **Re-read Step 12 before emitting its handoff, and emit that block VERBATIM with placeholders substituted** — do not paraphrase it. The operator runs `archive-epic` once the ve `ve/...` PR(s) (and any `ve-list-work` Option C amendments) have merged **into the bug branch**, and **BEFORE the `[BUG]` PR merges into the base branch**, so the delta rides the open PR for post-merge `stitch-delta`. Never tell the user the archive runs post-merge — that inverts the invariant.
