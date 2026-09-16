# User Stories - Detailed Steps

## Purpose
**Convert requirements into user-centered stories with acceptance criteria**

User Stories focus on:
- Translating business requirements into user-centered narratives
- Defining clear acceptance criteria for each story
- Creating user personas that represent different stakeholder types
- Establishing shared understanding across teams
- Providing testable specifications for implementation
- Slicing each story small and single-purpose (Step 1.5 SPIDR rules) so a reviewer can check its implementation against it as one bounded, mechanical unit of work

## Prerequisites
- Workspace Detection must be complete
- Requirements Analysis recommended (can reference requirements if available)

> 🔴 **Three parts in this stage**: **Part 1 — Planning** (plan the story set — **the plan itself is NOT approved**), **Part 2 — Generation** (all stories generated at once + personas + populate the Story Tracker, gated by **GATE 1 — Story Set Approval**), **Part 3 — Push to Tracker** (runs **only after GATE 1 is approved**; then dispatches automatically, no further questions, on the configured tracker — JIRA / ADO / GITHUB / LOCAL). The fixed `team_size` AND the **Story Slicing Rules** (Step 1.5) drive story granularity; each story's `Requires` dependencies are assigned in the **Dependency Graph** stage that runs immediately after this one.
>
> 🤖 **The story PLAN (Part 1) has NO approval gate** — it is auto-approved and announced (Step 12). 🛑 **The GENERATED STORY SET (Part 2) DOES have a mandatory approval gate — GATE 1** (Steps 19–22): once all stories are generated and the coverage/granularity checks pass, the complete set is presented for explicit human approval and the workflow HALTS. Part 3 (Push to Tracker) does not start until GATE 1 is approved.

---

# PART 1: PLANNING

## Step 1: Begin Story Planning — `team_size` is FIXED at 2 (🤖 NEVER asked)

User Stories always execute for every software development request.

**🔴 Do NOT ask the user how many developers will work on implementation.** The team size is a
**fixed framework default of `2`** — it exists only to set story granularity, and asking for it
added a question whose answer barely changes the outcome.

- Record `team_size: 2` in `.spec/aire-docs/aire-state.md` without prompting. **The Dependency Graph
  stage reuses this value — it is neither asked nor re-derived there.**
- Tune story granularity to it: break the work into enough small, independent stories that **≥ 2**
  stories can run in parallel (unless the architecture genuinely makes parallelism impossible).
- Log in `.spec/aire-docs/audit.md` that `team_size` was defaulted to 2 (no question presented).
- If the user *volunteers* a different team size at any point, honour it, update `team_size` in
  state, re-tune granularity, and log it — that is an interrupt, not a gate.

Then proceed to Step 1.5.

## Step 1.5: Apply Story Slicing Rules (MANDATORY — small, single-purpose stories)

**Purpose**: The single biggest lever for cutting a human reviewer's effort is a small, single-purpose
story — one story, one bounded diff, one thing to confirm. A story that bundles multiple unrelated
behaviors forces the reviewer to hold several mental models at once and manually untangle which part
of a large diff maps to which part of the story. Slicing narrowly removes that untangling work
entirely: read the story, look at its diff, confirm the one thing it claims to do.

**Slicing method — apply SPIDR to every capability in the Epic/requirements BEFORE drafting stories.**
Split along these axes, in priority order, instead of writing one story per capability:
- **R — Rules**: a distinct business rule, validation, or decision branch (e.g., "discount applies
  when order > $100") is its OWN story, separate from the base behavior it modifies.
- **P — Paths**: the happy path and each meaningfully different path (alternate flow, error/failure
  handling, empty/boundary state) are SEPARATE stories, not extra ACs bolted onto one story — unless
  the alternate path is a one-line variation with no independent logic worth reviewing on its own.
- **I — Interfaces**: a different entry point (REST endpoint vs UI form vs CLI vs webhook, or a new
  vs an existing consumer) is its OWN story, even when the underlying logic is shared.
- **D — Data**: a new data variation, type, or format (e.g., supporting CSV in addition to JSON) is
  its OWN story rather than an AC tacked onto the story that introduced the first format.
- **S — Steps**: a multi-step workflow (e.g., checkout: cart → payment → confirmation) is split one
  story per step, never one story for the whole workflow.
- **CRUD**: when a capability has Create/Read/Update/Delete facets, each verb is its OWN story unless
  two verbs are trivially thin (e.g., delete is a one-line soft-flag flip identical to an existing
  pattern already in the codebase) — combine only in that case, and say so explicitly in the story.

**Hard sizing ceilings — a story MUST be split further if it exceeds ANY of these**:
- More than **5 acceptance criteria**.
- Touches more than **one architectural layer newly** (e.g., a new UI screen AND a new backend
  service AND a new schema, all in the same story) — unless the extra layers are pure pass-through
  with no independent logic to verify.
- Its title needs "and"/"or" to describe what it does (e.g., "Create and edit profile") — split on
  the conjunction.
- Verifying it would require the reviewer to check more than **one distinct scenario class** at once
  (happy path, one error case, one edge case, etc.) — one scenario class per story.

**Still apply INVEST (Step 4) on top of this** — slicing narrowly must not produce a story that is no
longer independently valuable or testable; if SPIDR-slicing would strand a story with no observable
value on its own, keep the thinnest useful end-to-end slice instead of a pure-plumbing story.

- [ ] Log in `.spec/aire-docs/audit.md` which SPIDR axis (or axes) was used to split each capability from
  the Epic/requirements into story boundaries, before the plan is created in Step 2.

## Step 2: Create Story Plan
- Assume the role of a product owner
- Generate a comprehensive plan with step-by-step execution checklist for story development
- Each step and sub-step should have a checkbox []
- Focus on methodology and approach for converting requirements into user stories

## Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the requirements and context to identify ALL areas where clarification would improve story quality and team understanding. Be proactive in asking questions to ensure comprehensive user story development.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect story quality. It's better to ask too many questions than to create incomplete or unclear stories.

**See `common/question-format-guide.md` for question formatting rules**

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve story creation decisions
- **When in doubt, ask the question** - overconfidence leads to poor stories

### 🔴 MANDATORY QUESTION — Number of Stories to Create (smart suggestion, always included)

**Every generated question set MUST include this question — it is NOT optional and NOT context-dependent.** While the other questions in this step are context-appropriate (asked only when relevant), the number-of-stories question is ALWAYS asked, with a concrete AI-computed recommendation and the reasons behind it.

Before writing it into the plan, **do the analysis** so the suggestion is grounded, not arbitrary:
- Read the Parent Epic brief (`.spec/aire-docs/planning/requirements/epic-brief.md`) and `.spec/aire-docs/planning/requirements/requirements.md` (if present).
- Read `## Context References` in `aire-state.md`. **IF `Use References: Yes`**, load all listed reference paths — UX wireframes inform story scope (one screen/flow per story), API specs inform endpoint boundaries, etc. Use them as inputs when counting capabilities and deciding story boundaries.
- Count the distinct capabilities / functional requirements (REQ-IDs), user journeys, and personas involved, and gauge their complexity.
- **Apply the Step 1.5 Story Slicing Rules (SPIDR) to that count** — for each capability, count how many separate Rules / Paths / Interfaces / Data-variations / Steps / CRUD-verbs it contains; each becomes its own candidate story rather than a sub-bullet of one larger story.
- Compute a **recommended story count** that (a) keeps each story small, single-purpose, and INVEST-compliant against the Step 1.5 hard sizing ceilings, and (b) yields **≥ `team_size` (= 2) independently workable stories** so no developer is left idle.

Embed EXACTLY this question in the plan (fill in the computed values — never leave it open-ended without a recommendation):

```
❓ How many user stories should I create for this work?

   💡 Recommended: [X] stories  (suggested range: [X-lo]–[X-hi])

   Why [X]:
   - [reason 1 — e.g. "8 functional requirements SPIDR-sliced into single-purpose stories (rules, paths and CRUD verbs split out)"]
   - [reason 2 — e.g. "keeps ≥ [team_size] stories runnable in parallel so no developer is idle"]
   - [reason 3 — e.g. "each story stays within the Step 1.5 sizing ceilings (≤5 ACs, one layer, one scenario class) so review is small and mechanical"]

   Reply with a number to override, or "ok"/"use recommended" to accept [X].
[Answer]:
```

- **ALWAYS compute and show a concrete recommended number `[X]` and the reasons** — never present this as an open-ended question with no suggestion.
- When the user accepts, use `[X]`. If the user gives a different number, use theirs — but if it would break the parallelism rule (fewer than `team_size` independent stories) or force oversized/undersized stories, flag the trade-off during Step 9/10 analysis and confirm before generation.
- Record the agreed value as `target_story_count` in `.spec/aire-docs/aire-state.md`. The Generation phase (Part 2) MUST create this many stories (adjusting only if Step 9/10 analysis or the Step 18.5 coverage check proves a different count is required — log any deviation and its reason in audit.md).

**Question categories to evaluate** (consider ALL categories):
- **User Personas** - Ask about user types, roles, characteristics, and motivations
- **Story Granularity** - Ask about appropriate level of detail, story size, and breakdown approach
- **Story Format** - Ask about format preferences, template usage, and documentation standards
- **Breakdown Approach** - Ask about organization method, prioritization, and grouping strategies
- **Acceptance Criteria** - Ask about detail level, format, testing approach, and validation methods
- **User Journeys** - Ask about user workflows, interaction patterns, and experience flows
- **Business Context** - Ask about business goals, success metrics, and stakeholder needs
- **Technical Constraints** - Ask about technical limitations, integration requirements, and system boundaries

## Step 4: Include Mandatory Story Artifacts in Plan
- **ALWAYS** include these mandatory artifacts in the story plan:
  - [ ] Generate stories.md with user stories following INVEST criteria
  - [ ] stories.md MUST begin with the Parent Epic header line (see Step 16 — Epic header rule)
  - [ ] Generate personas.md with user archetypes and characteristics
  - [ ] Ensure stories are Independent, Negotiable, Valuable, Estimable, Small, Testable — "Small" means passing the Step 1.5 hard sizing ceilings (≤5 ACs, one new architectural layer, no title conjunction, one scenario class)
  - [ ] Include acceptance criteria for each story
  - [ ] **EVERY story carries a `**Covers**: [REQ-IDs]` line** naming the requirements from `requirements.md` its acceptance criteria implement (MANDATORY — see `common/requirements-traceability.md` Rule 2; "reference requirements if available" is superseded, coverage is never optional)
  - [ ] **Requirements Coverage Matrix + full-coverage check** — every REQ-ID fully expressed by the union of its covering stories' ACs (see Step 18 / `common/requirements-traceability.md` Rule 3)
  - [ ] Map personas to relevant user stories

## Step 5: Present Story Options
- Include different approaches for story breakdown in the plan document:
  - **User Journey-Based**: Stories follow user workflows and interactions
  - **Feature-Based**: Stories organized around system features and capabilities
  - **Persona-Based**: Stories grouped by different user types and their needs
  - **Domain-Based**: Stories organized around business domains or contexts
  - **Epic-Based**: Stories structured as hierarchical epics with sub-stories
- Explain trade-offs and benefits of each approach
- Allow for hybrid approaches with clear decision criteria

## Step 6: Store Story Plan
- Save the complete story plan with embedded questions in `.spec/aire-docs/planning/plans/` directory
- Filename: `story-generation-plan.md`
- Include all [Answer]: tags for user input
- Ensure plan is comprehensive and covers all story development aspects

## Step 7: Request User Input
- Ask user to fill in all [Answer]: tags directly in the story plan document
- Emphasize importance of audit trail and decision documentation
- Provide clear instructions on how to fill in the [Answer]: tags
- Explain that all questions must be answered before proceeding

## Step 8: Collect Answers
- Wait for user to provide answers to all questions using [Answer]: tags in the document
- Do not proceed until ALL [Answer]: tags are completed
- Review the document to ensure no [Answer]: tags are left blank

## Step 9: ANALYZE ANSWERS (MANDATORY)
Before proceeding, you MUST carefully review all user answers for:
- **Vague or ambiguous responses**: "mix of", "somewhere between", "not sure", "depends", "maybe", "probably"
- **Undefined criteria or terms**: References to concepts without clear definitions
- **Contradictory answers**: Responses that conflict with each other
- **Missing generation details**: Answers that lack specific guidance for implementation
- **Answers that combine options**: Responses that merge different approaches without clear decision rules
- **Incomplete explanations**: Answers that reference external factors without defining them
- **Assumption-based responses**: Answers that assume knowledge not explicitly stated

## Step 10: MANDATORY Follow-up Questions
If the analysis in step 9 reveals ANY ambiguous answers, you MUST:
- Create a separate clarification questions file using [Answer]: tags
- DO NOT proceed to approval until ALL ambiguities are completely resolved
- **CRITICAL**: Be thorough - ask follow-up questions for every unclear response
- Examples of required follow-ups:
  - "You mentioned 'mix of A and B' - what specific criteria should determine when to use A vs B?"
  - "You said 'somewhere between A and B' - can you define the exact middle ground approach?"
  - "You indicated 'not sure' - what additional information would help you decide?"
  - "You mentioned 'depends on complexity' - how do you define complexity levels and thresholds?"
  - "You chose 'hybrid approach' - what are the specific rules for when to use each method?"
  - "You said 'probably X' - what factors would make it definitely X vs definitely not X?"
  - "You referenced 'standard practice' - can you define what that standard practice is?"

## Step 11: Avoid Implementation Details
- Focus on story creation methodology, not prioritization or development tasks
- Do not discuss technical generation at this stage
- Avoid creating development timelines or sprint planning
- Keep focus on story structure and format decisions

## Step 12: Announce the Plan (🤖 AUTOMATIC — no approval gate)

**The story PLAN itself is NOT gated.** The user's answers to the Step 3 questions (including the
story count) already shaped it. The story SET the plan produces is different — it carries a
**mandatory approval gate, GATE 1** (Steps 19–22), presented after generation and before Part 3 (Push
to Tracker).

- Log in `.spec/aire-docs/audit.md` (ISO 8601 timestamp) that the story plan was finalized and
  auto-approved, including the plan path and a one-line summary of the approach chosen.
- Present a short announcement (NOT a question):
  ```
  📝 Story plan ready — .spec/aire-docs/planning/plans/story-generation-plan.md
     Approach: [breakdown approach] | Target stories: [X] | team_size: [N]
     Generating all stories now — the complete set will be presented for your approval (GATE 1) before anything is pushed to the configured tracker.
  ```
- **Do NOT ask for plan approval and do NOT wait here.** Proceed directly to Part 2 (Generation) — the actual approval gate comes later, at Step 21.

## Step 13: (removed — plan approval no longer gated)

Superseded by Step 12. If the user *volunteers* changes to the approach after seeing the Step 12
announcement, apply them and continue — that is an interrupt, not a gate.

## Step 14: (removed — no plan approval response to record)

Only the Step 12 auto-approval note is logged here. This stage records no approval response at all.

---

# PART 2: GENERATION

## Step 14.5: Story Creation Mode — FIXED to all-at-once (🤖 NEVER asked)

**🔴 Do NOT ask how the stories should be created.** The mode is a **fixed framework default:
`all-at-once`** — every story is generated together in a single pass, with no per-story approval
loop and no final story-set approval.

- [ ] Record `story_creation_mode: all-at-once` in `.spec/aire-docs/aire-state.md` without prompting.
- [ ] Log in `.spec/aire-docs/audit.md` that the mode was defaulted to `all-at-once` (no question presented).
- [ ] The one-by-one mode no longer exists — never present an A/B choice here, and never pause
      between stories for approval.

## Step 15: Load Story Generation Plan
- [ ] Read the complete story plan from `.spec/aire-docs/planning/plans/story-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context and requirements for that step

## Step 16: Execute Current Step
- [ ] Perform exactly what the current step describes
- [ ] Generate story artifacts as specified in the plan
- [ ] Follow the approved methodology and format from Planning
- [ ] Use the story breakdown approach specified in the plan
- [ ] **Generate ALL stories together in one pass** (`story_creation_mode: all-at-once`, Step 14.5) — never one at a time, never pausing for a per-story approval:

**🔗 Epic header rule (BOTH creation modes — applies when stories.md is first created)**:
- [ ] The VERY FIRST line of `.spec/aire-docs/planning/user-stories/stories.md` MUST be the Parent Epic header:
  ```markdown
  EPIC TICKET: [full Epic URL/reference, e.g. https://<site>.atlassian.net/browse/PROJ-50, or a local description for LOCAL]
  ```
  Read the Epic URL from `## Tracker` in `.spec/aire-docs/aire-state.md` (Epic URL line). If no Parent Epic is recorded at creation time, write `EPIC TICKET: none (no Parent Epic recorded)` — and when an Epic is later resolved during the tracker push (Step 25), UPDATE this header line with the full Epic URL/reference in the same interaction. All stories are appended BELOW this header.

**🧾 Requirements traceability rule (BOTH creation modes — applies to every story generated)**:
- [ ] EVERY story written to `stories.md` carries a `**Covers**: REQ-F-xx, REQ-NF-yy` line naming the requirement IDs from `.spec/aire-docs/planning/requirements/requirements.md` its acceptance criteria implement (`common/requirements-traceability.md` Rule 2). A story with an empty `Covers` is invalid — fix it before presenting the story. For multi-requirement stories, an AC-level breakdown (`AC-n → REQ-ID`) is encouraged. When a requirement is split across stories for parallelism, the integration behavior between the slices MUST be owned by an explicit AC on one of them.

- [ ] Generate ALL stories together in one pass, write them to `stories.md` beneath the Epic header, then continue to Step 17. **No approval is requested at any point** — the complete set is announced at Step 20 and pushed to the configured tracker automatically (Part 3).

## Step 17: Update Progress
- [ ] Mark the completed step as [x] in the story generation plan
- [ ] Update `.spec/aire-docs/aire-state.md` current status
- [ ] **Populate the Story Tracker**: add one row per generated story to the `## Story Tracker` table in `.spec/aire-docs/aire-state.md`. Columns: Story ID, Title, **Requires = `TBD`** (assigned next stage), `Tracker ID` = `—`, `Status` = `🟢 Ready for Development` (the initial status for every new story), Start/End blank, `Recorded` = current timestamp. Use the table format defined in `planning/dependency-graph-generation.md` (Story Tracker Table Format section).
- [ ] Save all generated artifacts

## Step 18: Continue or Complete Generation
- [ ] If more steps remain, return to Step 15
- [ ] If all steps complete, verify stories are ready for next stage
- [ ] Ensure all mandatory artifacts are generated

## Step 18.5: Requirements Full-Coverage Check (MANDATORY — automatic, BEFORE the Step 20 announcement)
Execute `common/requirements-traceability.md` Rule 3 — silent and blocking, NO user prompt:
- [ ] Build the coverage matrix: every REQ-ID in `requirements.md` → the story ID(s) whose `Covers` names it
- [ ] **Gap A — uncovered requirement** (a REQ-ID with zero covering stories): add/extend stories automatically, then re-check
- [ ] **Gap B — partial coverage** (the union of the covering stories' ACs does not express the requirement's full end-to-end behavior, including cross-story seams): strengthen the ACs automatically, then re-check
- [ ] Append the matrix to `stories.md` as `## Requirements Coverage Matrix` (REQ-ID | covering stories | status)
- [ ] Log the check outcome (pass, or gaps found + fixes applied) in `.spec/aire-docs/audit.md`
- [ ] Include a coverage summary line in the Step 20 announcement (e.g., `🧾 Requirements coverage: 12/12 REQ-IDs fully covered by story ACs`)
- [ ] Do NOT present the Step 20 announcement until the matrix shows every REQ-ID fully covered

## Step 18.6: Story Granularity & Splitting Check (MANDATORY — automatic, BEFORE the Step 20 announcement)
Runs immediately after Step 18.5 passes — silent and blocking, NO user prompt. Purpose: guarantee
every story that reaches the developer/reviewer actually obeys the Step 1.5 slicing rules, not just
that the plan intended it to.
- [ ] Scan every story in `stories.md` against the Step 1.5 **hard sizing ceilings**: AC count > 5,
  more than one newly-touched architectural layer, a title conjunction ("and"/"or"), or more than one
  distinct scenario class bundled into its ACs.
- [ ] **Violation found**: split the story along whichever SPIDR axis (Rules / Paths / Interfaces /
  Data / Steps / CRUD) produced the violation, generate a new story ID for the split-off piece, and
  carry its `Covers` REQ-ID(s) and persona mapping forward — a split only ever narrows a story, it
  never drops requirements coverage.
- [ ] Re-run the Step 18.5 coverage check on the resulting set, then re-check the ceilings; repeat
  until every story in `stories.md` passes both checks.
- [ ] Log the outcome (pass, or violations found + splits applied, listing story IDs before → after)
  in `.spec/aire-docs/audit.md`.
- [ ] Include a granularity summary line in the Step 20 announcement (e.g., `✂️ Story granularity:
  14 stories, 0 ceiling violations after 3 auto-splits`).
- [ ] Do NOT present the Step 20 announcement until every story passes the ceilings.

## Step 19: Log the Generated Story Set (🛑 approval prompt follows)
- **This stage has a MANDATORY approval gate — GATE 1.** The story set is generated and announced, then the workflow HALTS for explicit human approval before anything is pushed to the configured tracker.
- Log in `.spec/aire-docs/audit.md` (ISO 8601 timestamp) that the complete story set was generated and is awaiting approval: the story count, the breakdown approach, the coverage-check outcome, and the path to `stories.md`.
- Use the audit heading `## User Stories — GATE 1: Story Set Approval (awaiting response)`.

## Step 20: Present the Completion Announcement
- Present the announcement in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 📚 User Stories Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of generated stories
        - Format: "User stories generation has created [description]:"
        - List key personas generated (bullet points)
        - List user stories created with counts and organization
        - Mention story structure and compliance (INVEST criteria, acceptance criteria)
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> The user stories and personas are at: `.spec/aire-docs/planning/user-stories/stories.md` and `.spec/aire-docs/planning/user-stories/personas.md`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the story set (a story, an AC, a split, coverage) before it is pushed
> ✅ **Approve & Continue** - Approve the story set; it will be **pushed now** (project [PROJECT_KEY], issue type Story[, linked to Parent Epic [EPIC-KEY]]), then the **Dependency Graph** is generated

---
```

## Step 21: 🛑 GATE 1 — Wait for Explicit Approval (MANDATORY)
- **DO NOT proceed to Part 3 (Push to Tracker) until the user explicitly responds.** This is a hard halt — do not push any issue, do not derive the project/repo identifier for pushing, do not proceed to the Dependency Graph.
- **On "Request Changes"**: apply the requested change(s) to `stories.md` and the Story Tracker (re-running the Step 18.5/18.6 coverage and granularity checks if the change affects them), then re-present the Step 20 announcement and return to this gate. Repeat until the user approves.
- **On "Approve & Continue"**: proceed to Step 22, then Part 3 (Push to Tracker).
- A change volunteered by the user AFTER approval (i.e., after the push has started or completed) is still honored as an interrupt — apply it to `stories.md`, the Story Tracker and the corresponding tracker issues per the Tracker Sync Rule — but it does not reopen GATE 1 for stories already pushed.

## Step 22: Record the Approval Response (MANDATORY)
- Log the user's complete raw response (Approve & Continue / Request Changes + full text) with an ISO 8601 timestamp in `.spec/aire-docs/audit.md`, under a heading such as `## User Stories — GATE 1: Story Set Approval (response received)`.
- If changes were requested, log what was changed and that the gate is being re-presented.
- Only once "Approve & Continue" is recorded does this stage's approval gate count as passed.

## Step 23: Update Progress
- Mark User Stories stage complete in `aire-state.md` (only after GATE 1 is approved)
- Update the "Current Status" section
- Prepare for transition to **Part 3 (Push to Tracker)**, then the **Dependency Graph** stage

---

# PART 3: PUSH TO TRACKER (runs only after GATE 1 approval — then automatic, no further confirmation)
Once the story set is generated, the coverage/granularity checks pass, AND **GATE 1 (Step 21) has been
explicitly approved**, the stories are pushed to the configured tracker **automatically** — no
further "push? yes/no" question, no project-key confirmation, and no issue-type question (those were
already covered by the GATE 1 approval).
Every step below dispatches on `## Tracker` → `Type` in
`.spec/aire-docs/aire-state.md` — read `common/tracker-sync.md` Section 3 (issue creation), Section 4 (status
transition), and Section 6 (Parent Epic linking) before executing this Part; those sections are the single
source of truth for the actual per-tracker commands, not re-derived here.

> **Note**: This pushes **stories** and links each one to the **Parent Epic** — the existing Epic the user provided at workflow start (stored in `.spec/aire-docs/aire-state.md` under `## Tracker`). **When `Type: LOCAL`, this whole Part is a no-op announcement** — stories stay in `stories.md` + the Story Tracker only, `Tracker ID` is set to `LOCAL`, and Steps 24–28 below are skipped in favor of a single announcement (see the LOCAL block at the end of Step 24).

## Step 24: Push After Approval (no further question)
- [ ] Log in `.spec/aire-docs/audit.md` with timestamp that the tracker push is starting because GATE 1 was approved (reference the Step 22 approval entry).
- [ ] Announce (NOT a question) — for JIRA/ADO/GITHUB:
  ```
  📚 [N] user stories approved — pushing to [TRACKER TYPE] now.
     Project/Repo: [PROJECT_KEY / org-repo / org-project] | Issue type: Story
     [Include this line ONLY if aire-state.md `## Tracker` records a Parent Epic:
      "Each story will be linked to Parent Epic [EPIC-ID]."]
  ```
  **For LOCAL**, announce instead and STOP this Part here (skip Steps 25–28 entirely):
  ```
  📚 [N] user stories approved. Tracker is set to Local — stories stay in stories.md and the
     Story Tracker only (Tracker ID: LOCAL for each). Proceeding to the Dependency Graph.
  ```
- [ ] For JIRA/ADO/GITHUB, proceed straight to Step 25. **Never ask "push these stories? (yes/no)".**

## Step 25: Resolve the Parent Epic & Tracker Target (automatic — derive, verify, do NOT confirm)
- [ ] **Read the Parent Epic** from `.spec/aire-docs/aire-state.md` `## Tracker` (Type + Epic ID + URL + Project Key / Repo / Org). This works even in a brand-new chat — the Epic was stored at workflow start.
- [ ] **Project/Repo identifier — derive, never ask**: take it from the Epic key/reference (e.g., JIRA `PROJ-50` → `PROJ`), or reuse the value already recorded in `## Tracker`. **Do NOT ask the user to confirm it.** Announce the derived value in the Step 24 message.
- [ ] **Issue type — fixed default `Story`** (or the tracker's nearest native equivalent — ADO's `User Story`, GitHub's plain issue). Do NOT ask. Only if the project genuinely has no matching type (verified via the tracker's own metadata query — `getJiraProjectIssueTypesMetadata` for JIRA) fall back to the nearest equivalent, announce the substitution, and log it.
- [ ] **Verify the Epic exists** using the fetch mechanism for the configured type (`common/tracker-sync.md` Section 2). If it cannot be fetched, STOP and report — do not push stories against an unverified Epic.
- [ ] **Only if NO Parent Epic and NO project/repo identifier can be resolved from state** (no Epic was ever provided) is a single question unavoidable — ask it once and store the answer:
  ```
  ❓ No Parent Epic or project/repo is recorded. Where should these stories be created?
     Paste an Epic link/key/ID to link them to, or just the project key / org-repo to push unlinked.
  ```
  Store the answer in `## Tracker` (Parent Epic / Epic URL / Project Key / Repo / Org) before pushing. If the answer has no Epic, record `Parent Epic: none` and skip Step 26b entirely.

## Step 26: Create Issues (dispatch per Tracker Type)
- [ ] For each story, create an issue using the mechanism for the configured type, per `common/tracker-sync.md` Section 3:
  - **JIRA**: `createJiraIssue` (Atlassian MCP) — issueType Story, summary = story title, description = story narrative + acceptance criteria + persona (Markdown with REAL line breaks, never literal `\n` escapes; Rovo converts Markdown → ADF), ending with a footer line `---` then `Built with AIRE v[N]` ([N] read live from CLAUDE.md). Labels: `[aire, aire-v[N]]`. **Mandatory fixed fields** — always set, never asked, never varied per story: Component = `default`, Organization = `All Orgs`, Severity = `Low`. These may be custom fields — if `createJiraIssue` rejects them by name, call `getJiraIssueTypeMetaWithFields` to resolve their field IDs and retry. Never skip them.
  - **ADO**: `az boards work-item create --type "User Story"` with the AC as an HTML checklist field and `System.Tags` including `ai-generated;aire;aire-v[N]`, per `common/tracker-sync.md` Section 3.
  - **GITHUB**: `gh issue create` with labels `story`, `ai-generated`, `aire-v[N]`, `status:ready-for-dev`, and `--milestone` set to the Parent Epic's milestone title, per `common/tracker-sync.md` Section 3.
  - **LOCAL**: not reached — Part 3 already stopped at Step 24.
- [ ] **VERIFY** each creation succeeded; capture the returned issue key/number/ID.
- [ ] If a creation fails, STOP, report the error, and do not silently continue.

## Step 26a: Transition Each Story to "Ready for Development" (MANDATORY)
- [ ] New issues start in the tracker's default initial state (e.g., Backlog / To Do / New) — stories MUST NOT be left there. Immediately after each story is created, transition it to "Ready for Development" (or the type's nearest equivalent state/label) using `common/tracker-sync.md` Section 4:
  - **JIRA**: `getTransitionsForJiraIssue` → `transitionJiraIssue` to "Ready for Development" (accept close variants like "Ready for Dev").
  - **ADO**: `az boards work-item update --state "New"` (or the project's verified equivalent).
  - **GITHUB**: ensure the `status:ready-for-dev` label is present (already applied at creation in Step 26; verify it landed).
- [ ] **VERIFY** by re-fetching the issue and confirming the state/label. If the target state genuinely doesn't exist in the project's workflow, STOP and report to the user — do not leave stories silently in the default state.
- [ ] Log each transition (issue key, from → to status) in `.spec/aire-docs/audit.md` with timestamp.

## Step 26b: Link Each Story to the Parent Epic (AUTOMATIC — skip only when `Parent Epic: none`)
- [ ] For each created story, link it to the Parent Epic — **automatic, no confirmation** (linking to the recorded Parent Epic is part of the same authorized push), per `common/tracker-sync.md` Section 6:
  - **JIRA**: `editJiraIssue` set Epic Link / parent = `[EPIC-KEY]` (or `createIssueLink` if the project uses issue links). (If the project supports it, setting `parent` directly in `createJiraIssue` at Step 26 is equally valid — then this step is verification only.)
  - **ADO**: `az boards work-item relation add --relation-type "System.LinkTypes.Hierarchy-Reverse" --target-id [EPIC-ID]`.
  - **GITHUB**: the Milestone set at creation (Step 26) IS the link — this step is verification only.
- [ ] **VERIFY each link landed**: fetch each story back and confirm its parent/Epic Link/Milestone is the Parent Epic. If a link fails, STOP and report — never leave stories silently unlinked.
- [ ] Report the Epic → linked story keys mapping to the user.

## Step 27: Write Keys Back
- [ ] In `.spec/aire-docs/planning/user-stories/stories.md`, annotate each story with its Tracker ID and link (`**Tracker ID**: PROJ-123` + URL, or the ADO/GitHub equivalent).
- [ ] Verify the `EPIC TICKET:` header at the TOP of stories.md carries the resolved Parent Epic's full URL/reference — update it now if it still reads `none` (or leave `none` only if the user explicitly chose "none" at push time).
- [ ] In the `## Story Tracker` of `.spec/aire-docs/aire-state.md`, set each story's `Tracker ID` column to its key/number/ID and update `Recorded` to the current timestamp.
- [ ] Confirm to the user: list each Story ID → Tracker ID.

## Step 28: Log the Push
- [ ] Append to `.spec/aire-docs/audit.md`: that the push ran automatically after story generation, the PROJECT_KEY (and how it was derived), the Parent Epic key, the created issue keys, the transitions applied, and the story→Epic links, with timestamps.
- [ ] **No confirmation is required in this turn** — the push is part of the automatic story stage. Everything created is still **verified** after the fact (Steps 26/26a/26b) and any failure STOPS the run and is reported. For LOCAL, log that the push was skipped by design (Type: LOCAL) instead.

---

# CRITICAL RULES

## Planning Phase Rules
- **CONTEXT-APPROPRIATE QUESTIONS**: Only ask questions relevant to this specific context
- **MANDATORY ANSWER ANALYSIS**: Always analyze answers for ambiguities before proceeding
- **NO PROCEEDING WITH AMBIGUITY**: Must resolve all vague answers before generation
- **PLAN HAS NO GATE, STORY SET DOES**: the story plan is auto-approved and announced (Step 12) — nothing waits for a user approval there. The generated story set is DIFFERENT: it carries a **mandatory approval gate, GATE 1** (Steps 19–22) — the workflow HALTS after the Step 20 announcement until the user responds "Approve & Continue" or "Request Changes"
- **NO TEAM-SIZE QUESTION**: `team_size` is the fixed default `2` (Step 1) — never ask it
- **NO CREATION-MODE QUESTION**: `story_creation_mode` is the fixed default `all-at-once` (Step 14.5) — never ask it, never generate stories one at a time
- **SLICE BEFORE DRAFTING**: apply the Step 1.5 SPIDR slicing rules to every capability before the plan is written — granularity is designed in up front, not patched on after generation

## Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the story generation plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **USE APPROVED METHODOLOGY**: Follow the story approach from Planning
- **VERIFY COMPLETION**: Ensure all story artifacts are complete before proceeding
- **ENFORCE SIZING CEILINGS**: no story may exceed the Step 1.5 hard sizing ceilings — the Step 18.6 granularity check MUST split any violator before the story set is announced

## Completion Criteria
- All planning questions answered and ambiguities resolved
- `team_size: 2` and `story_creation_mode: all-at-once` recorded in state without either being asked
- Story plan finalized, auto-approved and announced (Step 12) — no user approval required for the plan
- Every story carries a non-empty `**Covers**:` line; the Requirements Coverage Matrix in stories.md shows EVERY REQ-ID from requirements.md fully covered (Step 18.5 passed)
- All stories generated together in a single pass; the complete set announced (Steps 19–20) and **explicitly approved by the user at GATE 1** (Steps 21–22), with the approval response logged in audit.md
- All steps in story generation plan marked [x]
- All story artifacts generated according to plan (stories.md, personas.md)
- Every story passes the Step 1.5 hard sizing ceilings (Step 18.6 granularity check passed — 0 outstanding violations)
- Stories pushed to the configured tracker only after GATE 1 approval (issues created, transitioned to Ready for Development, linked to the Parent Epic, keys written back) — verified, with no separate push/project-key/issue-type questions asked (GATE 1 already covered that decision); for LOCAL, stories stay local by design (no push)
- Stories verified and ready for next stage
