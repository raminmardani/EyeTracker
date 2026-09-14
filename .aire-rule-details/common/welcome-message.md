# aire Welcome Message

**Purpose**: This file contains the user-facing welcome message that should be displayed ONCE at the start of any aire workflow.

---

# 👋 Welcome to HelixAI-AIRE 👋


I'll guide you through an adaptive software development workflow that intelligently tailors itself to your specific needs.

## What is HelixAI-AIRE?

HelixAI-AIRE is a structured yet flexible software development process that adapts to your project's needs. Think of it as having an experienced software architect who:

- **Analyzes your requirements** and asks clarifying questions when needed
- **Plans the optimal approach** based on complexity and risk
- **Skips unnecessary steps** for simple changes while providing comprehensive coverage for complex projects
- **Documents everything** so you have a complete record of decisions and rationale
- **Guides you through each phase** with clear checkpoints and approval gates

## The Three-Phase Lifecycle

```
                         User Request
                              |
                              v
        +---------------------------------------+
        |     PLANNING PHASE                   |
        |     Planning & Application Design     |
        +---------------------------------------+
        | * Workspace Detection (ALWAYS)        |
        | * Reverse Engineering (COND)          |
        | * Requirements Analysis (ALWAYS)      |
        | * User Stories (ALWAYS, all at once   |
        |   + GATE 1 approval, then auto        |
        |   push to tracker)                    |
        | * Dependency Graph (ALWAYS, requires) |
        | * Workflow Planning (ALWAYS)          |
        | * Application Design (CONDITIONAL)    |
        +---------------------------------------+
                              |
                              v
        +---------------------------------------+
        |     IMPLEMENTATION PHASE                |
        |     Design & Implementation           |
        +---------------------------------------+
        | * System-Level DESIGN stages:         |
        |   - Functional Design (COND)          |
        |   - NFR Requirements Assess (COND)    |
        |   - NFR Design (COND)                 |
        |   - Infrastructure Design (COND)      |
        | * >> STOP << (before code gen)        |
        | * Code Generation (per-story, via     |
        |   `dev-implement`; + unit tests to threshold) |
        | * Code Review & Remediate (OPTIONAL)  |
        +---------------------------------------+
              |                    |
              |                    +----------------------+
              |                                           |
              |                            +---------------------------------------+
              |                            |  ve TRACK (parallel, NOT a phase)   |
              |                            +---------------------------------------+
              |                            | * Test Plan per story via        |
              |                            |   `/ve-implement` (manual test      |
              |                            |   steps from the story's acceptance   |
              |                            |   criteria - no code)                 |
              |                            | * `ve-list-work` on the epic or     |
              |                            |   base branch moves tested, merged    |
              |                            |   stories to Ready for Testing        |
              |                            +---------------------------------------+
              v
        +---------------------------------------+
        |     OPERATIONS PHASE                  |
        |     Placeholder for Future            |
        +---------------------------------------+
        | * Operations (PLACEHOLDER)            |
        +---------------------------------------+
                              |
                              v
                          Complete
```

### Phase Breakdown:

**PLANNING PHASE** - *Planning & Application Design*
- **Purpose**: Determines WHAT to build and WHY
- **Activities**: Understanding requirements, analyzing existing code (if any), planning the approach
- **Output**: Clear requirements, execution plan, a Story Tracker, a story breakdown with **dependencies mapped** so independent stories can be developed in parallel (stories pushed to your chosen tracker — Jira, Azure DevOps, or GitHub — and linked to your existing Parent Epic, or kept fully local)
- **Your Role**: Answer the clarifying questions, review and approve the generated story set (GATE 1) before it is pushed


**IMPLEMENTATION PHASE** - *Detailed Design & Implementation*
- **Purpose**: Determines HOW to build it
- **Activities**: System-level detailed design (when needed), then — after a mandatory **STOP** — per-story code generation that you trigger with the **`dev-implement`** keyword (on a story branch cut from the Epic branch, with unit tests generated and run to the `unitTestCoverageMin` threshold, plus — when the story adds/changes an API endpoint — an automated **API & Contract Testing Gate**: functional behavior, response-code validation, role-based authorization 401/403, error-response validation, request validation, and response contract/schema validation), and optional code review
- **Output**: Working code, unit tests, API & Contract test evidence (when applicable)
- **Your Role**: Review designs, type `dev-implement` to build each story, approve implementation plans, validate results

**ve TRACK** - *Test Plan, in parallel with development*
- **Purpose**: Proves each story meets its acceptance criteria
- **Not a Implementation stage** — neither at epic level nor at story level. ve drives it independently and can start immediately, without waiting for any code
- **Activities**: **`/ve-implement`** generates one story's Test Plan artifacts — manual test steps for every applicable test plan (integration, E2E, API, contract, security, performance, accessibility — whichever apply; there is no build-verification artifact), derived from the story's acceptance criteria, never from source code — into `.spec/aire-docs/tests/<JIRA-ID>-<jira-title>/`. The mandatory Playwright Test Automation extension means `/playwright-implement` always turns the UI-relevant steps into executable browser automation once both the dev's and ve's PRs have merged. **`ve-list-work`** (on the cycle's integration branch — epic, bug, or enhancement) reports which stories/tickets dev has merged and moves the ones ve has tested to Ready for Testing
- **Your Role (as ve)**: type `/ve-implement` per story, execute the test steps, then `ve-list-work` to sign off

**OPERATIONS PHASE** - *Deployment & Monitoring (Future)*
- **Purpose**: How to DEPLOY and RUN it
- **Status**: Placeholder for future deployment and monitoring workflows
- **Current State**: Testing is handled by the parallel ve track (`/ve-implement`)

## Key Principles:

- ⚡ **Fully Adaptive**: Each stage independently evaluated based on your needs
- 🎯 **Efficient**: Simple changes execute only essential stages
- 📋 **Comprehensive**: Complex changes get full treatment with all safeguards
- 🔍 **Transparent**: You see and approve the execution plan before work begins
- 📝 **Documented**: Complete audit trail of all decisions and changes
- 🎛️ **User Control**: You can request stages be included or excluded

## What Happens Next:

1. **I'll analyze your workspace** to understand if this is a new or existing project — and I'll ask whether there are any **context-project artifacts** (human-authored notes on how your current system works, under `.spec/context-project/existing-knowledge/`) I should use for this task
1.5. **I'll ask about reference materials** — UX wireframes, design mockups, API specs, or any other reference docs (under `.spec/context-project/new-references/`) that should guide what I build. These define the target state.
1.6. **I'll ask which issue tracker to use** — Jira, Azure DevOps, GitHub, or Local-only (no external tracker at all, everything tracked right here in the project's own state file). Whichever you pick is used for every story, bug, and enhancement from that point on — Local is a fully supported, complete option, not a fallback.
2. **I'll gather requirements** and ask clarifying questions if needed
3. **I'll create an execution plan** showing which stages I propose to run and why
4. **You'll review and approve** the plan (or request changes)
5. **We'll execute the plan** with checkpoints at each major stage
6. **You'll get working code** with complete documentation and tests

The aire process adapts to:
- 📋 Your intent clarity and complexity
- 🔍 Existing codebase state
- 🎯 Scope and impact of changes
- ⚡ Risk and quality requirements

Let's begin!
