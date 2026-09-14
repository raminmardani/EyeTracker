# 📦 Archive Epic Agent — Close a Release Cycle (Epic, Bug, or Enhancement)

## 🐞 Bug / ✨ Enhancement Mode (read this first)

This agent closes **epic cycles**, **bug cycles** (`Workflow Type: bug` in `aire-state.md` `## Tracker`, produced by `bug-fix`/`bug-fix-implement`), AND **enhancement cycles** (`Workflow Type: enhancement`, produced by `enhancement-implement`). The steps below are written in epic terms; in **bug or enhancement mode** apply these substitutions everywhere:
- **Cycle ID** = the ticket key (`Parent Ticket`, e.g. `PROJ-123`); **cycle name** = the ticket title. Wherever the steps say `<EPIC-ID>`/`<epic-name-slug>`, use the ticket ID and its slug.
- **Archive path**: epic cycles archive to **`aire-archives/epics/<EPIC-ID>-<epic-name-slug>/`**; bug cycles to **`aire-archives/bugs/<BUG-ID>-<ticket-name-slug>/`**; enhancement cycles to **`aire-archives/enhancements/<ENH-ID>-<ticket-name-slug>/`**. Wherever the steps say `aire-archives/<EPIC-ID>-<epic-name-slug>/`, read the type-appropriate subfolder path. Never write archives directly under `aire-archives/` — always inside `epics/`, `bugs/`, or `enhancements/`.
- **Delta folder** naming is unchanged in shape: `delta/<CYCLE-ID>-<slug>/` (e.g., `delta/PROJ-123-login-timeout/`) — bug and enhancement deltas coexist with epic deltas and are stitched by `stitch-delta` identically.
- **Invocation mode**: **epic mode is the ONLY auto-triggered mode** — pr-generator invokes it on an Epic → Base PR, and that auto-trigger auto-selects workspace-reset option A. 🔴 **Bug and enhancement cycles are ALWAYS operator-invoked (manual)**: `bug-fix-implement` (Step 12) and `enhancement-implement` (Step 19) deliberately do NOT invoke this skill, and pr-generator's Phase 7 auto-trigger explicitly excludes `[BUG]`/`[ENH]` → Base PRs. In bug/enhancement mode, therefore, **always ask the Step 6 workspace-reset question** — never treat those cycles as auto-triggered.
  - **Why bug/enhancement archives are manual**: ve work lands on the cycle branch on its own schedule and is not synchronised with the `[BUG]`/`[ENH]` PR — `/ve-implement` writes `.spec/aire-docs/tests/<TICKET-ID>-<title>/` on its own `ve/...` branch + PR (possibly raised *after* the fix is done), and `ve-list-work` Option C amends an existing test plan later still. Because this skill takes a ONE-SHOT destructive snapshot and then resets the live docs, an archive taken automatically at PR time would silently omit `tests/` or miss later test-plan edits, and nothing would ever re-capture them. The operator archives once everything has landed — see Step 2's ve readiness check.
- **Release Readiness (Step 2) in bug/enhancement mode**: ve signs off **on the cycle branch, before this archive** (`ve-list-work` Option B). 🔴 **The cycle closes on BOTH sign-off outcomes** — approve and reject alike — so the ticket's status is NOT a pass/fail criterion here. What matters is only that the sign-off **happened**:
  - **Ticket `🧪 Ready for Testing`** → ve approved. Archive normally, no warning.
  - **Ticket `🔵 In Development` AND the ticket carries the `ve-rejected` label (or audit.md records an Option B rejection for it)** → ve rejected. This is a **legitimate, expected cycle close, NOT a gap**: the rejection is a completed decision, the follow-up defect is tracked as its own ticket via `/raise-defect`, and this cycle's record (including the rejection) must be archived. Archive normally — **do NOT warn, do NOT recommend re-running `ve-list-work`, and do NOT ask "archive anyway?"**. Note in audit.md and in `archive-manifest.md` that the cycle closed on an ve rejection, naming the follow-up defect key if one is recorded.
  - **Ticket `🔵 In Development` with NO rejection evidence** → sign-off genuinely has not run yet. Only here: warn and ask whether to archive anyway (recommend: no — run `ve-list-work` Option B on this branch first, so the decision is captured in the archive).
  - ALSO verify the `[BUG]` / `[ENH]` PR has been **raised and is still open** (`Bug PR` / `Enhancement PR` in `## Branching`) — it must NOT be merged yet, because this skill's cycle-close commit has to ride it to the base branch. If the PR is already merged, warn loudly: the delta will not reach the base branch and `stitch-delta` will find nothing.

You are a **release manager** closing a release cycle. You will:
1. Generate the epic's **delta reverse engineering artifacts** (epic-namespaced — stitching is NOT done here; it happens post-merge on the base branch via the **`stitch-delta`** skill)
2. **Archive** the complete `.spec/aire-docs/` (including `audit.md`, `aire-state.md`, the root reverse engineering documents, and the epic's delta) into an epic-named archive folder
3. Optionally reset the live workspace for the next epic cycle

**Why no stitching here**: N teams run N epics in parallel. If each epic branch stitched the root docs itself, every PR would carry a different version of the same root documents — guaranteed merge conflicts. Instead, each epic's PR carries ONLY its own delta folder (`delta/<EPIC-ID>-<slug>/`, conflict-free by implementation), and root docs are only ever modified on top of current main by `stitch-delta` after the PR merges.

**Confirm-first ethos applies throughout**: every destructive or irreversible step requires explicit user confirmation. NEVER delete anything before the archive copy is verified.

**The ONE deliberate exception — Step 3a's delta prune (AUTOMATIC, no prompt)**: Step 3a deletes already-stitched delta folders **from the archive copy only**, and runs without asking. This is safe by implementation and is NOT to be turned into a prompt: it removes only content that is already folded into the root reverse engineering documents inside that same archive; the live tree still holds every file at that moment (Step 6 has not run); and it never touches the live `delta/` folder. It is recorded in audit.md and in `archive-manifest.md` instead of being confirmed. No other deletion in this skill may claim this exception.

---

## Step 0: Load the Source Rules

**MANDATORY**: Read and load:

```
.aire-rule-details/planning/reverse-engineering.md
```

Specifically the **"Delta Reverse Engineering & Stitching (End of Release Cycle)"** section — its **Delta Generation** rules govern Step 3 below. (The Stitching Rules are executed later by the `stitch-delta` skill, not here.)

Also load `common/content-validation.md` (content validation for generated delta documents).

---

## Step 1: Preconditions & Epic Identification

1. Verify `.spec/aire-docs/aire-state.md` exists. If not, STOP: tell the user there is no active AIRE project to archive.
2. Resolve the **cycle type and ID**:
   - Read `## Tracker` in `.spec/aire-docs/aire-state.md`. `Workflow Type: bug` → **bug mode**; `Workflow Type: enhancement` → **enhancement mode** (both: Cycle ID = `Parent Ticket`, name from the ticket title / `bug-brief.md` / `enhancement-brief.md`); otherwise **epic mode** (Cycle ID = `Parent Epic`, name from `epic-brief.md`).
   - Fallback: ask the user:
     ```
     ❓ Which Epic, Bug, or Enhancement ticket does this release cycle belong to?
        Provide the ID and name (e.g., "PROJ-50, User Authentication",
        "PROJ-123, Login timeout (bug)" or "PROJ-456, Export to CSV (enhancement)").

     [Answer]:
     ```
3. Derive the archive folder: `aire-archives/epics/<EPIC-ID>-<epic-name-slug>/` (epic mode), `aire-archives/bugs/<BUG-ID>-<ticket-name-slug>/` (bug mode), or `aire-archives/enhancements/<ENH-ID>-<ticket-name-slug>/` (enhancement mode) — kebab-case the name (e.g., `PROJ-50-user-authentication`, `PROJ-456-export-to-csv`).
4. **MANDATORY**: Log the invocation in `.spec/aire-docs/audit.md` (append-only, complete raw input).

---

## Step 2: Release Readiness Check

Read the `## Story Tracker` in `aire-state.md`:
- 🔴 **First apply the bug/enhancement exception above**: a bug/enhancement ticket left `🔵 In Development` by an **ve rejection** (`ve-rejected` label / an Option B rejection in audit.md) is a legitimate cycle close — treat that row as READY and skip the prompt below for it entirely. Never ask "archive anyway?" for a rejected ticket.
- Otherwise, if any story is NOT `🧪 Ready for Testing`, present the list of incomplete stories and ask:
  ```
  ⚠️ [N] stories are not yet Ready for Testing: [list with statuses]

  Archive anyway? (yes / no)
  ```
- Block until the user answers. Log the answer in audit.md. On "no", STOP.

### Step 2.5: ve Artifact Readiness Check (🔴 MANDATORY — the archive is one-shot)

The archive is a ONE-SHOT snapshot: anything not in the working tree right now is lost from the cycle record, and the workspace reset means nothing re-captures it later. Before archiving, verify the ve's work has actually landed on this branch. **Never skip this check, in any mode** (it is the reason bug/enhancement archives are manual).

1. **Pull the branch first**: confirm the current branch is the cycle branch and is up to date with origin (`git fetch origin && git status -sb`). If it is behind, run automatic `git pull --ff-only`.
2. **Check for the expected test docs**: for every ticket/story in scope, look for `.spec/aire-docs/tests/<TICKET-ID>-<title>/`. Also check for un-merged ve branches/PRs targeting this cycle branch (`gh pr list --base <cycle-branch>` — look for `ve/...` heads).
3. If any expected test folder is **missing**, or an ve PR into this branch is still **open**, warn and ask — do NOT archive silently:
   ```
   ⚠️ ve artifacts look incomplete for this cycle:
      • Missing .spec/aire-docs/tests/ folder for: [list of tickets/stories]
      • Open ve PR(s) into <cycle-branch> not yet merged: [list with URLs]

   Archiving now permanently omits these from the archive — the archive is one-shot and the
   workspace reset that follows leaves nothing to re-capture. Recommended: merge the ve PR(s),
   `git pull --ff-only` on <cycle-branch>, then re-run archive-epic.

   Archive anyway? (yes — archive incomplete / no — stop so I can merge the ve work)
   ```
   Block until answered. On **no**, STOP (nothing written). On **yes**, proceed and record the omission explicitly in audit.md AND in the Step 5.4 `archive-manifest.md` as a `**Known Gaps**:` line naming exactly what was missing.
4. Log the check — folders found, PRs inspected, and the user's raw answer — in audit.md.

### Step 2.6: 🛑 ve COMPLETION Checkpoint — bug & enhancement cycles ONLY (typed `proceed` required)

🔴 **In bug or enhancement mode this checkpoint is MANDATORY and ALWAYS runs**, even if Step 2.5 found no problems and even if the user just typed `archive-epic` deliberately. It exists because those cycles are archived manually precisely so the operator can confirm ve is finished. **Skip this checkpoint in epic mode only** (epic cycles complete ve sign-off on the epic branch before the Epic PR).

Present this message VERBATIM (substituting real values) and then **HALT — do not read, write, copy, or delete anything until the user replies**:

```
🛑 Before I archive this [bug | enhancement] cycle — has ALL the ve work for [TICKET-ID]
   been MERGED and COMPLETED on `<cycle-branch>`

   ❌ NOT complete → do NOT proceed. Merge/finish the outstanding ve work into
      `<cycle-branch>`, then `git pull --ff-only` on it, then run `archive-epic` again.
   ✅ Complete     → type **proceed**

[Answer]:
```

**Rules for this checkpoint**:
- 🔴 **An ve REJECTION counts as COMPLETE.** "Completed" means the ve's test plan is merged and their Option B **decision has been made** — approve *or* reject. A rejected ticket (still `🔵 In Development`, carrying `ve-rejected`) closes its cycle exactly like an approved one, so never treat a rejection as outstanding work, never push the user back to `ve-list-work` over it, and never imply the archive should wait.
- **Only  `proceed`**  opens the checkpoint. Anything else — "yes", "ok", "go ahead", silence, a question — is NOT consent: restate the checkpoint once and keep waiting. Never infer consent from the fact that the user invoked the skill.
- On anything indicating incompleteness, **STOP the whole skill** with nothing written, and tell the user exactly what to merge first.
- Log the checkpoint prompt and the user's complete raw answer in audit.md before continuing.

---

## Step 3: Generate Delta Reverse Engineering Artifacts

Follow the **Delta Generation** rules from `reverse-engineering.md`:

0. **Re-run check**: if `delta/<EPIC-ID>-<epic-name-slug>/` already exists (a previous archive-epic run for this same epic), ask:
   ```
   ⚠️ Delta folder delta/<EPIC-ID>-<epic-name-slug>/ already exists from a previous run.
   Regenerate it fresh from the current branch state, or keep the existing delta? (regenerate / keep)
   ```
   On "keep", skip to Step 5 (archive) using the existing delta. On "regenerate", replace ONLY this epic's delta folder. Log the answer in audit.md.
1. Read `.spec/aire-docs/planning/reverse-engineering/reverse-engineering-timestamp.md` for **Analyzed At Commit** (or **Analysis Date** as fallback).
   - If NO root reverse engineering artifacts exist (greenfield epic), skip delta generation (this step); note this in audit.md, and the archive in Step 5 simply contains whatever exists.
2. Compute what the epic changed: git history since the recorded commit/date, story summaries in `.spec/aire-docs/implementation/code/`, the Story Tracker, and implementation design artifacts.
3. Write the delta artifacts into the **epic-namespaced** folder `.spec/aire-docs/planning/reverse-engineering/delta/<EPIC-ID>-<epic-name-slug>/` — `delta-summary.md` plus per-document `delta-<artifact>.md` files exactly as specified in the source rules. 🔴 The namespaced folder is MANDATORY: it is what lets N parallel epics' deltas coexist on the base branch without merge conflicts. NEVER write delta files directly under `delta/`, and NEVER touch another epic's delta folder.
   - 🔴 **Delta generation is ADD-ONLY**: the ONLY writes are NEW files inside `delta/<EPIC-ID>-<epic-name-slug>/`. NEVER modify, rename, move, replace, or delete ANY root reverse engineering document (`business-overview.md`, `architecture.md`, `code-structure.md`, `api-documentation.md`, `component-inventory.md`, `technology-stack.md`, `dependencies.md`, `reverse-engineering-timestamp.md`, etc.) — the originals must be byte-identical before and after this step. The delta is stitched INTO them later, on the base branch, by `stitch-delta` — not here, and never by renaming a root doc into a delta doc.
   - **Post-generation check**: run `git status` on `.spec/aire-docs/planning/reverse-engineering/` — the only changes allowed are additions under `delta/<EPIC-ID>-<epic-name-slug>/`. If any root document shows as modified/deleted/renamed, restore it (`git checkout -- <file>`) before proceeding, and log the correction in audit.md.
4. **Delta verification checkpoint (MANDATORY)**: adversarially fact-check every delta document against the codebase at HEAD — verify each checkable claim by reading/grepping the actual code (claims about pre-existing code must match the existing code, not the epic's own documents), and re-measure every quantitative figure with the real command. Fix discrepancies BEFORE proceeding; record checks, commands, and corrections in audit.md.
5. Present a short delta summary and **wait for explicit approval**:
   ```
   📄 Delta artifacts generated at delta/<EPIC-ID>-<epic-name-slug>/
   Documents affected: [list] ([n] additions / [n] modifications / [n] removals)
   ✅ Verification: [N] claims checked against the codebase at HEAD; [M] corrected

   Proceed to archive? (yes / review changes)
   ```
6. **MANDATORY**: Log the delta generation, verification outcome, and the user's response in audit.md.

---

## Step 4: Stitching Handoff (NOT executed here)

🔴 Do NOT stitch the delta into the root reverse engineering documents in this skill. Root docs are only modified on the base branch, post-merge, by the **`stitch-delta`** skill — it discovers un-stitched deltas via the `stitch-epic.md` ledger and applies them in merge order. The epic's PR carries the delta folder; after the PR merges, the user runs `stitch-delta` on the base branch (Step 7's completion message instructs them).

---

## Step 5: Create the Epic Archive

🔴 **Path rule for this step and every step after it**: wherever the text below writes a shorthand archive path like `aire-archives/<EPIC-ID>-<epic-name-slug>/`, the REAL path ALWAYS includes the cycle-type subfolder resolved in Step 1.3 — `aire-archives/epics/<EPIC-ID>-<slug>/`, `aire-archives/bugs/<BUG-ID>-<slug>/`, or `aire-archives/enhancements/<ENH-ID>-<slug>/`. Nothing is ever written directly under `aire-archives/`.

1. Append a final audit entry to `.spec/aire-docs/audit.md` recording the archive event (epic, timestamp, archive path) — do this BEFORE copying, so the archive carries the complete trail.
2. Create the archive folder resolved in Step 1.3 — `aire-archives/epics/<EPIC-ID>-<epic-name-slug>/`, `aire-archives/bugs/<BUG-ID>-<slug>/`, or `aire-archives/enhancements/<ENH-ID>-<slug>/` — at the workspace root (create the `epics/`/`bugs/`/`enhancements/` subfolder if missing).
   - **If `aire-archives/` (or its subfolders) already exist**: reuse them as-is. NEVER recreate them, and NEVER touch, replace, or delete any OTHER cycle folder inside them — only the folder for THIS cycle is ever written.
   - **If a folder with this exact epic name already exists** inside `aire-archives/`, do NOT silently overwrite — ask:
     ```
     ⚠️ Archive folder aire-archives/<EPIC-ID>-<epic-name-slug>/ already exists.

     Replace it with a fresh archive from this run? (yes / no)
     ```
     - On **yes**: delete only that same-name epic folder and recreate it fresh from this run's `.spec/aire-docs/`. All other epic folders remain untouched.
     - On **no**: STOP the archive step — do not write anything into `aire-archives/`. Log the decision in audit.md.
   - Log the collision check and the user's raw answer in audit.md.
3. 🔴 **Copy the ENTIRE live `.spec/` tree into the archive as ONE folder.** The archive is an exact mirror — one command, no unpacking, no per-folder logic, no exclusions:
   ```bash
   ARCH="aire-archives/epics/<EPIC-ID>-<epic-name-slug>"   # or bugs/ | enhancements/
   mkdir -p "$ARCH"
   cp -R .spec "$ARCH/.spec"
   ```
   That single copy carries **everything** the cycle was built from and produced:
   - `.spec/aire-docs/` — `audit.md`, `aire-state.md`, `architecture.md`, `planning/`, `implementation/`, `tests/`, and the stitched root reverse engineering documents with their `delta/` folder
   - `.spec/aire-docs/implementation/code/behavior/` — one `.feature` file per work unit: the Gherkin contract the code was built against
   - `.spec/context-project/existing-knowledge/` and `.spec/context-project/new-references/` — the human-authored inputs: the notes describing the existing system, and the wireframes/specs/mockups that defined the target

   🔴 **Mirror it exactly — same folder name, same structure, same depth.** The archive contains `.spec/` (a dot-folder), not a renamed or unpacked copy. Use `ls -a` to inspect it. Keeping the name identical is what makes the copy verifiable with a single diff and the restore path unambiguous.

   The copy is ALWAYS unfiltered; the single permitted narrowing happens afterwards, in Step 3a below.
   - ⚠️ **Size**: `new-references/` can hold large binaries (mockups, PDFs, videos). Record the archive's total byte size in the manifest so growth stays visible. Do **not** filter it — an incomplete reference set is worse than a large one.
   - 🔴 **GUARDRAIL — NEVER flatten**: do NOT copy `.spec/`'s *contents* into the archive folder root (never `cp -R .spec/. "$ARCH/"` or `cp -R .spec/* "$ARCH/"`). The archive folder must contain exactly `.spec/` and `archive-manifest.md` — never `aire-docs/`, `planning/`, `implementation/`, `aire-state.md` or `audit.md` sitting loose beside the manifest. Flattening instead of mirroring is the #1 cause of inconsistent archive layouts across cycles.
   - 🔴 **GUARDRAIL — ARCHIVE EVERYTHING, for EVERY cycle type**: a **complete, recursive, unfiltered** copy — every folder and every file at every depth, whatever it is named and whoever produced it. **The cycle type only changes the destination subfolder (`epics/` | `bugs/` | `enhancements/`), never WHAT gets copied**: a bug cycle archives the same full tree an epic cycle does. There is **exactly ONE** permitted exclusion in this entire skill — the already-stitched delta folders pruned by Step 3a — applied AFTER this copy, never as a filter during it. No other exclusion may EVER be inferred from it.
     - **NEVER** archive a hand-picked subset, whitelist, or "the folders this cycle touched".
     - **NEVER** skip a folder for looking empty, unused, stale, irrelevant to this cycle type, produced by another role (ve's `tests/`), or authored by a human rather than the framework (`existing-knowledge/`, `new-references/`). If it is inside `.spec/`, it goes into the archive.
     - **NEVER** exclude dotfiles/dot-folders, hidden files, or files without a `.md` extension (logs, `.yml`, `.json`, coverage reports, images, binaries). Do not use extension- or name-based filters, and do not apply `.gitignore` rules — untracked and ignored files inside `.spec/` are still archived. Use a plain recursive copy, never `git archive`, never a `find … -name '*.md'` loop.
     - **NEVER** move, delete, rewrite, truncate, reformat, summarize, or "tidy" anything while copying — the archive is a byte-for-byte snapshot, not a curated export.

3a. 🔴 **Prune ALREADY-STITCHED deltas from the ARCHIVE COPY ONLY (ledger-gated)** — run this immediately after the Step 3 copy completes, and never before it.

   **Why**: prior cycles' deltas that have already been stitched are, by definition, represented inside the root reverse engineering documents this archive carries — keeping their folders too makes every archive contain every earlier cycle's delta, so total archive size grows quadratically with the number of cycles. Pruning only the stitched ones drops that to linear while losing nothing.

   1. Read the ledger **from the archive copy**: `<archive-folder>/.spec/aire-docs/planning/reverse-engineering/stitch-epic.md`. If it does not exist, or has no rows, **prune NOTHING** and skip to Step 4.
   2. Build the prune list = the `Delta Folder` values recorded in the ledger.
   3. 🔴 **Subtract THIS cycle's own delta** (`delta/<CYCLE-ID>-<slug>/`, generated in Step 3 of this skill) from the prune list, unconditionally — it has NOT been stitched yet (stitching happens post-merge, via `stitch-delta`), and it is the whole reason this archive exists. It must ALWAYS remain in the archive, even in the pathological case where a stale ledger row names it.
   4. 🔴 **Keep every delta folder NOT in the ledger.** A delta on disk with no ledger row is a **pending, un-stitched delta** — its content exists nowhere else in stitched form. This is the case that makes the exclusion safe.
   5. Delete the resulting folders **from the archive copy only**:
      ```bash
      rm -rf "<archive-folder>/.spec/aire-docs/planning/reverse-engineering/delta/<stitched-slug>"
      ```
   6. 🔴 **NEVER touch the live tree.** `.spec/aire-docs/planning/reverse-engineering/delta/` or `.spec/aire-docs/planning/reverse-engineering/` in the working tree is left completely untouched by this step — no deletions, no moves. The live `delta/` folder is what the cycle's PR carries to the base branch for `stitch-delta` to discover; pruning it there would destroy other cycles' pending deltas and reintroduce exactly the cross-cycle merge conflicts the namespacing exists to prevent. Verify with `git status` that this step produced **no** change under `.spec/aire-docs/`.
   7. 🔴 **NEVER prune anything else.** `stitch-epic.md` itself is always kept. This step may delete ONLY whole `delta/<ID>-<slug>/` folders that satisfy 2–4 above.

4. Write `aire-archives/<type>/<CYCLE-ID>-<slug>/archive-manifest.md` (as a SIBLING of the `.spec/` folder just created — NOT inside it):
   ```markdown
   # Epic Archive Manifest
   - **Epic**: [EPIC-ID] — [Epic name]
   - **Archived**: [ISO timestamp]
   - **Stories**: [total] ([n] Ready for Testing, [n] other — list any incomplete)
   - **Reverse Engineering**: this epic's delta generated at `delta/<EPIC-ID>-<epic-name-slug>/`; stitching PENDING — run `stitch-delta` on the base branch after the epic PR merges
   - **Analyzed At Commit**: [SHA]
   - **Archived Files**: [N] files, [total size] (complete recursive mirror of `.spec/`; verified equal to the live tree except the pruned deltas listed below)
   - **Contents**: aire-docs · [N] work-unit bundles ([list slugs]) · context-project [present/absent] · new-references [present/absent, [size]]
   - **ve Artifacts**: [test folders present: list | ⚠️ Known Gaps: <what was missing / which ve PR was still open> — user chose to archive anyway at Step 2.5]
   ```
5. **Verify the copy** — check BOTH of the following before proceeding; do NOT proceed until both pass:
   - **Structural check (layout guardrail)**: list the archive folder's immediate children (`ls -a aire-archives/epics/<EPIC-ID>-<epic-name-slug>/`) — it MUST contain EXACTLY two entries: `.spec/` and `archive-manifest.md`. If ANY other entry appears at this level (e.g. `aire-docs/`, `implementation/`, `planning/`, `aire-state.md`, `audit.md`), the copy was flattened instead of mirrored — redo Step 3 before continuing.
   - **Content check**: spot-check key files exist at their mirrored paths: `.spec/aire-docs/aire-state.md`, `.spec/aire-docs/audit.md`, `.spec/architecture.md`, `.spec/aire-docs/planning/reverse-engineering/reverse-engineering-timestamp.md`, and one `.spec/aire-docs/implementation/code/behavior/<work-unit>.feature`.
   - 🔴 **Completeness check (BLOCKING — same for every cycle type)**: prove nothing was dropped **except exactly the deltas Step 3a pruned**, by comparing the live tree against the archived copy:
     ```bash
     # relative path lists — the ONLY permitted difference is the pruned delta paths
     # ONE diff covers the whole mirror — the only permitted difference is the pruned delta paths
     diff <(cd .spec && find . | sort) \
          <(cd "aire-archives/<type>/<CYCLE-ID>-<slug>/.spec" && find . | sort)
     ```
     (PowerShell equivalent: `Compare-Object` on the two `-Force` relative-path lists.)
     Read the diff as follows — **all three conditions must hold**:
     1. Every line is a **live-only** entry (present in `.spec/`, absent from the archive). An **archive-only** entry means the archive contains something the live tree does not — always a defect; re-run Step 3.
     2. Every such line sits under `./aire-docs/planning/reverse-engineering/delta/<ID>-<slug>/` for an `<ID>-<slug>` on Step 3a's prune list. **Any** live-only path outside those folders means the copy dropped something it must not have — re-run the full recursive copy of Step 3 and re-verify.
     3. The set of pruned `<ID>-<slug>` folders appearing in the diff **equals** Step 3a's prune list exactly — no folder pruned that was not on the list, and none on the list left behind.
     🔴 If Step 3a pruned nothing, the diff MUST be completely empty. 🔴 `delta/<CYCLE-ID>-<slug>/` (this cycle's own delta) and any pending un-stitched delta MUST NOT appear in the diff at all — if either does, Step 3a over-pruned: restore it into the archive from the live tree and re-verify before continuing.
     **Do NOT proceed to Step 6 (which deletes the live docs) until all three conditions hold.** Report the archived file count in the completion message and the manifest.
   - Log the structural check, the file count, and the completeness-diff result in the live `.spec/aire-docs/audit.md` (Step 6 has not yet deleted it at this point).

**MANDATORY reference layout** — every archive folder produced by this skill MUST match this shape exactly (no exceptions, no variation between epic/bug/enhancement cycles):
```
aire-archives/epics/<EPIC-ID>-<epic-name-slug>/
├── .spec/aire-docs/                  ← the ENTIRE .spec/aire-docs/ tree, folder name preserved
│   ├── aire-state.md
│   ├── audit.md
│   ├── planning/
│   │   └── reverse-engineering/
│   │       ├── stitch-epic.md          ← always kept
│   │       └── delta/                  ← THIS cycle's delta + any pending un-stitched
│   │           └── <EPIC-ID>-<epic-name-slug>/   deltas; already-stitched ones pruned (Step 3a)
│   ├── implementation/
│   ├── tests/
│   ├── operations/
│   └── …                         ← EVERY other folder/file that exists under .spec/aire-docs/, at every depth
└── archive-manifest.md           ← sibling of .spec/aire-docs/, never inside it
```
(`bugs/<BUG-ID>-<slug>/` and `enhancements/<ENH-ID>-<slug>/` follow the identical shape and the identical full-tree contents — the folders shown above are illustrative, not a whitelist: archive whatever exists, nothing less.)

> The **latest epic archive folder** is the reference point for the most recent reverse engineering artifacts — workspace detection offers to restore from it when a new cycle starts without live artifacts, reading `<archive>/.spec/aire-docs/planning/reverse-engineering/` (this ONLY resolves correctly if Step 3 mirrored `.spec/` as specified above).

---

## Step 6: Reset the Live Workspace (Confirm-First)

**Auto-triggered exception — EPIC CYCLES ONLY**: if this skill was invoked **automatically by pr-generator after an Epic → Base branch PR** (not by the user typing a trigger phrase), do NOT ask the question below — **auto-select option A**. 🔴 This exception NEVER applies to bug or enhancement cycles: those are always operator-invoked, so **always ask the question** there, even if the user ran `archive-epic` immediately after the `[BUG]`/`[ENH]` PR. (Reset, keep root reverse engineering docs). Option A is the safe default in this context: the epic PR just raised carries the delta, and A keeps `reverse-engineering/` (including `delta/` and `stitch-epic.md`) intact on the branch. Announce the auto-selection to the user:

```
📦 Auto-triggered from pr-generator (Epic → Base PR) — applying workspace reset
   option A: keep root reverse engineering docs, clear epic-scoped content.
```

Log the auto-selection (and that the question was skipped, with the reason) by appending to the **archived** audit copy at `aire-archives/epics/<EPIC-ID>-<epic-name-slug>/.spec/aire-docs/audit.md` (the live audit.md is deleted by this reset), then perform option A's reset. Option B is NEVER auto-selected.

Otherwise (standalone invocation), ask the user — NEVER reset without explicit choice:

```
📦 Archive created and verified at aire-archives/<EPIC-ID>-<epic-name-slug>/

How should the live workspace be prepared for the next epic cycle?

A) Reset, keep root reverse engineering docs (recommended) — clear cycle-scoped
   content (requirements, stories, plans, implementation docs, audit, state, and the
   per-work-unit .spec/<slug>/ bundles) but KEEP:
     - .spec/aire-docs/planning/reverse-engineering/ — INCLUDING the delta/ subfolder
       and stitch-epic.md: this epic's delta MUST stay on the branch so the PR carries
       it to the base branch for stitch-delta to apply post-merge
     - .spec/context-project/ and .spec/context-project/new-references/ — human-authored and
       cross-cycle; the next cycle reads them again
B) Full reset — remove .spec/ entirely (aire-docs, every work-unit bundle, AND the
   context-project/ with both its subfolders); the next cycle restores reverse
   engineering docs from this archive or regenerates them via reverse-engineer-root
   ⚠️ also removes the human-curated context inputs from the working tree. They are
   in this archive, but re-curating them is manual — prefer A unless you mean to
   start from nothing
   ⚠️ removes this epic's un-stitched delta from the branch — only choose B if the
   epic PR (carrying the delta) has ALREADY been raised/merged, or you accept
   stitching from the archive copy manually

[Answer]:
```

🔴 **Option A post-reset verification (MANDATORY)**: after an option-A reset, the ENTIRE `.spec/aire-docs/planning/reverse-engineering/` folder must be intact and unchanged — all root documents PLUS `delta/` PLUS `stitch-epic.md`. Compare the file list before and after the reset; if anything under `reverse-engineering/` was removed or modified, restore it immediately (`git checkout -- .spec/aire-docs/planning/reverse-engineering/` or copy back from the just-verified archive) and log the correction in audit.md. "Reset, keep root reverse engineering docs" means exactly that — the reset clears ONLY requirements, stories, plans, application-design, implementation docs, audit, state, and the per-work-unit `.spec/aire-docs/implementation/code/behavior/` bundles (already archived inside `<archive>/.spec/` in Step 3). 🔴 It must NOT touch `.spec/context-project/existing-knowledge/` or `.spec/context-project/new-references/` — those are human-authored, cross-cycle inputs. Verify both survived the reset, and restore them from the archive if not.

🔴 **`.spec/aire-docs/` (including every work unit's `.feature` file) is deleted on BOTH A and B** — it is cycle-scoped, and Step 3 mirrored it into `<archive>/.spec/`. Verify the mirror exists before deleting; if `<archive>/.spec/aire-docs/` is missing, STOP and redo Step 3.

🔴 **`.spec/context-project/existing-knowledge/` and `.spec/context-project/new-references/` are deleted ONLY on B.** They are human-authored inputs, not cycle output, so option A preserves them in place — deleting them would silently discard work no framework step can regenerate.

On A or B, `.spec/aire-docs/audit.md` and `.spec/aire-docs/aire-state.md` are **deleted along with the other epic-scoped docs — do NOT seed a replacement audit.md or state file**. The archive copy holds the epic's complete trail; the next cycle's Workspace Detection creates fresh ones. This also keeps parallel epics conflict-free: no two epic PRs carry competing audit/state files onto the base branch.

**MANDATORY**: From this point on, the live `.spec/aire-docs/audit.md` no longer exists — log the user's raw answer (or the auto-selection), the reset actions taken, and everything in Step 6.5 by APPENDING to the **archived** copy at `aire-archives/epics/<EPIC-ID>-<epic-name-slug>/.spec/aire-docs/audit.md`, so the trail stays complete.

---

## Step 6.5: Commit & Push the Epic-Close Changes (MANDATORY — the delta must ride the PR)

Everything this skill produced so far exists only in the working tree. 🔴 **If it is not committed and pushed, the epic PR will NOT carry the delta, and `stitch-delta` on the base branch will find nothing to stitch.**

1. Stage the epic-close changes:
   - `.spec/aire-docs/planning/reverse-engineering/delta/<EPIC-ID>-<epic-name-slug>/` (new delta artifacts)
   - `aire-archives/<EPIC-ID>-<epic-name-slug>/` (the verified archive)
   - The workspace-reset changes from Step 6 (deleted epic-scoped docs, including `audit.md` and `aire-state.md`)
2. Commit on the current (epic) branch:
   ```
   docs: close epic <EPIC-ID> — delta artifacts, release archive, workspace reset
   ```
3. **Push (confirm-first)** — ask:
   ```
   ⬆️ Push the epic-close commit to origin/<epic-branch>?
      [If a PR is already open for this branch:] The open PR (<PR URL/number>) tracks this
      branch and will automatically include this commit — the delta then rides the PR to
      the base branch for stitch-delta.
      (yes / no)
   ```
   On yes: push and verify (`git log origin/<epic-branch> -1`). On no: warn explicitly that the delta will NOT reach the base branch until this commit is pushed, and that the PR must not be merged before then. Log the answer and outcome by appending to the archived audit copy (`aire-archives/epics/<EPIC-ID>-<epic-name-slug>/.spec/aire-docs/audit.md`).
4. If a PR is open for this branch (`gh pr list --head <epic-branch>`), confirm after pushing that the PR now includes the commit.
5. **Update the PR description** so reviewers aren't surprised by the epic-close diff: fetch the current body (`gh pr view <PR> --json body`) and append (via `gh pr edit <PR> --body ...`, never replacing the existing content):
   ```markdown
   ## 📦 Epic-Close Commit (added after PR creation)
   This PR also includes the epic-close commit from `archive-epic`:
   - **Added**: delta reverse engineering artifacts at `.spec/aire-docs/planning/reverse-engineering/delta/<EPIC-ID>-<slug>/` (stitched into root docs post-merge via `stitch-delta`)
   - **Added**: release archive at `aire-archives/<EPIC-ID>-<slug>/` (complete aire-docs snapshot incl. audit trail and state)
   - **Removed**: epic-scoped working docs (requirements, stories, plans, implementation docs, `audit.md`, `aire-state.md`) — preserved in the archive above
   - **Unchanged**: root reverse engineering documents
   ```

---

## Step 7: Completion Message

```markdown
# 📦 Epic Archive Complete

- **Archive**: `aire-archives/<EPIC-ID>-<epic-name-slug>/`
- **Contents**: `aire-docs/` (audit.md, aire-state.md, all planning/implementation artifacts) + `specs/` (every work-unit Spec-DD bundle) + root reverse engineering documents + this epic's delta (`delta/<EPIC-ID>-<epic-name-slug>/`)
- **Workspace**: [reset choice taken]
- **Epic-close commit**: [pushed to origin/<epic-branch> — included in PR <URL> | ⚠️ NOT pushed — the delta will not reach the base branch until you push]

➡️ NEXT ACTIONS — do these in order (this delta is NOT yet stitched into the root
   reverse engineering documents; nothing further happens until you do this):
   1️⃣  Merge the open PR into `<base-branch>`: <PR URL>
       (the epic-close commit above rides this PR — that is how the delta reaches the base branch)
   2️⃣  Switch to the base branch: `<base-branch>` (pull the latest)
   3️⃣  Use the skill stitch-delta
       It applies this delta (and any other pending cycles' deltas, in merge order) to the root
       reverse engineering documents and records it in `stitch-epic.md`.
       This is ALWAYS the final action of a cycle — nothing follows it.

🔴 Use the skill names EXACTLY as shown — do not describe what you want in your own words.
   Any other phrasing is not a framework trigger and the workflow will not advance.
```

**Rules for this message**:
- Substitute every placeholder with real values (`<base-branch>` and the PR URL from `## Branching` / `gh pr list`) — never ship a placeholder to the user.
- 🔴 **The invariant is now IDENTICAL for EVERY cycle type**: `ve-list-work` (Option B) runs on the **cycle's own branch before this archive** — the epic branch for epic cycles, the bug/enhancement branch for those — so step 3️⃣ is always ✅ informational, never an action. `stitch-delta` is ALWAYS last. Never present the stitch before the promotion, never send the ve to the base branch to sign off, and never present anything after the stitch.
- Show only the bracketed variant that matches the resolved cycle type (`Workflow Type` in `## Tracker`) — never print both.
- If the epic-close commit was **NOT pushed** (the user answered "no" at Step 6.5), replace line 1️⃣ with: `1️⃣  ⚠️ Push the epic-close commit first — the delta will NOT reach the base branch, and the PR must NOT be merged, until you do: git push origin <branch>`.
- Output **nothing after this block** — no options menu, no further suggestions.
