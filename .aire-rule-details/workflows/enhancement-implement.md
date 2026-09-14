# ✨ WORKFLOW: `enhancement-implement <TICKET-ID>` (Enhancement — Analysis + Implementation in ONE flow)

## MANDATORY: Rule Details Loading

May be invoked standalone in a fresh session. Resolve `.aire-rule-details/` and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- `common/branching-strategy.md` — **Bug Branch Model** section (the enhancement branch follows the same single-branch model, with the `enhancement/` prefix)
- `planning/workspace-detection.md`, `planning/reverse-engineering.md` (if RE runs), `planning/requirements-analysis.md`, `planning/workflow-planning.md`
- `implementation/code-generation.md` (planning/generation/coverage mechanics — story selection and story-branch steps do NOT apply here). 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- `workflows/code-review.md` (auto-run after the implementation) and `workflows/remediate.md` (on the Remediate path)
- `common/eval-framework.md` — the Static Eval Gate D1–D7 (baseline at Step 10, gate at Step 14.5), the J1/J2 judge scores (Step 15a), and rubric derivation at Step 8. Evidence key for this flow: `enhancement-[TICKET-ID]`

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `implementation/code-review.md` / `implementation/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).
- Extensions per CLAUDE.md's Extensions Loading rules (Security Baseline is ALWAYS mandatory)

Skills used **as-is — NEVER edit them**: **`pr-generator`** (pass target branch = the **Base Branch**; PR type `[ENH]`), **`pr-review`** (AUTO MODE after the PR), and **`archive-epic`** in **cycle mode** (🔴 **NEVER auto-invoked by this workflow — the operator runs it manually** after all ve work has landed on the enhancement branch; archives under `aire-archives/enhancements/`; see Step 19).

Display the welcome message (`common/welcome-message.md`) once at start. All CLAUDE.md audit-logging rules apply: log EVERY user input verbatim in `.spec/aire-docs/audit.md` (append-only, ISO 8601 timestamps).

## MANDATORY: Audit Entry Format — TRACKER ITEM on EVERY entry

Every audit.md entry in this workflow carries the `**User Email**:` field (current session email, read live), the `**TRACKER ITEM**:` field (the enhancement ticket as a clickable link for JIRA/ADO/GITHUB, or the local ID for LOCAL), and — from Phase B onward — the `**AIRE VERSION**:` field (read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` — never hardcoded), exactly as `dev-implement` does.

## 🤖 THIS WORKFLOW IS FULLY AUTOMATIC — IT HAS NO APPROVAL GATES

**The Implementation Checkpoint ("Ready to implement now? yes / no", between Phase A and Phase B) is
the ONLY user decision in Phase B.** Everything after that `yes` — the implementation plan, the code,
the unit-test/coverage gate, the regression gates, the automated Code Review, **the remediation of any
findings it reports**, the commit, the push, the `[ENH]` PR and the PR review — runs **without a
single approval prompt**.

- ❌ There is **NO GATE 2** (implementation-plan approval). The plan is built, announced and executed.
- ❌ There is **NO GATE 3** (review decision). A review with findings is **remediated automatically**,
  then re-reviewed, **looping until the verdict is clean** — never an Approve/Remediate question.
- ❌ There is **NO GATE 1** either — that was the epic flow's story-set approval, which no longer
  exists anywhere in the framework.
- ✅ The **Implementation Checkpoint remains** — it is deliberately unnumbered flow control (it also
  marks the ve handoff), not a numbered approval gate.
- 🔴 **Never write the word "GATE" into an audit heading from this workflow.** Plan and review
  outcomes are logged as auto-approved decisions under plain headings.
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
| **SH-LOOP-1** | Unit Test & Coverage | Step 13 | All unit tests green **and** coverage on new/changed code ≥ 90% |
| **SH-LOOP-7** | Behavioural B1 + B2 (Gherkin) | Step 13.2 | The enhancement's scenarios pass with every AC tag executed, AND the entire existing behaviour suite stays green |
| **SH-LOOP-8** | Behavioural B3 (epic scope) | Step 13.2 | The full suite + the ticket's end-to-end journey pass |
| **SH-LOOP-2** | API & Contract Testing | Step 13.5 | Every applicable checklist item passes on every touched endpoint |
| **SH-LOOP-3** | Full Regression | Step 14 | Zero NEW failures versus the Step 10 baseline |
| **SH-LOOP-4** | Static Eval D1–D7 | Step 14.5 | Zero NEW findings above the `.evals/config.json` thresholds on changed files |
| **SH-LOOP-6** | Judge Gates J1 + J2 | Step 15a Item 2.5 | `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin` (`N/A` passes) |
| **SH-LOOP-5** | Auto-Remediate (code review + security findings) | Step 15c | Review verdict clean — zero 🔴 and zero 🟠 |

**SH-1 — Attempt budget.** Each loop is allowed a **maximum of 3 remediation attempts**. One attempt
is one complete `fix → re-verify` cycle. The initial verification run that first detects the failure
is **not** an attempt (it is attempt 0). Attempts are numbered 1, 2, 3.

**SH-2 — Counters are per-loop, independent, and never silently reset.** Maintain a separate counter
per SH-LOOP ID. A counter is never shared between loops, never reset by another loop's success, and
never reset by advancing to a later gate. When a later loop's remediation forces re-entry into an
earlier loop (for example Step 15c re-running the Step 14 regression comparison), that re-entry **continues the earlier loop's existing
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
   external tracker. The ticket stays `🔵 In Development` on its enhancement branch. The attempted fixes stay in the working tree for inspection.
3. Emit the **Retry-Limit Report** below as the run's final output.
4. Append the same content to `audit.md` under the heading
   `## Self-Healing Retry Limit Reached — [SH-LOOP-ID] (Enhancement [TICKET-ID])`, carrying the standard
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
   Work unit: Enhancement [TICKET-ID] — [ticket title]
   Branch:    [enhancement branch]

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
   C) 🙋 Take it over manually — fix it in the working tree, then re-invoke `enhancement-implement` for
      this work unit to resume from this gate.
   D) 🗂️ Raise a defect and stop — log the blocker via `/raise-defect` and leave the work unit
      `🔵 In Development` for a later session.

[Answer]:
```

🔴 **Log the user's raw response in `audit.md`** under
`## Self-Healing Retry Limit — User Direction ([SH-LOOP-ID])`. A new budget is granted for the named
loop ONLY, and ONLY under option A or B; every other loop keeps the counter it already held.

---

# PHASE A — Analysis (trimmed Planning + design)

## Step 1 — Ticket Capture

1. **Resume check first**: if `.spec/aire-docs/aire-state.md` exists, read it. If `## Tracker` records a DIFFERENT ticket/epic, ask the user which to keep — NEVER silently overwrite. If it records this same ticket with `Workflow Type: enhancement`, resume from the recorded stage per `common/session-continuity.md`. If `## Tracker` doesn't exist yet, ask the Tracker Selection question (`common/tracker-sync.md` Section 1) first.
2. Dispatch on `## Tracker` → `Type`, per `common/tracker-sync.md` Section 8:
   - **JIRA/ADO/GITHUB**: parse the `<TICKET-ID>` from the invocation (key/ID/number or URL). If missing, ask for it and wait. Fetch the ticket (`getJiraIssue` / `az boards work-item show` / `gh issue view`) — issue type **Story or Task** (a Bug should go through `bug-fix` instead — warn if it's a Bug and confirm before continuing). Save summary, description, and acceptance criteria to `.spec/aire-docs/planning/requirements/enhancement-brief.md`.
   - **LOCAL**: no ID expected. Ask `❓ Describe the enhancement (what should change, and why):`, capture the answer, and mint a local ID `ENH-LOCAL-N` (next unused N found by scanning `aire-state.md`) to use as `<TICKET-ID>` for the rest of this flow. Write the captured description directly to `enhancement-brief.md`.
   The enhancement-brief is the intake brief: it defines WHAT to enhance and is the primary input to every later stage.
3. Record in `.spec/aire-docs/aire-state.md`:
   ```markdown
   ## Tracker
   - Type: JIRA
   - Workflow Type: enhancement
   - Parent Ticket: PROJ-456        (the enhancement being built — issue type: [Story/Task]; or ENH-LOCAL-N for LOCAL)
   - Ticket URL: https://<site>.atlassian.net/browse/PROJ-456   (— for LOCAL)
   - Project Key / Repo / Org: PROJ (derived from the key — confirm before first use; — for LOCAL)
   - Parent Epic: none              (enhancement flow — all Parent-Epic sync steps are skipped)
   ```
   `Workflow Type: enhancement` is the marker every resumed session reads FIRST — it routes execution to this workflow's rules.
4. **MANDATORY**: Log the invocation (complete raw input) and the ticket fetch/capture in audit.md.

## Step 2 — Workspace Detection + Enhancement Branch (branch FIRST, before requirements)

1. Execute `planning/workspace-detection.md` Steps 1–4 as written (workspace scan, brownfield/greenfield, RE-artifact search anywhere in the repo, state file creation). An enhancement is expected to be **brownfield**; if the workspace is empty, STOP and suggest the full epic flow instead.
2. **Create the ENHANCEMENT branch (automatic)** — same single-branch model as the bug flow (`common/branching-strategy.md` Bug Branch Model), with the `enhancement/` prefix:
   - Record the **base branch** (`git branch --show-current` — never assume `main`).
   - Create `enhancement/<TICKET-ID>-<kebab-case-ticket-title>` (whole name ≤ 60 chars; working tree must be clean, else show `git status` and ask).
   - Record in `aire-state.md`:
     ```markdown
     ## Branching
     - Base Branch: main
     - Enhancement Branch: enhancement/PROJ-456-export-to-csv
     - Enhancement PR: (pending — raised at the end after code review approval)
     ```
   - **ALL work — docs and code — happens on this ONE branch.** No story branches are ever cut.
3. Log the branch creation (name, base) in audit.md; present the Workspace Detection completion message and proceed automatically.

## Step 3 — Reverse Engineering (CONDITIONAL — as-is)

Exactly per the epic flow: if RE artifacts exist anywhere in the repo (or restorable from `aire-archives/`), reuse them and skip. Otherwise run `planning/reverse-engineering.md` in full, with its approval gate. Log everything in audit.md.

## Step 4 — Requirements Analysis (as-is, enhancement-scoped)

1. Execute `planning/requirements-analysis.md` with `enhancement-brief.md` as the primary input. Depth will usually be **minimal/standard** (the ticket defines the enhancement); use comprehensive only if it is genuinely complex or high-risk. Its Step 1.5 reads the `## Context Project` answer captured by `ticket-implement` (Step 3.5) and, if `Use Artifacts: Yes`, uses **only** the recorded path as background context about the existing system — do NOT re-ask.
2. Extension opt-ins are presented as usual; Security Baseline is always enforced.
3. **Wait for explicit approval** of requirements.md.
4. On approval: commit the planning artifacts on the **enhancement branch**. 🔴 **Do NOT raise a PR here** — the single `[ENH]` PR is raised at the end, after code review approval.
5. **MANDATORY**: Log the user's response verbatim in audit.md.

## Step 5 — Impact Analysis (NO AI-Origin Detection)

**Purpose**: Find WHERE the enhancement lands — the files/components to change and the blast radius — for an accurate implementation plan.

1. Using the RE artifacts, the enhancement-brief, and code search (grep/glob/read), identify the **affected files/components**: where the new behavior plugs in, what must change, and the blast radius (callers, consumers, shared files, tests). Cite explicit **`file:line-range`** evidence per touch point.
2. Write `.spec/aire-docs/planning/impact-analysis.md`:
   ```markdown
   # Impact Analysis — [TICKET-ID]
   ## Change Approach
   [Where the enhancement plugs in and why, with file:line evidence]
   ## Affected Files
   | File | Why it must change |
   |------|--------------------|
   ## Blast Radius
   [Callers/consumers/tests that could be impacted by the change]
   ```
3. **🤖 AUTOMATIC — no approval gate.** Present the Impact Analysis summary as an **announcement** and proceed straight to Step 6 — do NOT ask for approval and do NOT block. The analysis is evidence-based (`file:line` citations), is re-validated against current code at Step 11.2, and is re-surfaced inside the announced implementation plan (Step 11). Log in audit.md that it was completed and auto-approved, with the affected-file list. If the user volunteers a correction, update `impact-analysis.md`, re-announce, and continue (an interrupt, not a gate). This document is the primary planning input for the implementation phase.

## Step 6 — Single Story (replaces User Stories + Dependency Graph)

1. Write **exactly ONE story** to `.spec/aire-docs/planning/user-stories/stories.md`, derived from the ticket + requirements + impact analysis: story ID `1.1`, title = the enhancement, acceptance criteria from the ticket (plus regression-safe), and a `**Covers**: REQ-F-xx, …` line naming the REQ-IDs assigned in the enhancement-scoped `requirements.md` (`common/requirements-traceability.md` Rules 2 & 7) — coverage must be complete: every REQ-ID from that requirements.md maps to this one story. Do NOT ask team size, do NOT generate extra personas, do NOT ask about pushing to the tracker (the ticket already exists, or for LOCAL never existed externally — no new issue is ever created), do NOT create `dependency-graph.yml`.
2. Populate the Story Tracker in `aire-state.md` with the single row (Tracker ID column = the existing enhancement ticket — the Tracker Sync Rule applies to it at every status change):
   | Story | Title | Requires | Tracker ID | Status | Start | End | Recorded |
   |-------|-------|----------|------------|--------|-------|-----|----------|
   | 1.1 | [Enhancement title] | none | PROJ-456 (or ENH-LOCAL-N for LOCAL) | 🟢 Ready for Development | | | [timestamp] |
3. **Wait for explicit approval** of the story; log the response verbatim.

## Step 7 — Workflow Planning (as-is)

Execute `planning/workflow-planning.md`: determine which Implementation design stages EXECUTE/SKIP for this enhancement (small enhancements skip most design stages), generate the execution plan + visualization (validate Mermaid), **announce it, and proceed automatically** — that file's Step 9/10 are an announcement, not an approval gate. Each design stage the plan selects still runs its own approval when it executes.

## Step 8 — Implementation Design Stages (CONDITIONAL, as-is)

Run the system-level design stages the plan selected (Functional Design → NFR Requirements → NFR Design → Infrastructure Design), each per its rule file with its standardized 2-option completion message and approval gate. Scope each to the enhancement-brief + impact analysis.

**📐 Derive the architecture rubric (automatic, no gate — after the last design stage, or immediately when all design stages were skipped)**: per `common/eval-framework.md` Section 3, derive `.evals/rubrics/architecture-rubric.json` from the design artifacts produced here plus the registered `## Design References`, version it, and commit it with the design artifacts at the ve Handoff Break push. **Small enhancements skip most design stages** — when there is nothing to derive from, apply the Section 3 **fallback chain** (a prior cycle's committed rubric → the reverse-engineering artifacts → J1 recorded `N/A`) and record which link was used. 🔴 Never hand-write a generic rubric and never score J1 against a borrowed or unrelated one. Also create `.evals/rubrics/security-rubric.json` (OWASP-based, per `implementation/architecture-doc.md` Section 4.1) and `.evals/config.json` from the eval-framework.md Section 1 template if they do not exist yet. Log in audit.md.

---

# 🛑 ve HANDOFF BREAK → 🚦 Implementation Checkpoint (ask, don't stop)

After the design stages complete (or are all skipped), mark in `aire-state.md`: `Analysis complete — awaiting implementation approval`, log in audit.md.

**This is a deliberate BREAK in the flow.** The analysis + design artifacts are everything the ve needs, and the ve must not have to wait for the code. So before Phase B:

1. **Commit + push the analysis and design artifacts on the enhancement branch (automatic — this is what unblocks ve)**: stage `.spec/aire-docs/planning/**` (enhancement-brief, requirements, impact analysis, the single story), `.spec/aire-docs/implementation/design/**`, the updated `aire-state.md` and `audit.md`; commit on the enhancement branch with an `AIRE-Version: [N]` trailer (`[N]` read live from `CLAUDE.md`); push to origin. Announce the commit hash + pushed branch and log both in audit.md. 🔴 If the push fails, say so explicitly and tell the user to push manually — **the ve cannot start until this branch is on origin**. Still no `[ENH]` PR here.
2. Present the break message below and **block on its yes/no**.

```markdown
# ✅ Enhancement Analysis Done — Design Artifacts Pushed

✨ **Ticket**: [TICKET-ID] — [title]
📍 **Impact**: [N] files identified in .spec/aire-docs/planning/impact-analysis.md
🧩 Design stages: [list which ran vs were skipped]
🌿 Branch: enhancement/[TICKET-ID]-[title] (cut from [base branch]) — analysis + design **committed and pushed** ([commit hash])

> **🧪 <u>**ve — start NOW, in parallel. The code does not have to exist.**</u>**
> 1️⃣  `git fetch origin && git checkout enhancement/[TICKET-ID]-[title] && git pull --ff-only`
> 2️⃣  Type **`/ve-implement [TICKET-ID]`**
>     It cuts `ve/[TICKET-ID]-[title]` from this branch, writes the MANUAL test steps to
>     `.spec/aire-docs/tests/[TICKET-ID]-[title]/` from the ticket's acceptance criteria, and raises its
>     own PR back into `enhancement/[TICKET-ID]-[title]` — so the test docs ride the `[ENH]` PR into [base branch].

> **⚙️ <u>**DEV — continue with the implementation plan and code generation**</u>**
> ❓ **Ready to implement now? (yes / no)**
> **yes** → everything below runs automatically, with no further questions:
>           baseline regression → implementation plan (announced) → code + unit
>           tests (the `unitTestCoverageMin` threshold) → FULL regression → auto code review, with any findings
>           auto-remediated and re-reviewed until clean (max 3 rounds) → `[ENH]` PR to
>           [base branch] → auto PR review → then STOP (the cycle archive is MANUAL — you run
>           `archive-epic` after the ve test-plan PR merges into the enhancement branch).
> **no**  → I halt here; the state is saved. Resume any time with `ticket-implement [TICKET-ID]`
>           (or `enhancement-implement [TICKET-ID]`) and it picks up at this gate.

🔴 Use `/ve-implement` and the keywords EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

**Block until the user answers.** On **no**, halt here (state is saved — re-invoking `enhancement-implement <TICKET-ID>` or `ticket-implement <TICKET-ID>` resumes at this gate). On **yes**, log the response verbatim and continue to Phase B. Substitute every placeholder (`[TICKET-ID]`, `[base branch]`, `[commit hash]`) with real values — never ship a placeholder to the user.

---

# PHASE B — Implementation (same flow, after "yes")

## Step 9 — Ticket → 🔵 In Development (automatic)

The user's "yes" IS the claim. Without asking, dispatch on `## Tracker` → `Type` per `common/tracker-sync.md` Section 4/Section 5/Section 9:
1. Story Tracker (single row): Status → `🔵 In Development`, Start + Recorded timestamps set.
2. Transition the ticket to the tracker's "In Development" state/label (non-LOCAL): **JIRA** — resolve the actual transition via `getTransitionsForJiraIssue` → `transitionJiraIssue` (never hardcode the state name); **ADO** — `az boards work-item update --state "Active"`; **GITHUB** — swap the status label to `status:in-development`. **Verify it landed**, announce it, log in audit.md. **LOCAL**: no external call.
3. **👤 Assign the ticket to the operator (automatic — same claim)**: read the session **email** LIVE from the session context, then **JIRA**: resolve via `lookupJiraAccountId` + `editJiraIssue`; **ADO**: `az boards work-item update --assigned-to "<session-email>"`; **GITHUB**: a cached GitHub username + `gh issue edit --add-assignee`; **LOCAL**: no assignee concept, skip. **Verify** (non-LOCAL) by fetching the issue back. Unresolvable/ambiguous identity → leave unassigned, warn, continue (non-blocking). Announce and log in audit.md.
4. **Add the AIRE version label/tag** `aire-v[N]` to the ticket per `common/tracker-sync.md` Section 9 (JIRA label / ADO `System.Tags` / GitHub label / LOCAL a note on the local entry), `[N]` read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` — never hardcoded. Skip if already present. Verify (non-LOCAL), announce, log.
5. 🔴 Skip all Parent-Epic sync steps — `## Tracker` records `Parent Epic: none`.

## Step 10 — 🧪 BASELINE Regression Run (BEFORE any change)

Same as the bug flow: discover and run the **entire repo's unit test suite** with no code changes yet; record the baseline (commands, results, pre-existing failures) in `.spec/aire-docs/implementation/code/enhancement-<TICKET-ID>-summary.md`; pre-existing failures are logged, not fixed. Log in audit.md. If the repo has no test suite, record that explicitly.

**🔎 BASELINE STATIC EVAL RUN (MANDATORY, AUTOMATIC — same moment, before any change)**: also run the **Static Eval Gate checks D1–D7** per `common/eval-framework.md` Section 2 (lint, type check, SAST, dependency vulnerabilities, licences, complexity, secrets) and save the raw output to `.spec/aire-docs/implementation/code/eval-evidence/enhancement-<TICKET-ID>/static/baseline/`. Exactly like the regression baseline: **every finding is pre-existing debt, not this enhancement's** — logged, not fixed, never blocking; it exists only so Step 14.5 can tell this change's findings apart.

**🔧 BOOTSTRAP FIRST (eval-framework.md Section 2.3, MANDATORY — same step, immediately BEFORE the baseline run)**: for every check with **no config in the repo**, create the minimal *recommended* config (eslint/ruff/golangci, tsconfig/mypy, `.gitleaks.toml`, the linter's complexity rule at the `.evals/config.json` threshold) so the check is actually runnable. **A check whose config exists is used AS-IS** — the repo's own standards win, never overridden. Announce every file created and log it (`bootstrap` block of `eval.json`) — it adds files to the user's repo, so it is never silent; those files commit with the enhancement. 🔴 **AND INSTALL THE TOOLS — retried, never skipped (Section 2.4.1)**: for every gate, work the chain *already present → package manager → alternative installer → **OCI image via Podman***, 3 attempts per rung, verifying each install with a version command. Recording a gate `N/A` for a missing tool **before the Podman rung has been tried** is a bootstrap failure, not an `N/A`. If the whole chain is exhausted, **HALT with the per-rung report** — never continue with an unmeasured gate, and never phrase deferred setup as `N/A` ("not wired yet", "not installed", "not enabled yet" — all ERROR, Section 2.5.2).
- 🔴 **ORDER MATTERS**: bootstrap → baseline → implement → Step 14.5 → diff. A config created AFTER the baseline would make both runs measure under **different rules**, blaming this change for findings on pre-existing code.
- 🔴 Recommended presets, never strict/all, and **never a config that pre-suppresses findings**.
- 🔴 A check is recorded `N/A` **only after the full Section 2.4.1 install chain — including the Podman image rung — has been attempted and recorded**, and only for a reason on the Section 2.5.1 closed list (inapplicable to this stack / to this work unit / no such tool exists). If the chain is exhausted, that is an **ERROR: HALT** with the per-rung report — never `N/A`, never silently skipped, and never phrased as deferred work ("not wired yet", "not installed", "not enabled yet").

## Step 11 — Implementation Plan (🤖 announced, not gated)

1. Build the plan from `impact-analysis.md` + the design artifacts, using `code-generation.md`'s Part 1 planning format (checkboxed steps), ending with the mandatory Unit Test & Coverage step, the API & Contract Testing Gate (Step 13.5, when the enhancement touches an API endpoint), and the Full Regression Gate (Step 14). **📐 GROUND THE PLAN in the previously generated docs** — every step MUST trace back to the ticket's acceptance criteria, `enhancement-brief.md`, `requirements.md`, the impact analysis, and any design artifacts; never invent scope, files, or behavior not backed by them. **🧾 REQ-ID THREAD**: tag every plan step with the REQ-ID(s)/AC(s) it implements and self-check that every REQ-ID from `requirements.md` and every AC of the single story appears in ≥1 step before presenting the plan (`common/requirements-traceability.md` Rules 5 & 7).
2. **Re-validate the impact analysis against current code.** If the plan must touch files NOT in the impact analysis, add them to `impact-analysis.md` first .
3. **🤖 Announce the plan and proceed — NO approval gate**:
   1. **Log the finalized plan** in `.spec/aire-docs/audit.md` (ISO 8601 timestamp) under a **plain heading** — e.g. `## Implementation Plan — Finalized (auto-approved, no gate) (Enhancement [TICKET-ID])` — with the plan path, the step count and the REQ/AC trace summary. **The word "GATE" must NOT appear in the heading.**
   2. Present the plan as an **announcement** (NOT a question):
      ```
      📋 Implementation plan ready for Enhancement [TICKET-ID] — [N] steps.
      Plan: .spec/aire-docs/implementation/plans/enhancement-[TICKET-ID]-implementation-plan.md
      ➡️ Generating the enhancement now (Step 12).
      ```
   3. **Do NOT wait for a response** — go straight to Step 12. If the user volunteers a change to the plan, apply it, update the plan document, announce the revision, log it, and continue (an interrupt, not a gate).

## Step 11.5 — 🥒 Write the Behaviour Spec (MANDATORY — before any code)

Write `.spec/aire-docs/implementation/code/behavior/enh-<TICKET-ID>.feature` per `common/behavior-spec.md` Section 2 — one Gherkin scenario per acceptance criterion, `@AC-n` tagged, failure paths included (for a bug, including the scenario that reproduces the defect). Authored **BEFORE** the implementation: it is the contract, not a description of what was built.

🔴 **That is the ONLY spec file this work unit gets.** No per-unit requirements, architecture, constraints or knowledge-graph document. The agent reads the tracker item for acceptance criteria, `requirements.md` for the covered REQ-IDs, `.spec/architecture.md` for design constraints, and `.evals/config.json` for thresholds — copying any of that per unit only creates something that can drift.

Announce the file path and the scenario/AC counts. Log both in audit.md.

## Step 12 — Generate the Enhancement

Execute the approved plan step by step on the enhancement branch, marking each checkbox `[x]` in the same interaction it completes. **📁 All application code goes into `src/`** (or the recorded `## Code Root` — `common/directory-structure.md`), test code into `tests/`, and nothing into `.spec/`. **🛡️ PLAN FIDELITY**: implement EXACTLY the announced plan — no unplanned files, features, refactors, or scope drift. If a deviation is genuinely needed, **revise the plan document (Step 11), announce the revision (what changed and why) in your output and in audit.md, and continue** — never applied silently, and never via an approval prompt. Write code to the workspace root per the existing project structure. Log progress in audit.md.

## Step 13 — Unit Tests + Coverage Gate (threshold from `.evals/config.json`)

1. Write unit tests covering all new/changed code, exercising the enhancement's acceptance criteria.
2. RUN them; fix failures; measure coverage on the new/changed code; iterate in the SAME run until **≥90%**. 🔁 **This is SH-LOOP-1 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT, emit the Retry-Limit Report, and do NOT proceed below the threshold.**
3. Capture evidence (tests X/X passing + measured %) in `enhancement-<TICKET-ID>-summary.md` and audit.md, with the machine-readable coverage report per dev-implement's evidence rules (`.spec/aire-docs/implementation/code/unit-test-evidence/story-1.1/`).

## Step 13.2 — 🥒 Behavioural Test Gate (Gherkin — three tiers)

Execute the tiered behavioural gate defined in `common/behavior-spec.md` Section 4.4. Implement the step definitions in `tests/behavior/steps/`, bound to the application's **public surface** (endpoint / service method / CLI) — never to internals — then run the tiers **in order**:

1. **B1 — Unit scope**: this work unit's own `.spec/aire-docs/implementation/code/behavior/enh-<TICKET-ID>.feature`. **Verification**: every scenario passes AND every `@AC-n` tag is executed.
2. **B2 — Cumulative scope**: every **other** feature file already in the repo — earlier work units in this cycle plus everything from prior cycles. **Verification**: all green. 🔴 A B2 failure is THIS unit's problem — it turned that scenario red, so it fixes it. "That scenario belongs to another story" is not a defence.
3. **B3 — Epic scope** (🔴 **last work unit of the cycle ONLY**): B1 ∪ B2 **plus** the cross-unit journeys in `.spec/behavior.feature`, tagged `@REQ-<id>`. 🔴 Detect "last" from **PR MERGE STATE, never the tracker status label** (`common/behavior-spec.md` Section 6.1): for every OTHER work unit read its PR from the Story Tracker and verify live with `gh pr view <n> --json state`. **All others merged → this is the last unit → RUN B3** — including the normal case where those units are still `🔵 In Development` awaiting ve sign-off, because the label lags the merge. Defer ONLY when a unit has no merged PR, recording `B3: N/A — deferred, <n> units with unmerged PRs (<list with PR state>)`. 🔴 Never defer on a status label alone, and never report a deferred B3 as a pass.

**Execution** — 🔴 **every tier runs in a Podman pod** (`common/behavior-spec.md` Section 5): the image built from `.evals/behavior/Containerfile`, plus a fresh ephemeral **test database** where the repo needs one, invoked through `.evals/behavior/run.sh <tier>` — the same image and command a developer runs locally, so a CI-only failure is impossible by construction. 🔴 **The ONLY permitted native run is Podman not being installed** (proven by `command -v podman`), recorded as `"containerised": false, "reason": "podman not installed"`. 🔴 "No browser needed", "backend only", "no new dependency" and "faster natively" are **forbidden justifications** — a tier recorded that way is a gate violation, not a pass. Never fall back to the Docker CLI. A tier runs only once the previous is green.

**Evidence** — per tier, to `.spec/aire-docs/implementation/code/behavior-test-evidence/enhancement-<TICKET-ID>/<b1|b2|b3>/`: `behavior-test-run.log`, the **mandatory machine-readable** `behavior-test-report.*`, and an `evidence-manifest.md` recording the image ref + digest, the exact command, whether it ran containerised, the tier's feature-file set, and every scenario with its tag and result. A raw log alone does NOT satisfy the gate.

**Self-healing** — 🔁 **B1/B2 failures → SH-LOOP-7; B3 failures → SH-LOOP-8, its own separate 3-attempt budget** (an epic-scope failure is usually an integration gap between units, not a bug inside one, so arriving at the epic gate with the story budget already spent must not halt the cycle). Both capped at 3 attempts; on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report.

🔴 **Fix the code, never the scenario.** A scenario changes only when the AC or requirement it encodes genuinely changed — and then the AC, `requirements.md` and the tracker item are amended together and the reconciliation is logged. Deleting, skipping or `@ignore`-ing a scenario to go green is forbidden (SH-6).

**N/A** — B1 is N/A only for a work unit with no externally observable behaviour (pure build-config or docs change); a unit with acceptance criteria is never N/A. B2 is N/A only when the repo genuinely contains no other feature file. Record the reason explicitly.

## Step 13.5 — 🔌 API & Contract Testing Gate (MANDATORY WHEN APPLICABLE)

**Applicability (automatic, no question asked)**: applies when the implementation plan (Step 11) adds or changes an API endpoint/route/controller/handler. **If the plan touches no API layer, this gate is N/A** — record that explicitly in `enhancement-<TICKET-ID>-summary.md` and proceed to Step 14.

1. Generate automated tests against the actual new/changed endpoint(s) — via the stack's standard integration-test mechanism (in-process test client or a spun-up test server) — covering, for each endpoint:
   - **Functional / happy path** — the documented behavior per acceptance criterion
   - **Response Code Validation** — correct HTTP status code for every documented success and failure path
   - **Authorization Testing (role-based access)** — unauthenticated → `401`; authenticated with insufficient role → `403`; correct role → success (N/A only for a genuinely public endpoint)
   - **Error Response Validation** — standard error envelope/format and correct error code for each documented error condition
   - **Request Validation** — required fields, data types, and enum constraints on the request payload are enforced (N/A only for an endpoint with no request body)
   - **Response Contract Validation** — the response payload matches its declared schema/contract (required fields, types, enum values)
2. RUN them; fix failures; iterate in the SAME run until every applicable checklist item passes. 🔁 **This is SH-LOOP-2 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.**
3. Capture evidence (per-endpoint checklist + tests X/X passing) in `enhancement-<TICKET-ID>-summary.md` and audit.md, with proof artifacts saved to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-1.1/` (`api-contract-test-run.log`, the **mandatory machine-readable** `api-contract-test-report.*` — invoke the runner with its report-emitting flag/plugin, e.g. `pytest --junitxml=...` / `jest --json --outputFile=...`; a raw log alone does NOT satisfy the gate unless the runner genuinely has no such capability (documented, surfaced exception) — and `evidence-manifest.md`). This gate is separate from and does not replace ve's `/ve-implement` MANUAL API/Contract test steps.

## Step 14 — 🧪 FULL Regression Gate (after the change)

Re-run the **entire repo's unit test suite** (including any new API & Contract tests from Step 13.5) and compare against the Step 10 baseline — exactly as the bug flow: **new failures** (passing at baseline, failing now) are 🔴 BLOCKING (fix and re-run until zero); pre-existing failures are listed, not blocking. 🔁 **This is SH-LOOP-3 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.** Append the complete outcome to `enhancement-<TICKET-ID>-summary.md` and log the comparison in audit.md.

## Step 14.5 — 🔎 STATIC EVAL GATE — D1–D7 (MANDATORY, AUTOMATIC — after Step 14, before Code Review)

Re-run D1–D7 per `common/eval-framework.md` Section 2, save to `eval-evidence/enhancement-<TICKET-ID>/static/`, and **diff against the Step 10 baseline**. Only findings **NEW versus the baseline, on files this enhancement changed**, count. **No user prompt — fix and continue.**

1. **NEW findings above the `.evals/config.json` thresholds** → introduced by this change, so **this change resolves them in THIS SAME run**, then re-run and re-diff until the diff is clean. 🔴 BLOCKING. 🔁 **This is SH-LOOP-4 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.**
2. 🔴 **NEVER suppress a finding to pass the gate** — no blanket `eslint-disable`, no `# nosec`, no `# type: ignore`, no ignore-list entry, no widening `disallowedLicenses`. That is the exact analogue of deleting a failing test to go green and is equally forbidden. **Fix the code.**
3. **Findings already present at baseline** → pre-existing, listed not blocking.
4. Write `eval.json` + `eval-summary.md` (eval-framework.md Section 6) and append the gate outcome to `enhancement-<TICKET-ID>-summary.md`. Log in audit.md. Do NOT proceed with new findings outstanding.

## Step 15 — AUTO Code Review → 🤖 Verdict Routing + Auto-Remediate Loop

Mirrors dev-implement Sections A–C, enhancement-scoped. The Code Review runs **automatically**, and so does everything that follows from it — the user is asked nothing.

### 15a. AUTO Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Enhancement [TICKET-ID] (ISO 8601 timestamp).
2. Auto-run `workflows/code-review.md` scoped to this change (read-only — it MUST NOT edit source) → versioned report `.spec/aire-docs/implementation/reviews/enhancement-<TICKET-ID>-code-review-v[X].md`. Pass in the Step 13/14/14.5 evidence — the review MUST NOT re-run the tests, re-measure coverage, or re-run the D1–D7 checks; it cites the stored evidence.
2.4. **🛡️ AUTOMATED SECURITY REVIEW (MANDATORY, automatic — inside this review pass)**: the review's **Phase 2.5** runs the `agents/code-security-review-agent.md` procedure against this change's diff (all 16 Security Baseline rules, scoped to the changed files + the attack surface they reach) and writes `.spec/aire-docs/code-security-reviews/security-review-YYYY-MM-DD.md`. Its **🔴/🟠 findings on the changed surface become real `SEC-ISS-XXX` findings** — routed by 15b and **auto-remediated by 15c (SH-LOOP-5) until clean, within its 3-round budget**, exactly like AC findings. 🟡/🔵 and pre-existing violations on untouched lines are **advisory only** (`/raise-defect` for those). 🔴 Never suppress instead of fixing; never widen the scan to the whole repo.
2.5. **⚖️ JUDGE GATES J1 + J2 — 🔴 BLOCKING (MANDATORY, automatic — computed HERE and nowhere else)**: compute the two judge scores per `common/eval-framework.md` Section 4 from this work unit's diff — **J1** against `.evals/rubrics/architecture-rubric.json` (derived from `.spec/architecture.md` Section 10; apply the Section 3 **fallback chain**: this cycle's rubric → a prior cycle's committed rubric → derived from Atlas / the reverse-engineering artifacts → **`N/A` with the reason**; this flow skips most design stages, so `N/A` is a normal outcome and is never scored against a borrowed rubric) and **J2** against `security-rubric.json`. Write them with their **per-criterion breakdown** to `eval-evidence/enhancement-<TICKET-ID>/judge/`, merge into the **`gates`** block of `eval.json`, refresh `eval-summary.md`, report both in the review report.
   - **Scoring discipline** (Section 4.1): score **once** per review pass — never re-roll for a better number; every criterion below 1.0 **MUST cite `file:line`**; score only what the diff shows; a criterion this diff cannot exercise is `N/A`, excluded, remaining weights renormalised to 1.0 — never scored 0.
   - **🔁 Gate**: `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin` from `.evals/config.json`. `J1 = N/A` passes. **Below minimum → SH-LOOP-6**: remediate the cited criteria worst-weighted-loss first, re-run whatever gates the fix touched, re-score on the next review pass. **Capped at 3 attempts; on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report.**
   - 🔴 **Forbidden ways to pass** (SH-6): editing `architecture.md` Section 10, editing the rubric JSON, lowering either minimum, re-scoring until it clears, or marking an applicable criterion `N/A`.
3. **MANDATORY — audit the complete review log**: the `**TRACKER ITEM**:` field, report path, verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High). Do not summarize away findings.
4. Proceed to **15b**.

### 15b. 🤖 Review Verdict Routing (AUTOMATIC — no question, no gate)

The review's own verdict decides what happens next. **Do NOT present an A/B choice and do NOT wait for the user.** Announce the verdict, then route:
   ```
   🔍 Automated Code Review complete for Enhancement [TICKET-ID].
      Report: .spec/aire-docs/implementation/reviews/enhancement-[TICKET-ID]-code-review-v[X].md
      Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]
   ➡️ [Proceeding to commit + [ENH] PR. | Findings found — remediating them automatically now (round [n]).]
   ```
1. **Verdict clean (zero 🔴 and zero 🟠)** → go to **Step 16 (Commit, Push & Raise the `[ENH]` PR)**.
2. **Any 🔴 or 🟠 finding** → go to **15c (SH-LOOP-5)**. The framework fixes its own findings within a budget of **3 remediation rounds**; it hands them back to the user only when that budget is exhausted (SH-4), and then it HALTS instead of raising the `[ENH]` PR.
3. **MANDATORY**: log the routing decision in audit.md under a plain heading (`## Review Verdict — Clean, Proceeding to PR (Enhancement [TICKET-ID])` or `## Review Verdict — Findings, Auto-Remediating (Enhancement [TICKET-ID])`) with the full findings list by severity. **No "GATE" in the heading, and no user response to record.**

### 15c. 🤖 Auto-Remediate Loop — SH-LOOP-5 (AUTOMATIC — max 3 rounds)

**Entered whenever the review verdict reports findings. Every round is automatic — no prompts at any point. The loop is bounded by the Self-Healing Retry Policy: one round = one attempt, maximum 3.**
1. **Check the SH-LOOP-5 counter BEFORE starting a round.** If 3 attempts have already been spent, do not start another — go directly to step 7 (Exhaustion).
2. **Log** in audit.md that automatic remediation round `[n] of 3` is starting for Enhancement [TICKET-ID], naming the review report being remediated, the findings in scope, and the identified root cause of each (SH-3, SH-7).
3. Run `workflows/remediate.md` scoped to that report (fix → unit test → green). 🤖 **Its scope-confirmation prompt is SKIPPED** — every 🔴/🟠 finding is in scope and nothing is deferred. **Re-run the FULL repo suite if the remediation touched non-test code**, comparing against the Step 10 baseline again — only NEW failures block, and they are fixed in the same round. If the remediation touched API-layer code that Step 13.5 covered, also re-run the affected endpoint(s)' API & Contract tests and keep them green. Per SH-2, these re-entries **continue** the SH-LOOP-3 / SH-LOOP-2 counters — they do not reset them.
4. **MANDATORY — audit the complete remediate log**: the round number (`[n] of 3`), which findings were fixed (by severity), files changed, unit-test evidence, regression comparison. Record the complete log, not a summary.
5. **Re-review automatically**: return to **15a** (produces the next report version `v[X+1]`), then **15b** again.
6. **Loop control**:
   - **Verdict clean** → the loop exits successfully → **Step 16 (Commit, Push & Raise the `[ENH]` PR)**.
   - **Findings remain AND attempts spent < 3** → increment the counter and return to step 1.
   - **Findings remain AND attempts spent = 3** → **exhausted** → step 7.
   - **Stall (SH-5)** — a round produced **no code change at all** AND the next review returned an **identical** finding set → the loop cannot progress. Treat as exhausted immediately, regardless of attempts remaining → step 7, noting the early end.
7. **🛑 Exhaustion (SH-4) — HALT, do not raise the `[ENH]` PR.** When the budget is exhausted (3 rounds, or an SH-5 stall):
   - Do **not** run a 4th round, do **not** commit, do **not** push, do **not** raise a PR, and do **not** change the local Story Tracker or the external tracker. The ticket stays `🔵 In Development` and the remediation work stays in the working tree.
   - Emit the **Retry-Limit Report** (Self-Healing Retry Policy, above) with `[loop name]` = `Auto-Remediate (code review + security findings)` and `[SH-LOOP-ID]` = `SH-LOOP-5`, listing every unresolved finding with its ID, severity, file:line, and the reason automatic remediation failed on it.
   - Append the same content to audit.md under `## Self-Healing Retry Limit Reached — SH-LOOP-5 (Enhancement [TICKET-ID])`.
   - **HALT and wait for the user's direction.** 🔴 Never silence a finding by deleting it from the report, never weaken the review scope to manufacture a clean verdict, and never let an exhausted loop pass unreported.

### 15d. Status
The ticket stays `🔵 In Development` throughout review and remediation.

## Step 16 — Commit, Push & Raise the `[ENH]` PR — 🤖 FULLY AUTOMATIC

🔴 **A clean review verdict is the ONLY thing that triggers this step.** An exhausted SH-LOOP-5 (15c.7) does NOT reach it — that path HALTS at the gate and waits for the user. The commit, push,
PR creation, labels, tracker update (Step 17) and auto PR review (Step 18) run **automatically with
no prompts**. Announce each action; never ask whether to do it.

1. Verify the active branch is the Enhancement Branch (switch automatically and announce if not). Stage and commit (code + tests + updated docs) with the framework signature trailer, `[N]` read live from CLAUDE.md:
   ```
   git add <files>
   git commit -m "[ENH][TICKET-ID] <concise enhancement summary>" -m "AIRE-Version: [N]"
   ```
   Record the hash in audit.md.
2. Invoke **`pr-generator`** (as-is) **in WORKFLOW mode**, passing **target branch = the Base Branch** from `## Branching`. The PR title carries the **`[ENH]`** prefix; the skill applies the `ai-generated` and `aire-v[N]` labels (plus the `AIRE Framework: v[N]` line in the PR body). 🤖 **Its Phase 5 confirmation is SKIPPED — this workflow has no gates; the Implementation Checkpoint authorized the whole of Phase B.** It announces the draft and raises the PR without asking.
3. Record the PR URL in `## Branching` (`Enhancement PR: <url>`) and the full outcome in audit.md.

## Step 17 — Tracker Update (NO Ready-for-Testing transition)

1. Story Tracker: keep Status = `🔵 In Development`; set **End** = today and **Recorded** = now; note the PR URL.
2. 🔴 **Do NOT transition the tracker ticket to "Ready for Testing"** — the ticket stays In Development after the PR. Promotion is ve's, via `ve-list-work` Option B, run **on `<enhancement-branch>` while the `[ENH]` PR is still OPEN** — never post-merge on the base branch (see Step 19). Add a **comment** on the ticket (**automatic** — part of the prompt-free post-review sequence, same as the bug flow), dispatched per `common/tracker-sync.md` Section 10 (LOCAL: note on the local entry), linking the PR with evidence (tests passing, coverage %, regression clean vs baseline).
3. Log in audit.md (with the TRACKER ITEM field).

## Step 18 — AUTO PR Review

Invoke the **`pr-review`** skill (as-is) in **AUTO MODE** against the just-raised PR: it posts a plain COMMENT review (summary + inline comments) automatically — no prompt, never a formal APPROVE/REQUEST_CHANGES. Record the outcome in audit.md.

## Step 19 — Archive Handoff (MANUAL)

🔴 **RE-READ FIRST.** Before writing any part of this step's output, `Read` this Step 19 section from the file again. Do NOT reconstruct it from memory or from earlier in this session's context — "I already read this file earlier" does not satisfy this.

### The ordering invariant

| # | Action | Relative to the archive |
|---|--------|-------------------------|
| 1 | `ve/...` PR(s) merge into `<enhancement-branch>` | BEFORE |
| 2 | `ve-list-work` Option C amendments pushed to `<enhancement-branch>` | BEFORE |
| 3 | `ve-list-work` Option B sign-off → ticket `🧪 Ready for Testing` | BEFORE |
| 4 | **`archive-epic`** (enhancement mode) | ⬅ **THE ARCHIVE** |
| 5 | **`[ENH]` PR merges into `<base-branch>`** | AFTER |
| 6 | `stitch-delta` on `<base-branch>` | AFTER |

🔴 **`archive-epic` runs at row 4 — BEFORE the `[ENH]` PR merges (row 5).** Its cycle-close commit must ride the still-OPEN `[ENH]` PR; that is the ONLY path by which the RE delta reaches `<base-branch>` for `stitch-delta`.

**TWO DIFFERENT PRs appear here — never write "the PR" unqualified:**
- the **`ve/...` PR** → merges into `<enhancement-branch>`. The archive **waits for this one**.
- the **`[ENH]` PR** → merges into `<base-branch>`. The archive **must precede this one**.

"Wait until all ve work has landed" means rows 1–3 **only** — never row 5.

**🔴 BANNED OUTPUT — each inverts the invariant. Never emit them, in any wording:**
- "archive runs post-merge" / "it runs post-merge only"
- "when the `[ENH]` PR merges, run `archive-epic`"
- "DO NOT invoke `archive-epic` manually now"
- any instruction for the developer to transition the tracker ticket in this step

Do NOT invoke `archive-epic`, do NOT ask whether to invoke it, and do NOT add an options menu or any competing next-steps block. The block below is the entire output of this step.

### Emit this message VERBATIM (placeholders substituted)

The ONLY permitted modification is substituting `<url>`, `<enhancement-branch>`, `<base-branch>`, `[TICKET-ID]`, `<slug>` with real values from `## Branching` / the Step 16 PR. **Never ship an unsubstituted placeholder**; never add, remove, reorder, reword, or summarise a line:

```
✅ Enhancement complete — [ENH] PR: <url> (ticket [TICKET-ID] remains 🔵 In Development).
   📦 The cycle archive was deliberately NOT run — it is yours to run, at step 4️⃣ below.

➡️ NEXT ACTIONS (in this order):
   1️⃣  Wait until the ve `ve/...` PR(s) for [TICKET-ID] have MERGED into `<enhancement-branch>`
       (the ve PR into the enhancement branch — NOT the [ENH] PR into `<base-branch>`)
   2️⃣  On `<enhancement-branch>`: `git checkout <enhancement-branch> && git pull --ff-only`
       (pulls the merged `.spec/aire-docs/tests/<TICKET-ID>-.../` docs in so the archive captures them)
   3️⃣  ve: use the skill ve-list-work — on `<enhancement-branch>`, NOT on `<base-branch>`
       • Option C to amend a test plan (commit + push to `<enhancement-branch>` so the archive captures it)
       • Option B to sign off — promotes ticket [TICKET-ID] 🔵 In Development → 🧪 Ready for Testing
       (Sign-off happens HERE, before the archive — so the tracker still exists and the sign-off
        plus test-plan edits are captured in the archive.)
       🎭 Where the Playwright Test Automation extension is enabled, ve-list-work's own output
          will point you at `/playwright-implement [TICKET-ID]` once manual steps exist — run it here,
          on `<enhancement-branch>`, same as an epic cycle.
   4️⃣  Use the skill archive-epic  (enhancement mode → `aire-archives/enhancements/<TICKET-ID>-<slug>/`)
       🔴 MUST happen while the [ENH] PR is still OPEN — its cycle-close commit rides that
          open PR, which is how the RE delta reaches `<base-branch>`.
   5️⃣  ONLY NOW merge the [ENH] PR into `<base-branch>`: <url>
   6️⃣  Switch to `<base-branch>` and pull the latest
   7️⃣  Use the skill stitch-delta (applies this enhancement's RE delta to the root docs — final action;
       the ONLY base-branch step)

🔴 ORDER IS LOAD-BEARING: archive-epic (4️⃣) runs BEFORE the [ENH] PR merges (5️⃣).
   Merging first breaks stitch-delta and forces a manual recovery PR.
🔴 Use the skill names EXACTLY as shown — do not describe what you want in your own words.
   Any other phrasing is not a framework trigger and the workflow will not advance.
```

---

## Critical Rules
- EVERY audit entry carries `**User Email**:` and `**TRACKER ITEM**:`; Phase B entries also carry `**AIRE VERSION**:` (read live from CLAUDE.md — never hardcoded).
- ONE branch (`enhancement/...`) created FIRST — before requirements; ONE story, NO dependency graph, NO new tracker issues (except LOCAL's locally-minted ID, never pushed externally), NO epic branch, NO Parent-Epic sync.
- NO PR at requirements approval — the single `[ENH]` PR is raised at Step 16 after review approval, target = Base Branch, via `pr-generator` only, `ai-generated` + `aire-v[N]` labels.
- The **ve Handoff Break** runs BEFORE the Implementation Gate question: ALWAYS commit + push the analysis/design artifacts on the enhancement branch first (the ve's `/ve-implement` needs them on origin) and present the ve instructions. The ve's run is independent of the yes/no answer and of the code existing at all.
- The Implementation Gate is a **yes/no question in the same flow** — never auto-continue into Phase B without the user's explicit "yes"; on "no", halt with state saved. It is **deliberately unnumbered** (flow control, not an approval gate) — and it is now the ONLY question this workflow asks.
- 🔴 **NO GATES AT ALL** — the implementation plan is announced and executed (no GATE 2), and the review verdict routes the run automatically (no GATE 3). Never present a plan-approval or Approve-&-continue/Remediate prompt, and never write "GATE" into an audit heading from this workflow. The Implementation Checkpoint (yes/no) survives as unnumbered flow control.
- 🔴 **THE FRAMEWORK FIXES ITS OWN FINDINGS, WITHIN A BOUNDED BUDGET** — any 🔴/🟠 finding triggers the auto-remediate loop (15c, **SH-LOOP-5**): remediate → regression → re-review, looping until the verdict is clean **or the 3-attempt budget is exhausted**. On exhaustion (3 rounds, or an SH-5 stall — no code change + identical findings) the run **HALTS at the gate**: no commit, no push, no `[ENH]` PR, no tracker change; the Retry-Limit Report is emitted to the user and to audit.md, and the run waits for user direction.
- 🔴 Mid-coding plan deviations are applied only after the plan document is revised and the change announced + logged — never silently, and never via an approval prompt.
- At Step 9, ALWAYS assign the ticket to the operator per `common/tracker-sync.md` Section 5 (automatic, verified where applicable, logged; failure non-blocking). LOCAL has no assignee concept.
- ALWAYS run the BASELINE regression BEFORE any change and the FULL regression AFTER; only NEW failures (vs baseline) block; log both runs in `enhancement-<TICKET-ID>-summary.md`.
- 🔴 ALWAYS BOOTSTRAP missing tool configs BEFORE the baseline static run (Step 10, `common/eval-framework.md` Section 2.2) — a check with no config is **set up**, not marked N/A; an existing config is used **as-is**. Bootstrap → baseline → implement → gate → diff: a config created after the baseline blames this change for pre-existing findings. Announce every file created.
- 🔴 ALWAYS run the BASELINE static eval checks D1–D7 before any change (Step 10) and the STATIC EVAL GATE after the regression gate (Step 14.5); only findings NEW vs baseline on changed files block, and this change resolves them in the same run. **NEVER suppress a finding to pass the gate** — that is the analogue of deleting a failing test. Baseline findings are pre-existing debt: logged, ignored. See `common/eval-framework.md`.
- 🔴 The J1/J2 judge scores are computed ONCE in Step 15a and are **output only** — never a gate, never a review finding, never fed to remediation, never re-scored, never in the `verdict`. J1 = `N/A` is a normal outcome when the design stages were skipped and no rubric is derivable.
- 🔴 The 15c auto-remediate loop (**SH-LOOP-5**) is **capped at 3 rounds** by the Self-Healing Retry Policy and is otherwise **unchanged by the eval layer** — it receives no eval input and gains no other stop condition. The J1/J2 judge scores never enter it.
- Plan grounded in the previously generated docs; coding follows the announced plan exactly — deviations revised into the plan, announced and logged, never silent. Coverage on new/changed code ≥90%.
- 🔴 **API & Contract Testing Gate (Step 13.5) is MANDATORY WHEN the enhancement touches an API endpoint** — applicability is plan-derived and automatic, never asked. Generate automated tests against the real endpoint(s), RUN them, and iterate until every applicable checklist item (functional, response-code validation, role-based authorization 401/403, error-response validation, request validation, response contract/schema validation) passes, in the SAME run, BEFORE the Full Regression Gate (Step 14). This is **SH-LOOP-2**, capped at **3 remediation attempts**; on exhaustion apply SH-4 (HALT + Retry-Limit Report). N/A (with a stated reason) when the enhancement touches no API layer. Capture proof artifacts to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-1.1/`. This gate does NOT replace ve's `/ve-implement` MANUAL API/Contract test steps.
- The ticket stays `🔵 In Development` after the PR — promotion to Ready for Testing is ve's, via `ve-list-work` Option B run **on the enhancement branch, before `archive-epic` and before the `[ENH]` PR merges** (not post-merge on the base branch — after the archive's workspace reset there is no Story Tracker left to promote).
- **NEVER run Build & Test in this workflow.** Test Plan is not a Implementation step at any level — it belongs to ve and is run separately, per ticket, via the **`/ve-implement`** skill (black-box, from the ticket's acceptance criteria, into `.spec/aire-docs/tests/<TICKET-ID>-<title>/`). Do not load `implementation/test-plan.md` here and do not write anything under `.spec/aire-docs/implementation/build-and-test/`.
- 🔴 After the PR: AUTO `pr-review` (comment-only), then **STOP — the archive is MANUAL**. NEVER invoke `archive-epic` from this workflow. **Re-read Step 19 before emitting its handoff, and emit that block VERBATIM with placeholders substituted** — do not paraphrase it. The operator runs `archive-epic` once the ve `ve/...` PR(s) (and any `ve-list-work` Option C amendments) have merged **into the enhancement branch**, and **BEFORE the `[ENH]` PR merges into the base branch**, so the delta rides the open PR for post-merge `stitch-delta`. Never tell the user the archive runs post-merge — that inverts the invariant.
- Security Baseline extension always applies; other extensions per their recorded opt-ins.
