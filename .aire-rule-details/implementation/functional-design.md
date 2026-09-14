# Functional Design

## Purpose
**Detailed business logic design at the system level (single pass)**

Functional Design focuses on:
- Detailed business logic and algorithms for the whole system
- Domain models with entities and relationships
- Detailed business rules, validation logic, and constraints
- Technology-agnostic design (no infrastructure concerns)

**Note**: This builds upon high-level component design from Application Design (PLANNING phase)

## Prerequisites
- User Stories and Dependency Graph must be complete (stories + Story Tracker exist)
- Intake brief available at `.spec/aire-docs/planning/requirements/epic-brief.md` (from the provided Epic, or from the user's requirements document / natural language)
- Application Design recommended (provides high-level component structure)
- Execution plan must indicate Functional Design stage should execute

## Overview
Design detailed business logic for the whole system, technology-agnostic and focused purely on business functions.

## Steps to Execute

### Step 1: Analyze System Context
- Read the intake brief from `.spec/aire-docs/planning/requirements/epic-brief.md` (if present) — it defines WHAT to build
- Read requirements from `.spec/aire-docs/planning/requirements/requirements.md`
- Read stories from `.spec/aire-docs/planning/user-stories/stories.md` and the `## Story Tracker` in `aire-state.md`
- Read `.spec/aire-docs/planning/application-design/` artifacts (if Application Design ran) for component structure and boundaries
- Read `## Context References` in `aire-state.md`. **IF `Use References: Yes`**, load all listed reference paths — UX wireframes define interaction flows, states, and validation rules; API specs define data contracts and operation semantics. Use them as primary inputs for detailed business logic design.

### Step 2: Create Functional Design Plan
- Generate plan with checkboxes [] for functional design
- Focus on business logic, domain models, business rules
- Each step should have a checkbox []

### Step 3: Generate Context-Appropriate Questions
**DIRECTIVE**: Thoroughly analyze the intake brief, requirements, and stories to identify ALL areas where clarification would improve the functional design. Be proactive in asking questions to ensure comprehensive understanding.

**CRITICAL**: Default to asking questions when there is ANY ambiguity or missing detail that could affect functional design quality. It's better to ask too many questions than to make incorrect assumptions.

- EMBED questions using [Answer]: tag format
- Focus on ANY ambiguities, missing information, or areas needing clarification
- Generate questions wherever user input would improve functional design decisions
- **When in doubt, ask the question** - overconfidence leads to poor designs

**Question categories to consider** (evaluate ALL categories):
- **Business Logic Modeling** - Ask about core entities, workflows, data transformations, and business processes
- **Domain Model** - Ask about domain concepts, entity relationships, data structures, and business objects
- **Business Rules** - Ask about decision rules, validation logic, constraints, and business policies
- **Data Flow** - Ask about data inputs, outputs, transformations, and persistence requirements
- **Integration Points** - Ask about external system interactions, APIs, and data exchange
- **Error Handling** - Ask about error scenarios, validation failures, and exception handling
- **Business Scenarios** - Ask about edge cases, alternative flows, and complex business situations
- **Frontend Components** (if applicable) - Ask about UI component structure, user interactions, state management, and form handling

### Step 4: Store Plan
- Save as `.spec/aire-docs/implementation/plans/functional-design-plan.md`
- Include all [Answer]: tags for user input

### Step 5: Collect and Analyze Answers
- Wait for user to complete all [Answer]: tags
- **MANDATORY**: Carefully review ALL responses for vague or ambiguous answers
- **CRITICAL**: Add follow-up questions for ANY unclear responses - do not proceed with ambiguity
- Look for responses like "depends", "maybe", "not sure", "mix of", "somewhere between"
- Create clarification questions file if ANY ambiguities are detected
- **Do not proceed until ALL ambiguities are resolved**

### Step 6: Generate Functional Design Artifacts
- Create `.spec/aire-docs/implementation/design/functional-design/business-logic-model.md`
- Create `.spec/aire-docs/implementation/design/functional-design/business-rules.md`
- Create `.spec/aire-docs/implementation/design/functional-design/domain-entities.md`
- If the system includes frontend/UI: Create `.spec/aire-docs/implementation/design/functional-design/frontend-components.md`
  - Component hierarchy and structure
  - Props and state definitions for each component
  - User interaction flows
  - Form validation rules
  - API integration points (which backend endpoints each component uses)

### Step 7: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 🔧 Functional Design Complete - [project-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary of functional design
        - Format: "Functional design has created [description]:"
        - List key business logic models and entities (bullet points)
        - List business rules and validation logic defined
        - Mention domain model structure and relationships
        - DO NOT include workflow instructions ("please review", "let me know", "proceed to next phase", "before we proceed")
        - Keep factual and content-focused
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the functional design artifacts at: `.spec/aire-docs/implementation/design/functional-design/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the functional design based on your review  
> ✅ **Continue to Next Stage** - Approve functional design and proceed to **[next-stage-name]**

---
```

### Step 8: Wait for Explicit Approval
- Do not proceed until the user explicitly approves the functional design
- Approval must be clear and unambiguous
- If user requests changes, update the design and repeat the approval process

### Step 9: Record Approval and Update Progress
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- Mark Functional Design stage complete in aire-state.md
