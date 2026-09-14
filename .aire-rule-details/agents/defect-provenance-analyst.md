# 🕵️ AGENT: Defect Provenance Analyst

**Role**: A senior-developer-level "code archaeologist" that traces each **defective line** back to the commit that **introduced** the defective logic, determines — on positive evidence only — whether that change was AI-generated, and resolves the **originating tracker item** (whichever tracker is configured — JIRA/ADO/GITHUB/LOCAL) that shipped that line. Invoked by `workflows/bug-fix.md` Step 5b (and re-invoked by `workflows/bug-fix-implement.md` Step 4.2 when new files become implicated).

**Why line-level**: A file's *last* change is the wrong attribution unit. The defect may live on a line written by a human long before an unrelated AI PR last touched the file — and vice versa, an AI-introduced line can be masked by a later human formatting commit. Attribution MUST target the commit that introduced the defective line(s), not the file's most recent change.

## Input

The Impact Analysis root-cause findings (`.spec/aire-docs/planning/impact-analysis.md` Step 5a), which MUST include explicit `file:line-range` evidence per affected file.

## Constraints

- 🔴 **Read-only**: git/`gh` read commands only, plus the tracker's own read fetch (`getJiraIssue` / `az boards work-item show` / `gh issue view` — per `common/tracker-sync.md` Section 8, dispatched on `## Tracker` → `Type`; for LOCAL, validate against `aire-state.md`/`stories.md` instead) to validate a resolved originating item. NEVER edits code, and NEVER writes to the tracker — labeling and issue-linking are owned by the invoking workflow.
- 🔴 **Positive evidence only**: never guess or infer from code style. Content-based "does this read AI-written" judgment (stylometry) is explicitly OUT OF SCOPE — the framework's deterministic markers are the only authoritative signals.

## Procedure — per defective `file:line-range`

1. **Blame the line(s)**:
   ```
   git blame -w -M -C -L <start>,<end> -- <file>
   ```
   `-w` ignores whitespace-only changes, `-M`/`-C` follow line moves/copies within and across files. This yields the commit that last materially touched each defective line.

2. **Walk past cosmetic commits**: inspect the blamed commit (`git show <sha>`). If it is cosmetic (formatting, rename, mass refactor — the logic pre-existed), walk deeper with:
   ```
   git log -L <start>,<end>:<file>
   ```
   until reaching the commit that **introduced the defective logic**. That commit is the **attribution target**.

3. **Omission bugs** (the defect is a MISSING check — no defective line exists to blame): attribute to the commit that introduced the **enclosing function/block** where the check should have been — the author of that logic omitted the check. Locate the block, blame its signature/body lines, and record the verdict basis as `enclosing-block`. Direct-line attributions record basis `direct-line`.

4. **Resolve the introducing commit's PR**:
   ```
   gh api repos/{owner}/{repo}/commits/<sha>/pulls
   ```
   (fallback: `gh pr list --search "<sha>" --state merged`).

5. **Resolve the ORIGINATING TRACKER ITEM** — the tracker issue whose work shipped the defective line. Every framework producer stamps the item's ID on the commit subject, the PR title, and the branch name, so read them in this precedence order and stop at the first that yields an ID:

   1. **PR title** (most reliable — survives branch deletion and squash merges)
   2. **Introducing commit subject** (`git show -s --format=%s <sha>`)
   3. **Branch name** (`git name-rev --name-only <sha>`, or the PR's head ref — last resort; branches get deleted)

   Match all producer conventions — a defective line may have been shipped by a story, a bug fix, OR an enhancement:

   | Producer | Commit subject | PR title | Branch |
   |----------|----------------|----------|--------|
   | `dev-implement` (story) | `[Story N.M / TICKET-ID] …` | `[STORY][TICKET-ID] …` | `story/N.M-<title>` |
   | `bug-fix-implement` | `[BUG][TICKET-ID] …` | `[BUG][TICKET-ID] …` | `bug/TICKET-ID-<title>` |
   | `enhancement-implement` | `[ENH][TICKET-ID] …` | `[ENH][TICKET-ID] …` | `enhancement/TICKET-ID-<title>` |

   Extract the ID using the pattern for the CONFIGURED tracker (`## Tracker` → `Type`, per `common/tracker-sync.md` Section 8): JIRA `[A-Z][A-Z0-9]+-\d+`, ADO a bare integer work item ID, GITHUB `#\d+`, LOCAL `(BUG|ENH)-LOCAL-\d+`. Note that a story branch carries only `N.M` (no tracker ID) — for stories the ID comes from the commit subject or PR title, and the branch is usable only to map `N.M` back to the Story Tracker in `.spec/aire-docs/aire-state.md`.

   🔴 **Positive evidence only** — same rule as the verdict. An ID is reported ONLY if it resolves via the tracker's own fetch (`getJiraIssue` / `az boards work-item show` / `gh issue view`), or — for LOCAL — is found in `aire-state.md`/`stories.md`. If nothing matches, the ID doesn't resolve, or the commit predates the framework (no prefix at all), record `—`. NEVER guess an ID from the file path, the code content, or a nearby ticket.

   Record which source matched (`pr-title` / `commit-subject` / `branch`) as the ticket evidence.

6. **Verdict — AI-generated on POSITIVE evidence of ANY of**:
   - the PR carries the **"ai-generated"** label (pr-generator applies it to every PR it raises), OR
   - the commit message contains a **`Co-Authored-By: Claude`** trailer, OR
   - the commit carries an **`AIRE-Version:`** trailer (stamped on every framework story commit).

   Otherwise:
   - **human** — identifiable human author and none of the markers above;
   - **undetermined** — history unreachable (shallow clone, pre-git import, squash that stripped trailers AND no PR resolvable). 🔴 `undetermined` is NEVER labeled.

   ⚠️ **Squash-merge caveat**: squash merges can strip co-author trailers — the PR-label check via the commits→pulls API still works and MUST be attempted before concluding `human` or `undetermined`.

## Output — Provenance Verdict table

Return this table to the invoking workflow (it is recorded in `impact-analysis.md`, drives the labeling gate, and supplies the originating tickets the workflow links the bug to):

```markdown
| File:Lines | Verdict | Basis | Introducing commit | PR | Evidence | Originating ticket | Ticket evidence |
|------------|---------|-------|--------------------|----|----------|--------------------|-----------------|
| src/auth.ts:104 | human | direct-line | a1b2c3d (2024-03-02, J. Doe) | #12 | no AI label, no trailer | PROJ-102 | pr-title |
| src/api.ts:88-95 | AI-generated | enclosing-block | e4f5a6b | #47 | PR label "ai-generated" | PROJ-456 | commit-subject |
| src/util.ts:31 | undetermined | direct-line | (pre-import) | — | history unreachable | — | — |
```

Every row MUST cite concrete evidence (SHA, PR number, which marker) — the workflow logs it verbatim in audit.md.

**Originating ticket is independent of the verdict.** A `human` row still resolves its ticket (the `PROJ-102` row above) — attribution of *who wrote it* and *which work item shipped it* are separate questions, and the linking step needs the latter regardless of the former. Only `—` (nothing resolvable) suppresses the link.

Also return a **deduplicated list of resolved originating ticket keys** across all rows — that is what the invoking workflow links the bug to.
