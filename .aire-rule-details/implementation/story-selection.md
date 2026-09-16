# Story Selection - Detailed Steps

**Purpose**: Before generating code, determine WHICH story is being implemented — the user types the story's **Tracker ID** (a Jira key, an ADO work item ID, a GitHub issue number) or, for a `LOCAL` tracker, the local Story ID (`N.M`) directly — run the Doability Gate, and move it from `🟢 Ready for Development` to `🔵 In Development` **automatically** (picking the story is the claim — no confirmation is asked for this transition, on any tracker or the local tracker).

**Story statuses** (the only valid Story Tracker statuses — see the Story Status Lifecycle in `CLAUDE.md`):
`🟢 Ready for Development` → (this stage, on `dev-implement`) → `🔵 In Development` (stays here through code gen, review, PR raise, PR review) → (after the PR is **MERGED**) → `🧪 Ready for Testing`.

**Runs**: At the start of Code Generation (Step 0), once per story, when the user invokes `dev-implement`. Mandatory.

## Prerequisites
- User Stories stage complete (`.spec/aire-docs/planning/user-stories/stories.md` exists)
- Dependency Graph stage complete (`.spec/aire-docs/planning/dependency-graph.yml` exists with `requires`/`enables`)
- `.spec/aire-docs/aire-state.md` contains a `## Story Tracker` table and a `## Tracker` section (`Type: JIRA | ADO | GITHUB | LOCAL`)

---

## Step 0: No Bulk PR-Merge Reconciliation Here (by design)

Story Selection does **NOT** scan every `🔵 In Development` story and promote it to `🧪 Ready for Testing`
Instead, dependency readiness is checked **live, per prerequisite, only for the story being selected** — see the **Doability Gate (Step 4)** below. Nothing in this step mutates the Story Tracker or the external tracker.

## Step 1: Verify Tracker Availability

Read `## Tracker` → `Type` in `.spec/aire-docs/aire-state.md` and verify accordingly:
- [ ] **JIRA**: confirm the Atlassian MCP is connected. If NOT available, STOP and tell the user Jira integration is required (connect the Atlassian MCP first).
- [ ] **ADO**: confirm `az boards` is authenticated (`az account show`). If not, STOP and tell the user to run `az login` first.
- [ ] **GITHUB**: confirm `gh` is authenticated (`gh auth status`). If not, STOP and tell the user to run `gh auth login` first.
- [ ] **LOCAL**: nothing to verify — proceed directly, no external integration is required at all.

## Step 2: Present Story Selection Prompt

Present the following, tailored to the configured tracker:

```text
Which story would you like to develop?

Type the story's Tracker ID (e.g. PROJ-123 / ADO work item ID / GitHub issue number),
or the Story ID (e.g. 1.2) if the tracker is Local:
```

**DO NOT guess which story to implement. Wait for the user to type the ID.**

## Step 3: Resolve the Selected Story — 🤖 NO CONFIRMATION
- [ ] Take the ID the user typed — do NOT assume it.
- [ ] Resolve it per `common/tracker-sync.md` Section 8 (adapted here to a STORY rather than a bug/enhancement ticket):
  - **JIRA**: fetch the issue (`getJiraIssue`) and show its summary, status, priority, and acceptance criteria as an announcement.
  - **ADO**: fetch via `az boards work-item show --id [ID] --project "{PROJECT}"` and show the same fields.
  - **GITHUB**: fetch via `gh issue view [NUMBER] --repo ORG/REPO --json title,body,labels,state` and show the same fields.
  - **LOCAL**: no fetch needed — resolve directly from `stories.md` / the Story Tracker by Story ID and show the same fields from there.
- [ ] 🔴 **Do NOT ask "Implement this story? (yes / no)".** The user typing the ID IS the selection — re-confirming it is the same decision twice. Display the resolved story and continue straight to the Doability Gate.
  - Only exception: the ID does not exist, or resolves to an issue that is **not a story of this epic** — then report the mismatch and re-ask for the ID (that is error handling, not confirmation).
- [ ] Map the resolved issue to a local story in `stories.md` via the `Tracker ID` column (or the Story ID directly, for LOCAL). If no matching local story exists, create one from the issue body so code generation has a reference. Note its `Requires`.

## Step 4: 🚦 Doability Gate (MANDATORY — live PR-merge check; `dev-implement` NEVER merges anything)
- [ ] Look up the chosen story in `dependency-graph.yml` → read its `requires`. No `requires` (or empty) → doable, skip to Step 5.
- [ ] For EACH story in `requires`, resolve doability directly:
  - If its Story Tracker `Status` already reads `🧪 Ready for Testing` → doable, no further check needed for this prerequisite.
  - Otherwise, read its recorded `PR` column. If a PR URL is present, check its real state LIVE:
    ```
    gh pr view <PR-URL-or-number> --json state,mergedAt,baseRefName,isDraft,reviewDecision,mergeable,mergeStateStatus,author,reviews
    ```
    - `mergedAt` set (state MERGED) → doable.
    - Anything else (OPEN — whether approved or not, CLOSED without merging, or no PR recorded yet) → **NOT doable.** 🔴 **`dev-implement` NEVER merges a prerequisite's PR itself, not even one that is already approved** — merging a PR is always a manual action the user performs (in GitHub / the tracker's PR UI), never something this workflow does on the user's behalf, with or without asking.
- [ ] **Doable IFF every prerequisite resolves doable above** — i.e. each has its PR **MERGED into the epic branch** (its code is present there). If ANY prerequisite is NOT doable, 🛑 **STOP THE RUN** (do not loop back to Step 2, do not let the user bypass this gate, and do not offer to merge it):
  ```
  🛑 Cannot start Story [N.M] yet.
     It requires Story [X.Y] ([TRACKER-ID]), whose PR is not merged yet:
       • Story [X.Y] — [TRACKER-ID] — <PR URL, or "no PR raised yet"> — status: <OPEN, approved by [reviewer] — go merge it / OPEN, not yet approved / CLOSED (not merged) / none>

       [list every unmet prerequisite]

  ➡️ Merge Story [X.Y]'s PR into the epic branch yourself, then run `dev-implement`
     again to develop Story [N.M].
  ```
  Log the block (which prerequisite(s) and their live-checked PR state) in audit.md, then END this `dev-implement` run. No story/tracker status has changed at this point — Step 5 (the move to `🔵 In Development`) has not run yet. The user re-invokes `dev-implement` once the blocking PR(s) are merged.
- [ ] If every prerequisite resolves doable, proceed to Step 5. This live check is authoritative and agrees with the branch-cut dependency-merge check in `common/branching-strategy.md` Section 3 (which remains as a defense-in-depth safety net at branch-creation time, e.g. if a merge were undone between this gate and the branch cut).

## Step 5: Move Story to In Development (AUTOMATIC — no confirmation)

**Picking a story IS the claim.** Once the user selects the story and the Doability Gate passes, move it to `🔵 In Development` automatically — do NOT ask the user to confirm the tracker transition or the local tracker update. Dispatch per `common/tracker-sync.md` Section 4 (transition) and Section 5 (assignment):

- [ ] If the selected story has a non-LOCAL Tracker ID, transition immediately:
  - **JIRA**: `@atlassian transitionJiraIssue [TRACKER-ID] -> "In Development"`, add comment `"Development started via aire (story moved to In Development)."`
  - **ADO**: `az boards work-item update --id [TRACKER-ID] --state "Active"`, plus a discussion comment via `az boards work-item update --discussion "..."`.
  - **GITHUB**: swap the status label to `status:in-development` (`gh issue edit [NUMBER] --remove-label "status:ready-for-dev" --add-label "status:in-development"`), plus a comment via `gh issue comment`.
  - **LOCAL**: no external call — this step is a no-op beyond the Story Tracker update in Step 6.
- [ ] **VERIFY** (JIRA/ADO/GITHUB): fetch the issue back and confirm the transition landed. If rejected, list available transitions/states and retry with the exact name. Still failing → STOP and report.
- [ ] **👤 ASSIGN THE STORY TO THE OPERATOR (AUTOMATIC — same claim)**: the developer who typed `dev-implement` claims the story, so set them as the assignee — no confirmation asked. Dispatch per `common/tracker-sync.md` Section 5:
  1. Read the operator's **email** LIVE from the session context (the same email stamped as `**User Email**:` in audit.md — never ask, never cache).
  2. **JIRA**: resolve the account via `lookupJiraAccountId` with that email, then `editJiraIssue` with `assignee = <resolved accountId>`.
  3. **ADO**: `az boards work-item update --id [TRACKER-ID] --assigned-to "<session-email>"` directly (ADO accepts email/UPN).
  4. **GITHUB**: ask ONCE per session for the operator's GitHub username (cache it in `## Tracker` as `GitHub Username:` — email does not map to a login), then `gh issue edit [NUMBER] --add-assignee <login>`.
  5. **LOCAL**: no assignee concept — skip; optionally note the operator's session email as a comment on the Story Tracker row.
  6. **VERIFY** (JIRA/ADO/GITHUB): fetch the issue back and confirm the assignee matches. If the identity resolves to NO account (or multiple ambiguous matches), do NOT guess — leave the assignee unchanged, warn the user (`⚠️ Could not resolve <identity> to a tracker account — story left unassigned; assign manually.`), and log the failure in audit.md. Assignment failure is NON-blocking: development proceeds either way.
- [ ] Announce the change to the user (informational, not a question): "🔵 Story [N.M] claimed — [Tracker Type] [TRACKER-ID or 'local tracker'] moved to In Development, assigned to [session email/username]."
- [ ] **🔷 EPIC → In Development (AUTOMATIC — first story only)**: If this is the FIRST story to move to `🔵 In Development` (no other story in the Story Tracker is `🔵 In Development` or `🧪 Ready for Testing`), also transition the **Parent Epic** (from `## Tracker` in `aire-state.md`) to "In Development" using the same per-type mechanism as above, targeting the Epic's ID instead of the story's.
  Verify the transition landed (retry with the exact state/label name if rejected), announce it ("🔷 Epic [EPIC-ID] moved to In Development — development has started."), and log it in audit.md. Skip silently if `## Tracker` records `Parent Epic: none`, if `Type: LOCAL`, or the Epic is already In Development (or beyond).
- [ ] These are the ONLY automatic transitions in the workflow (story → In Development on pick, plus the Epic → In Development on the first pick) — every OTHER status change (e.g., `🧪 Ready for Testing`) still follows the confirm-first Tracker Sync Rule.

## Step 6: Update Story Tracker (AUTOMATIC — no confirmation)
- [ ] In `.spec/aire-docs/aire-state.md` `## Story Tracker`, for the selected story set (without asking):
  - **Status** → `🔵 In Development` (moved from `🟢 Ready for Development`)
  - **Start** → today's date (`YYYY-MM-DD`) if not already set
  - **Recorded** → current timestamp (`YYYY-MM-DD HH:MM`)
- [ ] Append to `.spec/aire-docs/audit.md`: the selected story, the automatic status change `🟢 Ready for Development → 🔵 In Development` (tracker + local, with verification result), and the assignee set (email/username + resolved account, or the resolution failure) with timestamps. The entry MUST include the `**TRACKER ITEM**:` field — the story's Tracker ID as a clickable link where applicable (`[PROJ-XXX](<site-base-url>/browse/PROJ-XXX)` for JIRA, the issue/work-item URL for ADO/GITHUB), or the local Story ID when `Tracker ID = —`/`LOCAL` (see the Audit Entry Format in `workflows/dev-implement.md`).
- [ ] The story now **stays `🔵 In Development`** through Code Generation, the automated Code Review, any Remediate loop, the PR raise, and the auto PR Review — it moves to `🧪 Ready for Testing` ONLY when its PR is **MERGED** into the epic branch, promoted exclusively by the `ve-list-work` skill, after ve has tested it. (dev-implement/story-selection only ever live-check a prerequisite's PR at the Doability Gate — they never promote this story's own tracker status.)

## Step 7: Hand Off to Code Generation
- [ ] Return the resolved story (ID, title, acceptance criteria, Tracker ID/link if any) to Code Generation Part 1.
- [ ] Code Generation proceeds to plan and generate code for this story (implementation, then unit tests to ≥90% coverage) into the application code structure, on the story branch cut from the epic branch (see code-generation.md Critical Rules and `common/branching-strategy.md`).

---

## Critical Rules
- 🔴 Story selection is **tracker-driven** — the user types the story's Tracker ID (JIRA key / ADO work item ID / GitHub issue number) or, for `Type: LOCAL`, the local Story ID directly. If the configured tracker's integration (Atlassian MCP / `az` / `gh`) is unavailable, STOP — except LOCAL, which never requires an integration.
- 🔴 NEVER guess which story to implement — always ask the user to type the ID and wait.
- 🔴 NEVER bypass the Doability Gate — all of a story's `requires` must be confirmed **MERGED** via `gh pr view` at gate time (or already `🧪 Ready for Testing` in the tracker). Any prerequisite that remains unmerged → 🛑 STOP the run with a clear message naming it (never loop back silently, never let the user bypass it).
- 🔴 **`dev-implement` NEVER MERGES A PR, EVER — not automatically, not with confirmation, not even when it is already approved.** A prerequisite's PR approval is always a manual human action performed outside this workflow (GitHub / the tracker's PR UI); merging it is likewise always the user's own action. The Doability Gate only ever reads PR state — it has no merge step of any kind. When the blocking prerequisite is already approved, the stop message says so, so the user knows merging it (themselves) is all that's left.
- 🔴 This gate never writes to the prerequisite's Story Tracker row at all — it only reads live PR state. `Merged`/`Recorded` reflect the user's own merge once it happens; `Status`/`End` change only when `ve-list-work` promotes it to `🧪 Ready for Testing`.
- 🔴 The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`. This stage moves the story to `🔵 In Development` only.
- 🔴 ALWAYS take the ID the user types at development time — do not assume it. Once typed, **do NOT ask them to confirm it** ("Implement this story? yes/no" is removed): show the fetched issue and proceed to the Doability Gate. Re-ask only when the ID is invalid or resolves to the wrong issue.
- 🔴 The `🟢 Ready for Development → 🔵 In Development` transition is AUTOMATIC on story pick — apply it to the configured tracker AND the Story Tracker without asking, ALWAYS verify the transition landed (non-LOCAL), and announce it. All OTHER tracker transitions remain confirm-first per the Tracker Sync Rule.
- 🔴 On every story pick, ALWAYS set the assignee to the operator who invoked `dev-implement`, per `common/tracker-sync.md` Section 5 (automatic, verified where applicable, logged). If the identity can't be resolved, leave unassigned, warn, and continue — assignment failure never blocks development. LOCAL has no assignee concept.
- 🔴 When the FIRST story of the epic moves to `🔵 In Development`, ALWAYS also transition the Parent Epic (from `## Tracker`) to "In Development" automatically — verify (non-LOCAL), announce, and log it.
- 🔴 ALWAYS record the selected story (and its Start/Recorded timestamps) in the Story Tracker before code generation begins.
- 🔴 When a project/repo identifier is needed (e.g., a "pick from the tracker" search), FIRST reuse the value recorded in `aire-state.md` `## Tracker` → `Project Key / Repo / Org`; ask the user only if none is recorded — never hard-code it.
