# 🔑 WORKFLOW: `dev-implement` (Implementation Phase — Code Generation)

## 🤖 THIS WORKFLOW IS FULLY AUTOMATIC — IT ASKS NOTHING AFTER THE STORY KEY

**Typing `dev-implement` and naming the story is the ONLY user decision in the entire run.**
Everything after it — the implementation plan, code generation, the unit-test/coverage gate, the
API & Contract Testing gate (when the story touches an API layer), the regression gates, the
automated Code Review, **the remediation of any findings it reports**, the
commit, the push, the PR and the PR review — happens **without a single approval prompt**.

- ❌ There is **NO GATE 2** (plan approval). The plan is written, announced, and executed.
- ❌ There is **NO GATE 3** (review decision). A review with findings is **remediated automatically**,
  then re-reviewed, **looping until the review comes back clean** — the user is never asked to choose
  between "Approve & continue" and "Remediate".
- 🔴 **Never write the word "GATE" into an audit heading from this workflow.** Plan and review
  outcomes are logged as auto-approved decisions, not gated ones.
- The machine checkpoints that DO still stop the run are **not** approvals and remain fully in force:
  the **Doability Gate** and the **Story Branch dependency-merge check**. The Doability Gate **never
  merges a prerequisite's PR itself, not even one a human has already approved** — merging is always
  a manual action the user performs outside this workflow. It simply stops — naming the reason — for
  any prerequisite that isn't merged yet, whether it's unapproved, draft, conflicted, blocked by
  required checks, or already approved and just waiting on the user to merge it.
- A user who volunteers a correction at any point (plan, code, review finding) is an **interrupt** —
  apply it and continue. Never convert it into a standing gate.
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
| **SH-LOOP-7** | Behavioural B1 + B2 (Gherkin) | Step 6.1 | This unit's scenarios pass with every AC tag executed, AND every other feature file in the repo stays green |
| **SH-LOOP-8** | Behavioural B3 (epic scope) | Step 6.1 | On the LAST work unit only: the whole cycle suite + the `.spec/behavior.feature` cross-unit journeys pass |
| **SH-LOOP-2** | API & Contract Testing | Step 6.2 | Every applicable checklist item passes on every touched endpoint |
| **SH-LOOP-3** | Full Regression | Step 6.5 | Zero NEW failures versus `baseline-regression.log` |
| **SH-LOOP-4** | Static Eval D1–D7 | Step 6.6 | Zero NEW findings above the `.evals/config.json` thresholds on changed files |
| **SH-LOOP-6** | Judge Gates J1 + J2 | Section A Step 2.5 | `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin` (`N/A` passes) |
| **SH-LOOP-5** | Auto-Remediate (code review + security findings) | Section C | Review verdict clean — zero 🔴 and zero 🟠 |

**SH-1 — Attempt budget.** Each loop is allowed a **maximum of 3 remediation attempts**. One attempt
is one complete `fix → re-verify` cycle. The initial verification run that first detects the failure
is **not** an attempt (it is attempt 0). Attempts are numbered 1, 2, 3.

**SH-2 — Counters are per-loop, independent, and never silently reset.** Maintain a separate counter
per SH-LOOP ID. A counter is never shared between loops, never reset by another loop's success, and
never reset by advancing to a later gate. When a later loop's remediation forces re-entry into an
earlier loop (for example Section C re-running the Step 6.5 regression diff), that re-entry **continues the earlier loop's existing
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
   external tracker. The story stays `🔵 In Development` on its story branch. The attempted fixes stay in the working tree for inspection.
3. Emit the **Retry-Limit Report** below as the run's final output.
4. Append the same content to `audit.md` under the heading
   `## Self-Healing Retry Limit Reached — [SH-LOOP-ID] (Story N.M)`, carrying the standard
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
   Work unit: Story [N.M] — [story title]
   Branch:    [story branch]

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
   C) 🙋 Take it over manually — fix it in the working tree, then re-invoke `dev-implement` for
      this work unit to resume from this gate.
   D) 🗂️ Raise a defect and stop — log the blocker via `/raise-defect` and leave the work unit
      `🔵 In Development` for a later session.

[Answer]:
```

🔴 **Log the user's raw response in `audit.md`** under
`## Self-Healing Retry Limit — User Direction ([SH-LOOP-ID])`. A new budget is granted for the named
loop ONLY, and ONLY under option A or B; every other loop keeps the counter it already held.

---

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone (the user just types `dev-implement`, possibly in a fresh session). Before doing anything else, resolve the rule details directory (check  `.aire-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- The REQ-ID thread rules from `common/requirements-traceability.md` (plan-level trace + fallback coverage verification)
- The eval rules from `common/eval-framework.md` (the Static Eval Gate D1–D7 at Step 1.5 Item 4.6 + Step 6.6, and the J1/J2 judge scores inside Section A)
- The branching model from `common/branching-strategy.md` (epic branch → story branches)
- Story selection steps from `implementation/story-selection.md`
- The detailed code generation steps from `implementation/code-generation.md`. 🔴 **Follow the Guardrail defined there (Generation Phase Rules)** for any generated code.
- The reviewer steps from `workflows/code-review.md` (auto-run after code generation) and the fixer steps from `workflows/remediate.md` (on the Remediate path)

🔴 **GUARDRAIL — `code-review` and `remediate` are WORKFLOW RULE FILES, NOT Claude skills.** Whenever this workflow "runs Code Review" or "runs Remediate", you MUST `Read` and follow `workflows/code-review.md` / `workflows/remediate.md` (which pull their detailed steps from `implementation/code-review.md` / `implementation/remediate.md`) as instructions. There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, invoked as-is).

This workflow also uses the **`pr-generator`** Claude skill (`.claude/skills/pr-generator/`) to push the branch and raise the PR — always pass it the **target branch** explicitly (story PRs target the **Epic Branch** from `aire-state.md` `## Branching`). Passing a target means it runs in **workflow mode**, where its Phase 5 confirmation is **skipped** and the push + PR happen **automatically** (the user's `dev-implement` invocation is the authorization). **NEVER edit that skill — invoke it as-is.**

After the PR is raised (the story STAYS `🔵 In Development` — it is promoted to `🧪 Ready for Testing` only when the PR MERGES), this workflow also auto-invokes the **`pr-review`** Claude skill (`.claude/skills/pr-review/`) against that same PR in its **AUTO MODE** — it posts a plain COMMENT review (summary + inline comments) automatically, with no user prompt and no formal GitHub approve/request-changes. **NEVER edit that skill — invoke it as-is.**

This workflow does **NOT** itself flip any story's tracker status to `🧪 Ready for Testing` — that promotion is performed ONLY by the **`ve-list-work`** skill (`.claude/skills/ve-list-work/`), which ve runs separately on the epic branch after it has tested the merged stories. Instead, when the user picks a story that `requires` another story, the **Doability Gate** (`implementation/story-selection.md` Step 4) checks that specific prerequisite's PR merge state LIVE, right there — if it's already merged the pick proceeds; **if it is not merged for any reason — including an already-approved PR just waiting to be merged — the gate blocks with a clear message and the run stops.** The gate never merges anything itself. See Step 1.5 below.

All paths below are relative to the resolved rule details directory.

---

## MANDATORY: Audit Entry Format for this Workflow — TRACKER ITEM on EVERY entry

**EVERY audit.md entry written during a `dev-implement` run — from Story Selection, through the Story Branch checkpoint, code-generation planning, code generation done, Unit Test & Coverage, automated Code Review, Remediate, and Approve/PR — MUST include the `**User Email**:`, `**TRACKER ITEM**:`, `**Epic Link**:` and `**AIRE VERSION**:` fields.** No dev-implement audit entry may omit them.

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context]
**User Input**: "[Complete raw user input - never summarized]"
**TRACKER ITEM**: "[Complete tracker item (Jira ticket / ADO work item / GitHub issue / local Story ID) that was implemented]"
**Epic Link**: "[Full Parent Epic URL as a clickable link, from ## Tracker in aire-state.md — or "none"]"
**AIRE VERSION**: "[Framework version [N] read from the "AIRE Framework Version" line in CLAUDE.md — do not hardcode]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

- **AIRE VERSION**: read at runtime from the canonical "AIRE Framework Version" line in `CLAUDE.md` — this records which framework version the work unit was developed with. Never omit it and never hardcode a literal version.
- **Epic Link**: the FULL Parent Epic URL read from `## Tracker` in `.spec/aire-docs/aire-state.md` (Epic URL line), written as a clickable Markdown link `[EPIC-ID](<site-base-url>/browse/EPIC-ID)` for JIRA/ADO/GITHUB. If `## Tracker` records `Parent Epic: none` (or `Type: LOCAL` with no Epic), write `none` — the field itself is never dropped.
- For a tracker-linked story, write the item as a clickable Markdown link (`[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)` for JIRA, the work-item/issue URL for ADO/GITHUB) — never bare text.
- For local-only stories (`Tracker ID = —`/`LOCAL`), put the local Story ID (e.g., `Story 1.2 (local — no external tracker)`) in the same field — the field itself is never dropped.
- This applies to every step's entries: selection prompt/response, automatic In-Development transition, branch creation (or Case B stop), plan approval, per-step generation logs, coverage evidence, review outcome, remediate outcome, and the commit/push/PR result.

---

## Step 1 — Keyword Behavior (on invocation)

1. **Read `## Branching`** from `.spec/aire-docs/aire-state.md` (Base Branch + Epic Branch). If missing, run `common/branching-strategy.md` Section 1 now (create the epic branch) before proceeding.
1.5. **🔗 No bulk STATUS reconciliation here (by design)**: dev-implement does NOT promote any story's **status** at the start of a run — it never moves a story to `🧪 Ready for Testing` in the Story Tracker or the external tracker, for any story, ever (that is `ve-list-work`'s job alone). It DOES sweep and merge approved PRs (Step 1.6) and record the resulting **factual** `Merged`/`Recorded` columns — merging is not promoting. Dependency readiness is then verified **live, per prerequisite**, inside the **Doability Gate** (Step 2 below → `implementation/story-selection.md` Step 4) at the moment a story with `requires` is picked:
   - Each prerequisite's PR is checked directly (`gh pr view <PR> --json state,mergedAt,baseRefName,isDraft,reviewDecision,mergeable,mergeStateStatus,author,reviews`) unless its Story Tracker `Status` already reads `🧪 Ready for Testing`.
   - **Merged (or already `🧪 Ready for Testing`)** → that prerequisite is doable; proceed.
   - **Anything else — OPEN (approved or not), draft, conflicted, blocked by checks, CLOSED (not merged), or no PR yet** → 🛑 the Doability Gate BLOCKS with a clear message naming the unmerged prerequisite and its PR, and the run STOPS — no story/tracker status is changed by dev-implement itself. 🔴 **`dev-implement` never merges the prerequisite's PR itself, not even an already-approved one** — merging is always the user's own manual action; when the PR is already approved the stop message says so, so the user knows merging it is all that's left.
   The Story Tracker/tracker **status** is moved to `🧪 Ready for Testing` only when ve runs the **`ve-list-work`** skill on the epic branch — it lists the stories whose PRs have merged and promotes the ones ve confirms it has finished testing.
1.75. **⚠️ Sequential-development banner (MANDATORY — show on EVERY invocation, before Story Selection)**: display this note to the user verbatim, then continue:
   ```
   ⚠️ Note: stories are NOT to be developed in parallel in this session — dev-implement builds ONE story at a time, sequentially (each story branch is cut from the epic branch).
   To develop stories in parallel, open a NEW folder/clone of this same repo, check the Dependency Graph, and run dev-implement there on an INDEPENDENT story.
   ```
2. **Story Selection + Doability Gate**: execute `implementation/story-selection.md` in full — it asks which story (Story ID / number, title, or Tracker ID), reads it from the local Story Tracker / `stories.md` (or resolves the Tracker ID), runs the Doability Gate (**which only ever reads PR state — it never merges a prerequisite's PR itself, not even an already-approved one**), and moves the story from `🟢 Ready for Development` to `🔵 In Development` **automatically** (picking the story is the claim — the tracker and the Story Tracker are both updated without asking, the transition verified for non-LOCAL, and the issue is **assigned to the operator who invoked `dev-implement`** per `common/tracker-sync.md` Section 5, verified, non-blocking on failure). Do NOT re-implement the prompt or the gate here.
3. **🌿 Story Branch checkpoint (MANDATORY — immediately after story selection)**: In the SAME interaction where the story is chosen, create the story branch per **Step 1.5** below. Do NOT begin Code Generation until the story branch is created and active.
4. Only once the Doability Gate passes **and** the story branch is active **and** the BASELINE regression has been captured (Step 1.5 Item 4.5), proceed with **Code Generation** (Part 1 Planning → Part 2 Generation → unit tests to `unitTestCoverageMin` coverage → FULL regression vs baseline).

---

## Step 1.5 — 🌿 Story Branch checkpoint (MANDATORY)

Runs **after** Story Selection resolves the story (Doability Gate passed, story marked `🔵 In Development`) and **before** Code Generation Part 1. Execute **`common/branching-strategy.md` Section 3 — Story Branch Creation** in full. Summary (the strategy file is authoritative):

1. **Log the prompt** in `.spec/aire-docs/audit.md` (ISO 8601 timestamp) before asking anything.
2. Derive the branch name automatically — `story/<N.M>-<kebab-case-story-title>` (Tracker ID prefixed when present and non-LOCAL) — and **create it without asking**. 🤖 **No confirmation, no override prompt**: the name is fully determined by the story ID + title. Announce it (`🌿 Story branch: <name> (cut from <epic-branch>)`). On a name collision, append a short disambiguating suffix automatically and announce that too.
3. **Refresh the epic branch** (`git fetch origin && git checkout <epic-branch> && git pull --ff-only`), then run the **dependency-merge check** on the story's `requires`:
   - All prerequisites merged into the epic branch (or none) → cut the story branch **from the epic branch** (NEVER from main/the base branch).
   - Any prerequisite NOT merged → 🛑 **WARN AND STOP** with the Case B message from branching-strategy.md Section 3: tell the user to merge the prerequisite's PR into the epic branch first, do NOT create a story branch (there is no alternative base), revert the story to `🟢 Ready for Development` (tracker + external tracker, verified), log in audit.md, and END this `dev-implement` run — the user re-invokes it after merging.
4. **Record in audit.md**: the story branch name, the base it was cut from, and the user's raw responses.
4.5. **🧪 BASELINE Regression Run (MANDATORY, AUTOMATIC — BEFORE any code is generated)**: on the freshly cut story branch, run the **ENTIRE repo test suite** (not just this story's area) and save the raw runner output to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/baseline-regression.log`. Record the pass/fail counts and the full list of failing tests in audit.md. This is the reference point the post-implementation regression gate is diffed against. **No user prompt — capture it and continue.**
   - Any failures here were already present on the epic branch (introduced by a PREVIOUSLY MERGED story, not this one). **Logging them in `baseline-regression.log` is all that is required — do not try to fix them, and do not block on them.** They exist only to define what "already broken" means, so the post-implementation gate can tell this story's breakage apart from everyone else's.
   - If the repo has no test suite at all, record that explicitly in audit.md — the post-implementation gate then covers only this story's new tests.
4.6. **🔎 BASELINE STATIC EVAL RUN (MANDATORY, AUTOMATIC — same moment, BEFORE any code is generated)**: on the same freshly cut story branch, run the **Static Eval Gate checks D1–D7** per `common/eval-framework.md` Section 2 (lint, type check, SAST, dependency vulnerabilities, licences, complexity, secrets) and save the raw output to `.spec/aire-docs/implementation/code/eval-evidence/story-[N.M]/static/baseline/`. **No user prompt — capture it and continue.**
   - Exactly like the baseline regression: **every finding here is pre-existing debt on the epic branch, NOT this story's.** Record it and move on — do NOT fix it and do NOT block on it. It exists only to define "already broken" so Step 6.6 can tell this story's findings apart.
   - **🔧 BOOTSTRAP FIRST (eval-framework.md Section 2.3, MANDATORY — same step, immediately BEFORE the baseline run)**: for every check with **no config in the repo**, create the minimal *recommended* config (eslint/ruff/golangci, tsconfig/mypy, `.gitleaks.toml`, the linter's complexity rule at the `.evals/config.json` threshold) so the check is actually runnable. **A check whose config exists is used AS-IS** — the repo's own standards win, never overridden or "upgraded". Announce every file created and log it in audit.md (`bootstrap` block of `eval.json`) — it adds files to the user's repo, so it is never silent; those files commit with this story. 🔴 **AND INSTALL THE TOOLS — retried, never skipped (Section 2.4.1)**: for every gate, work the chain *already present → package manager → alternative installer → **OCI image via Podman***, 3 attempts per rung, verifying each install with a version command. Recording a gate `N/A` for a missing tool **before the Podman rung has been tried** is a bootstrap failure, not an `N/A`. If the whole chain is exhausted, **HALT with the per-rung report** — never continue with an unmeasured gate, and never phrase deferred setup as `N/A` ("not wired yet", "not installed", "not enabled yet" — all ERROR, Section 2.5.2).
     - 🔴 **ORDER MATTERS**: bootstrap → baseline → generate code → Step 6.6 → diff. A config created AFTER the baseline would make the baseline and the post-change run measure under **different rules**, so every finding it surfaces on pre-existing code would be blamed on this story. Never bootstrap later than this point.
     - 🔴 Recommended presets, never strict/all, and **never a config that pre-suppresses findings** (no seeded rule-offs, no source-tree excludes) — bootstrap makes the check runnable, never makes it pass.
   - 🔴 A check is recorded `N/A` **only after the full Section 2.4.1 install chain — including the Podman image rung — has been attempted and recorded**, and only for a reason on the Section 2.5.1 closed list (inapplicable to this stack / to this work unit / no such tool exists). If the chain is exhausted, that is an **ERROR: HALT** with the per-rung report — never `N/A`, never silently skipped, and never phrased as deferred work ("not wired yet", "not installed", "not enabled yet").
5. Carry the story branch forward — it is the target branch for the commit/push/PR step after review. **Do NOT proceed to Code Generation until the branch is created and confirmed active** (`git branch --show-current` matches).

> **Multiple developers**: Each dev independently runs `dev-implement` and selects a different ready story. The Dependency Graph (`requires` on each story) plus the Doability Gate ensure no two devs pick stories with unresolved dependencies.

> **Design context**: The system-level design artifacts (functional/NFR/infrastructure) live under `.spec/aire-docs/implementation/design/` and apply to every story. Code for the story is written into the application structure defined in Application Design (or code-generation.md's structure rules).

---

# Code Generation (per-story)

**Runs once per story selected via `dev-implement`.**

**Two parts, preceded by Story Selection + Story Branch checkpoint:**
1. **Part 1 - Planning**: Create a detailed code-generation plan (implement layers, then the mandatory Unit Test & Coverage step).
2. **Part 2 - Generation**: Execute the approved plan to generate code and artifacts, then generate + run unit tests until coverage is ≥90% (same run).

**Execution**:
1. **MANDATORY**: Log any user input during this stage in audit.md.
2. Load all steps from `implementation/code-generation.md`.
3. **STEP 0 — Story Selection (MANDATORY)**: Execute `implementation/story-selection.md` in full — it is dependency-aware and self-contained. It asks which story (ID / number, title, or Tracker ID), shows the currently ready stories, runs the **Doability Gate** (proceed only if every `requires` is confirmed MERGED — already `🧪 Ready for Testing`, or live-verified via `gh pr view`; else 🛑 STOP the run with a clear message naming the unmerged prerequisite — the gate never merges it itself, even if already approved), and — **automatically, no confirmation** — moves the chosen story from `🟢 Ready for Development` to `🔵 In Development` in the Story Tracker + configured tracker (transition verified for non-LOCAL, announced), **assigns the issue to the operator who typed `dev-implement`** per `common/tracker-sync.md` Section 5 (session email → account lookup, verified, non-blocking on failure), setting `Start`/`Recorded`. If the story is already `🔵 In Development`, warn that it may be claimed by another dev. Do NOT re-implement the selection prompt or gate logic here.
3.5. **STEP 0.5 — Story Branch checkpoint (MANDATORY)**: Execute **Step 1.5** — create the story branch from the epic branch (dependency-merge check; on any unmerged prerequisite, warn and STOP per Case B — merge first) and record it in audit.md. This branch is the target for the commit/push/PR step after review. Do NOT start Part 1 until the branch is active.
4. **PART 1 - Planning**: Create the code-generation plan with checkboxes — implementation steps per layer, ending with the mandatory **Unit Test & Coverage** step. **📐 GROUND THE PLAN in the previously generated docs**: every plan step MUST trace back to the story's acceptance criteria, `epic-brief.md`, `requirements.md`, and the design artifacts under `.spec/aire-docs/implementation/design/` + Application Design — never invent scope, files, or behavior not backed by those documents. **🎨 DESIGN REFERENCE GROUNDING (`common/design-reference-grounding.md` Rule DR-5 — automatic, adds NO question and NO gate)**: execute `code-generation.md` **Step 1.5** silently — read the `### Reconciliations` table first (**DR-8**: points already decided against a reference by an earlier design stage are settled — follow the framework's design docs there and never reintroduce an excluded capability), then re-open every registered design reference in `aire-state.md`'s `## Design References` that covers a component this story builds (a fresh read for THIS story's scope; "read in an earlier stage" does NOT count) and ground only the **unreconciled** points, and state per component either `Design reference: <path> — grounded (...)` or `Design reference: none covers this component`. On an unreconciled prototype/AC mismatch, apply **DR-6**: follow the design, say plainly in the plan what differed, amend the AC to stay truthful, record the reconciliation, and continue — it is stated plainly in the announced plan and in audit.md; do NOT halt or ask. **🧾 REQ-ID THREAD (`common/requirements-traceability.md` Rule 5)**: resolve the story's `Covers` REQ-IDs and read their text in `requirements.md` (the requirement, not just the AC restatement, is planning input), tag every plan step with the REQ-ID(s)/AC(s) it implements, and pass the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step — blocking, fixed silently) BEFORE announcing the plan. Then **announce the plan and execute it immediately — 🤖 there is NO approval gate.** Log it in audit.md under a plain heading (e.g. `## Code Generation Part 1 — Plan Finalized (auto-approved, no gate)`) with the plan path, the step count and the REQ/AC trace summary, per `code-generation.md` Step 8. Never ask "Approve this plan?" and never write "GATE" into the heading.
4.5. **🥒 WRITE THE STORY'S BEHAVIOUR SPEC (MANDATORY — before any code)**: write `.spec/aire-docs/implementation/code/behavior/story-[N.M].feature` per `common/behavior-spec.md` Section 2 — one Gherkin scenario per acceptance criterion, `@AC-n` tagged, failure paths included. It is authored **BEFORE** the implementation because it is the contract, not a description of what was built. 🔴 **That is the ONLY spec file this story gets.** No per-story requirements, architecture, constraints or knowledge-graph document — the agent reads the tracker item + `stories.md` for ACs, `requirements.md` for the `Covers` REQ-IDs, `.spec/architecture.md` for design constraints, and `.evals/config.json` for thresholds. Copying any of that per story only creates something that can drift. Announce the file path and the scenario/AC counts; log both in audit.md.
5. **PART 2 - Generation**: Execute the announced plan for this story, writing **all application code into `src/`** (or the recorded `## Code Root` for a brownfield repo — `common/directory-structure.md`), test code into `tests/`, and nothing into `.spec/`. **🛡️ PLAN FIDELITY**: implement EXACTLY the plan — no unplanned files, features, refactors, or scope drift; keep the generated code consistent with the design docs the plan was grounded in. If mid-coding you discover the plan must change, **revise the plan document, announce the revision (what changed and why) in your output and in audit.md, and continue** — do not ask for approval, and never apply a deviation without recording it.
6. **UNIT TEST & COVERAGE GATE (threshold from `.evals/config.json`) — MANDATORY, same run**: After the story's implementation is complete, execute the Unit Test & Coverage step defined in `code-generation.md` (Step 11a): generate unit tests for all new/changed code, RUN them, measure coverage, and if coverage is below `unitTestCoverageMin` add/adjust tests (and fix any defects the tests expose) within the SAME run until ≥90% is reached. 🔁 **This is SH-LOOP-1 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT, emit the Retry-Limit Report, and do NOT proceed below the threshold.** While the story is still `🔵 In Development`, **capture the PROOF artifacts of this run** to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/` — the raw runner output (`unit-test-run.log`), the coverage tool's **mandatory machine-readable report** (`coverage-report.*` — lcov/xml/json/HTML, produced by running the tool with the report-emitting flags such as `--cov-report=xml` / `--coverageReporters=lcov`; a terminal summary alone does NOT satisfy the gate), and an `evidence-manifest.md` (command run, tests X/X, measured coverage %, artifact links). These stored artifacts — not a hand-written claim — are the evidence carried into Code Review and the PR/tracker comment; every figure reported downstream MUST match them.
6.1. **🥒 BEHAVIOURAL TEST GATE — GHERKIN, THREE TIERS (MANDATORY, AUTOMATIC — after the Unit Test & Coverage gate, same run)**: execute the tiered behavioural gate defined in `common/behavior-spec.md` Section 4.4. Implement the step definitions in `tests/behavior/steps/` bound to the application's **public surface** (endpoint / service method / CLI) — never to internals — then run the tiers **in order**:

1. **B1 — Unit scope**: this work unit's own `.spec/aire-docs/implementation/code/behavior/story-[N.M].feature`. **Verification**: every scenario passes AND every `@AC-n` tag is executed.
2. **B2 — Cumulative scope**: every **other** feature file already in the repo — earlier work units in this cycle plus everything from prior cycles. **Verification**: all green. 🔴 A B2 failure is THIS unit's problem — it turned that scenario red, so it fixes it. "That scenario belongs to another story" is not a defence.
3. **B3 — Epic scope** (🔴 **last work unit of the cycle ONLY**): B1 ∪ B2 **plus** the cross-unit journeys in `.spec/behavior.feature`, tagged `@REQ-<id>`. 🔴 Detect "last" from **PR MERGE STATE, never the tracker status label** (`common/behavior-spec.md` Section 6.1): for every OTHER work unit read its PR from the Story Tracker and verify live with `gh pr view <n> --json state`. **All others merged → this is the last unit → RUN B3** — including the normal case where those units are still `🔵 In Development` awaiting ve sign-off, because the label lags the merge. Defer ONLY when a unit has no merged PR, recording `B3: N/A — deferred, <n> units with unmerged PRs (<list with PR state>)`. 🔴 Never defer on a status label alone, and never report a deferred B3 as a pass.

**Execution** — 🔴 **every tier runs in a Podman pod** (`common/behavior-spec.md` Section 5): the image built from `.evals/behavior/Containerfile`, plus a fresh ephemeral **test database** where the repo needs one, invoked through `.evals/behavior/run.sh <tier>` — the same image and command a developer runs locally, so a CI-only failure is impossible by construction. 🔴 **The ONLY permitted native run is Podman not being installed** (proven by `command -v podman`), recorded as `"containerised": false, "reason": "podman not installed"`. 🔴 "No browser needed", "backend only", "no new dependency" and "faster natively" are **forbidden justifications** — a tier recorded that way is a gate violation, not a pass. Never fall back to the Docker CLI. A tier runs only once the previous is green.

**Evidence** — per tier, to `.spec/aire-docs/implementation/code/behavior-test-evidence/story-[N.M]/<b1|b2|b3>/`: `behavior-test-run.log`, the **mandatory machine-readable** `behavior-test-report.*`, and an `evidence-manifest.md` recording the image ref + digest, the exact command, whether it ran containerised, the tier's feature-file set, and every scenario with its tag and result. A raw log alone does NOT satisfy the gate.

**Self-healing** — 🔁 **B1/B2 failures → SH-LOOP-7; B3 failures → SH-LOOP-8, its own separate 3-attempt budget** (an epic-scope failure is usually an integration gap between units, not a bug inside one, so arriving at the epic gate with the story budget already spent must not halt the cycle). Both capped at 3 attempts; on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report.

🔴 **Fix the code, never the scenario.** A scenario changes only when the AC or requirement it encodes genuinely changed — and then the AC, `requirements.md` and the tracker item are amended together and the reconciliation is logged. Deleting, skipping or `@ignore`-ing a scenario to go green is forbidden (SH-6).

**N/A** — B1 is N/A only for a work unit with no externally observable behaviour (pure build-config or docs change); a unit with acceptance criteria is never N/A. B2 is N/A only when the repo genuinely contains no other feature file. Record the reason explicitly.

6.2. **🔌 API & CONTRACT TESTING GATE (MANDATORY WHEN APPLICABLE — same run)**: **Applicability is plan-derived and automatic — never asked**: if this story's code-generation plan includes an API Layer Generation step (a new/changed endpoint), execute the **API & Contract Testing Gate** defined in `code-generation.md` (Step 11a.5) — generate automated tests against the actual endpoint(s) covering: functional/happy path, response-code validation, role-based authorization (401 unauthenticated vs 403 insufficient role), error-response validation (standard format + codes), request validation (required fields, data types, enums), and response contract/schema validation. RUN them and iterate within the SAME run until every applicable checklist item passes. 🔁 **This is SH-LOOP-2 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.** Within that budget the gate is never deferred to ve or to a later session. Capture PROOF artifacts to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/` (`api-contract-test-run.log`, the **mandatory machine-readable** `api-contract-test-report.*` — invoke the runner with its report-emitting flag/plugin, e.g. `pytest --junitxml=...` / `jest --json --outputFile=...`; a raw log alone does NOT satisfy the gate unless the runner genuinely has no such capability (documented, surfaced exception) — and `evidence-manifest.md` with the per-endpoint checklist). **If the story's plan has NO API Layer Generation step, this gate is N/A** — record that explicitly (with reason) and proceed straight to 6.5. This gate is separate from and does not replace ve's `/ve-implement` MANUAL API/Contract test steps.
6.5. **🧪 FULL REGRESSION GATE (MANDATORY, AUTOMATIC — after the Unit Test & Coverage gate and the API & Contract Testing Gate when applicable, same run)**: re-run the **ENTIRE repo test suite** (all pre-existing tests + this story's new tests, including any new API & Contract tests from Step 6.2), save the raw output to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/full-regression.log`, and diff it against `baseline-regression.log` from Step 1.5 Item 4.5. **No user prompt — fix and continue.**
   - **NEW failures (green at baseline, red now)** → **this story broke them, so this story fixes them.** Fix them within THIS SAME run, then re-run and re-diff, iterating until the diff is clean. 🔁 **This is SH-LOOP-3 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.** Within that budget, never hand a new failure back to the user. Fix each according to what actually broke, and a failing test is NEVER "fixed" by deleting or skipping it to make the suite green:
     - **Obsolete expectation** — behaviour legitimately changed, the assertion encodes the old contract → **update the assertion** (keep the test; it still guards real behaviour)
     - **Genuinely dead** — exercises a code path this story removed → **delete it** and confirm this story's new tests cover the replacement path
     - **Real regression** — the test is correct and the implementation broke it → **fix the implementation, never the test**
   - **Failures already red at baseline** → not this story's doing. Already logged in `baseline-regression.log`; ignore them and do not block on them.
   - Proceed to Code Review only once the diff is clean (zero NEW failures).
   - Record in `evidence-manifest.md`: baseline vs post-change pass/fail counts, and each NEW failure with what broke and how it was fixed. **Audit the diff in audit.md.**
6.6. **🔎 STATIC EVAL GATE — D1–D7 (MANDATORY, AUTOMATIC — after the Full Regression Gate, before Code Review)**: re-run the D1–D7 checks per `common/eval-framework.md` Section 2, save to `.spec/aire-docs/implementation/code/eval-evidence/story-[N.M]/static/`, and **diff against the Step 1.5 Item 4.6 baseline**. Only findings that are **NEW versus the baseline, on files this story changed**, count. **No user prompt — fix and continue.**
   - **NEW findings above the `.evals/config.json` thresholds** → **this story introduced them, so this story fixes them** in THIS SAME run, then re-run and re-diff, iterating until the diff is clean. 🔁 **This is SH-LOOP-4 — capped at 3 remediation attempts (SH-1). On exhaustion apply SH-4: HALT and emit the Retry-Limit Report.** Within that budget, never handed back to the user.
   - 🔴 **NEVER suppress a finding to pass the gate** — no blanket `eslint-disable`, no `# nosec`, no `# type: ignore`, no ignore-list entry, no widening the disallowed-licence list. That is the exact analogue of deleting a failing test to go green and is equally forbidden. Fix the code.
   - **Findings already present at baseline** → not this story's doing. Already logged under `static/baseline/`; ignore them and do not block on them.
   - Write `eval.json` + `eval-summary.md` (eval-framework.md Section 6) and **proceed to Code Review only once the diff is clean**. Audit the gate outcome in audit.md.
7. **POST-IMPLEMENTATION — status stays `🔵 In Development` until the PR is MERGED**: Do NOT change the tracker status here, and do NOT prompt for a board status. The story **remains `🔵 In Development`** through the automated Code Review (Section A), any Remediate loop (Section C), the commit/push/**PR raise** (Section D), and the automated PR Review (Section E). Raising the PR does **NOT** promote it. The story moves to `🧪 Ready for Testing` **only when its PR is MERGED into the epic branch** — and ve has signed it off with the `ve-list-work` skill (dev-implement itself only ever live-checks a specific prerequisite's merge state at its own Doability Gate — it never promotes tracker status). The developed ticket is recorded as a full tracker hyperlink in `.spec/aire-docs/audit.md`:
   - **MANDATORY — record the developed ticket as a full tracker hyperlink in `.spec/aire-docs/audit.md`**: for a tracker-linked story, resolve the site base URL (`getAccessibleAtlassianResources` for JIRA, or reuse the base already recorded in `.spec/aire-docs/`; the work-item/issue URL directly for ADO/GITHUB) and write the ticket as a clickable Markdown link (`[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)` for JIRA, the direct URL for ADO/GITHUB) in the audit entry for this implementation — never bare text. When the PR is raised (Section D) record the PR URL and that the story stays `🔵 In Development` (Merged=no); when the PR later merges, record the promotion to `🧪 Ready for Testing` with evidence (tests passing + measured coverage % ≥90%). For local-only stories (`Tracker ID = —`/`LOCAL`), record the local Story ID instead. Example entry:
      ```markdown
        ## [Stage Name or Interaction Type]
         **Timestamp**: [ISO timestamp]
         **User Email**: [current session email — read live from the session context]
         **User Input**: "[Complete raw user input - never summarized]"
        **TRACKER ITEM**: "[Complete tracker item that was implemented]"
        **Epic Link**: "[Full Parent Epic URL as a clickable link, from ## Tracker in aire-state.md — or "none"]"
        **AIRE VERSION**: "[Framework version [N] read from the "AIRE Framework Version" line in CLAUDE.md — do not hardcode]"
       **AI Response**: "[AI's response or action taken]"
       **Context**: [Stage, action, or decision made]
   
---      ```
8. **Update Dependency Graph**: After a story reaches `🧪 Ready for Testing` (i.e. its PR merged and ve signed it off via `ve-list-work`), recompute the ready set — stories whose `requires` are now all `🧪 Ready for Testing` become selectable.
9. **MANDATORY**: Present the code-generation completion announcement as defined in `code-generation.md` Step 14 (Code Generation Complete + file summary). This announces completion only — it does NOT ask the user to choose between review and continue anymore.
10. **AUTO-TRIGGER Code Review (MANDATORY — no longer user-selected)**: As soon as code generation for the story is done, automatically proceed into the **Post-Code-Generation Automation** section below. Code Review runs on its own; the user is NOT asked whether to run it.
11. **MANDATORY**: Log every user response in this stage in audit.md with complete raw input.

---

# Post-Code-Generation Automation — Auto Code Review → (Remediate) → Commit / Push / PR

**Runs automatically once Code Generation Part 2 completes for the story. The user is NOT asked whether to review — Code Review is triggered automatically.** The target branch for the commit/push/PR is the branch resolved in Step 1.5 (newly created, or the current branch).

## A. Auto Code Review (MANDATORY, automatic)
1. **Log** in audit.md that automated Code Review is starting for Story [N.M] (ISO 8601 timestamp).
2. **Run Code Review for this story**: load and execute `workflows/code-review.md` scoped to **this specific story** (target = "story [N.M]"), as a **read-only** review (it MUST NOT edit source). It produces the versioned report at `.spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v[X].md`. Code Review does **NOT** change the tracker status — the story stays `🔵 In Development`.
   - **⚡ NO TEST RE-RUN**: the Unit Test & Coverage gate (Step 6) measured coverage on this story's new/changed code to `unitTestCoverageMin`, the API & Contract Testing Gate (Step 6.2, when applicable) ran automated tests against every new/changed endpoint to a full pass, and the Full Regression Gate (Step 6.5) ran the ENTIRE repo suite and diffed it against the Step 1.5 baseline — all in THIS same run, with proof artifacts saved under `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/` (`unit-test-run.log`, `coverage-report.*`, `baseline-regression.log`, `full-regression.log`, `evidence-manifest.md`) and, when Step 6.2 applied, `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/` (`api-contract-test-run.log`, `api-contract-test-report.*`, `evidence-manifest.md`). Pass that captured evidence into the review — Code Review MUST NOT re-execute the unit tests, re-measure coverage, or re-run the API & Contract tests; it verifies test existence/AC coverage statically and **cites the stored proof artifacts** (link `unit-test-run.log` + `coverage-report.*`, and — when applicable — `api-contract-test-run.log` + the per-endpoint checklist from its `evidence-manifest.md`) in its report, rather than restating unverified numbers.
2.4. **🛡️ AUTOMATED SECURITY REVIEW (MANDATORY, automatic — inside this review pass)**: the review's **Phase 2.5** runs the `agents/code-security-review-agent.md` procedure against this story's diff, checking all 16 Security Baseline rules on the changed files and the attack surface they reach, and writes `.spec/aire-docs/code-security-reviews/security-review-YYYY-MM-DD.md`. Its **🔴 Critical / 🟠 High findings on the changed surface become real `SEC-ISS-XXX` findings in the review's issue list** — so they route through Section B exactly like AC findings and are **auto-remediated by Section C (SH-LOOP-5) until clean, within its 3-round budget**. 🟡/🔵 findings and any pre-existing violation on lines this story didn't touch are **advisory only** (reported, never remediated here, recommend `/raise-defect`). 🔴 Never suppress a finding instead of fixing it; never let the security pass go repo-wide.
2.5. **⚖️ JUDGE GATES J1 + J2 — 🔴 BLOCKING (MANDATORY, automatic — computed HERE and nowhere else)**: as part of this review pass, compute the two judge scores per `common/eval-framework.md` Section 4 — **J1 Architecture conformance** against `.evals/rubrics/architecture-rubric.json` (derived mechanically from `.spec/architecture.md` Section 10; apply the Section 3 fallback chain, `N/A` if it bottoms out) and **J2 Security (OWASP)** against `security-rubric.json` — from this story's diff. Write them with their **per-criterion breakdown** to `eval-evidence/story-[N.M]/judge/`, merge them into the **`gates`** block of `eval.json`, refresh `eval-summary.md`, and report both in the review report.
   - **Scoring discipline** (eval-framework.md Section 4.1): score **once** per review pass — never re-roll for a better number; score each criterion independently then weight; **every criterion below 1.0 MUST cite `file:line`** and say what violates it; score only what the diff shows; a criterion this diff cannot exercise is `N/A` and is excluded with the remaining weights renormalised to 1.0 — never scored 0.
   - **🔁 Gate**: `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin`, both read from `.evals/config.json`. A `J1` of `N/A` passes. **Below minimum → SH-LOOP-6**: remediate the specific criteria that scored below 1.0, worst weighted-loss first, using their citations; re-run whatever gates the fix touched; re-score on the next review pass. **Capped at 3 attempts (SH-1); on exhaustion apply SH-4 — HALT and emit the Retry-Limit Report** naming each failing criterion, its weight, its citation, and what the three attempts changed.
   - 🔴 **Forbidden ways to pass this gate** (SH-6 violations, all of them): editing `.spec/architecture.md` Section 10 to weaken or delete a constraint; editing the rubric JSON directly; lowering either minimum in `.evals/config.json`; re-scoring until a run clears the bar; marking an applicable criterion `N/A`. The architecture document changes only when the **design decision** changed — never because a score did not clear.
   - Record the pinned judge model and the `rubricVersion` alongside every score.
3. **MANDATORY — audit the complete review log**: append to `.spec/aire-docs/audit.md` the full Code Review outcome — the `**TRACKER ITEM**:` and `**Epic Link**:` fields, report path, review verdict, and the complete list of findings by severity (🔴 Blocker / 🟠 High — the only severities; findings map strictly to unmet/partially-met ACs and requirements), plus any tracker status change. Do not summarize away findings; record the complete log of this automated review.
4. Proceed to **B. Review Decision Gate**.

## B. Review Verdict Routing (🤖 AUTOMATIC — no question, no gate)

The review's own verdict decides what happens next. **Do NOT present an A/B choice and do NOT wait
for the user.** Announce the verdict, then route:

```
🔍 Automated Code Review complete for Story [N.M].
   Report: .spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v[X].md
   Verdict: [clean — all ACs Met / findings: 🔴 X  🟠 Y]
➡️ [Proceeding to commit + PR. | Findings found — remediating them automatically now (round [n]).]
```

1. **Verdict clean — zero 🔴, zero 🟠, AND both judge gates PASS (or J1 `N/A`)** → go straight to **D. Commit, Push & Raise PR**.
1.5. **Judge gate below minimum** → handled by **SH-LOOP-6** inside Section A Step 2.5 before this routing is reached. A run never arrives at Section D with a failing J1 or J2.
2. **Any 🔴 Blocker or 🟠 High finding** → go to **C. Auto-Remediate Loop (SH-LOOP-5)**. The framework
   fixes its own findings within a budget of **3 remediation rounds**; it hands them back to the user
   only when that budget is exhausted (SH-4), and then it HALTS instead of raising the PR.
3. **MANDATORY**: log the routing decision in audit.md under a plain heading
   (`## Review Verdict — Clean, Proceeding to PR (Story N.M)` or
   `## Review Verdict — Findings, Auto-Remediating (Story N.M)`), with the full findings list by
   severity. **No "GATE" in the heading, and no user response to record.**

## C. Auto-Remediate Loop — SH-LOOP-5 (🤖 AUTOMATIC — max 3 rounds)

**Entered whenever the review verdict reports findings. Every round is automatic — no prompts at any
point. The loop is bounded by the Self-Healing Retry Policy: one round = one attempt, maximum 3.**

1. **Check the SH-LOOP-5 counter BEFORE starting a round.** If 3 attempts have already been spent,
   do not start another — go directly to Step 8 (Exhaustion) below.
2. **Log** in `audit.md` that automatic remediation round `[n] of 3` is starting for Story [N.M],
   naming the review report being remediated, the findings in scope, and the identified root cause of
   each (SH-3, SH-7).
3. **Run Remediate**: load and execute `workflows/remediate.md` scoped to **this story's** review
   report (`story-[N.M]-code-review-v[X].md`). It fixes findings (fix → unit test → green, running
   ONLY this story's unit tests) and annotates the report in place. 🤖 **Its scope-confirmation prompt
   is SKIPPED in this mode** — every 🔴 and 🟠 finding is in scope by definition, and nothing is
   deferred. Remediate does **NOT** change the tracker status — the story stays `🔵 In Development`
   throughout.
4. **Re-run the FULL regression** (Step 6.5's diff vs `baseline-regression.log`) if the remediation
   touched non-test code, fixing any NEW failure in the same round. If the remediation touched
   API-layer code that Step 6.2 covered, also re-run the affected endpoint(s)' API & Contract tests
   and keep them green. Per SH-2, this re-entry **continues** the SH-LOOP-3 / SH-LOOP-2 counters — it
   does not reset them.
5. **MANDATORY — audit the complete remediate log**: append to `.spec/aire-docs/audit.md` the full outcome
   of the round — the `**TRACKER ITEM**:` and `**Epic Link**:` fields, the round number (`[n] of 3`),
   which findings were fixed (by severity), the files changed, unit-test evidence, and the regression
   comparison. Record the complete log, not a summary.
6. **Re-review automatically**: return to **A. Auto Code Review**, producing the next report version
   `v[X+1]`, then **B. Review Verdict Routing** again.
7. **Loop control**:
   - **Verdict clean** → the loop exits successfully → **D. Commit, Push & Raise PR**.
   - **Findings remain AND attempts spent < 3** → increment the counter and return to step 1.
   - **Findings remain AND attempts spent = 3** → **exhausted** → step 8.
   - **Stall (SH-5)** — a round produced **no code change at all** AND the next review returned an
     **identical** finding set → the loop cannot progress. Treat as exhausted immediately, regardless
     of attempts remaining → step 8, noting the early end.
8. **🛑 Exhaustion (SH-4) — HALT, do not raise a PR.** When the budget is exhausted (3 rounds, or an
   SH-5 stall):
   - Do **not** run a 4th round, do **not** commit, do **not** push, do **not** raise a PR, and do
     **not** change the local Story Tracker or the external tracker. The story stays
     `🔵 In Development` and the remediation work stays in the working tree.
   - Emit the **Retry-Limit Report** (Self-Healing Retry Policy, above) with `[loop name]` =
     `Auto-Remediate (code review + security findings)` and `[SH-LOOP-ID]` = `SH-LOOP-5`, listing every
     unresolved finding with its ID, severity, file:line, and the reason automatic remediation failed
     on it.
   - Append the same content to `audit.md` under
     `## Self-Healing Retry Limit Reached — SH-LOOP-5 (Story N.M)`.
   - **HALT and wait for the user's direction.** 🔴 Never silence a finding by deleting it from the
     report, never weaken the review scope to manufacture a clean verdict, and never let an exhausted
     loop pass unreported.

## D. Commit, Push & Raise PR (on a clean review verdict) — 🤖 FULLY AUTOMATIC

🔴 **A clean review verdict is the ONLY thing that triggers this section.** An exhausted SH-LOOP-5
(Section C.8) does NOT reach it — that path HALTS at the gate and waits for the user.
Everything below — the commit, the branch push, the PR creation, the labels, the tracker update,
and the auto PR review (Section E) — runs **automatically, with no prompts of any kind**.
Do NOT ask about pushing, opening the PR, the PR title/body, or the labels. Announce what you
are doing; never ask whether to do it.

1. **Log** in audit.md that the review verdict came back **clean** and the commit/push/PR step is starting, naming the target branch. 🔴 If SH-LOOP-5 was exhausted instead (Section C.8), this section is NOT reached — the run has already halted.
2. **Commit the story's changes to the target branch**:
   - Verify the active branch is the target branch from Step 1.5 (`git branch --show-current`). If it is not, switch to it automatically and announce the switch (no confirmation — the target branch was determined by this run).
   - Stage and commit the generated/remediated application code (do NOT commit unrelated changes). The commit message MUST carry an `AIRE-Version:` trailer as the framework signature, where `[N]` is read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` (do not hardcode a number). Use a clear message, e.g.:
     ```
     git add <story files>
     git commit -m "[Story N.M / TRACKER-ID] <concise summary of the implemented story>" -m "AIRE-Version: [N]"
     ```
     The `AIRE-Version: [N]` trailer goes on its own line at the end of the message body (alongside any existing trailers), with `[N]` substituted from the CLAUDE.md canonical line.
   - Record the commit hash in audit.md.
3. **Push & raise the PR via the `pr-generator` skill (used as-is — DO NOT edit it)**:
   - Invoke the **`pr-generator`** Claude skill **in WORKFLOW mode**, passing **target branch = the Epic Branch** from `aire-state.md` `## Branching` — story PRs merge into the epic branch, NEVER into main/the base branch. The skill diffs the story branch against the target, reads `aire-state.md` + `audit.md` for context, drafts the PR title/body (the title MUST carry the **`[STORY]`** prefix — this is a story → epic-branch PR), then pushes the branch, ensures the `ai-generated` and `aire-v[N]` labels, and opens the PR.
   - 🤖 **pr-generator's Phase 5 confirmation is SKIPPED in workflow mode** — the `dev-implement` invocation authorized the whole run, including the push and the PR. The skill announces the drafted title/body/labels/target and proceeds. **Never ask the user whether to push or open the PR.**
   - **Pass the eval scorecard** to pr-generator: give it the PATH `eval-evidence/story-[N.M]/eval-summary.md`; it pastes the file's CONTENTS verbatim into the PR body's `## Eval Scorecard` section.
   - 🔴 **VERIFY IT LANDED — do not assume.** After the PR is created, read the PR body back (`gh pr view <n> --json body`) and confirm the scorecard table is present. If it is missing, edit the PR to add it, then re-verify. **Never write "the PR carries the scorecard" into audit.md on the basis of having passed the path** — record only what reading the body actually showed. A claim in the audit trail that does not match the artifact is a defect in the audit trail.
4. **MANDATORY**: Record in audit.md the PR outcome returned by pr-generator (branch pushed, PR URL, labels applied — `ai-generated` + `aire-v[N]`), including the `**TRACKER ITEM**:` and `**Epic Link**:` fields.
5. **STORE THE PR AND KEEP THE STORY `🔵 In Development` (do NOT promote on PR raise)**:
   - In `.spec/aire-docs/aire-state.md` `## Story Tracker`, for this story set **PR** → the PR URL returned by pr-generator, **Merged** → `no`, **Recorded** → current timestamp. **Do NOT change Status** — the story **remains `🔵 In Development`**. Raising the PR is NOT the promotion trigger; **merging** it is.
   - **Do NOT transition the tracker here** and do NOT set `End`. The story moves to `🧪 Ready for Testing` — in the local tracker AND on the external tracker — ONLY when its PR is confirmed MERGED, handled by the `ve-list-work` skill (dev-implement's own Doability Gate live-checks a prerequisite's merge state when needed, but never promotes this story's tracker status itself).
   - **MANDATORY** — record in `.spec/aire-docs/audit.md` (per Step 7 above) the developed ticket as a full tracker hyperlink, the PR URL, and that the story stays `🔵 In Development` pending merge (Merged=no).
6. **Ready set unchanged**: because the story is still `🔵 In Development` (not `🧪 Ready for Testing`), it does NOT yet unblock dependents. Dependents become selectable only after this story's PR merges and it is promoted to `🧪 Ready for Testing`. (This aligns with the branch-cut dependency-merge check in `common/branching-strategy.md` — a dependent needs its prerequisite's code MERGED into the epic branch.)
7. **🔷 EPIC → Ready for Testing (only when ALL PRs are MERGED)**: The epic moves to Ready for Testing only when EVERY story is `🧪 Ready for Testing` (i.e. every PR merged). Since the just-raised PR is not merged yet, this typically does NOT fire here — it fires from the `ve-list-work` skill once the last PR merges and ve has signed every story off. **If this is the last story and one or more PRs are still open**, do NOT move the epic — instead report:
   ```
   ✅ Story [N.M] PR raised (kept 🔵 In Development until merged).
   ✋ As checked, these story PRs are still OPEN — hence keeping their status as 🔵 In Development,
      and the Parent Epic stays In Development until every PR is merged:
        • Story [X.Y] — [TRACKER-ID] — <PR URL>
        • ...
   ➡️ Merge those PRs, then ve (on the epic branch) uses the skill `ve-list-work` — it lists the
      merged stories, and promotes the ones ve has tested to 🧪 Ready for Testing; when ALL are
      signed off, the Epic is offered a move to Ready for Testing. The exact instructions are repeated in the Section F handoff below.
   ```
   Only when `ve-list-work` later leaves EVERY story `🧪 Ready for Testing` is the Parent Epic (from `## Tracker`) offered a confirm-first transition to "Ready for Testing" (verified, logged). Skip the epic transition silently if `## Tracker` records `Parent Epic: none`, or if `Type: LOCAL`.
8. Proceed to **E. Auto PR Review**.

## E. Auto PR Review (MANDATORY, automatic — runs right after the PR is raised; story is still `🔵 In Development`)
1. **Log** in audit.md that automated PR Review is starting for Story [N.M], naming the PR URL/number from Section D.
2. **Invoke the `pr-review` Claude skill** (`.claude/skills/pr-review/`, used as-is — DO NOT edit it) in its **AUTO MODE**, passing the PR just raised in Section D so it does not need to ask which PR (its Phase 0 is satisfied automatically). It reads the diff, grounds itself in `aire-state.md` + `audit.md`, and drafts inline comments + a summary review.
3. **AUTO MODE — post automatically, comments only, no prompt**: the skill posts the review **without asking the user** (its Phase 5 confirmation is skipped by design in this mode) and **only as a plain COMMENT review** (summary + inline comments) — NEVER a formal GitHub `APPROVE`/`REQUEST_CHANGES`. The same GitHub identity that just raised the PR is posting the review, so a formal self-review is impossible; there is no decision for the user to make here. Do not re-introduce a prompt around the skill.
4. **MANDATORY**: Record in audit.md the outcome — review posted automatically (AUTO MODE, comment-only), the posted review URL, findings summary, and the `**TRACKER ITEM**:` and `**Epic Link**:` fields.
5. Proceed to **F. Next-Action Handoff** — this run is NOT complete until that message is shown.

## F. 🎯 Next-Action Handoff (MANDATORY — the LAST thing this run outputs)

**This message closes every `dev-implement` run that raised a PR. It is not optional and it is not a summary — it tells the user the EXACT actions and the EXACT keyword to type next.** The story is `🔵 In Development` with an unmerged PR. Keep it to the minimum the user must actually do: **get the PR approved, then type the keyword.** Do NOT instruct them to check out or switch branches — the next workflow does that itself — and do NOT ask them to merge a PR that the next `dev-implement` run will merge automatically once it is approved (Case 2 is the exception: the last story's PR has no later run to merge it).

1. **Determine the remaining work first** — count the stories in the `## Story Tracker` that are still `🟢 Ready for Development` (call it `[K]`), and whether this story was the **last** one (no story is `🟢 Ready for Development` and no other story is `🔵 In Development` with an unmerged PR).
2. **Present EXACTLY ONE of the two blocks below (verbatim, placeholders substituted).** Show the `[K] stories remain` block when `K > 0`; show the `LAST story` block when this was the final story.

   **Case 1 — more stories remain (`K > 0`)**:
   ```
   🔀 PR RAISED — NOT MERGED. Story [N.M] stays 🔵 In Development until this PR merges.
      PR: <PR URL>  →  target branch: `<epic-branch>`

   ➡️ NEXT ACTIONS:
      1️⃣  Review, APPROVE, and MERGE the PR above into `<epic-branch>` yourself.
          🔴 `dev-implement` never merges a PR on your behalf, even once it's approved — merging is
          always your own action.
      2️⃣  Type this keyword to continue: dev-implement

   🔴 Type the keyword `dev-implement` EXACTLY as shown — do not describe what you want in your own
      words. Any other phrasing is not a framework trigger and the workflow will not advance.
   ```

   **Case 2 — this was the LAST story of the epic**:
   ```
   🔀 PR RAISED — NOT MERGED. Story [N.M] (the LAST story of epic [EPIC-ID]) stays 🔵 In Development
      until this PR merges.  PR: <PR URL>  →  target branch: `<epic-branch>`

   ➡️ NEXT ACTIONS — do these in order:
      1️⃣  Review, approve and MERGE the PR above into `<epic-branch>`.
          🔴 This is the last story, so no further `dev-implement` run will come along to merge it
             for you — merging it is yours to do.

      2️⃣  Hand over to ve — they type this skill: ve-list-work on epic branch (then pick Option B)
          It lists every story whose PR has merged, ve tests them, names the ones it has finished
          testing, and those move to 🧪 Ready for Testing (tracker + local, verified). When ALL are
          signed off it offers the Parent Epic move and points at `pr-generator` for the Epic PR.
          (ve's Test Plan Manual steps for each story come from `/ve-implement <story>`, run in parallel.)

   🔴 Type the keyword `ve-list-work` EXACTLY as shown — do not describe what you want in your own
      words. Any other phrasing is not a framework trigger and the workflow will not advance.
   ```
3. **Say NOTHING after this block** — no options menu, no extra suggestions, no "let me know if…". The handoff message is the end of the run.
4. **MANDATORY**: log in audit.md which case was presented (more-stories vs last-story) and the keyword the user was told to type.

---

## 🔄 Tracker Sync Rule (reminder)

This workflow changes story status (`🟢 Ready for Development` → `🔵 In Development` at story selection, then `🔵 In Development` → `🧪 Ready for Testing` **when the PR is MERGED** — NOT when it is raised). The **Tracker Sync Rule** in `CLAUDE.md` (mechanics in `common/tracker-sync.md` Section 4/Section 5) applies at every status change:
- If **Tracker ID = `—`/`LOCAL`** (local story, or `## Tracker` records `Type: LOCAL`): update only the local tracker. No external call.
- If **Tracker ID is a real JIRA/ADO/GITHUB identifier**: also transition the tracker issue via the mechanism for that type (Atlassian MCP / `az boards` / `gh`) and verify the transition. Never silently update only one side.
- **Exception — story transitions are automatic**: the `🟢 → 🔵 In Development` transition at story pick is applied to the tracker AND the local Story Tracker WITHOUT asking (picking the story is the claim), and the `🔵 → 🧪 Ready for Testing` transition on confirmed PR merge is likewise applied WITHOUT asking (the merged PR is the trigger) — both verified (non-LOCAL) + announced. Only non-story transitions (e.g., the Parent Epic moves) remain **confirm-first**.
- **Assignee on claim**: when the story moves to `🔵 In Development`, the tracker issue is ALSO **assigned to the operator who typed `dev-implement`**, per `common/tracker-sync.md` Section 5 — resolve the session email (the same one stamped as `**User Email**:` in audit.md) and set the assignee via the type-appropriate mechanism (JIRA: `lookupJiraAccountId` + `editJiraIssue`; ADO: `az boards work-item update --assigned-to`; GITHUB: a cached GitHub username + `gh issue edit --add-assignee`), verify, announce, log in audit.md. Automatic (part of the same claim, no confirmation). If the identity doesn't resolve, leave the issue unassigned, warn the user, and continue — never block development on assignment. LOCAL has no assignee concept.
- **Ready for Testing = PR merged**: a story moves `🔵 In Development` → `🧪 Ready for Testing` ONLY when its PR is confirmed MERGED AND ve has named it in the `ve-list-work` skill after testing it (verified + announced + logged). dev-implement never promotes it. Raising the PR stores the PR URL and keeps the story `🔵 In Development` (`Merged=no`).
- **Epic status sync**: when the FIRST story moves to `🔵 In Development`, the Parent Epic is transitioned to "In Development" **automatically** (Story Selection Step 5); when the LAST story reaches `🧪 Ready for Testing` (all PRs merged), the Parent Epic is transitioned to "Ready for Testing" **confirm-first** (from `ve-list-work`). Both are verified (non-LOCAL) and logged in audit.md.

---

## Critical Rules

- 📁 **ALL APPLICATION CODE GOES IN `src/`** — greenfield and brownfield alike. On a brownfield repo whose code lives elsewhere, use the root recorded in `aire-state.md` `## Code Root` and never introduce a second location (`common/directory-structure.md`). Test code goes in `tests/`; specs and docs go in `.spec/`; **never a source file under `.spec/`**.
- 🥒 **THE BEHAVIOUR SPEC IS WRITTEN BEFORE CODE** (Step 4.5, `common/behavior-spec.md`) — one file, `.spec/aire-docs/implementation/code/behavior/story-[N.M].feature`, authored BEFORE the implementation because it is the contract. 🔴 **That is the story's ONLY spec file.** No per-story requirements, architecture, constraints or knowledge-graph document — ACs come from the tracker + `stories.md`, requirements from `requirements.md`, design constraints from `.spec/architecture.md`, thresholds from `.evals/config.json`.
- ⚖️ **J1 AND J2 ARE BLOCKING GATES** (Section A Step 2.5, `common/eval-framework.md` Section 4) — they live under `gates` in `eval.json` and decide the verdict like every other gate. Below minimum → SH-LOOP-6, max 3 attempts, then HALT. 🔴 NEVER pass a judge gate by editing `architecture.md`, editing a rubric, lowering a minimum, or re-scoring.

- 🔁 **SELF-HEALING IS CAPPED AT 3 ATTEMPTS PER LOOP.** The **Self-Healing Retry Policy (SH-1 … SH-7)** at the top of this file governs SH-LOOP-1 … SH-LOOP-7 without exception. Track one counter per loop, log every attempt, and on exhaustion HALT at that gate, emit the Retry-Limit Report ("3 retries ended. Please suggest next steps."), and wait for the user. NEVER start a 4th attempt, never skip or weaken a failing gate to move on, and never continue to a later stage with an exhausted loop outstanding.
- 🔴 EVERY audit.md entry in this workflow — selection, branching, planning, generation, coverage, review, remediate, PR — MUST carry the `**User Email**:` (current session email), `**TRACKER ITEM**:`, `**Epic Link**:` (full Parent Epic URL from `## Tracker` in aire-state.md, or `none`) AND `**AIRE VERSION**:` fields (version read at runtime from the "AIRE Framework Version" line in `CLAUDE.md` — never hardcoded). See the Audit Entry Format section above.
- 🔴 EVERY story commit MUST carry the `AIRE-Version: [N]` trailer (framework signature, read live from `CLAUDE.md`) — see Section D Step 2.
- 🔴 ALWAYS show the sequential-development banner (Step 1.75) on every invocation, BEFORE Story Selection — one story at a time per session; parallel development happens in a separate folder/clone on an independent story.
- 🔴 NEVER guess which story to implement — always ask and wait.
- 🔴 NO GATES: this workflow asks for NO approval — no plan approval (GATE 2 removed) and no review decision (GATE 3 removed). Never present an approve/reject or Approve-&-continue/Remediate prompt, and never write "GATE" into an audit heading here. The Doability Gate and the branch-cut dependency-merge check are machine checks that STOP the run — they are not approvals and remain in force.
- 🔴 PLAN GUARDRAIL: the code-generation plan MUST be grounded in the previously generated docs (story acceptance criteria, epic-brief, requirements, design artifacts), and coding MUST follow the announced plan exactly — any needed deviation is applied only after the plan document is revised and the change announced + logged, never silently.
- 🔴 REQ-ID THREAD: `requirements.md` + the story's `Covers` REQ-IDs are MANDATORY planning inputs; every plan step is tagged with the REQ/AC it implements and the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step) MUST pass before the plan is executed. If `aire-state.md` has no `Requirements coverage verified post-design` record, run the Rule 4 fallback verification (silent, blocking) before planning. See `common/requirements-traceability.md`.
- 🔴 ALWAYS create the story branch (Step 1.5) right after Story Selection — cut from the refreshed EPIC branch per `common/branching-strategy.md`, NEVER from main/the base branch or a dependency branch — and run the dependency-merge check BEFORE any code is generated: if any prerequisite is unmerged into the epic branch, WARN AND STOP and tell the user to merge it first.
- 🔴 NEVER bypass the Doability Gate — a story is doable only when ALL its `requires` are confirmed MERGED: already `🧪 Ready for Testing` in the tracker, or live-verified via `gh pr view` at gate time (`implementation/story-selection.md` Step 4). Any prerequisite still unmerged → 🛑 STOP the run with a clear message naming it; do NOT loop back and do NOT let the user bypass it.
- 🔴 **THE GATE NEVER MERGES A PR — PERIOD.** Not automatically, not with a confirmation prompt, not even when the PR is already approved by a human. PR approval is always a manual action a human performs outside this workflow, and merging is likewise always the user's own action. The Doability Gate only ever reads live PR state (`gh pr view`) — it has no merge step of any kind. If the blocking prerequisite is already approved, say so in the stop message so the user knows merging it is all that remains.
- 🔴 The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`. The story stays `🔵 In Development` through code generation, Code Review, Remediate, the PR raise, AND the auto PR Review; it becomes `🧪 Ready for Testing` ONLY when its PR is confirmed **MERGED** into the epic branch, promoted exclusively by the `ve-list-work` skill, on ve's explicit say-so. Raising the PR NEVER promotes the story, and NEITHER does a later `dev-implement` run — it only ever live-checks a specific prerequisite's PR at its own Doability Gate.
- 🔴 At Section D, when the PR is raised, STORE the PR URL in the Story Tracker (`PR` column, `Merged=no`) and keep the story `🔵 In Development` — do NOT transition the tracker or set `End` here.
- 🔴 dev-implement does NOT bulk-reconcile or promote prior `🔵 In Development` stories at the start of a run (Step 1.5) — that promotion is exclusively the `ve-list-work` skill's job. dev-implement only ever live-checks the PR-merge state of a SPECIFIC prerequisite, at the Doability Gate, when a story that `requires` it is being selected — and STOPS the run with a clear message if that prerequisite isn't merged yet.
- 🔴 ALWAYS enforce the Unit Test & Coverage gate: after implementation, generate unit tests, RUN them, and iterate within the same run until coverage on the story's new/changed code meets `unitTestCoverageMin`. This is **SH-LOOP-1**, capped at **3 remediation attempts**; on exhaustion apply SH-4 — HALT, emit the Retry-Limit Report, and never mark the story done below the threshold.
- 🔴 ALWAYS enforce the API & Contract Testing Gate (Step 6.2) WHEN this story's plan includes an API Layer Generation step: generate automated tests against the real endpoints, RUN them, and iterate within the same run until EVERY applicable checklist item (functional, response-code validation, role-based authorization 401/403, error-response validation, request validation, response contract/schema validation) passes. This is **SH-LOOP-2**, capped at **3 remediation attempts**; on exhaustion apply SH-4 (HALT + Retry-Limit Report). Applicability is decided from the plan alone — never asked. When the plan has no API layer step, mark it N/A with a reason and proceed. Capture proof artifacts to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/` — never a hand-written claim. This gate runs BEFORE the Full Regression Gate (Step 6.5) and does NOT replace ve's `/ve-implement` MANUAL API/Contract test steps.
- 🔴 ALWAYS BOOTSTRAP missing tool configs BEFORE the baseline static run (Step 1.5 Item 4.6, `common/eval-framework.md` Section 2.2) — a check with no config is **set up**, not marked N/A; a check whose config exists is used **as-is**. Bootstrap → baseline → code → gate → diff, in that order: a config created after the baseline makes the two runs measure under different rules and blames this story for pre-existing findings. Announce every file created; only a genuinely unavailable tool is `N/A`.
- 🔴 ALWAYS run the BASELINE static eval checks D1–D7 alongside the baseline regression (Step 1.5 Item 4.6) and the STATIC EVAL GATE after the Full Regression Gate (Step 6.6), then diff them. Both runs are **automatic — never prompt the user for either**. Only findings NEW vs the baseline on files this story changed count, and this story **fixes them in the same run**. **NEVER suppress a finding to pass the gate** (`eslint-disable`, `# nosec`, `# type: ignore`, ignore lists, widening the licence list) — that is the analogue of deleting a failing test and is equally forbidden. Baseline findings are pre-existing debt: logged and ignored. See `common/eval-framework.md`.
- 🔴 The J1/J2 judge scores are computed ONCE inside Section A and are **output only** — never a gate, never a review finding, never fed to remediation, never re-scored, never in the `verdict`. A low score does not block the commit, push or PR. See `common/eval-framework.md` Section 5.
- 🔴 The auto-remediate loop (**SH-LOOP-5**) is **capped at 3 rounds** by the Self-Healing Retry Policy and is otherwise **unchanged by the eval layer** — it receives no eval input and gains no other stop condition. The J1/J2 judge scores never enter it.
- 🔴 ALWAYS run the BASELINE regression (entire repo suite) on the story branch BEFORE any code is generated (Step 1.5 Item 4.5) and the FULL regression AFTER the Unit Test & Coverage gate and the API & Contract Testing Gate (Step 6.5), then diff them. Both runs are **automatic — never prompt the user for either**. Failures NEW vs the baseline were broken BY this story, so this story **fixes them in the same run** — iterate until the diff is clean under **SH-LOOP-3** (capped at **3 remediation attempts**; on exhaustion apply SH-4 — HALT + Retry-Limit Report), fixing each according to what broke (update an obsolete expectation / delete a genuinely dead test / fix the implementation for a real regression). **NEVER delete, skip, or weaken a failing test merely to make the suite green, and NEVER hand a new failure back to the user.** Failures already red at baseline are not this story's doing — they are logged in `baseline-regression.log` and ignored. The the `unitTestCoverageMin` threshold gate is scoped to the story's new code and does NOT substitute for this — coverage on new code says nothing about assertions the change invalidated in pre-existing shared test files.
- 🔴 ALWAYS capture the TEST PROOF artifacts from that same run before leaving `🔵 In Development` — save the raw runner output (`unit-test-run.log`), the coverage tool's **mandatory machine-readable report** (`coverage-report.*` — lcov/xml/json/HTML), and `evidence-manifest.md` to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/`. Run the tool with the flags that emit the report file; a terminal summary alone does NOT satisfy the gate — when the stack HAS coverage tooling, no coverage-report file means the gate is not met, STOP and surface it. The only waiver is a stack with genuinely NO coverage-report tooling, and that must be a documented, user-surfaced exception in `evidence-manifest.md` — never a silent skip. Evidence is the actual tool output, never a hand-written claim; every X/X-passing and coverage-% figure in the completion message, Code Review report, and PR/tracker comment MUST match these stored artifacts.
- 🔴 After Code Generation, ALWAYS auto-run Code Review (`workflows/code-review.md`) and audit its complete log in audit.md. The verdict — not the user — decides what happens next (Section B).
- 🔴 **THE FRAMEWORK FIXES ITS OWN FINDINGS, WITHIN A BOUNDED BUDGET.** Any 🔴/🟠 finding triggers the **Auto-Remediate Loop** (Section C, **SH-LOOP-5**): remediate → re-run regression → re-review, looping until the verdict is clean **or the 3-attempt budget is exhausted**. Never ask whether to remediate, and never raise the PR on an unclean verdict. On exhaustion (3 rounds, or an SH-5 stall — no code change + identical findings) the run **HALTS at the gate**: no commit, no push, no PR, no tracker change; the Retry-Limit Report is emitted to the user and to audit.md, and the run waits for user direction.
- 🔴 The commit, push and PR are AUTOMATIC once the verdict is clean. Commit to the story branch from Step 1.5, then push + raise the PR ONLY via the `pr-generator` skill (used as-is), passing **target branch = the Epic Branch**. Story PR titles MUST carry the **`[STORY]`** prefix (pr-generator applies it).
- 🔴 **THE RUN HAS NO PROMPTS AFTER THE STORY KEY.** Story selection → branch → baseline (regression + static eval) → plan → code → coverage → regression → static eval gate → review → auto-remediate → commit → push → PR (pr-generator **workflow mode, Phase 5 skipped**) → labels → Story Tracker PR/Merged update → auto `pr-review` → Section F handoff, all uninterrupted. Asking anything in that chain (approve the plan, approve the review, whether to push, whether to open the PR, whether the title/body/labels are OK) is a defect. Announce each action; never ask.
- 🔴 The story branch name is derived and created **automatically — never confirmed or offered for override** (Step 1.5 Item 2); it is announced.
- 🔴 EPIC STATUS SYNC: on the FIRST story pick, the Parent Epic moves to "In Development" automatically; when ALL stories are `🧪 Ready for Testing` (i.e. ALL PRs merged), offer (confirm-first) to move the Parent Epic to "Ready for Testing". Verify every epic transition and log it. If the last story's PR is raised while other PRs are still open, do NOT move the epic — report the open PRs and keep everything `🔵 In Development`.
- 🔴 After the PR is raised (the story STAYS `🔵 In Development` — it is NOT yet Ready for Testing), ALWAYS auto-invoke the `pr-review` skill (used as-is) against that PR in **AUTO MODE** — it posts automatically as a plain COMMENT review (summary + inline comments) with NO user prompt and NEVER a formal GitHub APPROVE/REQUEST_CHANGES (the PR author's own identity cannot formally self-review). The skill's Phase 5 confirmation applies only to standalone runs.
- 🔴 EVERY run that raises a PR MUST end with the **Section F Next-Action Handoff** — the review/approve (Case 1) or merge (Case 2) instruction, and the ONE keyword to type (`dev-implement` when stories remain, `ve-list-work` when this was the last story). 🔴 Do NOT tell the user to switch branches — `dev-implement` refreshes the epic branch itself (`common/branching-strategy.md` Section 3) and `ve-list-work` resolves and switches on its own. 🔴 The framework never merges a PR for you, approved or not — say so plainly, and never imply the next run will merge it automatically. Never end a run with a bare "PR raised" summary, and never leave the next step to the user's own words. Nothing is output after the handoff block.
- 🔴 On every auto-remediate round, ALWAYS audit the complete remediate log, then re-review automatically — never offer "Approve & continue" or "Re-review" as a choice.
- 🔴 STORY tracker transitions are **automatic** (no confirmation): `🔵 In Development` at story pick, and `🧪 Ready for Testing` when the PR is confirmed MERGED. Any OTHER tracker transition (e.g., the Parent Epic moves) requires explicit user confirmation. ALWAYS verify every transition landed (non-LOCAL) and log it in audit.md.
- 🔴 At story pick, ALWAYS set the assignee to the operator who invoked `dev-implement` per `common/tracker-sync.md` Section 5 (automatic, verified where applicable, logged). Unresolvable identity → leave unassigned, warn, continue — assignment failure never blocks development. LOCAL has no assignee concept.
- 🔴 ALWAYS update the Story Tracker (and `Recorded` timestamp) on every status change.

---
