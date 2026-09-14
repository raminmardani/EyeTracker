# Requirements Traceability (REQ-ID Thread)

## Purpose
Requirement fidelity is enforced by ONE unbroken thread of stable requirement IDs, carried from `requirements.md` through the stories, through the post-design verification, and into every story's code-generation plan and code review. Without this thread, decomposition loss (requirements silently dropped or diluted between stages) is invisible to every downstream gate — each gate would only verify the previous stage's *derived* artifact against itself.

## Enforcement Mode — automatic, silent, blocking
**Every check in this file is AUTOMATIC and BLOCKING**:
- It runs silently INSIDE an existing stage — it NEVER adds a new approval gate, user question, or workflow stage.
- A failed check is fixed by the AI in the same interaction (regenerate/extend the deficient artifact) and re-checked BEFORE the stage's existing completion message is presented.
- Each check's outcome (pass, or gap found + fix applied) is logged in `.spec/aire-docs/audit.md` per the standard audit format appended at the end.

---

## Rule 1 — REQ-IDs at the source (Requirements Analysis)
`.spec/aire-docs/planning/requirements/requirements.md` MUST assign a stable ID to EVERY requirement:
- Functional: `REQ-F-01`, `REQ-F-02`, …
- Non-functional: `REQ-NF-01`, `REQ-NF-02`, …

IDs are permanent: never renumbered, never reused after removal. Every later artifact refers to requirements ONLY by these IDs.

## Rule 2 — Stories MUST carry coverage (User Stories)
Referencing requirements from stories is **MANDATORY, never optional** ("if requirements exist, reference them" is superseded — Requirements Analysis always executes, so requirements always exist):
- EVERY story in `stories.md` carries a `**Covers**: REQ-F-xx, REQ-NF-yy` line naming the requirement(s) its acceptance criteria implement (an AC-level breakdown `AC-n → REQ-ID` is encouraged for multi-requirement stories).
- A story with an empty `Covers` line is invalid — either it implements a requirement (name it) or it is scaffolding another story needs (cover it under that requirement's ID).

## Rule 3 — Full-coverage check at story generation (before the story-set approval is presented)
After all stories are generated and BEFORE the story set is announced (and gated behind GATE 1 approval prior to being pushed to the configured tracker):
1. Build the coverage matrix: every `REQ-ID` in requirements.md → the story ID(s) whose `Covers` names it.
2. **Blocking gap A — uncovered requirement**: any REQ-ID with ZERO covering stories → add/extend stories automatically, then re-check.
3. **Blocking gap B — partial coverage**: for each REQ-ID, the UNION of its covering stories' acceptance criteria must express the requirement's full end-to-end behavior (including cross-story seams: if a requirement is split across stories for parallelism, the integration behavior between the slices must be owned by an explicit AC on one of them). Diluted/partial expression → strengthen the ACs automatically, then re-check.
4. Append the coverage matrix to `stories.md` (section `## Requirements Coverage Matrix`: REQ-ID | covering stories | status ✅ Full) and include a one-line coverage summary in the stage completion message (e.g., `🧾 Requirements coverage: 12/12 REQ-IDs fully covered by story ACs`).

## Rule 4 — Post-design coverage re-verification (after the LAST design stage, before the STOP CHECKPOINT handoff)
The system-level design stages (Functional/NFR/Infrastructure) may refine or contradict behavior the stories assumed — and stories were written BEFORE design. Therefore, after the last executed design stage is approved (or immediately when ALL design stages are skipped), automatically:
1. Re-verify the coverage matrix (Rule 3) against the approved design artifacts under `.spec/aire-docs/implementation/design/`.
2. Reconcile in place any story AC the design contradicted or refined (update `stories.md` + the matrix; log every reconciliation in audit.md with the design artifact that drove it).
3. Record in `aire-state.md`: `Requirements coverage verified post-design: [R]/[R] REQ-IDs — [timestamp]`.
4. Report the coverage line in the Development Handoff message.

**Fallback**: if `dev-implement` is invoked and `aire-state.md` carries NO post-design verification record, run this rule's check first (scoped verification, silent) before Story Selection planning proceeds — the thread must never reach code generation unverified.

## Rule 5 — Plan-level trace (Code Generation Part 1 / dev-implement)
The per-story code-generation plan MUST:
1. Load `requirements.md` and resolve the story's `Covers` REQ-IDs — the requirement text (not just the story's AC restatement) is planning input.
2. Tag EVERY plan step with the REQ-ID(s) and acceptance criteria it implements (`(REQ-F-03, AC-2)`).
3. **Self-check completeness before the plan is announced**: every REQ-ID in `Covers` and every AC of the story appears in ≥1 plan step. A REQ/AC with no plan step is a blocking gap — extend the plan, then re-check. Include the trace summary in the plan document.

## Rule 6 — Review against the thread (Code Review)
"Mapped requirements" in the Code Review scope means EXACTLY the story's `Covers` REQ-IDs. The review verifies the code against each covered REQ-ID as written in `requirements.md`, in addition to the story's own acceptance criteria — an AC set that is a weaker statement than its requirement does not cap the review.

## Rule 7 — Single-story flows (enhancement / bug)
- **Enhancement**: the single story's `Covers` names the REQ-IDs from the enhancement-scoped `requirements.md`; plan steps are tagged per Rule 5.
- **Bug**: the "requirement" is the expected behavior in `bug-brief.md` — plan steps trace to the brief's expected-behavior statements and the impact-analysis entries instead of REQ-IDs.
