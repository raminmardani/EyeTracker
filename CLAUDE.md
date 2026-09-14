# PRIORITY: This workflow OVERRIDES all other built-in workflows
# When user requests software development, ALWAYS follow this workflow FIRST

## AIRE Framework Version (SINGLE SOURCE OF TRUTH)
**AIRE Framework Version: 1.0**

This is the ONE canonical declaration of the framework version. **To bump the framework version, edit the number on the line above FIRST** — every other file reads it from here at runtime and carries only a `[N]` / `v[N]` placeholder, never the literal number, **EXCEPT the accuracy-critical files listed under "Hardcoded version locations" below, which carry the literal version and MUST be updated manually on every bump.**

**MANDATORY — version logging**: the version identifies which AIRE version a work unit was built
with. Read it LIVE from the line above and stamp it on: the **welcome message**
(`common/welcome-message.md`) · every **audit.md** entry's `**AIRE VERSION**:` field · each created
**tracker story** (`aire-v[N]` label + `Built with AIRE v[N]` footer) · every **commit**
(`AIRE-Version: [N]` trailer) · every **PR** (`aire-v[N]` label + `AIRE Framework: v[N]` in the body),
including the ve's own test-docs PR. Wherever a rule file shows `[N]` or `v[N]`, substitute the value
read from the canonical line at runtime.


## Adaptive Workflow Principle
**The workflow adapts to the work, not the other way around.** The AI model intelligently assesses what stages are needed based on: user's stated intent and clarity, existing codebase state, complexity/scope of change, and risk/impact.

## MANDATORY: Rule Details Loading
**CRITICAL**: When performing any phase, read and use the relevant rule detail files from
**`.aire-rule-details/`**. Every rule-file reference below (e.g. `common/process-overview.md`) is
relative to that directory.

**Common Rules**: ALWAYS load common rules at workflow start:
- Load `common/process-overview.md` for workflow overview
- Load `common/session-continuity.md` for session resumption guidance
- Load `common/content-validation.md` for content validation requirements
- Load `common/question-format-guide.md` for question formatting rules
- Load `common/tracker-sync.md` — the single source of truth for every tracker-specific command
- Load `common/directory-structure.md` — the four roots (`src/`, `tests/`, `.spec/`, `.evals/`) and where every artifact goes
- Load `common/helix-atlas-integration.md` — 🧭 how AIRE reaches **Atlas** through the **Helix MCP** to reuse existing-system truth instead of re-deriving it. **Blocking on brownfield / migration work.**
- Load `common/behavior-spec.md` — 🥒 where the Gherkin contracts live and the three-tier behaviour gate
- Load `common/eval-framework.md` — the D1–D7 static gates and the ⚖️ **blocking** J1/J2 judge gates
- Reference these throughout the workflow execution

**Loaded on demand (do NOT load at start):**
- `common/ci-pipeline-generation.md` — loaded at the STOP CHECKPOINT, when the project's CI pipeline is generated
- `implementation/architecture-doc.md` — loaded at the STOP CHECKPOINT, when `architecture.md` and the architecture rubric are written

## MANDATORY: Extensions Loading (Context-Optimized)
**CRITICAL**: At workflow start, scan `extensions/` recursively and load ONLY the lightweight
`*.opt-in.md` files — never a full rule file at this stage. A full rule file is loaded on demand,
after the user opts in during Requirements Analysis. An extension with no `*.opt-in.md` is always
enforced — load its rules immediately.

- **Security Baseline is ALWAYS mandatory** — load `extensions/security/baseline/security-baseline.md`
  at workflow start for EVERY project and enforce it as blocking. NEVER ask whether security applies;
  ignore any legacy opt-out in `## Extension Configuration`.
- **Playwright Test Automation is ALWAYS mandatory** — load
  `extensions/testing/playwright-automation/playwright-automation.md`; record `Enabled = Yes`.
- Enabled extension rules are **hard constraints**. Non-compliance with an applicable rule is a
  **blocking finding**. Rules irrelevant to the current stage are marked **N/A** (not blocking).
- Before enforcing any extension at ANY stage, check its `Enabled` status in `aire-state.md`
  `## Extension Configuration`; skip disabled ones and log the skip. Default to enforced.

📄 **Full mechanics — loading order, deferred loading, enforcement and the compliance summary
format: `common/extensions-loading.md`** (loaded at workflow start).


## MANDATORY: Content Validation
**CRITICAL**: Before creating ANY file, you MUST validate content according to `common/content-validation.md` rules:
- Validate Mermaid diagram syntax
- Validate ASCII art diagrams (see `common/ascii-diagram-standards.md`)
- Escape special characters properly
- Provide text alternatives for complex visual content
- Test content parsing compatibility
- 🔴 **NEVER write the section-sign character "§" (U+00A7) in ANY file** — rule files, generated docs, specs, code, commit messages, PR bodies, tracker items. Write `Section 3` or just the number. It renders inconsistently across terminals, trackers and diff views.

## MANDATORY: Question Format
**CRITICAL**: Follow `common/question-format-guide.md` for all question formatting — multiple-choice
(A–E), the `[Answer]:` tag, answer validation and ambiguity resolution.

🔴 **Two questions are CHAT-ONLY and never get a question `.md` file**: the **Tracker Selection**
question (`common/tracker-sync.md`) and the **Context Opt-In** question
(`planning/workspace-detection.md` Step 4.7). Ask them conversationally and persist only the ANSWER
(to `aire-state.md` + `audit.md`).

## MANDATORY: Custom Welcome Message
**CRITICAL**: On ANY software development request, load `common/welcome-message.md` (in the resolved rule details directory) and display the complete message — ONCE at workflow start; do NOT reload it later (saves context).

## MANDATORY: Audit Trail, Session Identity & Timestamps

📄 **The complete contract lives in `common/audit-logging.md` — load it at workflow start.** It is
MANDATORY for EVERY workflow, stage, agent and skill. The non-negotiables:

- **Log EVERY user input** with the user's **COMPLETE RAW INPUT** — never summarized, never
  paraphrased — plus every approval prompt (before asking) and every response (after receiving).
- **Every `audit.md` entry carries `**User Email**:`** — the operator's email, read LIVE and silently
  from the session context, never asked, never a name, and recorded ONLY in `audit.md`. Local audit
  templates ADD fields to the base format; they NEVER drop this one.
- **Every timestamp comes from a real clock** at write time, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`), via
  EXACTLY ONE command — `date -u +%Y-%m-%dT%H:%M:%SZ` or
  `Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ"`. Never estimated, incremented, or copied forward.
- **Append only, chronological, to the END** of `.spec/aire-docs/audit.md`. 🔴 NEVER overwrite the
  file with its own contents plus additions — that duplicates the entire history.


# Adaptive Software Development Workflow

---

# PLANNING PHASE

**Purpose**: Planning, requirements gathering, and architectural decisions

**Focus**: Determine WHAT to build and WHY

**Stages in PLANNING PHASE**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (ALWAYS - no questions on team size or creation mode: `team_size` is fixed at 2 and all stories are generated at once; the generated story set requires explicit human approval — **GATE 1** — before it is pushed to the configured tracker, linked to the **Parent Epic** captured at workflow start)
- **Dependency Graph (ALWAYS — immediately after User Stories)** — records each story's `requires` dependencies; stories with no unfinished prerequisites are independently implementable in parallel
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)

## MANDATORY: Tracker Selection & Parent Epic Capture
aire asks the user ONCE which issue tracker to use — **JIRA**, **ADO**, **GITHUB**, or **LOCAL** (no external tracker; local Story Tracker is authoritative) — BEFORE Parent Epic Capture. **Skip and reuse** if `## Tracker` already exists (resumed project) — never re-ask. **NEVER infer/auto-select the tracker from a link the user pastes (e.g. a Jira Epic URL) — ALWAYS ask explicitly and wait for the answer**, even if it looks obvious. Full mechanics live in `common/tracker-sync.md` Section 1 — every tracker-facing rule below dispatches on `## Tracker` → `Type`. **LOCAL is fully complete** — zero external calls, ever (Section 12).

Users typically start with "using aire" + an existing Epic/tracking-item link or key, in whichever tracker was selected. If provided, record it in the `## Tracker` block in `.spec/aire-docs/aire-state.md` (exact schema: `common/tracker-sync.md` Section 1 — Type, Parent Epic, Epic URL, Project Key / Repo / Org). Rules:
- **Fetch the Epic content** per `common/tracker-sync.md` Section 2 (LOCAL: no fetch) into `.spec/aire-docs/planning/requirements/epic-brief.md` — primary input to Requirements Analysis and User Stories.
- **Conflict rule**: a DIFFERENT recorded Epic (resumed project) → ask the user which to keep — NEVER silently overwrite.
- No Epic provided → don't block; User Stories Part 3 asks before any push (LOCAL: never asks).
- Single source of truth for linking pushed stories to this Epic, unless the user chose `none` (record `Parent Epic: none`).

---

## Workspace Detection (ALWAYS EXECUTE)

1. **MANDATORY**: Log initial user request in audit.md with complete raw input
2. **MANDATORY**: Stamp `**User Email**:` on every audit entry (silent, email-only — `common/audit-logging.md`)
3. Load all steps from `planning/workspace-detection.md`
4. Execute workspace detection:
   - Check for existing aire-state.md (resume if found)
   - Scan workspace for existing code
   - Determine if brownfield or greenfield
   - **Resolve the code root** — if brownfield code does not live in `src/`, record `## Code Root` in aire-state.md per `common/directory-structure.md` and announce it. Never mass-move an existing tree.
   - Check for existing reverse engineering artifacts — search the WHOLE repo by their standard folder/file names (may live anywhere); if found, reuse and skip regeneration
4.5. **🧭 HELIX MCP GATE (`common/helix-atlas-integration.md`)**: on **brownfield**, or when the request/Epic indicates a **migration, re-platform, port, legacy rewrite or integration with an existing system**, Atlas is the source of existing-system truth. Resolve a Helix provider at runtime (never hardcode tool names) and record the binding. **If none resolves, emit the connect gate verbatim and HALT** — the user connects Helix, supplies exported Atlas docs, or explicitly approves local generation. Log the prompt and raw response. On greenfield with no existing system referenced, skip silently — never prompt.
5. **Ask Tracker Selection, then capture the Parent Epic** (both only AFTER the state check; skip Tracker Selection if `## Tracker` is already recorded): apply the rules above (`common/tracker-sync.md` Section 1), then, if the request contains an Epic link/key, write/merge `## Tracker` and fetch epic-brief.md per the configured tracker; log both in audit.md
6. **Create the Epic branch (automatic)**: per workspace-detection.md Step 4.5 / `common/branching-strategy.md` — record the base branch, create `epic/<EPIC-ID>-<title>`, record `## Branching` in aire-state.md. All work happens on this branch and story branches cut from it
7. Determine next phase: Reverse Engineering (if brownfield and no artifacts) OR Requirements Analysis
8. **MANDATORY**: Log findings in audit.md
9. Present the completion message (formats in workspace-detection.md), then proceed automatically

## Reverse Engineering (CONDITIONAL - Brownfield Only)

**🧭 ATLAS FIRST (`common/helix-atlas-integration.md` Section 5)**: AIRE never re-derives documentation
Atlas already holds and a human has already reviewed. Dispatch on Atlas coverage:

| Coverage | Behaviour |
|---|---|
| **Full** | ⏭️ **SKIP the stage.** Pull the deepdive docs into `.spec/aire-docs/planning/reverse-engineering/` and the graph into `knowledge-graph.md`, each with its provenance block. Announce the skip and the coverage list. |
| **Partial** | 🔀 Consume Atlas for what it covers; generate locally ONLY for the gaps, marking each locally generated file in its provenance block. |
| **None** (user approved local generation) | ▶️ Full local generation, with the banner *"Existing-system context derived locally; Atlas was not consulted."* on every artifact. |

Otherwise **execute** when existing code is detected and no prior RE artifacts exist; **skip** on
greenfield, or when prior artifacts already exist anywhere in the repo.

🔴 Atlas content is a **read-only input**. Never edit it to fit a plan. An Atlas/plan contradiction is
a finding to surface — follow Atlas, amend the AIRE-side artifact, say so plainly, log it.

**Execution**:
1. **MANDATORY**: Log start of reverse engineering in audit.md
2. Load all steps from `planning/reverse-engineering.md`
3. Execute: analyse all packages/components and generate — business overview (covering the business
   transactions), architecture, code structure, API documentation, component inventory, Interaction
   Diagrams, technology stack, and dependencies documentation
4. **Wait for Explicit Approval** (message format in reverse-engineering.md) — DO NOT PROCEED until
   the user confirms
5. **MANDATORY**: Log the user's response in audit.md with complete raw input

## Requirements Analysis (ALWAYS EXECUTE - Adaptive Depth)

**Always executes** but depth varies based on request clarity and complexity:
- **Minimal**: Simple, clear request - just document intent analysis
- **Standard**: Normal complexity - gather functional and non-functional requirements
- **Comprehensive**: Complex, high-risk - detailed requirements with traceability

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `planning/requirements-analysis.md`
3. Execute requirements analysis:
   - Load reverse engineering artifacts (if brownfield)
   - **Read the Parent Epic brief** (`.spec/aire-docs/planning/requirements/epic-brief.md`) if captured — the Epic's content defines what to build and is primary input here
   - Analyze user request (intent analysis)
   - Determine requirements depth needed
   - Assess current requirements
   - Ask clarifying questions (if needed)
   - Generate requirements document
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Follow approval format from requirements-analysis.md detailed steps - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input
7. Commit the planning artifacts on the Epic branch and push (automatic — no PR raised at this point; the Epic PR is raised manually by the user at the end of the cycle via `pr-generator`)

## User Stories (ALWAYS EXECUTE)

**Always executes** for every software development request. User stories ensure shared understanding, clear acceptance criteria, and testable specifications regardless of request type or complexity. Every project produces `stories.md` + `personas.md`, populates the Story Tracker in `aire-state.md`, and auto-pushes the stories to the configured tracker on approval (LOCAL: stays local).

**Note**: If Requirements Analysis executed, Stories can reference and build upon those requirements.

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `planning/user-stories.md`
3. Load reverse engineering artifacts (if brownfield)
4. If Requirements exist, reference them when creating stories
5. Execute at appropriate depth (minimal/standard/comprehensive)
6. **PART 1 - Planning**: **NEVER ask team size** — record the fixed default `team_size: 2` in `aire-state.md` (reused by Dependency Graph, never asked there either) and tune granularity so ≥ 2 independent stories can run in parallel. Create the story plan with its questions, wait for answers, analyze ambiguities. **The plan is announced, NOT approved**
7. **PART 2 - Generation**: **NEVER ask the creation mode** — `story_creation_mode` is the fixed default `all-at-once`. Generate every story in a single pass, then populate the Story Tracker (`Requires` filled in the next stage)
8. **🛑 GATE 1 — Story Set Approval (MANDATORY)**: announce the complete story set (user-stories.md Steps 19–20) and **Wait for Explicit Approval** — DO NOT PROCEED to Part 3 until the user chooses "Request Changes" or "Approve & Continue" (user-stories.md Step 21). A requested change is applied to `stories.md`/the Story Tracker, re-announced, and GATE 1 is presented again
9. **PART 3 - Push to the configured tracker (only after GATE 1 approval)**: follow user-stories.md Steps 24–28
10. **MANDATORY**: Log user's response in audit.md with complete raw input

> **Next**: Proceed immediately to **Dependency Graph** stage to map dependencies between all stories.

## Dependency Graph (ALWAYS EXECUTE — immediately after User Stories)

**Purpose**: Analyse story dependencies. Each story gets a `requires` list; stories whose prerequisites are all Done can be implemented in parallel by different developers. Produces `.spec/aire-docs/planning/dependency-graph.yml` and stamps `Requires` onto every story in the Story Tracker and `stories.md`.

**Execution**:
1. **MANDATORY**: Log start of Dependency Graph stage in audit.md
2. Load all steps from `planning/dependency-graph-generation.md` — it defines the execution steps (reuse the fixed `team_size: 2` — NEVER ask it), the TRUE-PARALLELISM RULES for computing `requires`, the `dependency-graph.yml` schema, and the **Story Tracker table format** (the canonical column definitions: Requires, Tracker ID, Status, PR, Merged, Start, End, Recorded)
3. Execute all steps from that file — **`requires` is INFERRED, never asked**
4. **AUTOMATIC — no gate**: announce the graph + ready-stories summary and PROCEED (enforced later by the Doability Gate and branch-cut merge check); a user correction is an interrupt
5. **MANDATORY**: Log the graph, inferred edges and any user correction in audit.md, with complete raw input

---

## MANDATORY: Tracker Sync Rule (applies everywhere a story status changes)

📄 **Mechanics: `common/tracker-sync.md` Section 4.** Whenever a story's status changes in the Story Tracker
(`aire-state.md`), dispatch on its **Tracker ID** column:

- **`—`/`LOCAL`** → update only the local tracker. No external action, ever.
- **A real JIRA/ADO/GITHUB id** → also transition the tracker issue, **confirm-first**
  (`🔄 Story 1.2 has Tracker ID PROJ-102. Transition to "[target status]"? (yes / skip)`). On yes:
  transition, verify it landed, log in audit.md. On skip: local only, and note the skip.
- **EXCEPTION — `In Development` is automatic**: picking a story via `dev-implement` IS the claim.
  Update both sides without asking, verify, announce. The story stays In Development through code
  generation, Code Review, Remediate, the PR raise and the auto PR review.

**🔷 Epic Status Sync** (skip silently when `Parent Epic: none` or `Type: LOCAL`):
- **First story starts** → also transition the Parent Epic to "In Development" — automatic, verified,
  announced, logged.
- **All stories done** (every story PR merged, last story at `🧪 Ready for Testing`) → offer
  **confirm-first** to move the Epic to "Ready for Testing". If any PR is still open, do NOT move the
  Epic — report the open PRs and keep everything In Development.

**Story↔Parent-Epic links** (User Stories Part 3) are **automatic, not confirm-first** — GATE 1
already gave explicit human approval to push the set — but still verified.

🔴 **NEVER** silently update only one side. Local and external trackers must stay in sync.

---


## Workflow Planning (ALWAYS EXECUTE)

1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `planning/workflow-planning.md`
3. **MANDATORY**: Load content validation rules from `common/content-validation.md`
4. Load all prior context:
   - Reverse engineering artifacts (if brownfield)
   - Intent analysis
   - Requirements (if executed)
   - User stories
5. Execute workflow planning:
   - Determine which phases to execute
   - Determine depth level for each phase
   - Create multi-package change sequence (if brownfield)
   - Generate workflow visualization (VALIDATE Mermaid syntax before writing)
6. **MANDATORY**: Validate all content before file creation per content-validation.md rules
7. **AUTOMATIC — no gate**: present the plan per workflow-planning.md Step 9 (stages can be added/removed any time) and proceed; each selected stage keeps its own approval
8. **MANDATORY**: Log the finalized plan and any user change in audit.md, with complete raw input

## Application Design (CONDITIONAL)

**Execute IF**:
- New components or services needed
- Component methods and business rules need definition
- Service layer design required
- Component dependencies need clarification

**Skip IF**:
- Changes within existing component boundaries
- No new components or methods
- Pure implementation changes

**Execution**:
1. **MANDATORY**: Log any user input during this phase in audit.md
2. Load all steps from `planning/application-design.md`
3. Load reverse engineering artifacts (if brownfield)
4. Execute at appropriate depth (minimal/standard/comprehensive)
5. **Wait for Explicit Approval**: Present detailed completion message (see application-design.md for message format) - DO NOT PROCEED until user confirms
6. **MANDATORY**: Log user's response in audit.md with complete raw input

## Transition to IMPLEMENTATION PHASE

After Application Design is approved (or after Workflow Planning approval when
Application Design is skipped), proceed directly to the **IMPLEMENTATION PHASE**.
The Implementation design stages run **once at system level**, scoped to the
**intake brief** at `.spec/aire-docs/planning/requirements/epic-brief.md`
(written from the provided Epic in whichever tracker was configured, or from
the user's requirements document / natural-language description). Log the
transition in audit.md.

---

# 🟢 IMPLEMENTATION PHASE

**Purpose**: Detailed design, NFR implementation, and code generation

**Focus**: Determine HOW to build it

**Stages in IMPLEMENTATION PHASE**:

1. **System-Level DESIGN Stages** (single pass, scoped to the intake brief; **no code generated here**)
   — Functional Design · NFR Requirements · NFR Design · Infrastructure Design (each CONDITIONAL).
2. **🏛️ `architecture.md` + Architecture Rubric + CI Pipeline** (ALWAYS — at the STOP CHECKPOINT,
   automatic, no gate): the design stages are consolidated into `.spec/architecture.md`; its
   Section 10 Verifiable Constraints mechanically derive `.evals/rubrics/architecture-rubric.json` (the
   **blocking** J1 gate); and this project's own `.github/workflows/agentic-eval-pipeline.yml` is
   generated from the repo's real stack and real thresholds.
3. 🛑 **MANDATORY STOP** — the workflow HALTS and waits. Code Generation NEVER starts on its own.
4. 🚀 **Development Handoff** — announce the ready stories; the user drives each one with
   **`dev-implement`**.
5. **Code Generation** (per-**story**, via the **`dev-implement`** keyword only) — full definition in
   `workflows/dev-implement.md`. In order:
   - **Story Selection** from the Dependency Graph, with a **Doability Gate** that never merges a
     prerequisite PR itself — even an approved one; merging stays a manual user action.
   - **Story branch** cut from the Epic branch (`common/branching-strategy.md`), then the D1–D7 +
     regression **baseline** capture.
   - 🥒 **Behaviour spec** written to `.spec/aire-docs/implementation/code/behavior/story-<N.M>.feature`
     — Gherkin authored BEFORE the code, because it is the contract. 🔴 That is the story's ONLY spec
     file; ACs, requirements, architecture and thresholds are read from their existing sources
     (`common/behavior-spec.md`).
   - **Code generation** into **`src/`**, tests into `tests/`.
   - **Gates, in sequence**: unit + coverage → 🥒 Gherkin in Podman (**B1** this unit → **B2** every other feature file → **B3** whole cycle, last unit only) → API & contract (when the
     story touches an API layer) → full regression vs baseline → static D1–D7 → automated Code Review
     including the diff-scoped Security Baseline review and the ⚖️ **blocking J1/J2 judge gates**.
   - **Every self-healing loop is capped at 3 attempts**; on exhaustion the run HALTS with the
     Retry-Limit Report rather than proceeding.
   - On a clean verdict: commit, push, PR, auto PR review. The story stays `🔵 In Development` until
     its PR **merges** and ve signs it off.
   - **🤖 Fully automatic — naming the story is the only user input.** The plan is announced (no
     GATE 2), the review routes on its own verdict (no GATE 3), findings are auto-remediated and
     re-reviewed until clean or the budget is spent.
6. **Code Review & Remediate** — `workflows/code-review.md` and `workflows/remediate.md`. Every review
   checks the acceptance criteria/requirements **and** the always-mandatory Security Baseline via a
   diff-scoped automated security review (`agents/code-security-review-agent.md` Phase 2.5), whose
   🔴/🟠 findings on the changed surface become real `SEC-ISS-XXX` findings. It also computes the
   ⚖️ **blocking** J1/J2 judge gates. Both run automatically inside every implement workflow and are
   ALSO invokable standalone, where they stay confirm-first.


**🧪 Test Plan is NOT part of this phase** — not at epic level, not at story level. It is ve's, run per story via the `/ve-implement` skill. No stage here runs it.

**Note on the STOP CHECKPOINT**: After Infrastructure Design (or after design stages are skipped), the workflow MUST stop and present the Development Handoff. It MUST NOT proceed into Code Generation on its own — the user explicitly drives code generation with the `dev-implement` keyword.

---

## System-Level DESIGN Stages (Single Pass)

**These DESIGN stages execute in sequence, ONCE for the whole system, scoped to the intake brief
captured at workflow start. Code Generation is NOT part of them** — it happens later, per-story, via
`dev-implement`, after the mandatory STOP CHECKPOINT.

**Primary inputs for EVERY design stage** (load before the stage's Step 1): `epic-brief.md` (defines
WHAT to build) · `requirements.md` · `stories.md` + the `## Story Tracker` · the Application Design
artifacts if that stage ran · 🧭 Atlas existing-system truth when the Helix MCP is bound — on brownfield
the existing architecture is the **starting state** and the design records the delta from it.

### The stages

| Stage | Rule file | Execute IF | Skip IF |
|---|---|---|---|
| **Functional Design** | `implementation/functional-design.md` | New data models or schemas · complex business logic · business rules need detailed design | Simple logic changes · no new business logic |
| **NFR Requirements** | `implementation/nfr-requirements.md` | Performance requirements exist · security considerations · scalability concerns · tech stack selection required | No NFR requirements · tech stack already determined |
| **NFR Design** | `implementation/nfr-design.md` | NFR Requirements executed · NFR patterns need incorporating | No NFR requirements · NFR Requirements skipped |
| **Infrastructure Design** | `implementation/infrastructure-design.md` | Infrastructure services need mapping · deployment architecture required · cloud resources need specification | No infrastructure changes · infrastructure already defined |

### Execution pattern — IDENTICAL for all four stages

1. **MANDATORY**: Log any user input during this stage in audit.md
2. Load all steps from the stage's rule file (table above)
3. Execute the stage **for the whole system**
4. **MANDATORY**: Present the standardized **2-option** completion message as defined in that stage's
   rule file — 🔴 DO NOT invent a 3-option menu or any other emergent navigation pattern
5. **Wait for Explicit Approval**: the user chooses "Request Changes" or "Continue to Next Stage" —
   DO NOT PROCEED until they confirm
6. **MANDATORY**: Log the user's response in audit.md with complete raw input

> **End of the System-Level DESIGN stages.** Once they have completed (or been skipped), DO NOT
> generate code. Proceed to the mandatory STOP CHECKPOINT below.

---


## 🛑 MANDATORY STOP — After Infrastructure Design, Before Code Generation

**This is a hard halt.** After the design stages complete (Infrastructure Design is done or skipped), the workflow MUST stop and wait for the user. **Code Generation MUST NOT start automatically.** Present the Development Handoff below, then block until the user invokes `dev-implement`.

1. **MANDATORY**: Log reaching the stop CHECKPOINT in audit.md.
1.3. **🥒 WRITE `.spec/behavior.feature` (automatic, no gate)**: per `common/behavior-spec.md` Section 3 — the **cross-story journeys that belong to no single story**, tagged `@REQ-<id>`. Written ONCE per cycle; this is what the **B3 tier** runs on the last work unit. 🔴 Genuine cross-unit journeys only, never copies of per-story scenarios; if the requirement has none, record that explicitly.
1.4. **🏛️ WRITE `architecture.md` (MANDATORY, automatic, no gate)**: per `implementation/architecture-doc.md`, consolidate the design stages into **`.spec/architecture.md`** — system context, component inventory, layering and boundaries, data architecture, API/integration contracts, cross-cutting decisions, non-functional targets, infrastructure, the delta from the existing system (brownfield), and **Section 10 Verifiable Constraints**. It is **assembled from the approved design artifacts and Atlas truth — never authored fresh**; a skipped design stage says so explicitly rather than being filled with an invented decision. Section 10 is mandatory and is what makes the blocking J1 gate fair: 3–8 constraints, each with an ID, an imperative one-sentence constraint, a *verifiable-as* rule naming exactly what scores 0 in a diff, a weight, and its source artifact; weights sum to 1.0. Version it and log it in audit.md.
1.5. **📐 Derive the rubrics (automatic, no gate)**: per `implementation/architecture-doc.md` Section 4 and `common/eval-framework.md` Section 3, generate `.evals/rubrics/architecture-rubric.json` **mechanically from `architecture.md` Section 10** — one constraint, one criterion, same wording, same weights, `rubricVersion` **equal to** the `architecture.md` version. Also create `.evals/rubrics/security-rubric.json` (OWASP-based, per `implementation/architecture-doc.md` Section 4.1) and `.evals/config.json` from the eval-framework.md Section 1 template if they do not exist yet. 🔴 **Artifact Ownership (`common/directory-structure.md`) — create if missing, never regenerate.** `config.json`, `scripts/`, `behavior/`, `security-rubric.json`: if present (inherited from base), use AS-IS. **If ABSENT, create them** deterministically (no timestamps, stable key order) and commit them **on the cycle branch**. 🔴 Never push to base and never raise a separate `[CI]` PR — they reach base when the cycle's PR merges. 🔴 **Never halt a cycle because base was not bootstrapped.** 🔴 **Never hand-write or hand-edit a rubric** — edit Section 10 and regenerate; J1 is a blocking gate and a rubric that cannot be traced to an approved decision cannot fairly fail a story. If nothing is derivable, apply the Section 3 fallback chain and record that J1 will be `N/A` (an `N/A` J1 never blocks). Log in audit.md.
1.6. **⚙️ Generate the project's CI pipeline (automatic; one setup gate)**: per `common/ci-pipeline-generation.md`, generate `.github/workflows/agentic-eval-pipeline.yml` **for THIS project** — every command from the repo's own build files, every threshold from `.evals/config.json`. Four stages mirroring local gates. **🔴 VALIDATE BEFORE COMMITTING (Section 4.0)**: YAML must parse, pass `actionlint`, reference only existing scripts — quote every `name:`, no bare colons, no `<placeholders>`. An invalid workflow is NEVER committed; after pushing, confirm a run started. **SonarQube**: generate `sonar-project.properties` + scan steps, present the setup gate (Section 4.1.2) and **HALT for `proceed` or `skip`**; 🔴 never write a token into any file, plus a self-repair job via **Claude Code CLI authenticated by `CLAUDE_CODE_OAUTH_TOKEN`**, capped at `retryLimitForSelfRepair`. Also generate `.evals/scripts/run-static-evals.*` (🔴 owns the D1–D7 baseline diff), `run-evals.*` and `auto-fix-agent.*`. 🔴 **Commit the pipeline + scripts on the CYCLE branch** (Section 2.1) — GitHub runs a `pull_request` workflow from the HEAD branch, so CI works from the first PR and reaches base when the cycle merges. Never push to base, never a separate `[CI]` PR. **Idempotent** — never overwrites a human-edited pipeline. 🔴 CI **re-verifies** local gates; it never relaxes them.
2. Mark in `aire-state.md`: `Design complete — awaiting dev-implement`.
3. **Commit + push the design artifacts on the Epic branch (automatic — this is what unblocks ve)**: stage `.spec/aire-docs/implementation/design/**`, `.spec/architecture.md`, `.evals/` (architecture-rubric + any files created by Step 1.5's create-if-missing rule), `aire-state.md`, `audit.md`. Commit with an `AIRE-Version: [N]` trailer and push. If the push fails, tell the user to push manually — **ve cannot start until this branch is on origin**.
4. Present the **Development Handoff** message (below).
5. **HALT.** Do not proceed to Code Generation or any later stage until the user types `dev-implement` (to build a story)
## 🚀 Development Handoff — Use `dev-implement` to Build Each Story

📄 At Step 4 of the STOP CHECKPOINT above, load `common/development-handoff.md` and emit its message
**verbatim** — that file carries the template and its substitution rules. Never ship an unsubstituted
placeholder. Log the handoff in audit.md, then **HALT**.

---

## Code Generation (Only execute when the user types `dev-implement`, per-story)

**On invocation of the `dev-implement` keyword, read `workflows/dev-implement.md` and follow it exactly.**

---

## Code Review & Remediate

**Status**: OPTIONAL standalone invocations, for **a specific story** or for **all stories together**.
Both also run automatically inside every implement workflow — this section is about the standalone use.

- **`code-review`** → read `workflows/code-review.md` and follow it exactly (REVIEWER, read-only).
- **`remediate`** → read `workflows/remediate.md` and follow it exactly (DEV, code-editing).

Each is self-contained — no separate detail file to load. 🔴 **NEVER auto-run them here**; standalone
invocations are user-initiated. After a story's PR is raised, *suggest* both as optional next steps
without running either. Log every user response and tracker update in audit.md with complete raw input.

---

# TICKET WORKFLOW (keyword: `ticket-implement <TICKET-ID>` — Bug OR Enhancement)

**On `ticket-implement <TICKET-ID>`** (an existing ticket in the configured tracker; omit the ID for LOCAL — describe the item inline instead): read `workflows/ticket-implement.md` and follow it exactly.

---

## Key Principles

- **Adaptive Execution** — run only the stages that add value; complex changes get full treatment,
  simple changes stay efficient.
- **Transparent Planning** — always show the execution plan before starting; the user may add or
  remove stages at any time.
- **Progress Tracking** — record executed and skipped stages in `aire-state.md`.
- **Complete Audit Trail** — every interaction logged with its complete raw input, not just approvals.
- **Content Validation** — validate all content before file creation (`common/content-validation.md`).
- **Bounded Self-Healing** — every automatic fix loop is capped at **3 attempts**; on exhaustion the
  run HALTS at that gate with the Retry-Limit Report and asks the user for next steps. A failing gate
  is never skipped, weakened, or carried forward.
- 🔴 **NO EMERGENT BEHAVIOR** — Implementation-phase design stages MUST use the standardized
  **2-option** completion message from their own rule file. Never invent a 3-option menu or any other
  navigation pattern.

## MANDATORY: Plan-Level Checkbox Enforcement

1. **NEVER complete work without updating the plan checkboxes.** Immediately after finishing ANY step
   described in a plan file, mark it `[x]` — in the **SAME interaction** where the work completed.
   No exceptions.
2. **Two levels**: plan-level tracks detailed progress within a stage; stage-level tracks overall
   workflow progress in `aire-state.md`. Both update in the same interaction as the work.


## Prompts Logging Requirements

📄 **Full contract, entry formats and file-handling rules: `common/audit-logging.md`** (loaded at
workflow start). Summary of the non-negotiables:

- Log EVERY user input and AI response, with the **COMPLETE RAW INPUT** — never summarized.
- Every entry carries `**Timestamp**:` (real clock, ISO 8601) and `**User Email**:` (session email,
  read live, email only). Implementation-flow entries add `**TRACKER ITEM**:`, `**Epic Link**:` and
  `**AIRE VERSION**:`; self-healing entries add `**SH-LOOP**:`, `**Root cause**:` and
  `**Verification**:`.
- Append to the END of `.spec/aire-docs/audit.md` in chronological order.
  🔴 Never overwrite the file with its own contents plus additions.


## Directory Structure

**CRITICAL RULE — four roots, nothing outside them**:
- **`src/`** — ALL application code, greenfield AND brownfield. If a brownfield repo keeps code
  elsewhere, record that root ONCE in `aire-state.md` `## Code Root` and treat it as `src/` for the
  whole cycle. 🔴 Never introduce a second code location; never mass-move an existing tree.
- **`tests/`** — `unit/`, `behavior/` (🥒 Gherkin step definitions), `e2e/` (Playwright)
- **`.spec/`** — specifications and documentation ONLY, 🔴 never a source file:
  `architecture.md` and `behavior.feature` at its root (**once per cycle, never per story**),
  `.spec/aire-docs/` (`planning/`, `implementation/` — incl. one `.feature` per work unit under
  `implementation/code/behavior/` — `tests/`, `aire-state.md`, `audit.md`), and the
  human-authored `.spec/context-project/` — `existing-knowledge/` (how the current system works) and
  `new-references/` (wireframes, mockups, API specs); read only at a user-supplied path, never auto-scanned
- **`.evals/`** — `config.json`, `rubrics/`, `scripts/`
- Generated per project: **`.github/workflows/agentic-eval-pipeline.yml`**
  (`common/ci-pipeline-generation.md`)
- Structure inside `src/`: see `implementation/code-generation.md` for patterns by project type


**Full canonical layout**: `common/directory-structure.md` — the complete tree (planning/implementation/tests/operations artifact paths, `.evals/`, Playwright's own root files, per-work-unit evidence folders). Load it on demand when you need to place or locate an artifact whose path isn't already fixed by the rule file you are following.
