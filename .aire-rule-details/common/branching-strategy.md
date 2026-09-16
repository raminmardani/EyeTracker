# Branching Strategy (Epic Branch → Story Branches; Bug Branch)

**Purpose**: Single source of truth for ALL git branching in aire. Loaded by Workspace Detection (epic branch creation), Requirements Analysis Step 10 (epic branch commit and push), `workflows/dev-implement.md` (story branches), and the bug workflows (`workflows/bug-fix.md` / `bug-fix-implement.md` — see the Bug Branch Model at the end).

## The Model

```text
main (or whatever branch the workflow started on — the "base branch")
 └── epic/PROJ-50-payment-portal          ← created automatically at workflow start
      ├── story/1.1-user-registration     ← cut from the EPIC branch (never main)
      ├── story/1.2-login-endpoint        ← cut from the EPIC branch
      └── story/2.1-profile-page          ← dependent story (see base-selection rules)
```

- **Epic branch** → created ONCE at workflow start; planning artifacts are committed and pushed after `requirements.md` approval (no PR raised at this point); the Epic PR is raised manually at the end of the cycle via `pr-generator`, and merged to the base branch (when stories are done).
- **Story branches** → one per story at `dev-implement`; PRs target the **EPIC branch** (never main).
- Story branches merge → epic branch. Epic branch merges → base branch.

---

## 1. Epic Branch Creation (at workflow start — automatic)

Runs during Workspace Detection, AFTER the aire-state.md resume check and Parent Epic capture. **Skip** if `## Branching` already exists in `aire-state.md` (resumed project) — verify the recorded epic branch still exists and switch to it.

1. Record the **base branch**: `git branch --show-current` — this is the branch the epic branch is cut from and the PR target later. It is NOT assumed to be `main`; use whatever the repo is on.
2. Derive the epic branch name:
   - Epic ID + title available (from `## Tracker` / epic-brief): `epic/<EPIC-ID>-<kebab-case-epic-title>` (e.g., `epic/PROJ-50-payment-portal` for JIRA, `epic/4821-payment-portal` for an ADO/GitHub numeric Epic ID). Truncate the title part to keep the whole name ≤ 60 chars.
   - No Epic provided (plain natural-language request): derive a short kebab slug from the intent. **🤖 AUTOMATIC — do NOT ask the user to confirm the derived name**; announce it instead (`🌿 Epic branch: <name> (cut from <base>)`). The user can rename it later with an ordinary git command if they dislike it.
3. Create it automatically (working tree must be clean; if not, show `git status` and ask how to proceed — that is the ONLY question in this section):
   ```
   git fetch origin
   git checkout -b epic/<EPIC-KEY>-<kebab-title>
   ```
4. Record in `.spec/aire-docs/aire-state.md`:
   ```markdown
   ## Branching
   - Base Branch: main            (the branch the epic branch was cut from)
   - Epic Branch: epic/PROJ-50-payment-portal
   - Epic PR: (not raised — raised manually at cycle end via pr-generator)
   ```
5. Log the creation (name, base branch) in `.spec/aire-docs/audit.md`.
6. **ALL subsequent Planning/Implementation artifacts and code are committed on the epic branch** (or on story branches cut from it) — never directly on the base branch.

## 2. Epic Branch Commit & Push (after requirements.md approval — Requirements Analysis Step 10)

1. Commit the Planning artifacts produced so far (`.spec/aire-docs/` requirements, state, audit) on the **epic branch**.
2. Push the epic branch to origin (`git push origin <epic-branch>`). **🔴 Do NOT raise an Epic → Base PR at this point.** The Epic PR is raised manually by the user at the end of the cycle (after all stories are developed, ve has approved them, and the epic branch is complete) via `pr-generator`.
3. Log the commit hash and push confirmation in audit.md.
4. Update `## Branching` in `aire-state.md`: `Epic PR: (not raised — raised manually at cycle end via pr-generator)`.
5. The epic branch continues to accumulate story merges during the cycle. The Epic PR is only raised at cycle end.

## 3. Story Branch Creation (at `dev-implement`, per story)

Runs after Story Selection resolves the story and the Doability Gate passes, BEFORE any code generation.

1. Derive the story branch name automatically: `story/<N.M>-<kebab-case-story-title>` (prefix with the story's Tracker ID when it is JIRA-style and non-LOCAL, e.g., `story/PROJ-102-1.2-login-endpoint`; for a bare numeric ADO/GitHub ID, which reads poorly as a prefix, keep the Story ID `N.M` as the prefix instead and mention the Tracker ID in the PR body per `common/tracker-sync.md` Section 11 — e.g., `story/1.2-login-endpoint`). **🤖 AUTOMATIC — do NOT ask the user to confirm or override the name.** The name is fully determined by the story ID and title, so announce it (`🌿 Story branch: <name> (cut from <epic-branch>)`) and create it. The only exception is a name collision with an existing branch — then append a short disambiguating suffix automatically and announce that too. Do NOT generate code on the epic branch directly.
2. Refresh the epic branch first — ALWAYS:
   ```
   git fetch origin
   git checkout <epic-branch> && git pull --ff-only
   ```
3. **Select the base for the story branch** (dependency-merge check):
   - Read the story's `requires` from `dependency-graph.yml`.
   - For EACH prerequisite story, determine whether its story branch has been **MERGED into the epic branch** (`gh pr view <dep-branch> --json state,mergedAt`, or `git branch --merged <epic-branch>`). In the normal `dev-implement` flow the Doability Gate ran first and already checked this live (`implementation/story-selection.md` Step 4) — the gate never merges anything itself, so anything still unmerged here is exactly what the Doability Gate already stopped on. Note: `🧪 Ready for Testing` now means the dep's PR has been **MERGED** (a story is not promoted to Ready for Testing until its PR merges — see the Story Status Lifecycle in `CLAUDE.md`), so the Doability Gate and this git-level check now agree; this remains the authoritative merge check and stays as a safety net (e.g. a merge undone, or a status set out of band).
   - **Case A — no prerequisites, or ALL prerequisites merged into the epic branch**: cut from the epic branch:
     ```
     git checkout -b story/<N.M>-<kebab-title> <epic-branch>
     ```
   - **Case B — one or more prerequisites NOT yet merged**: 🛑 **WARN AND STOP** (mandatory — never proceed, never offer an alternative base):
     ```
     🛑 Cannot start Story [N.M] yet.
        It depends on story [X.Y], whose branch `story/X.Y-...` is NOT yet merged
        into the epic branch — its code would be missing from any branch cut now.

     ➡️ Merge story [X.Y]'s PR into the epic branch first, then run `dev-implement`
        again to start Story [N.M]. (Unmerged prerequisites: [list all])
     ```
     Do NOT create a story branch. Do NOT cut from the unmerged dependency's branch. Log the warning in audit.md, revert the story's status from `🔵 In Development` back to `🟢 Ready for Development` in the Story Tracker (and the external tracker, verified) since development is not starting, and END the `dev-implement` run — the user re-invokes it after merging.
4. Verify the branch is active (`git branch --show-current`), record the story branch name + base used in audit.md, and carry it forward as the commit/push/PR target. (This is a self-check, not a user prompt.)

## 4. Story PR (dev-implement Section D)

- Invoke **`pr-generator`** passing **target branch = the Epic Branch** from `## Branching`. The PR title carries the **`[STORY]`** prefix (pr-generator applies it). Story PRs NEVER target the base branch/main directly.
- After merge, other stories that `require` this one become cuttable from the epic branch (Case A).

---

## Rules

- 🔴 The epic branch is created automatically at workflow start; everything the workflow produces lives on it or on story branches cut from it.
- 🔴 Story branches are ALWAYS cut per the base-selection rules above — from the refreshed epic branch, never from `main`/the base branch.
- 🔴 ALWAYS run the dependency-merge check; when any prerequisite is unmerged, WARN AND STOP (Case B) — tell the user to merge the prerequisite's PR into the epic branch first. NEVER cut a story branch from an unmerged dependency branch, and never proceed silently.
- 🔴 Branch names (epic and story) are derived and created **automatically — never confirmed with the user**; they are announced. Only a dirty working tree (epic branch creation) still asks.
- 🔴 Story PRs target the epic branch; the epic branch PR targets the recorded base branch. Pass the target explicitly to `pr-generator` — invoked this way it runs in **workflow mode**, so it pushes and opens the PR **automatically** (Phase 5 skipped; the invoking workflow's gate is the authorization). It asks the user only when invoked standalone without a target. Every PR title is prefixed **`[STORY]`** or **`[EPIC]`** accordingly — pr-generator enforces this.
- 🔴 Record every branch created (name, base, chooser's raw response) in audit.md and keep `## Branching` in aire-state.md current.
- 🔴 Story branches therefore ALWAYS have exactly one base: the refreshed epic branch. There is no alternative base under any circumstance.

---

## 5. Bug Branch Model (`bug-fix` / `bug-fix-implement`)

The bug flow uses **ONE branch for the entire cycle** — no epic branch, no story branches:

```text
main (base branch — whatever branch the workflow started on)
 └── bug/PROJ-123-login-timeout      ← created at bug-fix start; ALL docs + code live here
```

1. **Creation** (during `bug-fix` workspace detection, automatic): record the base branch (`git branch --show-current` — never assume `main`), then `git fetch origin && git checkout -b bug/<TICKET-ID>-<kebab-case-ticket-title>` (whole name ≤ 60 chars; clean working tree required, else show `git status` and ask; for `Type: LOCAL`, `<TICKET-ID>` is the locally-minted `BUG-LOCAL-N` per `common/tracker-sync.md` Section 8). Record in `aire-state.md`:
   ```markdown
   ## Branching
   - Base Branch: main
   - Bug Branch: bug/PROJ-123-login-timeout
   - Bug PR: (pending — raised by bug-fix-implement after code review approval)
   ```
   Skip creation if `## Branching` already records a Bug Branch (resumed bug) — verify it exists and switch to it. Log in audit.md.
2. **Single PR, at the END**: no PR is raised at requirements approval. `bug-fix-implement` raises the one PR — via **`pr-generator`**, target = the recorded **Base Branch**, title prefixed **`[BUG]`** — only after the automated code review's verdict is clean (findings are auto-remediated and re-reviewed until they are — there is no approval gate).
3. **Rules**: 🔴 never cut story branches in the bug flow; 🔴 never commit to the base branch directly; 🔴 the `[BUG]` PR targets the Base Branch (there is no epic branch to target); 🔴 record the PR URL in `## Branching` (`Bug PR: <url>`) and log every branching action in audit.md.
