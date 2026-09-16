# 🐞 WORKFLOW: `bug-fix <TICKET-ID>` (Bug/Defect — Planning)

**Purpose**: Take an existing defect ticket — in whichever tracker is configured (`## Tracker` → `Type`: a Jira key, an ADO work item ID, a GitHub issue ref, or — for `Type: LOCAL` — no ID at all, described inline instead) — through a trimmed Planning + design pass, **break once at the ve handoff** (Step 9 — design artifacts committed + pushed so the ve can start `/ve-implement` in parallel), then continue into `bug-fix-implement` on the user's `yes` — no second keyword needed. The ticket may be of issue type **Bug OR Story/Task** — raised by anyone (not necessarily via the `raise-defect` skill).

**How the bug flow differs from the epic flow**:
- ONE branch: `bug/<TICKET-ID>-<kebab-title>` cut from the **base branch**. No epic branch, no story branches.
- ONE story, derived from the ticket itself — no team-size question, no story generation loop, no push to the tracker (the ticket already exists, or for LOCAL never existed externally), **no Dependency Graph stage**.
- NO PR after Requirements approval — the single **`[BUG]`** PR is raised at the END by `bug-fix-implement`, after code review approval.
- A NEW **Impact Analysis + AI-Origin Detection** step replaces multi-story planning.
- The ticket is transitioned to "In Development" when `bug-fix-implement` starts and is **NEVER moved to "Ready for Testing" by these workflows**
- All Parent-Epic sync steps are **skipped** — there is no epic in this flow.

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone in a fresh session. Resolve the rule details directory (`.aire-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- `common/branching-strategy.md` — **Bug Branch Model** section
- `planning/workspace-detection.md`, `planning/reverse-engineering.md` (if RE runs), `planning/requirements-analysis.md`, `planning/workflow-planning.md`
- `agents/defect-provenance-analyst.md` — loaded at Step 5b (line-level AI-origin detection)
- Extensions per CLAUDE.md's Extensions Loading rules (Security Baseline is ALWAYS mandatory)

Display the welcome message (`common/welcome-message.md`) once at start. All CLAUDE.md audit-logging rules apply: log EVERY user input verbatim in `.spec/aire-docs/audit.md` (append-only, ISO 8601 timestamps).

## MANDATORY: Audit Entry Format — TRACKER ITEM on EVERY entry

Every audit.md entry written during this workflow MUST include the `**User Email**:` field (current session email) and the `**TRACKER ITEM**:` field with the defect ticket as a clickable link (JIRA/ADO/GITHUB) or the local ID (LOCAL):

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context]
**User Input**: "[Complete raw user input - never summarized]"
**TRACKER ITEM**: "[The defect ticket, as a tracker hyperlink, or the local BUG-LOCAL-N ID]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

## Approval Gates — there are NONE, in this file or downstream

The bug flow has **no numbered approval gates at all**. `bug-fix-implement` was made fully automatic:
its fix plan is announced and executed (the former **GATE 2** is removed), and its automated Code
Review routes on its own verdict — findings are **remediated automatically and re-reviewed until
clean** (the former **GATE 3** is removed). There is no GATE 1 either; that was the epic flow's
story-set approval, which no longer exists anywhere in the framework.

The remaining approvals inside THIS file (requirements at Step 4, the single story at Step 6) are
**stage approvals, NOT numbered gates**. **Impact Analysis (Step 5) and Workflow Planning (Step 7)
are NOT gated at all** — they are announced and the flow proceeds automatically. The Step 9 yes/no
is deliberately unnumbered flow control. 🔴 **Never put "GATE" in any audit heading written by this
workflow or by `bug-fix-implement`.**

---

## Step 1 — Ticket Capture

1. **Resume check first**: if `.spec/aire-docs/aire-state.md` exists, read it. If `## Tracker` records a DIFFERENT ticket/epic, ask the user which to keep — NEVER silently overwrite. If it records this same ticket with `Workflow Type: bug`, resume from the recorded stage per `common/session-continuity.md`. If `## Tracker` doesn't exist yet (standalone invocation before any aire workflow ran), ask the Tracker Selection question (`common/tracker-sync.md` Section 1) first.
2. Dispatch on `## Tracker` → `Type`, per `common/tracker-sync.md` Section 8:
   - **JIRA/ADO/GITHUB**: parse the `<TICKET-ID>` from the invocation (key/ID/number or URL). If missing, ask for it and wait. Fetch the ticket (`getJiraIssue` / `az boards work-item show` / `gh issue view`) — accept issue type **Bug or Story/Task**. Save summary, description, severity, steps to reproduce, environment, and acceptance criteria (if any) to `.spec/aire-docs/planning/requirements/bug-brief.md`.
   - **LOCAL**: no ID expected. Ask `❓ Describe the bug (what's broken, steps to reproduce, environment, expected vs actual behavior):`, capture the answer, and mint a local ID `BUG-LOCAL-N` (next unused N found by scanning `aire-state.md`) to use as `<TICKET-ID>` for the rest of this flow. Write the captured description directly to `bug-brief.md`.
   The bug-brief is the intake brief: it defines WHAT to fix and is the primary input to every later stage.
3. Record in `.spec/aire-docs/aire-state.md`:
   ```markdown
   ## Tracker
   - Type: JIRA
   - Workflow Type: bug
   - Parent Ticket: PROJ-123        (the defect being fixed — issue type: [Bug/Story]; or BUG-LOCAL-N for LOCAL)
   - Ticket URL: https://<site>.atlassian.net/browse/PROJ-123   (— for LOCAL)
   - Project Key / Repo / Org: PROJ (derived from the key — confirm before first use; — for LOCAL)
   - Parent Epic: none              (bug flow — all Parent-Epic sync steps are skipped)
   ```
   `Workflow Type: bug` is the marker every resumed session reads FIRST — it routes execution to this workflow's rules, not the epic flow's.
4. **MANDATORY**: Log the invocation (complete raw input) and the ticket fetch/capture in audit.md.

## Step 2 — Workspace Detection + Bug Branch

1. Execute `planning/workspace-detection.md` Steps 1–4 as written (workspace scan, brownfield/greenfield, RE-artifact search anywhere in the repo, state file creation). A bug fix is expected to be **brownfield**; if the workspace is empty, STOP and tell the user there is no code to fix.
2. **Step 4.5 replacement — create the BUG branch (automatic)** instead of an epic branch. Execute `common/branching-strategy.md` **Bug Branch Model**:
   - Record the **base branch** (`git branch --show-current` — never assume `main`).
   - Create `bug/<TICKET-ID>-<kebab-case-ticket-title>` (whole name ≤ 60 chars; working tree must be clean, else show `git status` and ask).
   - Record in `aire-state.md`:
     ```markdown
     ## Branching
     - Base Branch: main
     - Bug Branch: bug/PROJ-123-login-timeout
     - Bug PR: (pending — raised by bug-fix-implement after code review approval)
     ```
   - **ALL work — docs and code — happens on this ONE branch.** No story branches are ever cut in the bug flow.
3. Log the branch creation (name, base) in audit.md; present the Workspace Detection completion message and proceed automatically.

## Step 3 — Reverse Engineering (CONDITIONAL — as-is)

Exactly per the epic flow: if RE artifacts exist anywhere in the repo (or restorable from `aire-archives/epics/` or `aire-archives/bugs/` — workspace-detection Step 3 covers this), reuse them and skip. Otherwise run `planning/reverse-engineering.md` in full, with its approval gate. Log everything in audit.md.

## Step 4 — Requirements Analysis (as-is, bug-scoped)

1. Execute `planning/requirements-analysis.md` with `bug-brief.md` as the primary input. Depth will usually be **minimal** (the ticket defines the defect); use standard/comprehensive only if the fix is genuinely complex or high-risk. Its Step 1.5 reads the `## Context Project` answer captured by `ticket-implement` (Step 3.5) and, if `Use Artifacts: Yes`, uses **only** the recorded path as background context about the existing system — do NOT re-ask.
2. Extension opt-ins are presented as usual; Security Baseline is always enforced.
3. **Wait for explicit approval** of requirements.md.
4. On approval: commit the planning artifacts on the **bug branch**. 🔴 **Do NOT raise a PR here** — unlike the epic flow's Step 10, the bug flow raises its single `[BUG]` PR at the end, inside `bug-fix-implement`.
5. **MANDATORY**: Log the user's response verbatim in audit.md.

## Step 5 — 🆕 Impact Analysis + AI-Origin Detection

**Purpose**: Find WHERE the fix must be made (better planning), and determine whether the defective code was AI-generated (defect attribution).

### 5a. Impact Analysis
1. Using the RE artifacts, the bug-brief, and code search (grep/glob/read), identify the **affected files/components**: where the defect lives, the likely root cause, and the blast radius (callers, consumers, shared files). The Root-Cause Hypothesis MUST cite explicit **`file:line-range`** evidence per affected file — 5b's line-level provenance tracing consumes these exact ranges.
2. Write `.spec/aire-docs/planning/impact-analysis.md`:
   ```markdown
   # Impact Analysis — [TICKET-ID]
   ## Root-Cause Hypothesis
   [What is wrong and why, with file:line evidence]
   ## Affected Files
   | File | Why it must change | Defect-line origin (5b) | Originating ticket (5b) |
   |------|--------------------|-------------------------|-------------------------|
   ## Blast Radius
   [Callers/consumers/tests that could be impacted by the fix]
   ```
3. This document is the primary planning input for `bug-fix-implement`'s fix plan.

### 5b. AI-Origin Detection (line-level, via the Defect Provenance Analyst agent)
1. Load `agents/defect-provenance-analyst.md` and execute its procedure with 5a's root-cause `file:line-range` findings as input. It traces each **defective line** (not the file's last change) to the commit that **introduced** the defective logic (`git blame -w -M -C -L`, walking past cosmetic commits via `git log -L`; omission bugs attribute to the enclosing block's introducing commit), resolves that commit's PR, resolves the **originating tracker item** that shipped the line, and returns a **Provenance Verdict table** — verdict AI-generated / human / **undetermined**, each row with concrete evidence (SHA, PR number, which marker) plus the originating item and which source it came from.
2. Record each verdict (with introducing commit + evidence) in the impact-analysis table's **Defect-line origin (5b)** column, and include the full Provenance Verdict table in `impact-analysis.md`. 🔴 Label only on positive evidence (per the agent's marker rules) — NEVER guess; "undetermined" gets no label.
3. **If ANY defective line's introducing change is AI-generated — 🤖 apply the label AUTOMATICALLY (no confirmation)**, exactly like the 5c causal links and for the same reason: the analyst labels **only on positive, verified evidence** (an "ai-generated" PR label, a Claude co-author trailer, or an `AIRE-Version:` trailer), and "undetermined" is never labeled — so there is no judgement call left for the user to make.
   - Apply the label/tag `ai-generated-defect` to the ticket, dispatching on `## Tracker` → `Type` per `common/tracker-sync.md` Section 9 (JIRA: `editJiraIssue`; ADO: add to `System.Tags` via `az boards work-item update`; GITHUB: `gh issue edit --add-label`; LOCAL: note it directly on the local bug entry — no external call), **verify it landed** (non-LOCAL), and **announce it** (not a question):
     ```
     🤖 Labeled [TICKET-ID] `ai-generated-defect` — defective line(s) [file:line(s)] were introduced by
        AI-generated code (evidence: [PR #N "ai-generated" label / Claude co-author on <sha> / AIRE-Version trailer]).
     ```
   - Log the complete evidence (file:line, introducing commit SHA, PR number, which marker) in audit.md. If the label already exists, skip silently. If the tracker call fails, report the failure and continue — labeling is non-blocking.
4. If no defective line is AI-generated: log "human-origin (or undetermined) — no label applied" in audit.md with the per-line evidence.

### 5c. Link the Bug to its Originating Ticket(s) — AUTOMATIC (no confirmation)

Establishes the relationship `[Bug] --"is caused by"--> [Originating Story / Bug / Enhancement]` so the causal chain is queryable where the configured tracker supports it. This runs **automatically** — there is no confirm-first gate — because the analyst reports an item only on positive, verified evidence. Dispatch on `## Tracker` → `Type` per `common/tracker-sync.md` Section 7. **The steps below (2 through 3b) are the JIRA mechanics** — read them in full when `Type: JIRA`. For **ADO**, **GITHUB**, and **LOCAL**, skip straight to step 3c after step 1.

1. Take the analyst's **deduplicated list of resolved originating tracker items** (5b). Drop any item equal to the bug's own `Parent Ticket` (self-link guard). If the list is empty (all rows `—` or `undetermined`), skip silently and log "no originating item resolvable — no link created" in audit.md with the per-line evidence.

**JIRA mechanics (steps 2–3b):**

2. **Resolve the link type at runtime** via `getIssueLinkTypes` — 🔴 never hardcode a type name. Every Jira link type has an *outward* description (how A relates to B) and an *inward* description (how B relates to A); match on the **inward** one.

   **Selection rule** — exactly one type qualifies:
   - A type whose inward description is exactly **"is caused by"**. Use it (step 3a).
   - **Nothing else qualifies.** No near-matches, no "close enough" custom types, no semantic judgement. If no type has the inward description "is caused by", skip step 3a and take the fallback in step 3b.

   🔴 **Never substitute another type.** `Blocks`, `Duplicates`, `caused` and `Clones` mean specific, different things and must never stand in for causation. `Relates` is used **only** on the fallback path in 3b, and **only** alongside the comment that records the actual direction.

3a. **Primary path — an "is caused by" link type EXISTS.** For each remaining key, call `createIssueLink` using the type resolved in step 2, with:

   | Parameter | Issue |
   |---|---|
   | `inwardIssue` | **the originating ticket** `<originating key>` |
   | `outwardIssue` | **the bug** |

   🔴 **The bug is the `outwardIssue`. NEVER the `inwardIssue`.** Jira renders a link as `inwardIssue <type.outward> outwardIssue` — so `inwardIssue` is the issue that performs the type's **outward** description ("causes"). The MCP tool states this itself: *"A is blocked by B" → inwardIssue: B, outwardIssue: A* (B is the blocker). Putting the bug in `inwardIssue` produces **`bug causes <originating key>`** — the exact inverse. Note that step 2 matched the *type* on its **inward** description; that says NOTHING about which issue goes in `inwardIssue`. Conflating the two is the single known failure of this step.

   🔴 **The only acceptable end state is that the BUG ticket shows the originating ticket under "is caused by".** Not "causes".  Not "blocks", "duplicates" or any other description. If the bug's Linked issues panel reads anything other than **"is caused by"**, the step has FAILED regardless of whether a link was created.

   **Verify the DIRECTION, not the existence of a link.** Re-read the bug (`getJiraIssue` including `issuelinks`) and assert ALL THREE:
   1. a link of the resolved type is present on the bug, AND
   2. on that link the originating key sits in **`inwardIssue`** (if it sits in `outwardIssue`, the link is backwards), AND
   3. the description rendered on the **bug's** side is literally **"is caused by"**.

   If any assertion fails, **delete the link** (`deleteIssueLink`, or raw REST `DELETE /rest/api/3/issueLink/{linkId}`), recreate it per the table above, and re-verify. 🔴 Never leave a reversed link in place, and never report success on assertion 1 alone — a link that exists is not a link that is correct.

   In audit.md, log the direction in **parameter terms plus the verified read-back**: `inwardIssue=<originating key> --causes--> outwardIssue=<bug>; verified: <bug> shows <originating key> under "is caused by" (link id N)`. 🔴 A bare phrase like "linked <bug> is caused by <key>" is NOT sufficient — it reads identically whether or not the call was made backwards, so it cannot detect this defect after the fact.

   This is the ONLY path taken whenever "is caused by" is available: no `Relates` link is created and no explanatory comment is posted.

3b. **Fallback when no "is caused by" link type exists — generic link on `Relates to` + comment, BOTH, AUTOMATIC (no prompt).** Do NOT stop and do NOT ask the user to link manually. Do both of the following, in this order:

   **1 Link generically** — `createIssueLink` using the instance's general-association type (`Relates to` only). This makes the originating ticket visible and navigable from the bug's **Linked issues** panel, which a comment alone cannot do. ⚠️ `Relates` is **symmetric** — it carries no direction, so on its own it does NOT express "is caused by". It is a navigation aid only; is what records the actual relationship.

   **2 Comment the real relationship** — `addCommentToJiraIssue` on the bug. This comment is the **authoritative record of causation** whenever ① is a generic link. Keep it exactly this plain — formal, no emoji, no decoration:

   ```markdown
   **Is caused by**: [PROJ-102](<site-base-url>/browse/PROJ-102), [PROJ-456](<site-base-url>/browse/PROJ-456)

   The "is caused by" link type is not available on this Jira instance, so this defect has
   been linked to the above work item(s) as "relates to" instead. The direction of causation
   is recorded here: this defect is caused by the work item(s) listed above.

   Traced from the commit that introduced the defective line(s).
   ```

   Verify BOTH the link and the comment landed. In audit.md, log that the fallback path was used, which generic type was chosen, **the full list of link types the instance actually returned** (so an admin can see what's missing), and the same evidence chain as a real causal link.

   🔴 The generic link is **only ever** created on this fallback path, and **never without** the comment — a bare `Relates` link would silently lose the direction of causation. If the comment fails to post, remove the generic link (or, if removal fails, log the inconsistency prominently). If the instance has no general-association type either, post the comment alone.

   In the Step 5 summary, tell the user that adding an **"is caused by"** link type to the instance (Jira admin → Issues → Issue linking) would make the relationship queryable in JQL (`issueLinkType = "is caused by"`) — which the fallback path cannot provide.

**3c. ADO / GITHUB / LOCAL mechanics** (per `common/tracker-sync.md` Section 7 — no typed "is caused by" relation exists on these platforms, so a comment is always the authoritative record):
- **ADO**: best-effort `az boards work-item relation add --relation-type "System.LinkTypes.Related"` (the closest native type — carries no direction/semantics on its own) PLUS a mandatory discussion comment on the bug work item stating the causation explicitly (`az boards work-item update --discussion "Caused by work item #[ORIGIN-ID] — <one-line reason>"`). The comment is authoritative; the `Related` link is metadata only.
- **GITHUB**: no typed relation is reachable via `gh` — record causation as a plain comment on the bug issue (`gh issue comment [BUG-NUMBER] --body "Caused by #[ORIGIN-NUMBER] — <one-line reason>"`; GitHub auto-links the `#N` reference). This comment IS the record.
- **LOCAL**: write the causation directly into the bug's entry in `stories.md` / `impact-analysis.md` as a plain note (`Caused by: Story 1.3` or `Caused by: BUG-LOCAL-2`) — no external call.
4. Log every created link in audit.md with the complete evidence chain: `file:line` → introducing commit SHA → PR → matched source (`pr-title` / `commit-subject` / `branch`) → originating item → link/comment mechanism used. Log failures and skips with the same detail.
5. Announce the created links in the Step 5 completion summary.

### 5d. Announcement (🤖 AUTOMATIC — no approval gate)

Present the Impact Analysis summary (including the Provenance Verdict table, any `ai-generated-defect` label applied in 5b, and any links created in 5c) as an **announcement**, then **proceed straight to Step 6 — do NOT ask for approval and do NOT block.**

The impact analysis is evidence-based (`file:line` citations, git-traced provenance) and is not the last word: it is re-validated against the current code at `bug-fix-implement` Step 4.2, and its conclusions are re-surfaced inside the announced fix plan (`bug-fix-implement` Step 4). Gating it here would present the same content twice.

Log in audit.md that the impact analysis was completed and auto-approved, with the affected-file list and the provenance verdicts. If the user volunteers a correction ("you missed file X", "that's not the root cause"), update `impact-analysis.md`, re-announce, and continue — that is an interrupt, not a gate.

## Step 6 — Single Story (replaces User Stories + Dependency Graph)

1. Write **exactly ONE story** to `.spec/aire-docs/planning/user-stories/stories.md`, derived from the ticket + requirements + impact analysis: story ID `1.1`, title = the fix, acceptance criteria = defect resolved + regression-safe (from the ticket's expected behavior). Do NOT ask team size, do NOT generate personas beyond what the ticket implies, do NOT ask about pushing to the tracker (the ticket already exists, or for LOCAL never existed externally — no new issue is ever created), do NOT create `dependency-graph.yml`.
2. Populate the Story Tracker in `aire-state.md` with the single row:
   | Story | Title | Requires | Tracker ID | Status | Start | End | Recorded |
   |-------|-------|----------|------------|--------|-------|-----|----------|
   | 1.1 | [Fix title] | none | PROJ-123 (or BUG-LOCAL-N for LOCAL) | 🟢 Ready for Development | | | [timestamp] |
   The Tracker ID column is the **existing defect ticket** — the Tracker Sync Rule applies to it at every status change.
3. **Wait for explicit approval** of the story; log the response verbatim.

## Step 7 — Workflow Planning (as-is)

Execute `planning/workflow-planning.md`: determine which Implementation design stages EXECUTE/SKIP for this fix (most bugs skip most design stages), generate the execution plan + visualization (validate Mermaid), **announce it, and proceed automatically** — that file's Step 9/10 are an announcement, not an approval gate. Each design stage the plan selects still runs its own approval when it executes.

## Step 8 — Implementation Design Stages (CONDITIONAL, as-is)

Run the system-level design stages the plan selected (Functional Design → NFR Requirements → NFR Design → Infrastructure Design), each per its rule file with its standardized 2-option completion message and approval gate. Scope each to the bug-brief + impact analysis.

**📐 Derive the architecture rubric (automatic, no gate — after the last design stage, or immediately when all design stages were skipped)**: per `common/eval-framework.md` Section 3, derive `.evals/rubrics/architecture-rubric.json` from the design artifacts produced here plus the registered `## Design References`, version it, and commit it with the design artifacts at Step 9. **Most bugs skip most design stages** — when there is nothing to derive from, apply the Section 3 **fallback chain** (a prior cycle's committed rubric → the reverse-engineering artifacts → J1 recorded `N/A`) and record which link was used. 🔴 Never hand-write a generic rubric and never score J1 against a borrowed or unrelated one. Also create `.evals/rubrics/security-rubric.json` (OWASP-based, per `implementation/architecture-doc.md` Section 4.1) and `.evals/config.json` from the eval-framework.md Section 1 template if they do not exist yet. Log in audit.md.

## Step 9 — 🛑 ve HANDOFF BREAK → then continue into `bug-fix-implement`

After the design stages complete (or are all skipped), mark in `aire-state.md`: `Design complete — awaiting bug-fix-implement`. Log in audit.md.

**This is a deliberate BREAK in the flow.** The analysis + design artifacts are everything the ve needs, and the ve must not have to wait for the fix. So before the fix is built:

1. **Commit + push the analysis and design artifacts on the bug branch (automatic — this is what unblocks ve)**: stage `.spec/aire-docs/planning/**` (bug-brief, requirements, impact analysis, the single story), `.spec/aire-docs/implementation/design/**`, the updated `aire-state.md` and `audit.md`; commit on the bug branch with an `AIRE-Version: [N]` trailer (`[N]` read live from `CLAUDE.md`); push to origin. Announce the commit hash + pushed branch and log both in audit.md. 🔴 If the push fails, say so explicitly and tell the user to push manually — **the ve cannot start until this branch is on origin**. Still no `[BUG]` PR here.
2. Present the break message below and **block on its yes/no**.

```markdown
# ✅ Bug Analysis Done — Design Artifacts Pushed

🐞 **Ticket**: [TICKET-ID] — [title]  ([ai-generated-defect label applied / human-origin / undetermined])
🔗 **Caused by**: [PROJ-102, PROJ-456 — linked/commented per the configured tracker / none resolvable]
📍 **Impact**: [N] files identified in .spec/aire-docs/planning/impact-analysis.md
🧩 Design stages: [list which ran vs were skipped]
🌿 Branch: bug/[TICKET-ID]-[title] (cut from [base branch]) — analysis + design **committed and pushed** ([commit hash])

> **🧪 <u>**ve — start NOW, in parallel. The fix does not have to exist.**</u>**
> 1️⃣  `git fetch origin && git checkout bug/[TICKET-ID]-[title] && git pull --ff-only`
> 2️⃣  Type **`/ve-implement [TICKET-ID]`**
>     It cuts `ve/[TICKET-ID]-[title]` from this branch, writes the MANUAL test steps to
>     `.spec/aire-docs/tests/[TICKET-ID]-[title]/` from the ticket's acceptance criteria, and raises its
>     own PR back into `bug/[TICKET-ID]-[title]` — so the test docs ride the `[BUG]` PR into [base branch].

> **🔧 <u>**DEV — continue to the fix implementation**</u>**
> ❓ **Continue to bug fix implementation now? (yes / no)**
> **yes** → everything below runs automatically, with no further questions: baseline regression →
>           fix plan (announced) → fix + unit tests (≥90% coverage) → FULL regression → auto code
>           review, with any findings auto-remediated and re-reviewed until clean → `[BUG]` PR to [base branch]
>           → auto PR review → then STOP (the cycle archive is MANUAL — you run `archive-epic`
>           after the ve test-plan PR merges into the bug branch).
> **no**  → I halt here; the state is saved. Resume any time with `ticket-implement [TICKET-ID]`
>           (or `bug-fix-implement`) and it picks up at the fix.

🔴 Use `/ve-implement` and the keywords EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

3. **Block until the user answers.** Log the raw answer in audit.md.
   - On **no** — halt here. The break is the end of the run; say nothing further.
   - On **yes** — read `workflows/bug-fix-implement.md` and follow it exactly from its Step 1, in the same session, as if the user had typed `bug-fix-implement`. That workflow is **fully automatic** — it asks nothing: the fix plan is announced and executed, and any code-review finding is auto-remediated and re-reviewed until the verdict is clean, after which the `[BUG]` PR is raised on its own.

Substitute every placeholder (`[TICKET-ID]`, `[base branch]`, `[commit hash]`) with real values — never ship a placeholder to the user.

---

## Critical Rules
- 🔴 EVERY audit entry carries the `**JIRA TICKET**:` field.
- 🔴 Step 9 is a **BREAK, not a stop-and-wait-for-a-keyword**: ALWAYS commit + push the analysis/design artifacts on the bug branch FIRST (the ve's `/ve-implement` needs them on origin), present the ve handoff, then ask the yes/no. On **yes** continuation into `bug-fix-implement` happens in the same session — no second keyword. On **no**, halt with state saved. The yes/no is **flow control, deliberately unnumbered** — never write "GATE" into its audit heading. It is the LAST question of the entire bug cycle: `bug-fix-implement` has no gates.
- 🔴 The Step 9 break NEVER blocks the ve on the dev: the ve's `/ve-implement [JIRA-ID]` run is independent of the yes/no answer and of the fix existing at all.
- 🔴 This workflow owns **NO numbered gate**, and neither does `bug-fix-implement` — the framework has no numbered gates left. Its own approvals (requirements, story) are stage approvals; NEVER write "GATE" into an audit heading from this file.
- 🔴 ONE branch (`bug/...`), ONE story, NO dependency graph, NO new Jira issues, NO epic branch, NO Parent-Epic sync.
- 🔴 NO PR at requirements approval — the single `[BUG]` PR is raised by `bug-fix-implement` after review approval.
- 🔴 AI-origin labeling is evidence-based, **line-level** (introducing commit of the defective line(s), per `agents/defect-provenance-analyst.md`) and **AUTOMATIC — never confirm-first**: on positive evidence ("ai-generated" PR label OR Claude co-author trailer OR `AIRE-Version:` trailer) apply `ai-generated-defect`, verify, announce, log the full evidence chain. "Undetermined" is never labeled — which is exactly why no confirmation is needed.
- 🔴 Impact Analysis (Step 5d) is **announced, never gated** — it is re-validated at `bug-fix-implement` Step 4.2 and re-surfaced inside the announced fix plan.
- 🔴 The **"is caused by" link** to the originating ticket (Step 5c) is created **automatically — no confirmation** — for every originating key the analyst resolves on positive evidence, whether the defective line was AI-generated or human-written. The originating ticket may be a **story, a bug, or an enhancement** (all three producers stamp their Jira key on the commit subject, PR title, and branch). Never link on a guessed key, never self-link, and never guess the Jira link type — resolve it via `getIssueLinkTypes` at runtime. If the instance has no causal ("is caused by") type, fall back automatically to a generic `Relates` link **plus** a comment recording the direction — both, never the bare link alone.
- 🔴 The defect ticket is NEVER transitioned to "Ready for Testing" by this flow 
- 🔴 Security Baseline extension always applies; other extensions per their recorded opt-ins.
