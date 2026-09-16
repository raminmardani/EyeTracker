# Code Review - Detailed Steps

> 🔴 **REVIEW-ONLY WORKFLOW.** The REVIEWER role MUST NOT edit source code, tests, or configs. It may write ONLY to `.spec/aire-docs/implementation/reviews/` and update the Story Tracker in `.spec/aire-docs/aire-state.md`. Findings are produced as a report; fixes are performed during **Remediate** (`implementation/remediate.md`). If issues are found, this workflow MUST recommend Remediate as the next step.

**Purpose**: **Strictly verify that each story's acceptance criteria and mapped requirements are completed by the code — nothing more.** Produce a versioned review report. Reviews can target a **specific story** or **all stories together** (the full Story Tracker reviewed against the code in one pass).

> ⚖️ **SCOPE DISCIPLINE (HARD RULE)** — Report a finding ONLY if it is one of:
> 1. An **acceptance criterion NOT met** (or only partially met) by the code
> 2. A **requirement mapped to the story NOT implemented** as specified
> 3. A **genuine defect** (bug, crash, security hole, broken flow) that prevents an AC/requirement from actually working
>
> Do **NOT** report: style/naming/formatting nits, refactoring or SOLID suggestions, "could be improved" / "consider adding" / nice-to-have items, missing docs/comments, or hypothetical future concerns. **A clean review (zero findings) is a valid and expected outcome — NEVER invent findings to justify the review.** This review runs automatically after every `dev-implement`; padding it with advisory items creates endless remediate loops.

**Recommended execution**: Run as a **read-only workflow** (no code-editing tools) so the reviewer physically cannot modify source. The orchestrator reads the returned report path and verdict.

## Agent Role
**REVIEWER** — analyzes and reports only.

---

## Tell Me What to Review

**DO NOT guess what to review. Present this prompt and wait:**

```text
What would you like me to review?

Options:
  a) A specific story                    (e.g., "story 1.2" — remediate can then fix that story alone)
  b) All stories together against the code   (type "all stories")
```

**Then, based on the answer, resolve the review target:**
- **Story**: identify the story number (e.g., N.M) and confirm it exists in the Story Tracker.
- **All stories**: every story in the `## Story Tracker` whose implementation has begun — Status `🔵 In Development` or `🧪 Ready for Testing` — is in scope. **EXCLUDED**: `🟢 Ready for Development` stories (no code yet). Note that a `🔵 In Development` story may still be mid-build (actively claimed by a developer, or awaiting its PR) — call this out so the user knows the review reflects its current, possibly-incomplete state. List the in-scope story IDs AND the excluded IDs (with reason) back to the user before starting.

---

## Phase 0: Review History Check (Prevents Endless Loops)

Before reviewing, ALWAYS check for a previous report matching the review target, then determine the review mode. Apply the rules below for the chosen target.

### If reviewing a story (story N.M)
1. **Previous review** — Does `.spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v*.md` exist? If yes, read the latest version; note its status (APPROVED / CHANGES REQUESTED) and prior issues. **Also check** for a newer `all-stories-code-review-v*.md` that covers this story — if one exists and is newer, surface its findings for this story so they are not double-reported or missed.
2. **Determine review mode**:
   - No previous review → **INITIAL_REVIEW** (🔴 + 🟠 — the only severities in this review)
   - Previous APPROVED + code unchanged → **SKIP**: "✅ Story [N.M] already approved. Code unchanged since last review."
   - Previous APPROVED + code changed → **NEW_CHANGES** (🔴 + 🟠 in changed files only)
   - Previous CHANGES REQUESTED → **FIX_VERIFICATION** (verify prior issues fixed + new 🔴/🟠 only)

### If reviewing all stories
1. **Previous review** — Does `.spec/aire-docs/implementation/reviews/all-stories-code-review-v*.md` exist? If yes, read the latest version; note its status (APPROVED / CHANGES REQUESTED) and prior issues per story. **Also check** individual `story-*-code-review-v*.md` reports newer than the last all-stories report — carry their open issues into this review so nothing is lost between the two report types.
2. **Determine review mode**:
   - No previous review → **INITIAL_REVIEW** (🔴 + 🟠 — the only severities in this review)
   - Previous APPROVED + code unchanged → **SKIP**: "✅ All stories already approved. Code unchanged since last review."
   - Previous APPROVED + code changed → **NEW_CHANGES** (🔴 + 🟠 in changed files only)
   - Previous CHANGES REQUESTED → **FIX_VERIFICATION** (verify prior issues fixed + new 🔴/🟠 only; apply per-story)

---

## Phase 1: Preparation
1. **Load review scope** — varies by review target:

   **If reviewing a story:**
   - [ ] Read the story from `.spec/aire-docs/planning/user-stories/stories.md`
   - [ ] Extract its acceptance criteria
   - [ ] Identify the files implementing this story (from `.spec/aire-docs/implementation/code/` summaries and the actual workspace code)
   - [ ] Note what is IN and OUT of scope

   **If reviewing all stories:**
   - [ ] Read the `## Story Tracker` in `.spec/aire-docs/aire-state.md` — enumerate every in-scope story (Status `🔵 In Development` or `🧪 Ready for Testing`; exclude `🟢 Ready for Development`)
   - [ ] For every in-scope story, read its acceptance criteria from `.spec/aire-docs/planning/user-stories/stories.md`
   - [ ] Read `.spec/aire-docs/planning/application-design/application-design.md` (if Application Design ran) and `.spec/aire-docs/planning/requirements/epic-brief.md` (if captured) for structural context — used only to locate code
   - [ ] Identify all implementation files (from `.spec/aire-docs/implementation/code/` summaries and workspace code)
   - [ ] Group findings by story in the report

2. **Read context** — error handling, logging, naming, and testing patterns from the design artifacts and any enabled extensions
3. **Read the code** — open all files to review, trace the main flows
4. **Load the eval inputs** — `.evals/config.json`, `.evals/rubrics/architecture-rubric.json` (applying the `common/eval-framework.md` Section 3 fallback chain; `N/A` if it bottoms out) and `security-rubric.json`, plus the existing `eval-evidence/<key>/eval.json` written by the Static Eval Gate. The J1/J2 scores are computed in Phase 3.5, where they act as **blocking gates**.

## Phase 2: AC & Requirements Verification (the ONLY review checklist)
- [ ] **Acceptance Criteria — verify each one**: for EVERY acceptance criterion of every in-scope story, trace the code and record a verdict:
  - ✅ **Met** — cite the evidence (`file:line` of the implementing code)
  - ⚠️ **Partially Met** — state exactly what part of the AC is missing or deviates from the spec
  - ❌ **Not Met** — state what is absent
- [ ] **Requirements coverage**: verify each requirement mapped to the story (from `requirements.md` / the story narrative) is implemented as written — same Met / Partially Met / Not Met verdicts with evidence
- [ ] **Genuine defects only**: report a bug, crash, security hole, or broken flow ONLY when it prevents an AC/requirement from actually working (e.g., the AC's flow throws, auth required by the story is absent, data required by an AC is never persisted)
- [ ] **Tests as AC evidence — STATIC check only, never re-run**: verify unit tests covering the ACs exist by READING them (they were generated + executed to ≥90% coverage during Code Generation's Unit Test & Coverage step). **Do NOT re-execute the unit test suite or re-measure coverage in this review** — when invoked via `dev-implement`, the gate just ran in the same session; reuse the passed-in/audit-recorded results (tests X/X passing, coverage %) as the report's evidence. Report a finding ONLY if an AC has no verification at all — do not nitpick test style or demand extra tests beyond the ACs
- [ ] **API & Contract Tests as evidence — STATIC check only, never re-run**: when the story/ticket touches an API layer, verify the API & Contract Testing Gate ran by READING `.spec/aire-docs/implementation/code/api-contract-test-evidence/<story-or-ticket-evidence-folder>/evidence-manifest.md` — confirm every new/changed endpoint has a checklist entry (functional, response-code validation, role-based authorization 401/403, error-response validation, request validation, response contract validation) marked ✅ Pass or N/A with a stated reason. **Do NOT re-execute these tests in this review** — reuse the recorded evidence. Report a finding ONLY if the gate should have applied (the code adds/changes an endpoint) but no evidence folder/manifest exists, or a checklist item is missing with no N/A reason — this is a Not Met/Partially Met finding against the relevant AC, not a style nitpick
- [ ] **Extension compliance** — if any extensions are enabled in `aire-state.md`, verify applicable rules (mark N/A where not relevant); violations of enabled extension rules are genuine findings

**Explicitly OUT of scope** (do NOT check, do NOT report): code style, naming, formatting, file organization, magic numbers, comment/documentation quality, SOLID/DRY/refactoring opportunities, performance ideas not required by an AC/NFR, and any "good to have" suggestion. If everything traces to Met with no defects → verdict is ✅ APPROVED with zero issues.

## Phase 2.5: 🛡️ Automated Security Review (MANDATORY — diff-scoped)

The AIRE **Security Baseline is always mandatory and blocking** for every project (`CLAUDE.md` Extensions Loading). This phase enforces it **per change**, automatically, instead of only when a human remembers to run the standalone `code-security-review` skill.

- [ ] **Run the `agents/code-security-review-agent.md` procedure** against the code in review scope. Follow that agent file exactly — it loads `extensions/security/baseline/security-baseline.md` and checks **all 16 rules (SECURITY-01 … SECURITY-16)** with their verification criteria, classifies severity, and shows file/line evidence
- [ ] 🔴 **SCOPE = THE CHANGE, NOT THE WHOLE REPO.** The agent's default is a full-codebase audit; that is far too heavy to run on every story and would flood the auto-remediate loop with pre-existing debt that this work unit did not introduce. Scope it to:
  - the **files this work unit added or changed**, and
  - the **attack surface those files reach** — the entry points, auth boundaries, data stores and external calls on the changed paths (Step 1 "map the attack surface", narrowed to the diff)
  - Rules that cannot apply to the changed surface are marked **N/A with the reason** — never silently dropped
  - The **full-codebase** audit remains the standalone `code-security-review` skill's job, unchanged
- [ ] **Write the security report** to `.spec/aire-docs/code-security-reviews/security-review-YYYY-MM-DD.md` per the agent's report structure (append a `-2` counter if one exists for today), noting in its header that the scan scope was this work unit's diff, not the full codebase
- [ ] **Map severities into THIS review's two reportable levels** and fold them into the issue list of Phase 3:
  | Security agent severity | Becomes | Behaviour |
  |---|---|---|
  | 🔴 Critical / Blocker | **🔴 Blocker** finding (`SEC-ISS-XXX`) | Blocking — drives the verdict and the auto-remediate loop |
  | 🟠 High | **🟠 High** finding (`SEC-ISS-XXX`) | Blocking — same |
  | 🟡 Medium / 🔵 Low | **Not a finding** | Listed in an explicitly non-blocking `## 🛡️ Security — Advisory (non-blocking)` section of the review report, carried into the security report, and NOT fed to remediation |
- [ ] Every mapped finding keeps its **SECURITY-XX rule ID, CWE/OWASP reference, evidence snippet and concrete remediation** from the agent's output — that is what makes it auto-fixable
- [ ] **Pre-existing findings are out of scope.** A Critical/High on a line this work unit did not touch is recorded in the security report and explicitly labelled pre-existing; it does **not** become a 🔴/🟠 finding here and does not block. Surface it to the user so it can be raised as its own ticket (`/raise-defect`) — the same treatment baseline regression failures and baseline static findings get
- [ ] 🔴 **NEVER suppress instead of fixing** — no `// nosec`, no `eslint-disable-next-line security/*`, no widening an allowlist, no marking a genuine finding N/A to clear the gate

**Why this is a finding while the judge scores are not**: a security violation is a concrete, reproducible defect with a named rule, a line number and a specific fix — exactly what the remediate loop closes deterministically, so it belongs in the issue list. The J1/J2 scores **also block** (Phase 3.5), but through their own threshold and their own repair loop (SH-LOOP-6), driven by per-criterion citations rather than by issue IDs. Keeping them out of the 🔴/🟠 list is what stops a moving number from churning the remediate loop.

## Phase 3: Document Findings
- [ ] Assign each issue a severity — only TWO are reportable: **🔴 Blocker** (AC/requirement Not Met, or a defect that breaks it) / **🟠 High** (AC/requirement Partially Met or deviates from spec) — plus a category, file:line, and a suggested fix. There are NO 🟡 Medium / 🟢 Low advisory findings in this review
- [ ] Create the report at the appropriate path (increment version `v[X]` on re-review). **The two targets use deliberately different filenames so Remediate can identify and intake either:**
  - **Story review**: `.spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v[X].md`
  - **All-stories review**: `.spec/aire-docs/implementation/reviews/all-stories-code-review-v[X].md`
- [ ] For all-stories reviews, group issues by story section in the report (issue IDs prefixed per story, e.g. `S1.2-ISS-001`, so Remediate can map every issue back to its story)
- [ ] **Include the Phase 2.5 security findings** in the issue list, keeping their `SEC-ISS-XXX` IDs, SECURITY-XX rule reference and remediation — they are first-class 🔴/🟠 findings alongside the AC/requirement ones
- [ ] Determine overall status strictly from the verdicts: any 🔴 (AC/req Not Met or broken, **or a Critical security finding**) → ❌ CHANGES REQUESTED; only 🟠 (Partially Met, **or a High security finding**) → ⚠️ APPROVED WITH COMMENTS; all ACs/requirements Met and zero security 🔴/🟠 → ✅ APPROVED
- [ ] 🔴 The **findings list** and the report's issue status are derived from AC/requirement verdicts **and Phase 2.5 security findings ONLY** — 🟡/🔵 security advisories never enter it, and neither do the Phase 3.5 scores. The **overall eval verdict** in `eval.json` additionally requires both Phase 3.5 judge gates to pass (or J1 to be `N/A`); a sub-minimum score blocks through its own gate, never by becoming a finding

## Phase 3.5: ⚖️ Judge Gates — J1 + J2 (🔴 BLOCKING)
Per `common/eval-framework.md` Section 4:
- [ ] **J1 — Architecture conformance**: score the diff against each criterion of `architecture-rubric.json` (derived from `.spec/architecture.md` Section 10), apply the criterion weights, and record the per-criterion breakdown to `eval-evidence/<key>/judge/architecture-score.json`. If the Section 3 fallback chain bottoms out (no derivable rubric — common for bug/enhancement work that skipped the design stages), record **`N/A` with the reason** and score nothing. 🔴 Never score against a generic or borrowed rubric — and an `N/A` **never blocks**
- [ ] **J2 — Security (OWASP 2025)**: score the diff against `security-rubric.json` (OWASP Top 10:2025 criteria applicable to this stack — broken access control, security misconfiguration, supply chain failures, cryptographic failures, injection, insecure design, authentication failures, data integrity failures, logging failures, mishandling of exceptional conditions) → `judge/security-score.json`
- [ ] **Scoring discipline** (Section 4.1): score **once** per review pass — 🔴 never re-roll for a better number; score each criterion independently, then weight; **every criterion below 1.0 MUST cite `file:line`** and state what violates it (an uncited sub-1.0 score is a defect in this pass — re-run that criterion); score only what the diff shows; a criterion this diff cannot exercise is **`N/A`**, excluded from the total, with the remaining weights renormalised to 1.0 — never scored 0
- [ ] Record the **pinned judge model** and the **`rubricVersion`** with both scores — a score without them is not comparable across runs
- [ ] Merge both into the **`gates`** block of `eval.json`, refresh `eval-summary.md`, and report both — with the J1 criteria breakdown — in the report
- [ ] **🔁 GATE**: `J1 ≥ llmJudgeArchitectureScoreMin` **and** `J2 ≥ llmJudgeSecurityScoreMin`, both read from `.evals/config.json`. Below minimum → the invoking workflow's **SH-LOOP-6** remediates the cited criteria (worst weighted-loss first) and this review re-scores on the next pass, **capped at 3 attempts**, then HALT with the Retry-Limit Report
- [ ] 🔴 **Forbidden ways to pass this gate** (SH-6): editing `architecture.md` Section 10 to weaken or delete a constraint · editing the rubric JSON · lowering either minimum · re-scoring until a run clears · marking an applicable criterion `N/A`
- [ ] 🔴 **The scores are still NOT 🔴/🟠 findings.** They gate through their own threshold, not through the issue list — so the anti-loop protection in rules 3, 5 and 10 stays intact

## Phase 4: Record the Verdict (NO Status Change)
- [ ] **Code Review is read-only and does NOT change the Story Tracker status.** A story under review stays `🔵 In Development` — the ONLY valid statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`, and the move to `🧪 Ready for Testing` happens only when the PR is raised via `dev-implement`. Do NOT set or demote any status here.
- [ ] Update only the review report and the audit trail — never the tracker Status column. (You MAY refresh the story row's `Recorded` timestamp to note that a review ran, but leave `Status` unchanged.)
- [ ] Because no status changes, there is normally **no tracker transition** in this phase. If your team's process nonetheless requires a board move on review completion, apply the **Tracker Sync Rule** (`common/tracker-sync.md` Section 4, confirm-first, verify) — but do NOT change the local tracker Status.
- [ ] Log the review verdict (✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUESTED) and the full findings list by severity in `.spec/aire-docs/audit.md` with timestamps

---

## Issue Severity

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| Blocker | 🔴 | AC/requirement NOT met, or a defect that breaks it | MUST fix before approval |
| High | 🟠 | AC/requirement PARTIALLY met / deviates from spec | SHOULD fix |

🟡 Medium / 🟢 Low do not exist in this review — anything that would have been advisory (style, refactoring, nice-to-have) is out of scope and is not reported at all.

---

## Output

**Location** (choose based on review target):
- Story: `.spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v[X].md`
- All stories: `.spec/aire-docs/implementation/reviews/all-stories-code-review-v[X].md`

### Code Review Report Template

```markdown
# Code Review - [Story N.M: <Story Name> | All Stories]

**Date**: [YYYY-MM-DD]
**Reviewed By**: REVIEWER (aire)
**Review Number**: [1, 2, ...]
**Review Mode**: [INITIAL_REVIEW / FIX_VERIFICATION / NEW_CHANGES]
**Review Target**: [Story N.M | All Stories]
**Status**: ✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUESTED
**Tracker ID**: [PROJ-NNN / ADO ID / GitHub #N, or list of IDs for all-stories, or — for LOCAL]

## Review Summary
**Components Reviewed**: [files]
**Stories in Scope**: [story numbers covered; for all-stories, also list stories excluded for having no code]
**Tests Reviewed**: [Yes/No — statically; suite NOT re-run]  **Coverage**: [X]% (from Code Generation's Unit Test & Coverage gate — not re-measured)
**API & Contract Tests**: [Applicable — X/X endpoints checklist-complete | N/A — no API layer touched] (from the API & Contract Testing Gate — not re-run)
**Static Eval Gate (D1–D7)**: [PASS | N/A per check] (from the Static Eval Gate — not re-run; cites `eval-evidence/<key>/eval-summary.md`)
**Security Baseline (SECURITY-01…16, diff-scoped)**: [X]/16 checked · [N] compliant · [N] N/A · Findings: [N] 🔴 / [N] 🟠 (blocking, in the issue list) · [N] 🟡 / [N] 🔵 (advisory) · [N] pre-existing (not this change) → report: `.spec/aire-docs/code-security-reviews/security-review-YYYY-MM-DD.md`
**Eval Scores (informational — NOT gates, NOT findings)**: Architecture [0.NN | N/A — reason] (ref [0.NN]) · Security [0.NN] (ref [0.NN])
**Overall Assessment**: [2-3 sentences — strictly on AC/requirement completion. Do NOT let the scores influence the verdict.]

## AC & Requirements Verification
[One table per in-scope story. EVERY acceptance criterion and mapped requirement gets a row — this is the core of the report.]

### Story N.M: [Title]
| # | AC / Requirement | Verdict | Evidence / Gap |
|---|------------------|---------|----------------|
| AC-1 | [criterion text] | ✅ Met | `path/file.ext:45` |
| AC-2 | [criterion text] | ⚠️ Partially Met | [what's missing] → ISS-001 |
| AC-3 | [criterion text] | ❌ Not Met | [what's absent] → ISS-002 |

## Issues Found
[For all-stories reviews: group issues under one `## Story N.M` section per story, and prefix IDs per story — e.g. `S1.2-ISS-001` — so Remediate can map every issue to its story.]

### ISS-001: [Title] 🔴 Blocker
**AC/Requirement**: [the specific AC or requirement this fails]  **File**: `path/file.ext:45-52`
**Issue**: [how the AC/requirement is not met, or the defect that breaks it]
**Suggested Fix**: [code or description]

### SEC-ISS-001: [Title] 🔴 Blocker
**Security Rule**: SECURITY-XX — [rule name] · **Criteria violated**: [the specific verification item]
**File**: `path/file.ext:45-52` · **Reference**: [CWE-XX / OWASP AXX]
**Issue**: [the vulnerability and what an attacker could achieve]
**Suggested Fix**: [the concrete remediation from the security agent's output]

[If there are NO issues, write "No issues — all acceptance criteria and requirements verified as Met; diff is clean against SECURITY-01…16." Do not pad this section.]

## 🛡️ Security — Advisory (non-blocking)
[🟡 Medium / 🔵 Low security findings on the changed surface, and any **pre-existing** 🔴/🟠 on lines this work unit did not touch — each with its SECURITY-XX rule and file:line. **These are NOT findings**: they do not affect the verdict and are never sent to remediation. Recommend `/raise-defect` for the pre-existing ones. Write "None." if empty.]

## Issue Summary
| # | ID | Severity | AC/Requirement or SECURITY rule | File | Status |
|---|-----|----------|----------------|------|--------|
| 1 | ISS-001 | 🔴 Blocker | AC-2 (Story 1.2) | auth.ext:45 | Must Fix |
| 2 | SEC-ISS-001 | 🟠 High | SECURITY-05 (Input Validation) | api/user.ext:88 | Must Fix |

**Counts**: Blockers: [a] | High: [b] — of which security: [c] 🔴 / [d] 🟠 · Advisory (non-blocking): [e]

## Approval Status
**Decision**: [APPROVED / APPROVED WITH COMMENTS / CHANGES REQUESTED]
**Reason**: [...]
```

---

## Anti-Loop Protection
1. ✅ ALWAYS check for previous reviews first
2. ✅ SKIP if already approved and code unchanged
3. ✅ Only 🔴 + 🟠 exist in this review — every finding must map to a specific AC/requirement **or a SECURITY-XX baseline rule** (Phase 2.5). Those are the ONLY two admissible grounds for a finding
4. ❌ DON'T invent findings — a clean review (zero issues) is valid and expected when all ACs are Met and the diff is security-clean
5. ❌ DON'T surface style/refactor/nice-to-have items — they are out of scope, on first review AND re-reviews. Security 🟡 Medium / 🔵 Low go in the explicitly non-blocking advisory section, never the issue list
5b. ❌ **DON'T scope the security review to the whole repo, and DON'T report pre-existing security findings as this work unit's** — both flood the remediate loop with debt the change didn't introduce. Diff scope only; pre-existing findings are labelled and surfaced, never remediated here (Phase 2.5)
6. ❌ **DON'T edit code, tests, or any non-review file** — review + report only
7. ❌ **DON'T re-run the unit test suite or re-measure coverage** — the Unit Test & Coverage gate in Code Generation already ran it to ≥90%; reuse that recorded evidence (this review reads tests, it does not execute them)
8. ❌ **DON'T re-run the API & Contract tests** — when applicable, the API & Contract Testing Gate already ran them to a full pass; reuse the recorded `evidence-manifest.md` (this review reads that evidence, it does not execute the tests)
9. ❌ **DON'T re-run the D1–D7 static checks** — the Static Eval Gate already ran and diffed them; cite `eval-evidence/<key>/eval-summary.md`
10. ❌ **DON'T turn the J1/J2 judge scores into 🔴/🟠 findings** — they block through their own threshold (Phase 3.5), not through the issue list. A sub-minimum score is reported with its per-criterion citations and routed to SH-LOOP-6; it is NEVER added to the findings list and NEVER re-scored within a pass (`common/eval-framework.md` Section 4). Folding them into the issue list would restart exactly the style-churn loop rules 3 and 5 exist to prevent

---

## After Review — Mandatory Next-Step Output

After writing the report, present ONLY this block (do not improvise code edits):

```
📋 Code review complete — .spec/aire-docs/implementation/reviews/<report-filename>.md
   Target: [Story N.M | All Stories]
   ACs verified: [met]/[total] Met | [p] Partially Met | [n] Not Met
   Status: [✅ APPROVED | ⚠️ APPROVED WITH COMMENTS | ❌ CHANGES REQUESTED]
   Issues: [a] 🔴 | [b] 🟠

▶️ Next step:
1️⃣  Remediate         ← required if ❌ CHANGES REQUESTED
                                              recommended if ⚠️ APPROVED WITH COMMENTS
                                              N/A if ✅ APPROVED
2️⃣  Implement / review the next story        ← if ✅ APPROVED

Type your choice (1 / 2).
```
