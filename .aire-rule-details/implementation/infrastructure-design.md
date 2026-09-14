# Infrastructure Design

## Prerequisites
- Functional Design must be complete (or skipped — then use the intake brief + requirements as inputs)
- NFR Design recommended (provides logical components to map)
- Execution plan must indicate Infrastructure Design stage should execute

## Overview
Map logical software components to actual infrastructure choices for deployment environments.

## Steps to Execute

### Step 1: Analyze Design Artifacts
- Read functional design from `.spec/aire-docs/implementation/design/functional-design/` (if it exists; else use the intake brief + requirements)
- Read NFR design from `.spec/aire-docs/implementation/design/nfr-design/` (if exists)
- Identify logical components needing infrastructure

### Step 2: Create Infrastructure Design Plan
- Generate plan with checkboxes [] for infrastructure design
- Focus on mapping to actual services (AWS, Azure, GCP, on-premise)
- Each step should have a checkbox []

### Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the functional and NFR design to identify ALL areas where clarification would improve infrastructure decisions. Be proactive in asking questions to ensure comprehensive infrastructure coverage.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect infrastructure quality. It's better to ask too many questions than to make incorrect infrastructure assumptions.

**MANDATORY**: Evaluate ALL of the following categories by asking targeted questions about each. For each category, determine applicability based on evidence from the functional and NFR design artifacts -- do not skip categories without explicit justification:

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve infrastructure decisions
- **When in doubt, ask the question** - overconfidence leads to poor infrastructure choices

**Question categories to evaluate** (consider ALL categories):
- **Deployment Environment** - Ask about cloud provider preferences, environment setup, and deployment targets
- **Compute Infrastructure** - Ask about compute service choices, sizing, and scaling requirements
- **Storage Infrastructure** - Ask about database selection, storage patterns, and data lifecycle needs
- **Messaging Infrastructure** - Ask about messaging/queuing services, event-driven patterns, and async processing
- **Networking Infrastructure** - Ask about load balancing, API gateway approach, and network topology
- **Monitoring Infrastructure** - Ask about observability tooling, alerting strategy, and logging requirements
- **Shared Infrastructure** - Ask about infrastructure sharing strategy, multi-tenancy, and resource isolation

### Step 4: Store Plan
- Save as `.spec/aire-docs/implementation/plans/infrastructure-design-plan.md`
- Include all [Answer]: tags for user input

### Step 5: Collect and Analyze Answers
- Wait for user to complete all [Answer]: tags
- Review for vague or ambiguous responses
- Add follow-up questions if needed

### Step 6: Generate Infrastructure Design Artifacts
- Create `.spec/aire-docs/implementation/design/infrastructure-design/infrastructure-design.md`
- Create `.spec/aire-docs/implementation/design/infrastructure-design/deployment-architecture.md`
- If shared infrastructure: Create `.spec/aire-docs/implementation/shared-infrastructure.md`

### Step 7: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🏢 Infrastructure Design Complete - [project-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of infrastructure design
        - Format: "Infrastructure design has mapped [description]:"
        - List key infrastructure services and components (bullet points)
        - List deployment architecture decisions and rationale
        - Mention cloud provider choices and service mappings
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the infrastructure design at: `.spec/aire-docs/implementation/design/infrastructure-design/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the infrastructure design based on your review  
> ✅ **Continue to Next Stage** - Approve infrastructure design and proceed to the **🛑 STOP CHECKPOINT / Development Handoff**

---
```

> 🛑 **STOP CHECKPOINT**: Infrastructure Design completion is the **mandatory stop before Code Generation**. Do **NOT** proceed into Code Generation automatically. Present the **Development Handoff** (see `CLAUDE.md`) and HALT — code is generated per-story only when the user types **`dev-implement`**.

### Step 8: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the infrastructure design
- Approval must be clear and unambiguous
- If user requests changes, update the design and repeat the approval process

### Step 9: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark Infrastructure Design stage complete in aire-state.md

### Step 10: Post-Design Requirements Coverage Re-Verification (MANDATORY — automatic, before the STOP CHECKPOINT handoff)
Execute `common/requirements-traceability.md` Rule 4 — silent and blocking, NO user prompt (this is verification, not a new stage). It runs here because Infrastructure Design is the LAST design stage; **if Infrastructure Design is skipped, the same check runs right after whichever design stage executed last (or immediately when ALL design stages are skipped), before the Development Handoff is presented**:
- Re-verify the Requirements Coverage Matrix in `stories.md` (every REQ-ID fully expressed by story ACs) against the approved design artifacts under `.spec/aire-docs/implementation/design/`
- Reconcile in place any story AC the design contradicted or refined (update `stories.md` + the matrix; log every reconciliation in audit.md with the design artifact that drove it)
- Record in `aire-state.md`: `Requirements coverage verified post-design: [R]/[R] REQ-IDs — [timestamp]`
- Include the coverage line in the Development Handoff message (e.g., `🧾 Requirements coverage: 12/12 REQ-IDs verified against the approved design`)
