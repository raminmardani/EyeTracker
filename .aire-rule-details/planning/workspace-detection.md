# Workspace Detection

**Purpose**: Determine workspace state and check for existing aire projects

## Step 1: Check for Existing aire Project

Check if `.spec/aire-docs/aire-state.md` exists:
- **If exists**: Resume from last phase (load context from previous phases)
- **If not exists**: Continue with new project assessment

## Step 1.5: Capture Session Identity (silent, email-only, audit.md ONLY)

Apply the **MANDATORY: Session Identity Capture** rules from the root workflow file (CLAUDE.md / equivalent). No shell commands, MCP, or external calls — and NO confirmation question to the user:

1. Read the **session email** from the session context provided by the AI environment (Claude Code injects the logged-in account's email automatically). Use it AS-IS — do NOT ask the user to confirm it, and do NOT derive or record a display name (email is the only identity field)
2. Only if the environment provides NO session email (non-Claude environments), ask the user for their email once
3. **Do NOT persist it anywhere**: the email goes ONLY into audit.md entries as the `**User Email**:` field — NEVER into aire-state.md (no `## Session Identity` section) or any other artifact
4. From this point stamp every audit.md entry with `**User Email**:` (read live from the session context) — at every approval flow this field records who approved. A different developer resuming the project automatically logs under their own session email

## Step 1.6: Sync the Local Base Branch with Remote (MANDATORY, before any freshness assessment)

**Why**: A previous cycle's `stitch-delta` commits the refreshed root reverse engineering docs + the `stitch-epic.md` ledger to the **remote** base branch (or, under branch protection, to an unmerged `docs/stitch-delta-*` PR). A new session's local base branch is often **behind** that. If Step 3 judges RE-doc freshness against a **stale local checkout**, it wrongly concludes the stitch never happened and that the RE docs are out of date. Sync FIRST, then judge.

**Run BEFORE scanning for code and BEFORE the Step 3 freshness assessment:**

1. Record the base branch: `git branch --show-current` (the branch the workflow started on — do NOT assume `main`). This runs before any epic branch exists, so the current branch IS the base branch.
2. `git fetch origin` — update remote-tracking refs.
3. **Fast-forward the local base branch to the remote**:
   - If the working tree is clean and the local base can fast-forward: `git pull --ff-only`.
   - **If the tree is dirty or the branches have diverged**: do NOT clobber. Show `git status` / the divergence and ask the user how to proceed (stash, commit, or continue against the current local state). Log the choice in audit.md.
4. **Detect a pending (unmerged) stitch**: check for an open stitch PR into the base branch — `gh pr list --base <base> --state open --search "stitch-delta in:title"` (or head branch `docs/stitch-delta-*`). If one exists, do NOT treat the RE docs as needing regeneration in Step 3 — instead inform the user a stitch is **pending merge** and that the RE docs will be current once that PR merges.
5. Log the sync result (fetched, fast-forwarded to `<sha>`, or the user's chosen action) in audit.md.

This step ONLY synchronizes the local base branch; it does not create the epic branch (that is Step 4.5).

## Step 1.7: Tracker Selection (ask ONCE, record, reuse on resume)

**Skip entirely if `aire-state.md` already contains a `## Tracker` section** (resumed project) — reuse the recorded value, do NOT re-ask.

Otherwise, load `common/tracker-sync.md` Section 1 and execute it exactly: ask which issue tracker to use (JIRA / ADO / GITHUB / LOCAL), record the answer in `## Tracker` in `.spec/aire-docs/aire-state.md`, then ask the type-specific one-time follow-up (ADO org/project, or GitHub org/repo — skipped entirely for LOCAL and for JIRA). Verify CLI/MCP auth for ADO (`az account show`) and GitHub (`gh auth status`) at this point; LOCAL requires no auth check at all.

Log the question and the complete raw answer in `audit.md`. This MUST run before Step 4.5 (Epic Branch Creation, which needs no tracker info) and before Parent Epic Capture (run by CLAUDE.md immediately after Workspace Detection completes) — Parent Epic Capture depends on knowing which tracker to query.

## Step 2: Scan Workspace for Existing Code

**Determine if workspace has existing code:**
- Scan workspace for source code files (.java, .py, .js, .ts, .jsx, .tsx, .kt, .kts, .scala, .groovy, .go, .rs, .rb, .php, .c, .h, .cpp, .hpp, .cc, .cs, .fs, etc.)
- Check for build files (pom.xml, package.json, build.gradle, etc.)
- Look for project structure indicators
- Identify workspace root directory (NOT .spec/aire-docs/)

**Record findings:**
```markdown
## Workspace State
- **Existing Code**: [Yes/No]
- **Programming Languages**: [List if found]
- **Build System**: [Maven/Gradle/npm/etc. if found]
- **Project Structure**: [Monolith/Microservices/Library/Empty]
- **Workspace Root**: [Absolute path]
```

## Step 3: Determine Next Phase

**IF workspace is empty (no existing code)**:
- Set flag: `brownfield = false`
- Next phase: Requirements Analysis

**IF workspace has existing code**:
- Set flag: `brownfield = true`
- **Search the ENTIRE repo for existing reverse engineering artifacts — they can live ANYWHERE, not only at the default path.** Folder and file names are always the same, so search by name:
  1. First check the default location: `.spec/aire-docs/planning/reverse-engineering/`
  2. If not there, glob the whole workspace for a directory named `reverse-engineering/` (e.g., `**/reverse-engineering/`) at any depth
  3. Also glob for the standard artifact filenames anywhere in the repo: `business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `component-inventory.md`, `technology-stack.md`, `dependencies.md`, `code-quality-assessment.md`, `reverse-engineering-timestamp.md` — a directory containing several of these IS the artifact set even if the folder is named differently
  4. If found outside the default path, record the discovered location in `aire-state.md` (`## Workspace State` → `Reverse Engineering Artifacts: <path>`) and use THAT path everywhere the artifacts are loaded later (Requirements Analysis, User Stories, design stages)
- **IF reverse engineering artifacts exist (at ANY location found above)** — do NOT regenerate them:
    - **Judge freshness against the stitch ledger, NOT file timestamps** (the local base was already synced in Step 1.6, so the ledger and delta folders now reflect the remote). Timestamps are unreliable across clones/checkouts and are the reason a stitched-but-stale local checkout was previously misread as "out of date":
      1. Read the ledger `.spec/aire-docs/planning/reverse-engineering/stitch-epic.md` and scan `.spec/aire-docs/planning/reverse-engineering/delta/*/` folders.
      2. A delta folder present on disk but NOT recorded in the ledger = a **pending un-stitched delta** → artifacts are stale.
      3. Every delta folder is recorded in the ledger (or there are none) = artifacts are **current** — the previous cycle's stitch is already reflected.
    - **Honor the pending-stitch signal from Step 1.6**: if Step 1.6 found an open `docs/stitch-delta-*` PR into the base, do NOT rerun Reverse Engineering — tell the user the stitch is **pending merge** and proceed with the existing artifacts (the docs become current when that PR merges).
    - **IF artifacts are current**: Load them, skip to Requirements Analysis
    - **IF artifacts are stale (un-stitched delta on disk, no pending stitch PR)**: Next phase is Reverse Engineering (rerun to refresh artifacts) — or offer to run `stitch-delta` to fold the pending delta in
    - **IF user explicitly requests rerun**: Next phase is Reverse Engineering regardless of freshness
- **IF no reverse engineering artifacts**: Check `aire-archives/epics/`, `aire-archives/bugs/` AND `aire-archives/enhancements/` for archive folders (created by the `archive-epic` skill at the end of a previous epic, bug, or enhancement release cycle)
    - **IF archives exist**: The most recently archived cycle folder — across BOTH subfolders, by archive date in `archive-manifest.md` — contains the latest stitched root reverse engineering documents (`<archive>/.spec/aire-docs/planning/reverse-engineering/`). Ask the user:
      ```
      ❓ No live reverse engineering artifacts found, but archived artifacts exist
         from the last release cycle ([EPIC-KEY or BUG-KEY] — [name], archived [date]).

      A) Restore the archived reverse engineering documents 
      B) Run fresh reverse engineering against the current codebase (recommended if the code changed since the archive)

      [Answer]:
      ```
      On A: copy the archived `reverse-engineering/` folder into `.spec/aire-docs/planning/reverse-engineering/`, log the restore in audit.md, then proceed to Requirements Analysis. On B: next phase is Reverse Engineering.
    - **IF no archives**: Next phase is Reverse Engineering

**Monorepo note**: Reverse engineering artifacts are always checked/generated at the workspace ROOT only — one artifact set covering all modules. Never look for or create per-module artifact sets (see `planning/reverse-engineering.md` "Monorepo Handling").

## Step 4: Create Initial State File

Create `.spec/aire-docs/aire-state.md`:

```markdown
# aire State Tracking

## Project Information
- **Project Type**: [Greenfield/Brownfield]
- **Start Date**: [ISO timestamp]
- **Current Stage**: PLANNING - Workspace Detection

## Workspace State
- **Existing Code**: [Yes/No]
- **Reverse Engineering Needed**: [Yes/No]
- **Workspace Root**: [Absolute path]

## Code Location Rules
- **Application Code**: Workspace root (NEVER in .spec/aire-docs/)
- **Documentation**: .spec/aire-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Stage Progress
[Will be populated as workflow progresses]
```

## Step 4.5: Create the Epic Branch (automatic)

Load `common/branching-strategy.md` and execute **Section 1 — Epic Branch Creation**:
- Record the **base branch** (the branch the workflow started on — do not assume `main`)
- Create `epic/<EPIC-KEY>-<kebab-case-epic-title>` automatically (confirm a name with the user only when no Epic was provided)
- Record `## Branching` (Base Branch, Epic Branch) in `.spec/aire-docs/aire-state.md`
- **Skip** if `## Branching` already exists (resumed project) — verify the epic branch exists and switch to it

Log the branch creation (name + base branch) in audit.md.

## Step 4.6: Ensure the Context Project Folder (ALL flows — check first, create only if missing)

Ensure **`.spec/context-project/`** exists with its two subfolders. This is the human-authored home for
everything a person wants the framework to read — the framework **never auto-populates it and never
auto-scans it**.

```text
.spec/context-project/
├── existing-knowledge/    # How the CURRENT system works — module notes, interview.md,
│                          # where things live, what each component does.
│                          # Brownfield only; leave empty on greenfield.
└── new-references/        # What to BUILD — UX wireframes, design mockups, UI specs,
                           # API specs, architecture diagrams, research docs.
                           # Applies to BOTH greenfield and brownfield.
```

- **Check first**: if `.spec/context-project/` (or either subfolder) already exists — reuse AS-IS.
  Do NOT recreate, empty, overwrite or delete it or anything under it.
- **Only if absent**: create the folder and both empty subfolders. Do NOT create a README inside them.
- `existing-knowledge/` uses one subfolder per repo module, named **exactly** after the module
  (e.g. `existing-knowledge/ALIX.BMS/interview.md`).
- This is a safety net so the folders exist even on flows that skip reverse engineering.

## Step 4.7: Context Opt-In (ALL flows — ask ONCE, in chat, record in state)

**Skip entirely if `aire-state.md` already contains a `## Context Project` section** — a resumed
project already answered. Reuse the recorded values; do NOT re-ask.

🔴 **ASK THIS IN THE CHAT SESSION ONLY.** Do NOT create a question `.md` file for it, and do not
apply `common/question-format-guide.md`'s file-based convention here — this question is answered
conversationally, in one turn, and only the ANSWER is persisted (to `aire-state.md` and `audit.md`).

Ask both parts together, once:

```
Do you have any context I should use for this work?

1) Existing knowledge — human-authored notes on how the CURRENT system works
   (module notes, interview.md, where things live). Place under
   .spec/context-project/existing-knowledge/
   [brownfield only — omit this part on greenfield]

2) New references — what to BUILD: UX wireframes, design mockups, UI specs,
   API specs, architecture diagrams, research docs. Place under
   .spec/context-project/new-references/

Reply with the exact path(s) to use, or "no" for either part.

[Answer]:
```

Record the answer in `.spec/aire-docs/aire-state.md`:

```markdown
## Context Project
- **Existing Knowledge**: [Yes/No]
- **Existing Knowledge Path(s)**: [exact path(s) the user gave — or —]
- **New References**: [Yes/No]
- **New Reference Path(s)**: [exact path(s) the user gave — or —]
```

Rules:
- Record the paths **exactly as given**. Only those paths are ever read — there is no auto-scan of the
  rest of `.spec/context-project/`.
- If a supplied path does not exist, say so and re-ask that part.
- On greenfield, ask part 2 only; record `Existing Knowledge: No`.
- Log the prompt and the user's complete raw answer in `audit.md`.
- Downstream, **Requirements Analysis**, **Workflow Planning**, **Application Design**, **Functional
  Design**, **User Stories** and **Code Generation** read `## Context Project`:
  **existing-knowledge** grounds understanding of what already exists; **new-references** is
  authoritative for what to build — wireframes and mockups dictate the UI, API specs dictate the
  endpoints and shapes.

## Step 4.8: Load the Design Reference Guardrail (NO question — enforcement only)

**Load `common/design-reference-grounding.md` and apply it for the remainder of the workflow.**

**Do NOT ask the user anything here.** This step adds no prompt. The guardrail is purely reactive: whenever the user names a file path, folder path, spec document, screenshot, or design URL in ANY input at ANY stage — the initial request, a clarifying answer, a request-changes message, a remediation comment — that artifact MUST be registered in `## Design References` in `aire-state.md` and its **actual content read** in the stage where it was named (rules DR-1 / DR-2 / DR-4), then re-consulted before design and code artifacts (DR-5).

If the user's initial request already names such an artifact, register it now and log it in `audit.md`.

## Step 5: Present Completion Message

**For Brownfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Brownfield project
• [AI-generated summary of workspace findings in bullet points]
• **Next Step**: Proceeding to **Reverse Engineering** to analyze existing codebase...
```

**For Greenfield Projects:**
```markdown
# 🔍 Workspace Detection Complete

Workspace analysis findings:
• **Project Type**: Greenfield project
• **Next Step**: Proceeding to **Requirements Analysis**...
```

## Step 6: Automatically Proceed

- **No user approval required** - this is informational only
- Automatically proceed to next phase:
  - **Brownfield**: Reverse Engineering (if no existing artifacts) or Requirements Analysis (if artifacts exist)
  - **Greenfield**: Requirements Analysis
