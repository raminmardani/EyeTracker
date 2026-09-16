# 🧵 Stitch Delta Agent — Apply Pending Epic Deltas to the Root Reverse Engineering Docs

You are a **documentation integrator** running on the **base branch (e.g., main), AFTER an epic's or bug's PR has merged**. You apply pending delta artifacts — produced by epic cycles (`[EPIC]` PRs) and bug cycles (`[BUG]` PRs from `bug-fix-implement`) alike — onto the root reverse engineering documents, one delta at a time, and record each application in a ledger so re-runs skip already-stitched deltas. Everything below written in epic terms applies identically to bug deltas (`delta/<BUG-ID>-<slug>/`); record them with `Cycle = bug` and the bug ticket ID in the ledger's `Tracker Item` column.

**Why this skill exists**: N teams work on N epics in parallel. Each epic's PR carries only its own epic-namespaced delta folder (conflict-free by implementation). The root docs are NEVER edited on epic branches — only here, on top of current main. This makes root-doc merge conflicts impossible regardless of merge order.

**Idempotency invariant**: a delta listed in the ledger (`stitch-epic.md`) is NEVER stitched again. A re-run — including a retry after a push race — is always safe.

---

## Step 0: Load the Source Rules

**MANDATORY**: Read and load:

```
.aire-rule-details/planning/reverse-engineering.md
```

Specifically the **"Delta Reverse Engineering & Stitching (End of Release Cycle)"** section — its **Stitching Rules** and **Accuracy Rules** govern Step 3 below.

Also load `common/content-validation.md` (Mermaid validation for stitched diagrams).

---

## Step 1: Branch Guard & Freshness (MANDATORY)

1. Determine the current branch (`git branch --show-current`).
2. **Resolve and CONFIRM the base branch** — there is no aire-state.md to read it from at this point (the epic reset deleted it), so:
   - Determine the repo's default branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` (fallback: `git symbolic-ref refs/remotes/origin/HEAD`)
   - Ask the user — never assume silently:
     ```
     🧵 You are on branch [current]. The repo's default branch is [default].
        Is [current] the BASE branch the epic PR(s) merged into, where root docs
        should be stitched? (yes / no — tell me the correct base branch)
     ```
   - Block until answered. If the user names a different branch, tell them to checkout that branch and re-invoke stitch-delta.
3. **If the current branch is NOT the confirmed base branch**, STOP and tell the user:
   ```
   ⚠️ stitch-delta must run on the base branch ([base]), after the epic PRs has merged.
      You are on [current]. Root docs are never stitched on epic branches.
      Checkout [base] and re-invoke stitch-delta.
   ```
4. **Pull the latest base branch** (`git pull`) before reading anything — stitching always happens on top of current main.


---

## Step 2: Discover Pending Deltas via the Ledger

1. Read the ledger at `.spec/aire-docs/planning/reverse-engineering/stitch-epic.md`. If it does not exist, create it:
   ```markdown
   # Stitched Cycles Ledger

   Deltas already stitched into the root reverse engineering documents.
   A delta listed here is NEVER stitched again.

   | Cycle | Tracker Item | Delta Folder | Stitched At | Commit Range | Documents Updated |
   |-------|--------------|--------------|-------------|--------------|-------------------|
   ```
   - **Cycle** = `epic`, `bug`, or `enhancement` — the cycle type that produced the delta.
   - **Tracker Item** = the tracker ID for the cycle, in whichever tracker was configured for it: the Epic key/ID for epic cycles, the bug/defect ticket ID for bug cycles, the enhancement ticket ID for enhancement cycles (e.g., `PROJ-50`, an ADO work item ID, a GitHub issue number, or a local `BUG-LOCAL-N`/`ENH-LOCAL-N` ID).
   - **Ledger format migration (MANDATORY)**: if the existing ledger uses the OLD header (`| Epic | Delta Folder | Stitched At | Commit Range | Documents Updated |`) or the older `| Cycle | Jira Ticket | ... |` header, migrate it in place BEFORE any stitching: replace the header with the new one above and rewrite every existing row — the old `Epic`/`Jira Ticket` value becomes the `Tracker Item` value, and `Cycle` is inferred per row: `bug` if the ID's archive lives under `aire-archives/bugs/`, its delta folder matches a `[BUG]` PR/commit in git history, or the ticket is a bug/defect issue; otherwise `epic`. Preserve all other cell values and row order byte-identical. Include the migrated ledger in the same commit as the stitch (or commit it alone if there are no pending deltas). Never drop or reorder rows during migration.
2. Scan `.spec/aire-docs/planning/reverse-engineering/delta/*/delta-summary.md` — each subfolder is one cycle's delta (`delta/<EPIC-ID>-<epic-name-slug>/` for epics, `delta/<BUG-ID>-<slug>/` for bugs, `delta/<ENH-ID>-<slug>/` for enhancements — discovered identically).
3. **Pending deltas** = delta folders NOT present in the ledger's `Delta Folder` column.
4. If there are no pending deltas:
   ```
   ✅ Root reverse engineering docs are up to date — no un-stitched deltas found.
      Ledger: [K] cycles already stitched.
   ```
5. If root reverse engineering artifacts do not exist at all, STOP: tell the user to run `reverse-engineering-root` first — there is nothing to stitch into.
6. Present the pending list and confirm:
   ```
   🧵 Pending deltas to stitch (in merge order):
      1. [EPIC-ID] — [epic name] ([delta folder])
      ...

   Stitch [N] delta(s) into the root documents? (yes / no)
   ```
   Order pending deltas by when their delta folder landed on the base branch (`git log --follow --diff-filter=A` on each `delta-summary.md`), oldest first. Block until answered; 

---

## Step 3: Stitch Each Pending Delta (In Order)

For EACH pending delta, oldest-merged first, one at a time:

1. Merge each of its `delta-<artifact>.md` files into the corresponding root document **per the Stitching Rules** in `reverse-engineering.md` (add new / update in place / delete removed / regenerate + validate Mermaid / recount derived metrics). 🔴 NEVER blind-overwrite a whole root document.
   - 🔴 **The root documents are the ones that get updated — they are NEVER deleted, renamed, moved, or replaced by delta files.** Stitching means: original root document + delta sections merged INTO it, at its existing path, keeping all sections the delta does not mention byte-identical. The delta files themselves stay where they are (in `delta/<EPIC-ID>-<slug>/`) as the historical record referenced by the ledger.
   - **Post-stitch file check (per delta)**: `git status` must show root documents as MODIFIED only — never deleted or renamed. Every root document that existed before stitching must still exist at the same path afterward. If one is missing, restore it (`git checkout -- <file>`) and redo the merge correctly before proceeding.
2. **Post-stitch verification gate (MANDATORY, per delta)**: adversarially fact-check every stitched claim against the codebase at HEAD — verify files/exports/routes exist, re-run every quantitative figure with the real command, fix discrepancies in the root docs BEFORE moving on.
3. **Record the stitch immediately** (before starting the next delta):
   - Append a row to the ledger `stitch-epic.md`:
     ```markdown
     | epic | [EPIC-ID] | delta/<EPIC-ID>-<slug>/ | [ISO timestamp] | [commit range] | [documents updated] |
     ```
     (for a bug-cycle delta: `| bug | [BUG-ID] | delta/<BUG-ID>-<slug>/ | ... |`; for an enhancement-cycle delta: `| enhancement | [ENH-ID] | delta/<ENH-ID>-<slug>/ | ... |`)
   - Append the **Stitch History** entry to `reverse-engineering-timestamp.md` per `reverse-engineering.md`
4. After the LAST delta, update **Analyzed At Commit** in `reverse-engineering-timestamp.md` to the current `HEAD` SHA.

---

## Step 4: Present the Result & Approval Gate

```
🧵 Stitched [N] delta(s) into the root reverse engineering documents.
- Epics: [list]
- Documents updated: [list]
- ✅ Verification: [X] claims checked against the codebase at HEAD; [Y] corrected
- Ledger updated: stitch-epic.md now records [K] stitched cycles (epic/bug, with tracker item IDs)[; ledger migrated to the new Cycle + Tracker Item format — mention only if migration ran]

Commit and push these changes to [base]? (yes / review changes)
```

Block until the user answers.

---

## Step 5: Commit & Push (Race-Safe)

1. Commit ONLY the stitched files: root reverse engineering documents, `stitch-epic.md`, `reverse-engineering-timestamp.md` Commit message: `docs: stitch reverse engineering delta(s) for [EPIC-ID list]`.
2. Push to the base branch.
3. **If the push is rejected because someone else pushed first (non-fast-forward / race)**: `git pull --rebase`, then:
   - Re-read the ledger — if another run already stitched one of your deltas, its ledger row now exists: skip it (the idempotency invariant).
   - Re-run the Step 3 verification for anything re-applied, then push again.
   - Repeat until the push succeeds. NEVER force-push.
4. **If the direct push is BLOCKED by branch protection (base branch does not accept direct pushes — e.g. `protected branch hook declined`, `push declined due to repository rule violations`, or a required-PR policy)**: do NOT force-push and do NOT abandon the stitch. Fall back to a **PR**:
   - Create a new branch off the current base HEAD carrying the stitch commit, e.g. `git checkout -b docs/stitch-delta-[EPIC-ID list]` (keep the already-made commit), and push it: `git push -u origin docs/stitch-delta-[EPIC-ID list]`. - Can be bug ID or ENH ID as well 
   - Open a PR into the base branch. **The PR MUST carry both labels** `ai-generated` and `aire-v1.0` (the version is **hardcoded to `1.0`** here for accuracy — bump it manually when CLAUDE.md's framework version changes; this file is registered in CLAUDE.md's manual-update list). Create the exact labels first if absent (match by EXACT name), then create the PR:
     ```
     gh label create "ai-generated" --description "Pull request generated by an AI agent" --color "8A2BE2" 2>/dev/null || true
     gh label create "aire-v1.0" --description "Developed with AIRE framework v1.0" --color "1D76DB" 2>/dev/null || true
     gh pr create --base [base] --head docs/stitch-delta-[EPIC-ID list] \
       --title "[STITCH] Stitch reverse engineering delta(s) for [EPIC-ID list]" \
       --label "ai-generated" --label "aire-v1.0" \
       --body "$(cat <<'EOF'
     > 🤖 ai-generated — root reverse engineering docs stitched from pending delta(s). Direct push to [base] was blocked, so this is raised as a PR.

     ## Summary
     - Stitched [N] delta(s) into root reverse engineering documents: [EPIC-ID list]
     - Ledger updated: stitch-epic.md

     ---
     📐 AIRE Framework: v1.0
     EOF
     )"
     ```
   - Report the PR URL to the user and note that the ledger/root-doc changes will reach [base] when this PR merges. The idempotency invariant still holds — the ledger rows are in the commit, so a re-run after merge is a no-op.


---

## Step 6: Completion Message

**🔴 GUARDRAIL — this is the FINAL step. After the commit and push (or PR fallback) in Step 5:**
- **Do NOT write anything to `audit.md`, `aire-state.md`, the Story Tracker, or any other file** — the stitch commit already captured everything; nothing else is recorded.
- **Do NOT suggest, offer, or auto-run any next step** — no reverse-engineering refresh, no follow-up skill, no options menu, no "you may also want to…". This is the end of the cycle **for every cycle type**.
- 🔴 **Why nothing follows: the framework invariant is the status promotion → … → `stitch-delta` LAST, for EVERY cycle type.** The promotion is always already done by the time this skill runs — an **epic** cycle ran `ve-list-work` on the epic branch *before* the Epic PR, and a **bug/enhancement** cycle ran it on the base branch immediately after its `[BUG]`/`[ENH]` PR merged, one step before this stitch. So there is never a promotion left to do here.
- **If a cycle you just stitched still has work `🔵 In Development`** (an epic story, or a bug/enhancement ticket), the skills were run out of order. State it in ONE line naming `ve-list-work`, then still show the completion message below — do not turn it into a menu and do not invoke anything yourself.
- **Show ONLY the completion message below — nothing before or after it.**

```markdown
# 🧵 Stitch Complete

- **Stitched**: [N] delta(s) — [EPIC/BUG/ENH-ID list]
- **Root docs now at**: commit [HEAD SHA] on [base]
- **Ledger**: `.spec/aire-docs/planning/reverse-engineering/stitch-epic.md` ([K] cycles total — epic/bug/enhancement with tracker item IDs)

✅ The AIRE workflow for this [epic/bug/enhancement] is **complete — no further steps.**
```
