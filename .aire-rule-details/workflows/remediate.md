# 🔑 WORKFLOW: `remediate`

**Status**: Runs in two ways:
- **🤖 Automatically** — as the auto-remediate loop (**SH-LOOP-5**) of `dev-implement` / `bug-fix-implement` / `enhancement-implement`, whenever their automated Code Review reports findings. No user decision is involved; the loop repeats until the review verdict is clean **or its 3-round retry budget is exhausted**.
- **Standalone** — user-initiated at any time against a chosen review report (confirm-first, as written below).

> **🤖 When reached from a workflow's AUTO-REMEDIATE LOOP** (`dev-implement`, `bug-fix-implement`, `enhancement-implement`): the review reported findings and the framework is fixing them **automatically — no user chose this**. The report is already known (`story-[N.M]-…` / `bug-<JIRA-ID>-…` / `enhancement-<JIRA-ID>-code-review-v[X].md`), so **SKIP the "which report" prompt (Step 2)** AND **SKIP the scope-confirmation HALT** (`implementation/remediate.md` Step 3 — automatic mode): every 🔴/🟠 finding is in scope and nothing is deferred. After the fixes + audit, control returns to the invoking workflow, which **re-runs Code Review automatically** and keeps looping until the verdict is clean or its budget runs out. Present no menu and ask nothing.
>
> 🔁 **RETRY-BUDGET DISCIPLINE in automatic mode.** The invoking workflow's **Self-Healing Retry Policy** allows **at most 3 remediation rounds**, and each invocation of this workflow consumes exactly one. Therefore:
> - **Report the round number** (`round [n] of 3`) that the invoking workflow supplies, in your output and in every audit entry for the round.
> - **Fix EVERY 🔴 and 🟠 finding in the report in this single round.** Do not stage fixes across rounds, do not defer a finding as "next round", and do not fix only the easy subset — there may be no next round.
> - **State the root cause before each fix** (SH-7). A speculative change with no stated root cause wastes a round.
> - **Never repeat a previous round's change.** If the report's annotations show a finding was already attempted and still stands, say so explicitly and describe what is blocking it, rather than reapplying the same edit.
> - **If a finding cannot be fixed in this round, return it unfixed with a written reason.** The invoking workflow needs that reason for its Retry-Limit Report. 🔴 Never mark a finding resolved that is not resolved, and never delete a finding from the report to make the round look complete — that is the analogue of deleting a failing test.

**Capability**: **Remediate** — DEV role. Fixes issues from a review report (fix → unit test → green; runs ONLY the unit tests of the story/stories in scope — never the full repo suite) and annotates the report in place.

> 🔎 **Intake format** (as produced by `workflows/code-review.md` / `implementation/code-review.md`): issues `ISS-XXX` (story) or `S[N.M]-ISS-XXX` (all-stories), each tied to a specific AC/requirement; only two severities exist — 🔴 Blocker (AC/req Not Met or broken) and 🟠 High (Partially Met) — and BOTH are mandatory to fix (defer only with explicit user consent).

---

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone. Resolve the rule details directory the same way `CLAUDE.md` does (check `.aire-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`, `common/question-format-guide.md`
- The detailed fixer steps from `implementation/remediate.md`

All paths below are relative to the resolved rule details directory.

---

## Recommended workflow execution

- Run **Remediate** as a **code-editing workflow**, scoped strictly to the issues in the named review report.
- The main workflow stays the orchestrator: it confirms the report and scope, spawns remediation, updates the Story Tracker, and handles all confirm-first tracker transitions (workflow never touches the board without confirmation, for any tracker type).

## Per-story / all-stories flow when invoked
1. **Check for reports** — `.spec/aire-docs/implementation/reviews/story-*-code-review-v*.md` (story-wise) and `all-stories-code-review-v*.md` (all stories together; distinct filename so it is unmistakably intakeable here). If none exist, **STOP**: "Run Code Review first to produce a report to remediate from."
2. **Ask which report to remediate** — DO NOT guess. Enumerate the newest version per story plus the newest all-stories report (grouped: story reports, all-stories reports and let the user choose — story-wise remediation from a story report, or a full sweep from an all-stories report.)
3. Load and execute all steps from `implementation/remediate.md` (load review target context → build backlog → **confirm scope and HALT — standalone mode only; skipped in the automatic loop** → fix → unit test → green (run only the in-scope story's unit tests), 🔴/🟠 mandatory → annotate report in place).
4. **Do NOT change the Story Tracker status.** Remediate edits code but does not introduce a status of its own — every story it touches stays `🔵 In Development` (it moves to `🧪 Ready for Testing` only when its PR is **merged**, promoted by the `ve-list-work` skill once ve has tested it). Record the fixes and evidence in the report and audit.md, not a status change.
5. **Recommend re-review** (`workflows/code-review.md`) — required if any 🔴 was fixed.
6. **Offer a PR of the changes** (standalone invocations only): the "After Remediation" next-step menu in `implementation/remediate.md` includes option 2️⃣ — "Satisfied with the remediation? Raise a PR of these changes". If chosen, invoke the **`pr-generator` skill** (`.claude/skills/pr-generator`) as-is (it confirms before push/PR) per Step 7. **The automatic loop shows NO menu at all** — the invoking workflow raises the PR itself once the review is clean.

## Execution
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load `implementation/remediate.md` when the user invokes this workflow OR when a development workflow's auto-remediate loop triggers it after a review with findings
3. Outside those auto-remediate loops it is **user-initiated** — never auto-run it in any other context
3.5. **🎨 DESIGN REFERENCE SUPPLIED DURING REMEDIATION (`common/design-reference-grounding.md` DR-1 + DR-7 — MANDATORY)**: if the user supplies a path, spec file, screenshot, or design URL while adjusting scope or describing an issue, it is a design reference — register it in `## Design References` in `aire-state.md` immediately and read its **actual content** (DR-2), not just the part covering the issue in hand. Then, before fixing anything:
   - **Assess its true blast radius**: determine everything the reference `Governs` — it is usually broader than the current story (a prototype for one control is often a prototype for the whole feature).
   - **State which ALREADY-COMPLETED stories/components it invalidates**, and which not-yet-built stories must now be grounded against it — a plain report in your output, **not a question**. Do NOT silently limit the reference to the story currently being remediated.
   - On a mismatch between the reference and an approved AC, apply **DR-8** then **DR-6**: a point already in the `### Reconciliations` table was decided deliberately — follow the artifact and do not reintroduce it. Otherwise follow the reference, say plainly what differed, amend the AC / `requirements.md` / the tracker item per `common/requirements-traceability.md` to stay truthful, record the new reconciliation, and continue — no A/B question, no halt (the remediation flow's own existing scope confirmation is the only checkpoint).
   - Log the registration, what was extracted, and the invalidation list in audit.md.
4. **MANDATORY**: Log user responses and any tracker updates in audit.md with complete raw input. Every entry MUST carry the `**TRACKER ITEM**:` field (the remediated story's tracker link, or local Story ID) AND the `**Epic Link**:` field (full Parent Epic URL from `## Tracker` in `.spec/aire-docs/aire-state.md`, or `none`) — per the Audit Entry Format in `workflows/dev-implement.md`

---

## 🔄 Tracker Sync Rule (reminder)

Remediate does **NOT** change the story status — every story it touches stays `🔵 In Development` — so there is normally no tracker transition to perform here. If a remediation ever does drive a status change, the **Tracker Sync Rule** in `CLAUDE.md` (mechanics in `common/tracker-sync.md` Section 4) applies (confirm-first, verify, never update only one side).

---

> **Next (optional)**: Re-run **Code Review** (`workflows/code-review.md`) — required if any 🔴 was fixed; otherwise proceed to the next story / Operations.
