# Application Design - Detailed Steps

## Purpose
**High-level component identification and service layer design**

Application Design focuses on:
- Identifying main functional components and their responsibilities
- Defining component interfaces (not detailed business logic)
- Designing service layer for orchestration
- Establishing component dependencies and communication patterns

**Note**: Detailed business logic design happens later in Functional Design (system-level, IMPLEMENTATION phase)

## Prerequisites
- Workspace Detection must be complete
- Requirements Analysis recommended (provides functional context)
- User Stories recommended (user stories guide design decisions)
- Execution plan must indicate Application Design stage should execute

## Step-by-Step Execution

### 1. Analyze Context
- Read `.spec/aire-docs/planning/requirements/requirements.md` and `.spec/aire-docs/planning/user-stories/stories.md`
- Read `## Context References` in `aire-state.md`. **IF `Use References: Yes`**, load all listed reference paths — UX wireframes/mockups define the component structure and UI layout; API specs define service interfaces; architecture diagrams inform component dependencies. Use them as primary design inputs alongside requirements and stories.
- Identify key business capabilities and functional areas
- Determine design scope and complexity

### 1.5 📐 RE-CONSULT the Design References (MANDATORY — automatic, ask the user nothing)

**Load `common/design-reference-grounding.md`** and read `## Design References` in `.spec/aire-docs/aire-state.md`.

**This step adds no question, no gate, and no checkpoint.** You do it silently as part of analysing context.

**Re-open** every reference whose `Governs` covers a component you are about to define. This is a **fresh read of the content for THIS stage's scope** — an earlier stage may have read only the parts within its own scope, so *"it was already read at Requirements Analysis"* does not count.

For a UI prototype, extract per component: real control types, grouping/ordering, labels and icons, interaction behaviour (search, multi-select, click-outside, keyboard, empty states), and custom CSS classes — then check whether those classes exist in the live app's global styles.

**`components.md` states, for EVERY component, exactly one of:**

```
Design reference: <path>/<file> — grounded (<what the reference actually specifies>)
Design reference: none covers this component — built from ACs only
```

This is your own self-check before writing the artifact — satisfy it yourself; do not pause for the user.

- Any reference still `Read? ⏳` — read it now (DR-2/DR-3/DR-4) and carry on.
- A contradiction between a reference and an approved artifact → apply **DR-8 precedence**, then **DR-6** reporting. If the artifact already records a decision on that point, follow the artifact. Otherwise follow the reference, say plainly what differed, update the artifact text to stay truthful, and continue. No A/B question, no halt.
- A capability the prototype shows that is **outside** the approved requirements/ACs → **state that you saw it and excluded it**, then continue. Never silently build it, never silently drop it, never ask about it.

**🔒 RECORD YOUR RECONCILIATIONS (DR-8 — MANDATORY).** Application Design is where most deliberate deviations from a reference are decided, and **later stages will re-open the same raw reference**. Any decision you take *against* what a reference shows — excluding a capability, narrowing a scope model, scoping a stylesheet locally instead of globally, deferring something to a later story, or overriding it for an NFR/accessibility reason — MUST be written in **both** places, or Code Generation will re-read the prototype and silently undo it:

1. In `components.md` (or the relevant artifact), as a stated decision with its reason
2. As a row in the `### Reconciliations` table under `## Design References` in `aire-state.md` — see the format in `common/design-reference-grounding.md` DR-8

An unrecorded deviation is treated by every later stage as if it never happened.

### 2. Create Application Design Plan
- Generate plan with checkboxes [] for application design
- Focus on components, responsibilities, methods, business rules, and services
- Each step and sub-step should have a checkbox []

### 3. Include Mandatory Design Artifacts in Plan
- **ALWAYS** include these mandatory artifacts in the design plan:
  - [ ] Generate components.md with component definitions and high-level responsibilities
  - [ ] Generate component-methods.md with method signatures (business rules detailed later in Functional Design)
  - [ ] Generate services.md with service definitions and orchestration patterns
  - [ ] Generate component-dependency.md with dependency relationships and communication patterns
  - [ ] Validate design completeness and consistency

### 4. Generate Context-Appropriate Questions
**DIRECTIVE**: Analyze the requirements and stories to generate questions relevant to THIS specific application design. Use the categories below as guidance. Evaluate each category and, when in doubt about applicability, ask the question rather than skipping it — overconfidence leads to poor outcomes (see overconfidence-prevention.md).

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve design decisions
- **When in doubt, ask the question** - overconfidence leads to poor designs

**Question categories to evaluate** (consider ALL categories):
- **Component Identification** - Ask about component boundaries, organization, and grouping strategies
- **Component Methods** - Ask about method signatures, input/output expectations, and interface contracts (detailed business rules come later)
- **Service Layer Design** - Ask about service orchestration, boundaries, and coordination patterns
- **Component Dependencies** - Ask about communication patterns, dependency management, and coupling concerns
- **Design Patterns** - Ask about architectural style preferences, pattern choices, and design constraints

### 5. Store Application Design Plan
- Save as `.spec/aire-docs/planning/plans/application-design-plan.md`
- Include all [Answer]: tags for user input
- Ensure plan covers all design aspects

### 6. Request User Input
- Ask user to fill [Answer]: tags directly in the plan document
- Emphasize importance of design decisions
- Provide clear instructions on completing the [Answer]: tags

### 7. Collect Answers
- Wait for user to provide answers to all questions using [Answer]: tags in the document
- Do not proceed until ALL [Answer]: tags are completed
- Review the document to ensure no [Answer]: tags are left blank

### 8. ANALYZE ANSWERS (MANDATORY)
Before proceeding, you MUST carefully review all user answers for:
- **Vague or ambiguous responses**: "mix of", "somewhere between", "not sure", "depends"
- **Undefined criteria or terms**: References to concepts without clear definitions
- **Contradictory answers**: Responses that conflict with each other
- **Missing design details**: Answers that lack specific guidance
- **Answers that combine options**: Responses that merge different approaches without clear decision rules

### 9. MANDATORY Follow-up Questions
If the analysis in step 8 reveals ANY ambiguous answers, you MUST:
- Add specific follow-up questions to the plan document using [Answer]: tags
- DO NOT proceed to approval until all ambiguities are resolved
- Examples of required follow-ups:
  - "You mentioned 'mix of A and B' - what specific criteria should determine when to use A vs B?"
  - "You said 'somewhere between A and B' - can you define the exact middle ground approach?"
  - "You indicated 'not sure' - what additional information would help you decide?"
  - "You mentioned 'depends on complexity' - how do you define complexity levels?"

### 10. Generate Application Design Artifacts
- Execute the approved plan to generate design artifacts
- Create `.spec/aire-docs/planning/application-design/components.md` with:
  - Component name and purpose
  - Component responsibilities
  - Component interfaces
- Create `.spec/aire-docs/planning/application-design/component-methods.md` with:
  - Method signatures for each component
  - High-level purpose of each method
  - Input/output types
  - Note: Detailed business rules will be defined in Functional Design (epic-level, IMPLEMENTATION phase)
- Create `.spec/aire-docs/planning/application-design/services.md` with:
  - Service definitions
  - Service responsibilities
  - Service interactions and orchestration
- Create `.spec/aire-docs/planning/application-design/component-dependency.md` with:
  - Dependency matrix showing relationships
  - Communication patterns between components
  - Data flow diagrams
- Create `.spec/aire-docs/planning/application-design/application-design.md` that consolidates the multiple design docs created above in a single doc.

### 11. Log Approval
- Log approval prompt with timestamp in `.spec/aire-docs/audit.md`
- Include complete approval prompt text
- Use ISO 8601 timestamp format

### 12. Present Completion Message

```markdown
# 🏗️ Application Design Complete

[AI-generated summary of application design artifacts created in bullet points]

> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the application design artifacts at: `.spec/aire-docs/planning/application-design/`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the application design if required
> ✅ **Approve & Continue** - Approve design and proceed to the **IMPLEMENTATION PHASE** (system-level design stages)
```

### 13. Wait for Explicit Approval
- Do not proceed until the user explicitly approves the application design
- Approval must be clear and unambiguous
- If user requests changes, update the design and repeat the approval process

### 14. Record Approval Response
- Log the user's approval response with timestamp in `.spec/aire-docs/audit.md`
- Include the exact user response text
- Mark the approval status clearly

### 15. Update Progress
- Mark Application Design stage complete in `.spec/aire-docs/aire-state.md`
- Update the "Current Status" section
- Prepare for transition to next stage
