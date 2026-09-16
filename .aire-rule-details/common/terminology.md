# aire Terminology Glossary

## Core Terminology

### Phase vs Stage

**Phase**: One of the three high-level lifecycle phases in aire
- 🔵 **PLANNING PHASE** - Planning & Architecture (WHAT and WHY)
- 🟢 **IMPLEMENTATION PHASE** - Design, Implementation & Test (HOW)
- 🟡 **OPERATIONS PHASE** - Deployment & Monitoring (future expansion)

**Stage**: An individual workflow activity within a phase
- Examples: Context Assessment stage, Requirements Assessment stage, Code Generation stage
- Each stage has specific prerequisites, steps, and outputs
- Stages can be ALWAYS-EXECUTE or CONDITIONAL

**Usage Examples**:
- ✅ "The IMPLEMENTATION phase contains 7 stages"
- ✅ "The Code Generation stage is always executed"
- ✅ "We're in the PLANNING phase, executing the Requirements Assessment stage"
- ❌ "The Requirements Assessment phase" (should be "stage")
- ❌ "The IMPLEMENTATION stage" (should be "phase")

## Three-Phase Lifecycle

### PLANNING PHASE
**Purpose**: Planning and architectural decisions  
**Focus**: Determine WHAT to build and WHY  
**Location**: `planning/` directory

**Stages**:
- Workspace Detection (ALWAYS)
- Reverse Engineering (CONDITIONAL - Brownfield only)
- Requirements Analysis (ALWAYS - Adaptive depth)
- User Stories (ALWAYS - no team-size or creation-mode question; the generated story set requires explicit human approval — GATE 1 — before it pushes to the configured tracker)
- Dependency Graph (ALWAYS - assigns `requires`; right after User Stories)
- Workflow Planning (ALWAYS)
- Application Design (CONDITIONAL)

**Outputs**: Requirements, user stories, Story Tracker, dependency-graph.yml (requires), architectural decisions

### IMPLEMENTATION PHASE
**Purpose**: Detailed design and implementation  
**Focus**: Determine HOW to build it  
**Location**: `implementation/` directory

**Stages**:
- Functional Design (CONDITIONAL, system-level)
- NFR Requirements (CONDITIONAL, system-level)
- NFR Design (CONDITIONAL, system-level)
- Infrastructure Design (CONDITIONAL, system-level)
- 🛑 STOP CHECKPOINT (MANDATORY — after design, before Code Generation)
- Code Generation (ALWAYS, per-**story**) — triggered by `dev-implement`; Story Selection (local Story Tracker or the configured tracker) → story branch cut from the Epic branch → Part 1: Planning (announced, not gated) → Part 2: Generation → unit tests to `unitTestCoverageMin` coverage. No approval gates
- Code Review (AUTOMATIC after every code generation, and standalone via `code-review`; read-only versioned report)
- Remediate (AUTOMATIC whenever the review reports findings — fixes them and loops back through review until clean; also standalone via `remediate`; fix → unit test → green, story-scoped unit tests only)

**Outputs**: Design artifacts, NFR implementations, code, unit tests

**Not in this phase**: **Test Plan** — it belongs to the ve track below, not to Implementation (neither at epic nor at story level).

### ve TRACK (parallel — not a phase)
**Purpose**: Prove each story meets its acceptance criteria
**Focus**: Determine WHETHER it works
**Location**: `.spec/aire-docs/tests/<TICKET-ID>-<title>/` (one folder per story)

**Stages** (both ve-initiated, never auto-run):
- Test Plan (per **story**, via **`/ve-implement`**) — manual test steps for every applicable test plan, derived from the story's acceptance criteria; runs in parallel with development and never reads application source code
- ve Sign-off (via **`ve-list-work`**, on the epic branch) — reports merged vs in-development stories and moves ve-tested merged stories to 🧪 Ready for Testing

**Outputs**: Per-story manual test plans and AC→test-case coverage matrices

### OPERATIONS PHASE
**Purpose**: Deployment and operational readiness  
**Focus**: How to DEPLOY and RUN it  
**Location**: `operations/` directory

**Stages**:
- Operations (PLACEHOLDER)

**Outputs**: Build instructions, deployment guides, monitoring setup, verification procedures

---

## Workflow Stages

### Always-Execute Stages
- **Workspace Detection**: Initial analysis of workspace state and project type
- **Requirements Analysis**: Gathering requirements (depth varies based on complexity)
- **User Stories**: Creating user stories and personas in a single pass; populates the Story Tracker; the generated story set is gated by GATE 1 (mandatory human approval) before it pushes to the configured tracker
- **Dependency Graph**: Mapping each story's `requires` dependencies so independent stories can run in parallel; writes `dependency-graph.yml`
- **Workflow Planning**: Creating execution plan for which phases to run
- **Code Generation**: Per-story, triggered by `dev-implement` — Story Selection → story branch → Part 1 (Planning) → Part 2 (Generation) → unit tests to `unitTestCoverageMin` coverage

### ve-Initiated Stages (parallel track — never auto-run)
- **Test Plan**: Per story, via `/ve-implement` — manual test steps generated from the story's acceptance criteria into `.spec/aire-docs/tests/<TICKET-ID>-<title>/`; runs alongside development, reads no application code
- **ve Sign-off**: Via `ve-list-work` on the epic branch — merged, ve-tested stories → 🧪 Ready for Testing

### Conditional Stages
- **Reverse Engineering**: Analyzing existing codebase (brownfield projects only)
- **Application Design**: Designing application components, methods, business rules, and services
- **Functional Design**: Technology-agnostic business logic design (system-level)
- **NFR Requirements**: Determining NFRs and selecting tech stack (system-level)
- **NFR Design**: Incorporating NFR patterns and logical components (system-level)
- **Infrastructure Design**: Mapping to actual infrastructure services (system-level)

### Automatic-in-Workflow Stages (also invokable standalone)
- **Code Review** (`code-review`): Read-only review of a story's code, or all stories together; produces a versioned report. Auto-runs after every code generation, where its verdict routes the run
- **Remediate** (`remediate`): Fixes issues from a review report (fix → unit test → green, running only the in-scope story's unit tests); annotates the report in place. Auto-runs on any review finding, looping with the review until the verdict is clean. Standalone runs stay confirm-first

## Application Design Terms

- **Component**: A functional system with specific responsibilities
- **Method**: A function or operation within a component with defined business rules
- **Business Rule**: Logic that governs method behavior and validation
- **Service**: Orchestration layer that coordinates business logic across components
- **Component Dependency**: Relationship and communication pattern between components

## Architecture Terms (Infrastructure)

### Service
An independently deployable component in a microservices architecture. Each service is separately deployable.

**Usage**: "The Payment Service handles all payment processing"

### Module
A logical grouping of functionality within a single service or monolith. Modules are not independently deployable.

**Usage**: "The authentication module within the User Service"

### Component
A reusable building block within a service or module. Components are classes, functions, or packages that provide specific functionality.

**Usage**: "The EmailValidator component validates email addresses"

## Development & Tracking Terms

### Story Tracker
A table in `.spec/aire-docs/aire-state.md` (section `## Story Tracker`) with one row per user story: Story ID, Title, Requires, Tracker ID, Status, PR, Merged, Start, End, Recorded. It is the single source of truth for story status. The ONLY valid statuses are `🟢 Ready for Development` (initial), `🔵 In Development` (picked via `dev-implement`, held through code generation, Code Review, Remediate, the PR raise, and the auto PR review), and `🧪 Ready for Testing` (only after the story's PR is **merged** into the epic branch). The `PR` column stores the PR URL (set when the PR is raised) and `Merged` is `no`/`yes`. Rows are created in User Stories, `Requires` filled by Dependency Graph; the `🟢→🔵` transition is driven by `dev-implement`, and the `🔵→🧪` transition happens after the PR merges, when ve signs the story off via `ve-list-work`. Code Review and Remediate do not change status.

### Tracker / Tracker Type
The issue tracker aire was configured to use for a given project — **JIRA**, **ADO** (Azure DevOps Boards), **GITHUB** (Issues/Projects), or **LOCAL** (no external tracker; the Story Tracker in `aire-state.md` is authoritative). Selected ONCE, at workflow start, and recorded in `## Tracker` in `aire-state.md` (`Type`, Parent Epic, Epic URL, Project Key / Repo / Org). Every tracker-facing mechanic in the framework (issue creation, status transitions, assignment, epic linking, causation links, comments) dispatches on this value — see `common/tracker-sync.md`, the single source of truth for the actual per-tracker commands. LOCAL is a complete, first-class mode, not a degraded one.

### Tracker ID
The identifier a story or ticket has in the configured tracker: a Jira key (`PROJ-123`), an ADO work item ID, a GitHub issue number, or `LOCAL` (or a locally-minted `BUG-LOCAL-N`/`ENH-LOCAL-N`) when no external tracker is configured. Stored in the Story Tracker's `Tracker ID` column and in `dependency-graph.yml`'s `tracker_id:` field.

### Ready Story
A story whose `requires` prerequisites are ALL `🧪 Ready for Testing` (or that has none). Ready stories have no dependencies on each other's in-progress work and can be implemented **in parallel** by different developers. Determined from the Dependency Graph at selection time (the Doability Gate).

### Dependency Graph
The Planning stage (run right after User Stories) that computes each story's `requires` dependencies. Outputs `.spec/aire-docs/planning/dependency-graph.yml` and a `## Dependency Graph` section (Mermaid + ready-stories summary) in `aire-state.md`.

### Parent Epic
The **existing** Epic (or equivalent — a GitHub Milestone/tracking issue, an ADO Epic work item, or a locally-described Epic for LOCAL) the user provides at workflow start (e.g., "using aire" + an Epic link **whose description defines what to build**). At capture time its summary/description/acceptance criteria are fetched into `.spec/aire-docs/planning/requirements/epic-brief.md` (primary input to Requirements Analysis and User Stories), and its ID/URL/Project Key are recorded in `.spec/aire-docs/aire-state.md` under `## Tracker` so any session — including a new chat resuming at the story stage — can find it. Every story pushed to the configured tracker during User Stories Part 3 is linked to this Parent Epic (unless the user chose `none` at push time, or the tracker is LOCAL). aire never creates Epics itself;

### `dev-implement` (keyword)
The keyword a developer types to build a single story. It triggers per-story Code Generation: Story Selection (moves the story `🟢 Ready for Development` → `🔵 In Development`) → Doability Gate (all `requires` `🧪 Ready for Testing`) → story branch cut from the Epic branch (`common/branching-strategy.md`) → code generation → unit tests generated + run to `unitTestCoverageMin` coverage → automated Code Review, whose verdict routes the run automatically (findings are auto-remediated and re-reviewed until clean — no approval is requested) → PR raised into the Epic branch. Raising the PR does NOT promote the story — it **stays `🔵 In Development`** (with the `PR` URL recorded and `Merged=no`). It moves to `🧪 Ready for Testing` only once that PR is **merged** into the Epic branch AND the ve signs it off via the `ve-list-work` skill (Option B); `dev-implement` never performs that promotion. See `workflows/dev-implement.md`.

### `team_size`
The assumed number of developers, **fixed at 2 and NEVER asked**. Drives story granularity so ≥ 2 independent stories are workable in parallel at any time. Written to `aire-state.md` by User Stories Part 1 and reused as-is by the Dependency Graph stage. If the user volunteers a different number, honour it as an interrupt.

## Terminology Guidelines

### When to Use Each Term

**Service**:
- When referring to independently deployable components
- In microservices architecture contexts
- In deployment and infrastructure discussions
- Example: "The Order Service will be deployed to ECS"

**Module**:
- When referring to logical groupings within a service
- In monolith architecture contexts
- When discussing internal organization
- Example: "The reporting module generates all reports"

**Component**:
- When referring to specific classes, functions, or packages
- In design and implementation discussions
- When discussing reusable building blocks
- Example: "The DatabaseConnection component manages connections"

## Stage Terminology

### Planning vs Generation
- **Planning**: Creating a plan with questions and checkboxes for execution
- **Generation**: Executing the plan to create artifacts

Examples (these are internal sub-steps within a single stage, not separate stages):
- Story Planning → Story Generation (within User Stories stage)
- NFR Planning → NFR Generation (within NFR Requirements stage)
- Code Generation Part 1 (Planning) → Code Generation Part 2 (Generation)

### Depth Levels
- **Minimal**: Quick, focused execution for simple changes
- **Standard**: Normal depth with standard artifacts for typical projects
- **Comprehensive**: Full depth with all artifacts for complex/high-risk projects

## Artifact Types

### Plans
Documents with checkboxes and questions that guide execution.
- Located in `.spec/aire-docs/plans/`
- Examples: `story-generation-plan.md`, `functional-design-plan.md`

### Artifacts
Generated outputs from executing plans.
- Located in various `.spec/aire-docs/` subdirectories
- Examples: `requirements.md`, `stories.md`, `design.md`

### State Files
Files tracking workflow progress and status.
- `aire-state.md`: Overall workflow state
- `audit.md`: Complete audit trail of all interactions

## Common Abbreviations

- **NFR**: Non-Functional Requirements
- **API**: Application Programming Interface
- **CDK**: Cloud Development Kit (AWS)
- **SAST**: Static Application Security Testing (D3 — scans your code for dangerous patterns)
- **SCA**: Software Composition Analysis (D4 — scans dependencies for known vulnerabilities)
- **OWASP**: Open Worldwide Application Security Project
- **SH-LOOP**: Self-Healing Loop (the 3-attempt repair budget per gate type)
