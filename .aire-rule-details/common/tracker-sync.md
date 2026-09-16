# Tracker Sync — Single Source of Truth for JIRA / ADO / GITHUB / LOCAL

**Purpose**: aire supports FOUR interchangeable issue trackers — **JIRA**, **ADO** (Azure DevOps Boards), **GITHUB** (GitHub Issues/Projects), and **LOCAL** (no external tracker at all). This file is the ONLY place tracker-specific mechanics are defined — every workflow, stage, and skill that needs to create an issue, transition a status, assign someone, link a story to its Epic, fetch an existing ticket, or record a comment dispatches through the tables below instead of re-deriving tracker-specific commands inline. When any other rule file says "apply the Tracker Sync Rule" or "per `common/tracker-sync.md`", it means: read `## Tracker` → `Type` in `.spec/aire-docs/aire-state.md`, then follow the row for that `Type` in the relevant table here.

**LOCAL is a fully first-class mode, not a degraded one.** When `Type: LOCAL`, aire MUST work end-to-end with zero external tool calls (no MCP, no `gh`, no `az`) — the Story Tracker in `aire-state.md` is the single source of truth, IDs are locally minted, and every "ticket-keyed" workflow (which normally takes an existing tracker ID as its invocation argument) gets an equivalent local entry point that asks the user to describe the item inline instead of fetching it. A LOCAL project must never be blocked or degraded because "the real flow assumes Jira."

---

## 0. Renamed / Generalized Vocabulary (apply EVERYWHERE, exact strings)

Every file in the framework that used to hardcode "Jira" as the only tracker adopts this vocabulary. This is a substitution of the tracker mechanism, not a rewrite of the surrounding workflow — approval gates, audit formats, ordering, and every other rule stay exactly as written.

| Old (Jira-only) | New (tracker-agnostic) |
|---|---|
| `## Jira` state section in `aire-state.md` | `## Tracker` |
| *(none)* | NEW first field under `## Tracker`: `- Type: JIRA \| ADO \| GITHUB \| LOCAL` |
| `Project Key` field | `Project Key / Repo / Org` — holds whichever identifier fits: Jira project key (`PROJ`), GitHub `org/repo`, ADO `org-url` + `project` (e.g. `https://dev.azure.com/myorg / MyProject`), or `—` for LOCAL |
| `Parent Epic:` / `Epic URL:` fields | unchanged names, generic meaning — a Jira Epic, a GitHub Milestone (or tracking issue), an ADO Epic work item, or a locally-described Epic (`Epic URL: —`) |
| Story Tracker column `Jira` | `Tracker ID` |
| `dependency-graph.yml` field `jira:` | `tracker_id:` |
| Audit field `**JIRA TICKET**:` | `**TRACKER ITEM**:` |
| The heading/concept "Jira Sync Rule" | "Tracker Sync Rule" |
| `<JIRA-ID>` keyword argument (`bug-fix <JIRA-ID>`, `ticket-implement <JIRA-ID>`, `enhancement-implement <JIRA-ID>`) | `<TICKET-ID>` — a Jira key, a GitHub issue ref (`#123` or URL), an ADO work item ID, **or omitted entirely for LOCAL** (the workflow then asks the user to describe the item inline and mints a local ID — see Section 8) |
| "Atlassian MCP" as the only integration path | one of four dispatch branches per capability table below: **JIRA** (Atlassian MCP) / **ADO** (`az boards` CLI) / **GITHUB** (`gh` CLI + `gh api graphql`) / **LOCAL** (no external call — local tracker only) |
| "Story selection is Jira-only" | Story selection is **tracker-driven**: the user types the Tracker ID for JIRA/ADO/GITHUB, or the local Story ID (`N.M`) for LOCAL |

---

## 1. Tracker Selection (asked ONCE, at the very start of the workflow)

Executed by `planning/workspace-detection.md`, immediately after Session Identity Capture and before Parent Epic Capture — this MUST be known before the Epic can be resolved. **Skip entirely and reuse the recorded value** if `aire-state.md` already contains a `## Tracker` section (resumed project) — never re-ask.

```markdown
❓ Which issue tracker should aire use for this project?

A) 🔷 Jira            — stories/epics pushed via the Atlassian MCP
B) 🔶 Azure DevOps    — work items pushed via the `az boards` CLI
C) 🐙 GitHub          — issues/milestones pushed via the `gh` CLI
D) 📍 Local only      — no external tracker; everything tracked in aire-state.md

[Answer]:
```

🔴 **GUARDRAIL — exactly these 4 options, nothing else.** Do NOT append an `X)`/`E)` "Other" option — this deliberately OVERRIDES `common/question-format-guide.md`'s general A–E/"Other" pattern; the tracker set is fixed and closed, so only `A`/`B`/`C`/`D` are valid answers. 🔴 Ask it plainly — do NOT justify or explain the "never infer the tracker" rule to the user (no "per the AIRE framework rules..." preamble); just present the question above and wait.

🔴 **ASK THIS IN THE CHAT SESSION ONLY.** Do NOT create a question `.md` file for it — this question deliberately does NOT use `common/question-format-guide.md`'s file-based convention. Present it conversationally and wait for the reply; only the ANSWER is persisted (to `aire-state.md` and `audit.md`).

🔴 **MANDATORY FOR ALL 4 CASES, NO EXCEPTIONS**: always ask — even when the pasted Epic link is on a domain that looks unambiguous (e.g. `atlassian.net` or `dev.azure.com`). Recognizing the domain is NEVER a reason to skip the question.

Record the answer immediately in `.spec/aire-docs/aire-state.md`:
```markdown
## Tracker
- Type: JIRA | ADO | GITHUB | LOCAL
- Parent Epic: none
- Epic URL: —
- Project Key / Repo / Org: —
```
Log the question and the complete raw answer in `audit.md`. **Every later stage reads `## Tracker` → `Type` before doing anything tracker-specific — never assume JIRA, and never re-ask this question once `## Tracker` exists.**

**Type-specific one-time follow-up, asked immediately after (skip entirely for LOCAL)**:
- **JIRA**: no extra question — Section 2 (Parent Epic Capture) derives the project key from the Epic key.
- **ADO**: `❓ Azure DevOps organization URL and project name? (e.g. https://dev.azure.com/myorg, "MyProject")` → record `Project Key / Repo / Org: <org-url> / <project>`. Verify auth: `az account show`; if it fails, tell the user to run `az login` first and wait.
- **GITHUB**: `❓ GitHub repo? (org/repo)` → record `Project Key / Repo / Org: <org>/<repo>`. Verify auth: `gh auth status`; if it fails, tell the user to run `gh auth login` first and wait.
- **LOCAL**: no question. `Project Key / Repo / Org: —` permanently. No CLI/MCP auth is ever checked or required for a LOCAL project.

---

## 2. Parent Epic Capture

Generalizes CLAUDE.md's "MANDATORY: Parent Epic Capture." The user normally starts with an existing Epic/tracking-issue/work-item reference in the SELECTED tracker.

| Type | User provides | Fetch command | If nothing provided |
|---|---|---|---|
| JIRA | Epic key/URL (e.g. `PROJ-50`) | `getJiraIssue [EPIC-KEY]` (Atlassian MCP) | Don't block — User Stories Part 3 asks before pushing |
| ADO | Epic work item ID/URL | `az boards work-item show --id [ID] --project "{PROJECT}"` | Same |
| GITHUB | Milestone number/URL, or a tracking issue | `gh api repos/{ORG}/{REPO}/milestones/{NUMBER}` (milestone) or `gh issue view {NUMBER} --repo {ORG}/{REPO}` (tracking issue) | Same |
| LOCAL | A plain-English description, pasted or typed inline | No fetch — write the user's description directly into `epic-brief.md` | Don't block — ask once during User Stories Part 1 if still missing, record `Parent Epic: none` |

Save the fetched (or typed) summary/description/acceptance-criteria to `.spec/aire-docs/planning/requirements/epic-brief.md` exactly as before — this is the primary input to Requirements Analysis and User Stories regardless of tracker.

Record in `## Tracker`:
```markdown
- Parent Epic: <key/number, or "none">
- Epic URL: <url, or "—" for LOCAL>
- Project Key / Repo / Org: <derived or asked value>
```

**Conflict rule (unchanged)**: if `## Tracker` already records a DIFFERENT Epic (resumed project), ask which to keep — NEVER silently overwrite.

---

## 3. Story/Issue Creation at Push Time (generalizes User Stories Part 3)

Runs once per approved story, immediately after GATE 1. **LOCAL never pushes anything** — stories simply stay in `stories.md` + the Story Tracker with `Tracker ID: LOCAL`.

### JIRA (unchanged from the existing framework behavior)
```
@atlassian createJiraIssue in project [PROJECT_KEY]:
  issueType: Story
  summary: [story title]
  description: [story narrative + acceptance criteria + persona]
  labels: [aire, aire-v[N]]
  Component: default | Organization: All Orgs | Severity: Low
```
Then: transition to "Ready for Development" (`getTransitionsForJiraIssue` → `transitionJiraIssue`), verify; link to Parent Epic (`editJiraIssue` parent/Epic Link, or `createIssueLink`), verify.

### ADO
```bash
STORY_WI_ID=$(az boards work-item create \
  --type "User Story" \
  --title "Story N.M: <Story Title>" \
  --description "<story narrative + AC as HTML>" \
  --project "{PROJECT}" \
  --fields "Microsoft.VSTS.Common.AcceptanceCriteria=<AC as HTML checklist>" \
           "System.Tags=ai-generated;aire;aire-v[N]" \
  --query "id" -o tsv)

az boards work-item relation add --id "$STORY_WI_ID" \
  --relation-type "System.LinkTypes.Hierarchy-Reverse" --target-id "$EPIC_WI_ID"

az boards work-item update --id "$STORY_WI_ID" --state "New" --project "{PROJECT}"
```
Verify creation (`az boards work-item show --id "$STORY_WI_ID"`) and the parent link before continuing. `$EPIC_WI_ID` is the Parent Epic's numeric ID from `## Tracker`.

### GITHUB
```bash
gh issue create --repo "ORG/REPO" \
  --title "Story N.M: <Story Title>" \
  --body "$(cat <<'EOF'
## Story Metadata
**Epic**: N - <Epic Name>

[story narrative + acceptance criteria + persona]
EOF
)" \
  --label "story" --label "ai-generated" --label "aire-v[N]" --label "status:ready-for-dev" \
  --milestone "Epic N: <Epic Name>"
```
Verify: exit code 0 AND captured output matches `^https://github\.com/[^/]+/[^/]+/issues/\d+$` → extract `ISSUE_NUMBER`. Content-parity check: `gh issue view ISSUE_NUMBER --repo "ORG/REPO" --json body --jq '.body | contains(...)'`. The Milestone (created once per Epic via `gh api repos/ORG/REPO/milestones --method POST`) IS the Parent Epic link — no separate linking step. **Status starts as the `status:ready-for-dev` label** (see Section 4 — GitHub issues have no native custom-state field, so status is always represented as a label, and the issue itself stays `open` for the story's whole lifecycle).

### Write-back (ALL non-LOCAL types)
Update the story file / `stories.md` header and the Story Tracker `Tracker ID` column with the returned key/number/ID. For LOCAL, the column is simply `LOCAL`.

---

## 4. Status Transitions (the "Tracker Sync Rule")

The Story Tracker's three valid statuses (`🟢 Ready for Development` → `🔵 In Development` → `🧪 Ready for Testing`) map onto each tracker as follows. **Applies at every point a story/ticket's status changes** — story pick, PR raise, PR merge + ve sign-off, Parent Epic sync, and the bug/enhancement single-ticket flows.

| Tracker Status | JIRA | ADO (`System.State`) | GITHUB (label swap, issue stays `open`) | LOCAL |
|---|---|---|---|---|
| 🟢 Ready for Development | Transition to "Ready for Development" (`getTransitionsForJiraIssue` → `transitionJiraIssue`) | `az boards work-item update --id X --state "New"` (or the project's nearest equivalent — verify via `az boards work-item show` / process metadata, announce any substitution) | `gh issue edit N --repo ORG/REPO --remove-label "status:in-development" --remove-label "status:ready-for-testing" --add-label "status:ready-for-dev"` | Update the Story Tracker only |
| 🔵 In Development | `transitionJiraIssue -> "In Development"` | `az boards work-item update --id X --state "Active"` | swap label to `status:in-development` | Update the Story Tracker only |
| 🧪 Ready for Testing | `transitionJiraIssue -> "Ready for Testing"` | `az boards work-item update --id X --state "Resolved"` (or nearest equivalent) | swap label to `status:ready-for-testing` | Update the Story Tracker only |

**Sync rule** (replaces "Jira Sync Rule" everywhere it was named):
- If **Tracker ID = `—`/`LOCAL`**: update ONLY the local Story Tracker. No external call of any kind.
- If **Tracker ID is a real JIRA/ADO/GITHUB identifier**: ALSO transition the tracker issue via the row above, per the type in `## Tracker`. **VERIFY** the transition landed (re-fetch/re-view the issue) before considering the change complete.
- **Exception — story pick and PR-merge transitions are automatic** (no confirmation): the `🟢→🔵` transition at story pick and the `🔵→🧪` transition on confirmed PR merge apply to the tracker AND the local tracker WITHOUT asking — both verified + announced. Any OTHER transition (e.g., the Parent Epic moving) remains confirm-first.
- **Epic status sync**: same triggers as before (first story → In Development is automatic; last story → Ready for Testing is confirm-first) — apply via the same per-type row, targeting the Parent Epic's ID instead of the story's.
- **NEVER silently update only one side** when a non-LOCAL Tracker ID exists — local tracker and the external tracker must always agree.

---

## 5. Assignment (on story pick / ticket claim)

| Type | Identity used | Command |
|---|---|---|
| JIRA | Session email → Jira account | `lookupJiraAccountId` (email) → `editJiraIssue` (`assignee = accountId`) → verify by re-fetching |
| ADO | Session email directly (ADO accepts email/UPN) | `az boards work-item update --id X --assigned-to "<session-email>"` → verify via `az boards work-item show` |
| GITHUB | GitHub login (email does NOT map to a login) | Ask ONCE per session (cache in `## Tracker` as `- GitHub Username: <login>`): `❓ Your GitHub username, for issue assignment?` then `gh issue edit N --repo ORG/REPO --add-assignee <login>` → verify via `gh issue view` |
| LOCAL | N/A | No assignee field — optionally note the operator's session email in the Story Tracker row as a comment; never blocks |

Unresolvable/ambiguous identity on JIRA/ADO/GITHUB → leave unassigned, warn the user, continue (non-blocking, exactly as the original Jira-only rule specified).

---

## 6. Linking a Story to its Parent Epic

| Type | Mechanism |
|---|---|
| JIRA | `editJiraIssue [STORY-KEY]`: set Epic Link / parent = `[EPIC-KEY]` (or `createIssueLink` if the project uses issue links) — verify by re-fetching |
| ADO | `az boards work-item relation add --id [STORY-ID] --relation-type "System.LinkTypes.Hierarchy-Reverse" --target-id [EPIC-ID]` — verify via `az boards work-item show --query relations` |
| GITHUB | The story issue is created with `--milestone "Epic N: <Name>"` (Section 3) — the Milestone IS the link; verify via `gh api repos/ORG/REPO/issues/N --jq '.milestone.title'` |
| LOCAL | The `Requires`/Epic reference lives only in `stories.md`'s header line and the Story Tracker — no external link to verify |

---

## 7. Causation Link ("is caused by" — used by `agents/defect-provenance-analyst.md`)

Establishes `[Bug] --"is caused by"--> [Originating item]` so the causal chain is queryable where the platform supports it.

| Type | Mechanism |
|---|---|
| JIRA | Unchanged existing behavior: resolve the link type via `getIssueLinkTypes` (never hardcode), matching the **inward** description; create the link with the bug as `outwardIssue` (never `inwardIssue` — see the direction warning in `defect-provenance-analyst.md`); verify direction by re-reading `issuelinks`; ALSO add a plain-text comment recording the relationship as the authoritative record when the link type is generic. If no "is caused by" type exists on the instance, fall back to a comment-only record and tell the user adding that link type would make it JQL-queryable. |
| ADO | ADO has no native "is caused by" relation. Best effort: `az boards work-item relation add --id [BUG-ID] --relation-type "System.LinkTypes.Related" --target-id [ORIGIN-ID]` (the closest native type — it does NOT encode direction/semantics), PLUS a mandatory comment on the bug work item stating the causation explicitly (`az boards work-item update --id [BUG-ID] --discussion "Caused by work item #[ORIGIN-ID] — <one-line reason>"`). The comment is the authoritative record; the "Related" link is best-effort metadata only. |
| GITHUB | GitHub issues have no typed relation API reachable via `gh`. Record causation as a plain comment on the bug issue (GitHub auto-links `#N` references): `gh issue comment [BUG-NUMBER] --repo ORG/REPO --body "Caused by #[ORIGIN-NUMBER] — <one-line reason>"`. This comment IS the record — there is no typed link to attempt first. |
| LOCAL | Write the causation directly into the bug's entry in `stories.md` / the impact-analysis doc as a plain note (`Caused by: Story 1.3` or `Caused by: BUG-LOCAL-2`) — no external call. |

This step runs automatically (no confirm-first gate) in all four cases — the analyst only reports a link on positive, verified evidence, per `defect-provenance-analyst.md`.

---

## 8. Fetching (or Creating) the "Ticket" for `ticket-implement` / `bug-fix` / `enhancement-implement`

These workflows normally take an existing tracker item as their invocation argument (`<TICKET-ID>`, formerly `<JIRA-ID>`). Each tracker resolves it differently; **LOCAL has no existing item to fetch — it mints one from an inline description instead.**

| Type | Invocation | Fetch/creation |
|---|---|---|
| JIRA | `bug-fix PROJ-123` | `getJiraIssue PROJ-123`: key, issue type, summary, description, acceptance criteria, labels |
| ADO | `bug-fix 4821` (work item ID) or a work-item URL | `az boards work-item show --id 4821 --project "{PROJECT}"` |
| GITHUB | `bug-fix #88` or an issue URL | `gh issue view 88 --repo ORG/REPO --json title,body,labels,state` |
| LOCAL | `bug-fix` (no ID given) | **No fetch.** Ask: `❓ Describe the bug/enhancement (what's broken or what should change, and why):` — capture the answer, mint a local ID (`BUG-LOCAL-N` / `ENH-LOCAL-N`, next unused N found by scanning `aire-state.md`), and write it as the "ticket" content the rest of the workflow (impact analysis, fix plan, etc.) reads exactly as it would read a fetched ticket. |

Everywhere the framework says `<JIRA-ID>` in a keyword (`bug-fix <JIRA-ID>`, `ticket-implement <JIRA-ID>`, `enhancement-implement <JIRA-ID>`), it now accepts `<TICKET-ID>` per the table above, OR no argument at all when `## Tracker` → `Type: LOCAL` (the workflow prompts for the inline description instead of parsing an ID from the invocation). Regex extraction of an ID from commit subjects / PR titles / branch names (used by `defect-provenance-analyst.md` and audit logging) likewise matches whichever pattern fits the configured tracker:
- JIRA: `[A-Z][A-Z0-9]+-\d+`
- ADO: a bare integer work item ID
- GITHUB: `#\d+` (or the bare issue number)
- LOCAL: `(BUG|ENH)-LOCAL-\d+`

---

## 9. Labels & Version Stamping

| Type | `ai-generated` marker | Framework version marker |
|---|---|---|
| JIRA | label `aire` | label `aire-v[N]` (full minor version, e.g. `aire-v1.0`) |
| ADO | tag `ai-generated` in `System.Tags` | tag `aire-v[N]` in `System.Tags` |
| GITHUB | label `ai-generated` | label `aire-v[N]` |
| LOCAL | N/A (no external object to label) | Record the version in the local story/ticket file's header line instead (unchanged — every framework artifact already does this for commits/PRs) |

`[N]` is always read live from the "AIRE Framework Version" line in `CLAUDE.md` — never hardcoded, regardless of tracker.

---

## 10. Comments

| Type | Mechanism |
|---|---|
| JIRA | `addCommentToJiraIssue` |
| ADO | `az boards work-item update --id X --discussion "<text>"` |
| GITHUB | `gh issue comment N --repo ORG/REPO --body "<text>"` |
| LOCAL | Append a dated note to the story's entry in `stories.md` / the relevant local doc — no external call |

---

## 11. Branch Naming (generic ID slug — feeds `common/branching-strategy.md`)

Branch names use whichever ID the tracker produced, in the SAME positions the framework already uses a "Jira key":
- `epic/<EPIC-ID>-<kebab-title>`, `story/<N.M>-<kebab-title>` (prefixed with the story's Tracker ID when non-LOCAL, e.g. `story/PROJ-102-1.2-login-endpoint`, `story/1.2-login-endpoint` for LOCAL/GITHUB-numeric/ADO-numeric where a bare number reads poorly as a prefix — use the Story ID `N.M` as the prefix instead and mention the Tracker ID in the branch's PR body), `bug/<TICKET-ID>-<kebab-title>`, `enhancement/<TICKET-ID>-<kebab-title>`.
- For LOCAL, `<TICKET-ID>` is the locally-minted `BUG-LOCAL-N` / `ENH-LOCAL-N` (never blank).

---

## 12. LOCAL Mode — Explicit Completeness Guarantee

A `Type: LOCAL` project MUST be able to run the ENTIRE framework — Planning through Implementation, including the bug/enhancement/ticket flows and ve's Test Plan — with zero external tracker calls:
- No MCP tool, no `gh`, no `az` command is ever invoked.
- Every "fetch the ticket" step becomes "ask the user to describe it inline" (Section 8).
- Every "transition/assign/link/label/comment" step becomes "update the local Story Tracker / local doc only" (Section 4–Section 10).
- Nothing in any workflow may block, warn, or degrade functionality because "Jira integration is required" — that assumption is retired everywhere in favor of dispatching on `## Tracker` → `Type`.

---

## 13. Critical Rules

- 🔴 Read `## Tracker` → `Type` at the START of any step that used to assume Jira — never hardcode "Jira" as the only path again.
- 🔴 The Tracker Selection question (Section 1) is asked EXACTLY ONCE per project, at workspace detection, before Parent Epic Capture. Never re-ask once `## Tracker` exists.
- 🔴 LOCAL is a complete, first-class mode (Section 12) — it is not "Jira with extra steps skipped."
- 🔴 Every transition/assignment/link is VERIFIED after the call (re-fetch/re-view), for JIRA, ADO, and GITHUB alike — never assume success from a non-error exit code alone.
- 🔴 NEVER silently update only the local tracker when a non-LOCAL Tracker ID exists, and never silently update only the external tracker without the local Story Tracker — both sides always move together.
- 🔴 ID-format regexes (Section 8) are tracker-specific — always match against the CONFIGURED tracker's pattern, never guess a format from content.
- 🔴 `[N]` (framework version) is always read live from `CLAUDE.md` — this rule is unaffected by which tracker is configured.
