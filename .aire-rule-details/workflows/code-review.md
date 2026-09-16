# 🔑 WORKFLOW: `code-review`

**Status**: Runs in two ways:
- **Automatically after Code Generation** — `workflows/dev-implement.md` (and the bug/enhancement implement workflows) auto-trigger this review for the just-implemented work (pre-scoped; skip the "what to review" prompt in that case) and audit its complete log. **Its verdict is what routes the run**: clean → straight to commit/push/PR; any 🔴/🟠 finding → the invoking workflow's **auto-remediate loop (SH-LOOP-5)** fixes it and calls this review again, repeating until the verdict is clean **or that loop's 3-round budget is exhausted**. The user is never asked to decide between them. 🔁 **This review is therefore invoked at most 4 times per work unit** — the initial pass plus one re-review per remediation round — each run producing the next report version `v[X+1]`. If the invoking workflow reports the budget exhausted, it HALTS; this review is not re-run again until the user directs it.
- **Standalone** — user-initiated at any time for a specific story or all stories together.

**Capability**: **Code Review** (`implementation/code-review.md`) — REVIEWER role, **read-only**. Reviews a **specific story** or **all stories together against the code**, and produces a versioned report at:
- Story: `.spec/aire-docs/implementation/reviews/story-[N.M]-code-review-v[X].md`
- All stories: `.spec/aire-docs/implementation/reviews/all-stories-code-review-v[X].md`

The two filenames are deliberately distinct so **Remediate** can intake either type.

MUST NOT edit source code.

> 🔁 **RETRY-BUDGET DISCIPLINE (applies whenever this review is auto-run inside a self-healing loop)**: the invoking workflow's **Self-Healing Retry Policy** caps its auto-remediate loop at **3 rounds**. Each review pass MUST be reproducible and deterministic in scope so the loop can converge: report the SAME finding under the SAME ID across versions, never re-open a finding that a prior round demonstrably closed, and never introduce a NEW finding class that was in scope but unreported in an earlier version of the report. Findings that appear only because the review changed its own scope between rounds burn the budget and are a defect in this review, not in the code.
>
> ⚖️ **STRICT SCOPE**: This review checks TWO things — **(1)** are the story's acceptance criteria and mapped requirements completed by the code, as written? and **(2)** does the changed code comply with the always-mandatory **Security Baseline (SECURITY-01…16)**? Findings are limited to: AC/requirement Not Met (🔴), AC/requirement Partially Met (🟠), a genuine defect that prevents an AC/requirement from working (🔴), or a **Critical (🔴) / High (🟠) security-baseline violation on the changed surface**. NO "good to have" suggestions, NO style/docs nits, NO 🟡/🟢 advisory items in the issue list. **Zero findings is a valid, expected outcome — never invent issues** (this review already runs automatically after every `dev-implement`; padded findings cause endless remediate loops).
>
> 🛡️ **SECURITY IS DIFF-SCOPED, NOT REPO-WIDE** (Phase 2.5): the security pass covers the files this work unit changed plus the attack surface they reach. Pre-existing violations on untouched lines, and 🟡/🔵 findings, are reported as **advisory** — never as findings, never remediated here. The full-codebase audit stays the standalone `code-security-review` skill's job.
>
> 🧾 **"Mapped requirements" is defined** (`common/requirements-traceability.md` Rule 6): it means EXACTLY the story's `**Covers**: [REQ-IDs]` list in `stories.md`. Read each covered REQ-ID's text in `.spec/aire-docs/planning/requirements/requirements.md` and verify the code against the requirement AS WRITTEN THERE, in addition to the story's ACs — an AC set that is a weaker statement than its requirement does NOT cap the review; the shortfall vs the requirement is a finding (Partially Met).

---

## MANDATORY: Rule Details Loading

This workflow may be invoked standalone. Resolve the rule details directory  (check `.aire-rule-details/`) and load:
- `common/process-overview.md`, `common/session-continuity.md`, `common/content-validation.md`
- The detailed reviewer steps from `implementation/code-review.md`
- `agents/code-security-review-agent.md` — the automated Security Baseline review run in Phase 2.5, **scoped to the diff**. Its 🔴 Critical / 🟠 High findings on the changed surface become real `SEC-ISS-XXX` findings that drive the verdict and get auto-fixed by the remediate loop; 🟡/🔵 and pre-existing findings are advisory only. (The agent also loads `extensions/security/baseline/security-baseline.md` itself.)
- `common/eval-framework.md` Section 4–Section 5 — the J1/J2 judge scores are computed inside this review and reported in the Review Summary. 🔴 **They are output only**: never a 🔴/🟠 finding, never part of the verdict, never fed to remediation, never re-scored within a run.

All paths below are relative to the resolved rule details directory.

---

## Recommended workflow execution

- Run **Code Review** as a **read-only workflow** (no code-editing tools) so it physically cannot modify source — enforcing separation of duties. It returns the report path and verdict.

## Per-story / all-stories flow when invoked
1. **Ask what to review** — DO NOT guess. Present:
   ```
   What would you like me to review?
   Options:
     a) A specific story                       (e.g., "story 1.2")
     b) All stories together against the code  (type "all stories")
   ```
   **Exception — auto-run from `dev-implement`**: when this review is triggered automatically after Code Generation, the target is already the just-implemented `story [N.M]`. SKIP this prompt and review that story directly.
   **⚡ NO TEST RE-RUN (auto-run from `dev-implement`)**: dev-implement's Unit Test & Coverage gate already ran the full unit test suite to ≥90% coverage in the same run, and — when the story touches an API layer — the API & Contract Testing Gate already ran its checklist to a full pass. Do NOT re-execute the tests or re-measure coverage here — reuse the evidence dev-implement passes in (tests X/X passing + coverage %; the API & Contract `evidence-manifest.md` when applicable; also recorded in audit.md) for the report's "Tests Reviewed / Coverage" and "API & Contract Tests" fields, and verify tests only statically (they exist and cover the ACs).
2. Load and execute all steps from `implementation/code-review.md` (Phase 0 history check → Phase 1 prep → Phase 2 checklist → Phase 3 findings → Phase 4 report/verdict).
3. **Produce the report** at the appropriate path per the review target.
4. **Do NOT change the Story Tracker status.** Code Review is read-only and does not introduce a status of its own — a story under review stays `🔵 In Development`. (The story only moves to `🧪 Ready for Testing` later, when its PR is **merged** — promoted by the `ve-list-work` skill once ve has tested it.) Record the verdict and findings, not a status change.
5. **If 🔴 Blocker or 🟠 High issues found**: when auto-run from a development workflow, return the verdict and let that workflow's **auto-remediate loop (SH-LOOP-5, capped at 3 rounds)** fix the findings immediately (no recommendation, no prompt). When run standalone, recommend **Remediate** as the next step.
6. The review report's verdict (clean / findings by severity) is the output the user acts on — it does not by itself advance the story's status.

## Execution
1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load `implementation/code-review.md` when the user invokes this workflow OR when `dev-implement` auto-triggers it after Code Generation
3. **Auto-run only as part of the `dev-implement` post-code-generation flow** (pre-scoped to the implemented story). Otherwise it is user-initiated — never auto-run it outside that flow.
4. **MANDATORY**: Log the complete review log (report path, verdict, findings by severity) and any tracker updates in audit.md with complete raw input. Every entry MUST carry the `**TRACKER ITEM**:` field (the reviewed story's tracker link, or local Story ID) AND the `**Epic Link**:` field (full Parent Epic URL from `## Tracker` in `.spec/aire-docs/aire-state.md`, or `none`) — per the Audit Entry Format in `workflows/dev-implement.md`

---

## 🔄 Tracker Sync Rule (reminder)

Code Review does **NOT** change the story status — the story stays `🔵 In Development` — so there is normally no tracker transition to perform here. If a review ever does drive a status change, the **Tracker Sync Rule** in `CLAUDE.md` (mechanics in `common/tracker-sync.md` Section 4) applies (confirm-first, verify, never update only one side).

---

> **Next (optional)**: If issues were found, run **Remediate**. If approved, implement/review the next story.
