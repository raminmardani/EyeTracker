# Requirements Analysis (Adaptive)

**Assume the role** of a product owner

**Adaptive Phase**: Always executes. Detail level adapts to problem complexity.

**See [depth-levels.md](../common/depth-levels.md) for adaptive depth explanation**

## Prerequisites
- Workspace Detection must be complete
- Reverse Engineering must be complete (if brownfield)

## Execution Steps

### Step 1: Load Reverse Engineering Context (if available)

**IF brownfield project**:
- Resolve the artifacts location: use `Reverse Engineering Artifacts: <path>` from `aire-state.md` `## Workspace State` if recorded (artifacts may live anywhere in the repo); else default to `.spec/aire-docs/planning/reverse-engineering/`
- Load `<artifacts-path>/architecture.md`
- Load `<artifacts-path>/component-inventory.md`
- Load `<artifacts-path>/technology-stack.md`
- Use these to understand existing system when analyzing request

### Step 1.5: Load Context Project Artifacts (if the user opted in)

Read the `## Context Project` section in `.spec/aire-docs/aire-state.md` (written during Workspace Detection):

- **IF `Use Artifacts: Yes`**: read **only** the exact `Artifact Path` recorded there — do NOT scan the rest of `.spec/context-project/existing-knowledge/`. Convert any non-markdown content to markdown as needed (see Step 4). These artifacts describe **how the CURRENT system works** (existing behavior, layout, module responsibilities) — use them as **background context** to ground your understanding of the codebase when analyzing the request; the WHAT-to-build still comes from the Epic brief (`epic-brief.md`). In the generated `requirements.md`, add a short **"Context Project artifacts consulted: `<path>`"** note for traceability.
- **IF `Use Artifacts: No`** (or the section is absent): proceed with no context-project input.

### Step 1.5b: Load Context References (if the user opted in)

Read the `## Context References` section in `.spec/aire-docs/aire-state.md` (written during Workspace Detection or ticket-implement):

- **IF `Use References: Yes`**: read **all** paths listed in `Reference Paths`. These are reference materials for the NEW work — UX wireframes, design mockups, API specs, research docs, architecture diagrams, etc. Use them as **primary inputs** that guide WHAT to build and HOW it should look/behave. For each path:
  - **UI wireframes / mockups / screenshots**: extract every control, layout, grouping, interaction, and visual element shown — these define the target UI
  - **API specs** (OpenAPI, Swagger, etc.): extract endpoints, schemas, request/response shapes — these define the target API surface
  - **Research docs / architecture diagrams**: extract relevant constraints, patterns, and decisions — these inform the system shape
  - Convert non-markdown content as needed (binary formats per DR-3 rules)
- In the generated `requirements.md`, add a **"Context References consulted"** section listing each reference path, its type, and what was extracted from it for traceability.
- **IF `Use References: No`** (or the section is absent): proceed with no new-references input.

### Step 1.6: READ the Design References (MANDATORY — blocking)

**Load `common/design-reference-grounding.md`.** Read the `## Design References` section in `.spec/aire-docs/aire-state.md` (written at Workspace Detection Step 4.8).

For **every** row with `Read? ⏳`, apply **DR-2** now — open the artifact's **actual content**, not just its path or its folder/file names:
- **UI prototype** → open the `*.component.html` / `*.ts` / `*.css` (or equivalent) of the components in scope; extract real control types, grouping, labels, icons, interaction behaviour, and custom CSS classes
- **Spec document** (`.docx`/`.xlsx`/`.pptx`/`.pdf`) → extract and read the body per **DR-3**; a binary format is never a reason to defer
- **Screenshot / mockup** → enumerate every control, grouping, and state it shows

Then:
- Flip the row to `Read? ✅` and stamp `Read At Stage: Requirements Analysis`
- Record what was extracted in `requirements.md` under a **"Design references consulted"** grounding note — per reference, what it governs and what was learned (not merely the path)
- If a reference contradicts the Epic brief or anything already approved, apply **DR-8 precedence** then **DR-6** reporting: where the existing artifact records a deliberate decision on that point, follow the artifact; otherwise follow the reference, state plainly in `requirements.md` and your output what differed and which you followed, and continue — do not halt and do not turn it into a question
- **Record any decision you take AGAINST a reference** (an exclusion, narrowing, or override) in the `### Reconciliations` table under `## Design References` per **DR-8** — later stages re-open the same raw reference and will otherwise undo it

Read every `⏳` reference before writing `requirements.md`. **This adds no question and no gate** — just read them and carry on.

### Step 2: Analyze User Request (Intent Analysis)

#### 2.1 Request Clarity
- **Clear**: Specific, well-defined, actionable
- **Vague**: General, ambiguous, needs clarification
- **Incomplete**: Missing key information

#### 2.2 Request Type
- **New Feature**: Adding new functionality
- **Bug Fix**: Fixing existing issue
- **Refactoring**: Improving code structure
- **Upgrade**: Updating dependencies or frameworks
- **Migration**: Moving to different technology
- **Enhancement**: Improving existing feature
- **New Project**: Starting from scratch

#### 2.3 Initial Scope Estimate
- **Single File**: Changes to one file
- **Single Component**: Changes to one component/package
- **Multiple Components**: Changes across multiple components
- **System-wide**: Changes affecting entire system
- **Cross-system**: Changes affecting multiple systems

#### 2.4 Initial Complexity Estimate
- **Trivial**: Simple, straightforward change
- **Simple**: Clear implementation path
- **Moderate**: Some complexity, multiple considerations
- **Complex**: Significant complexity, many considerations

### Step 3: Determine Requirements Depth

**Based on request analysis, determine depth:**

**Minimal Depth** - Use when:
- Request is clear and simple
- No detailed requirements needed
- Just document the basic understanding

**Standard Depth** - Use when:
- Request needs clarification
- Functional and non-functional requirements needed
- Normal complexity

**Comprehensive Depth** - Use when:
- Complex project with multiple stakeholders
- High risk or critical system
- Detailed requirements with traceability needed

### Step 4: Assess Current Requirements

Analyze whatever the user has provided:
   - Intent statements or descriptions (already logged in audit.md)
   - Existing requirements documents (search workspace if mentioned)
   - Pasted content or file references
   - Convert any non-markdown documents to markdown format 

### Step 5: Thorough Completeness Analysis

**CRITICAL**: Use comprehensive analysis to evaluate requirements completeness. Default to asking questions when there is ANY ambiguity or missing detail.

**MANDATORY**: Evaluate ALL of these areas and ask questions for ANY that are unclear:
- **Functional Requirements**: Core features, user interactions, system behaviors
- **Non-Functional Requirements**: Performance, security, scalability, usability
- **User Scenarios**: Use cases, user journeys, edge cases, error scenarios
- **Business Context**: Goals, constraints, success criteria, stakeholder needs
- **Technical Context**: Integration points, data requirements, system boundaries
- **Quality Attributes**: Reliability, maintainability, testability, accessibility

**When in doubt, ask questions** - incomplete requirements lead to poor implementations.

### Step 5.1: Extension Opt-In Prompts

**MANDATORY**: Scan all loaded `*.opt-in.md` files (loaded at workflow start from `extensions/` subdirectories) for an `## Opt-In Prompt` section. For each extension that declares one, include that question in the clarifying questions file created in Step 6. Present each opt-in question in the same language as the user's conversation.

**🔴 Opt-in questions are NEVER skipped, even when Step 6 judges the rest of requirements
"exceptionally clear and complete."** If every other clarifying question would otherwise be
skipped, still create the clarifying-questions file containing ONLY the opt-in question(s) — do not
fold "no requirements questions needed" into "no extension questions needed either." Each opt-in
question follows whatever default-answer behavior its own `*.opt-in.md` file specifies; absent such
a note, the tag stays blank per the standard format and an explicit answer is required. (Extensions
with no `*.opt-in.md` file at all — e.g. Security Baseline, Playwright Test Automation — are always
mandatory per CLAUDE.md and have no question here at all.)

After receiving answers:
1. Record each extension's enablement status in `.spec/aire-docs/aire-state.md` under `## Extension Configuration`:

```markdown
## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| [Extension Name] | [Yes/No] | Requirements Analysis |
```

2. **Deferred Rule Loading**: For each extension the user opted IN, load the full rules file now. The rules file is derived by naming convention: strip `.opt-in.md` from the opt-in filename and append `.md` (e.g., `security-baseline.opt-in.md` → `security-baseline.md`). For extensions the user opted OUT, do NOT load the full rules file.

### Step 6: Generate Clarifying Questions (PROACTIVE APPROACH)
   - **ALWAYS** create `.spec/aire-docs/planning/requirements/requirement-verification-questions.md` unless requirements are exceptionally clear and complete
   - Ask questions about ANY missing, unclear, or ambiguous areas
   - Focus on functional requirements, non-functional requirements, user scenarios, and business context
   - Request user to fill in all [Answer]: tags directly in the questions document
   - If presenting multiple-choice options for answers:
     - Label the options as A, B, C, D etc.
     - Ensure options are mutually exclusive and don't overlap
     - ALWAYS include option for custom response: "X) Other (please describe after [Answer]: tag below)"
   - Wait for user answers in the document
   - **MANDATORY**: Analyze ALL answers for ambiguities and create follow-up questions if needed
   - **MANDATORY**: Keep asking questions until ALL ambiguities are resolved OR user explicitly asks to proceed

### Step 6.5: Answers Naming a Path or Document — REGISTER and READ (MANDATORY — automatic, no new question)

Apply **DR-1 / DR-3 / DR-4** of `common/design-reference-grounding.md` to **every** answer received in Step 6. **This adds no question of its own** — it governs what you must do with answers the user has *already* given.

**Trigger — mechanical, not judgement-based.** If an answer contains a filesystem path, a spec filename (`.docx`/`.xlsx`/`.pptx`/`.pdf`/`.fig`), a screenshot, or a design URL, then:

1. **Register it** — add a row to `## Design References` in `aire-state.md` (DR-1). **The answer's framing is irrelevant**: *"the design/HTML is already built at X"* (a statement of fact) is the SAME trigger as *"refer to X for the widget names"* (an instruction). Both are references you must read.
2. **Read it NOW, in this stage** (DR-4) — an answer that points at a document is **not received** until that document has been read. Apply **DR-2**: open the real content; listing a prototype's component-folder **names**, or confirming the path exists, does NOT count as having read it.
3. **Never record "deferred to a later stage"** as the resolution of an answer. If the user says the detail lives in a document, read the document now and fold its actual content into the answer and into `requirements.md`.
4. If reading it reveals a contradiction with the Epic brief or an already-approved artifact, apply **DR-6** — follow the reference, state plainly what differed and that you followed it, and continue. Do NOT halt, do NOT raise a follow-up question about it.

**No new gate**: reading a referenced document is work you do on your own after the answers arrive — it never sends the question file back to the user and never adds a `[Answer]:` tag.

### ⛔ GATE: Await User Answers
DO NOT proceed to Step 7 until all questions in requirement-verification-questions.md are answered and validated.
Present the question file to the user and STOP.

Once the answers are in, read any documents they reference (Step 6.5) and proceed to Step 7 — this reading is silent and never re-prompts the user.

### Step 7: Generate Requirements Document
   - **PREREQUISITE**: Step 6 gate must be passed — all answers received and analyzed
   - Create `.spec/aire-docs/planning/requirements/requirements.md`
   - Include intent analysis summary at the top:
     - User request
     - Request type
     - Scope estimate
     - Complexity estimate
   - Include both functional and non-functional requirements
   - **MANDATORY — REQ-IDs (traceability thread)**: assign a stable ID to EVERY requirement — `REQ-F-NN` (functional) and `REQ-NF-NN` (non-functional) — per `common/requirements-traceability.md` Rule 1. IDs are permanent (never renumbered/reused); every downstream artifact (stories `Covers`, coverage matrix, code-generation plans, code reviews) refers to requirements ONLY by these IDs
   - Incorporate user's answers to clarifying questions
   - Provide brief summary of key requirements

### Step 8: Update State Tracking

Update `.spec/aire-docs/aire-state.md`:

```markdown
## Stage Progress
### 🔵 PLANNING PHASE
- [x] Workspace Detection
- [x] Reverse Engineering (if applicable)
- [x] Requirements Analysis
```

### Step 9: Log and Proceed
   - Log approval prompt with timestamp in `.spec/aire-docs/audit.md`
   - Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔍 Requirements Analysis Complete
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of requirements
        - Format: "Requirements analysis has identified [project type/complexity]:"
        - List key functional requirements (bullet points)
        - List key non-functional requirements (bullet points)
        - Mention architectural considerations or technical decisions if relevant
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the requirements document at: `.spec/aire-docs/planning/requirements/requirements.md`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** -  Ask for modifications to the requirements if required based on your review 
> ✅ **Approve & Continue** - Approve requirements and proceed 

---
```

   - Wait for explicit user approval before proceeding
   - Record approval response with timestamp
   - Update Requirements Analysis stage complete in aire-state.md
   - Then execute Step 10 (Epic Branch Commit & Push) BEFORE moving to User Stories

### Step 10: Epic Branch Commit & Push (MANDATORY — immediately after requirements.md approval)

**Runs only after the user has explicitly approved `requirements.md`.** The epic branch was already created at workflow start (Workspace Detection Step 4.5 → `common/branching-strategy.md` Section 1) — do NOT create a new branch here.

1. Confirm the active branch is the **Epic Branch** recorded in `aire-state.md` `## Branching` (`git branch --show-current`); switch to it if not.
2. Commit the Planning artifacts generated so far (`.spec/aire-docs/` requirements, plans, state, audit) on the epic branch so the work is persisted.
3. Push the epic branch to origin (`git push origin <epic-branch>`). **🔴 Do NOT raise an Epic → Base PR at this point.** The Epic PR is raised manually by the user at the end of the cycle (after all stories are developed, ve has approved them, and the epic branch is complete) via `pr-generator`. No PR is opened here.
4. Log in `.spec/aire-docs/audit.md`: commit hash and push confirmation, with timestamps.
5. Update `## Branching` in `.spec/aire-docs/aire-state.md`: `Epic PR: (not raised — raised manually at cycle end via pr-generator)`.
6. Then proceed to the **User Stories** stage (remaining on the epic branch).