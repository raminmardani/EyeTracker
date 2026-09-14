# aire Adaptive Workflow Overview

**Purpose**: Technical reference for AI model and developers to understand complete workflow structure.

**Note**: Similar content exists in welcome-message.md (user welcome message) and README.md (documentation). This duplication is INTENTIONAL - each file serves a different purpose:
- **This file**: Detailed technical reference with Mermaid diagram for AI model context loading
- **welcome-message.md**: User-facing welcome message with ASCII diagram
- **README.md**: Human-readable documentation for repository

## The Three-Phase Lifecycle:
• **PLANNING PHASE**: Planning and architecture (Workspace Detection → Requirements → User Stories → Dependency Graph → Workflow Planning → Application Design)
• **IMPLEMENTATION PHASE**: System-level design → 🛑 STOP → per-story Code Generation via `dev-implement` (on a story branch cut from the Epic branch; code, then unit tests to `unitTestCoverageMin` coverage, then — when the story touches an API layer — the API & Contract Testing Gate) → optional Code Review & Remediate
• **OPERATIONS PHASE**: Placeholder for future deployment and monitoring workflows

**🧪 ve TRACK (parallel, NOT part of any phase)**: **Test Plan belongs to ve, not to Implementation** — neither at epic level nor at story level. ve runs **`/ve-implement`** per story, at the same time as development, to generate that story's manual test steps from its acceptance criteria (no code is read) into `.spec/aire-docs/tests/<TICKET-ID>-<title>/`, and **`ve-list-work`** on the epic branch to move merged, tested stories to 🧪 Ready for Testing.

## The Adaptive Workflow:
• **Workspace Detection** (always; captures the Parent Epic link if provided, in whichever tracker was selected) → **Reverse Engineering** (brownfield only) → **Requirements Analysis** (always, adaptive depth) → **User Stories** (always; no team-size or creation-mode question — `team_size` is fixed at 2, all stories generated at once; the set requires explicit human approval — GATE 1 — then pushes to the configured tracker AUTOMATICALLY, linked to the Parent Epic) → **Dependency Graph** (always; assigns `requires`) → **Workflow Planning** (always) → **Application Design** (conditional) → **System-Level Design** (conditional; single pass) → 🛑 **STOP** → **Code Generation** (per-story, via `dev-implement`, on story branches cut from the Epic branch, with unit tests to `unitTestCoverageMin` coverage plus — when the story touches an API layer — the API & Contract Testing Gate, and NO approval gates) → **Code Review & Remediate** (automatic inside every implement workflow — review, auto-fix findings, re-review until clean; also invokable standalone, story-wise or all stories). Running alongside from the moment stories exist: the **ve track** — **`/ve-implement`** (Test Plan per story) and **`ve-list-work`**.

## How It Works:
• **AI analyzes** your request, workspace, and complexity to determine which stages are needed
• **These stages always execute**: Workspace Detection (incl. automatic Epic branch creation), Requirements Analysis (adaptive depth), User Stories (fixed team_size 2, all-at-once generation, GATE 1 human approval, then automatic push to the configured tracker), Dependency Graph (`requires`), Workflow Planning, Code Generation (per-story via `dev-implement`, with unit tests to `unitTestCoverageMin` coverage, plus the API & Contract Testing Gate when the story touches an API layer)
• **All other stages are conditional**: Reverse Engineering, Application Design, system-level design stages (Functional Design, NFR Requirements, NFR Design, Infrastructure Design)
• **Optional, user-initiated**: Code Review and Remediate — independently invokable at any time for a specific story or all stories together (`code-review`, `remediate`)
• **ve-initiated, parallel to everything above**: `/ve-implement` (Test Plan, per story) and `ve-list-work` (merged, tested stories → Ready for Testing). Never auto-run — ve types them.
• **Mandatory STOP**: after the design stages and before any code generation, the workflow halts — code is generated per-story only when the user types `dev-implement`
• **No fixed sequences**: Stages execute in the order that makes sense for your specific task

## Your Team's Role:
• **Answer questions** in dedicated question files using [Answer]: tags with letter choices (A, B, C, D, E)
• **Option E available**: Choose "Other" and describe your custom response if provided options don't match
• **Work as a team** to review and approve each phase before proceeding
• **Collectively decide** on architectural approach when needed
• **Important**: This is a team effort - involve relevant stakeholders for each phase

## aire Three-Phase Workflow:

```mermaid
flowchart TD
    Start(["User Request"])
    
    subgraph PLANNING["🔵 PLANNING PHASE"]
        WD["Workspace Detection<br/><b>ALWAYS</b>"]
        RE["Reverse Engineering<br/><b>CONDITIONAL</b>"]
        RA["Requirements Analysis<br/><b>ALWAYS</b>"]
        Stories["User Stories<br/>(all-at-once + GATE 1)<br/><b>ALWAYS</b>"]
        DG["Dependency Graph<br/>(requires)<br/><b>ALWAYS</b>"]
        WP["Workflow Planning<br/><b>ALWAYS</b>"]
        AppDesign["Application Design<br/><b>CONDITIONAL</b>"]
    end
    
    subgraph IMPLEMENTATION["🟢 IMPLEMENTATION PHASE"]
        FD["Functional Design<br/><b>CONDITIONAL</b>"]
        NFRA["NFR Requirements<br/><b>CONDITIONAL</b>"]
        NFRD["NFR Design<br/><b>CONDITIONAL</b>"]
        ID["Infrastructure Design<br/><b>CONDITIONAL</b>"]
        STOP["🛑 STOP — use dev-implement<br/><b>MANDATORY HALT</b>"]
        CG["Code Generation<br/>per-story + unit tests ≥ `unitTestCoverageMin`<br/><b>dev-implement</b>"]
        CR["Code Review / Remediate<br/><b>OPTIONAL</b>"]
    end
    
    subgraph veTRACK["🧪 ve TRACK — parallel, not a phase"]
        BT["Test Plan<br/>per story, manual steps from AC<br/><b>/ve-implement</b>"]
        QS["ve Sign-off<br/>merged + tested → Ready for Testing<br/><b>ve-list-work</b>"]
    end
    
    subgraph OPERATIONS["🟡 OPERATIONS PHASE"]
        OPS["Operations<br/><b>PLACEHOLDER</b>"]
    end
    
    Start --> WD
    WD -.-> RE
    WD --> RA
    RE --> RA
    
    RA --> Stories
    Stories --> DG
    DG --> WP
    
    WP -.-> AppDesign
    AppDesign -.-> FD
    WP -.-> FD
    FD -.-> NFRA
    NFRA -.-> NFRD
    NFRD -.-> ID
    ID --> STOP
    WP --> STOP
    STOP -->|user types dev-implement| CG
    CG -.->|repeat per story| CG
    CG -.-> CR
    Stories -.->|ve starts in parallel| BT
    BT -.->|repeat per story| BT
    BT --> QS
    CG --> QS
    QS -.-> OPS
    QS --> End(["Complete"])
    
    style WD fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RA fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style Stories fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style DG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style WP fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style STOP fill:#E53935,stroke:#B71C1C,stroke-width:3px,color:#fff
    style CG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style BT fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style QS fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style CR fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style OPS fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style RE fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style AppDesign fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style FD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRA fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style NFRD fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style ID fill:#FFA726,stroke:#E65100,stroke-width:3px,stroke-dasharray: 5 5,color:#000
    style PLANNING fill:#BBDEFB,stroke:#1565C0,stroke-width:3px, color:#000
    style IMPLEMENTATION fill:#C8E6C9,stroke:#2E7D32,stroke-width:3px, color:#000
    style veTRACK fill:#B2DFDB,stroke:#00695C,stroke-width:3px, color:#000
    style OPERATIONS fill:#FFF59D,stroke:#F57F17,stroke-width:3px, color:#000
    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    
    linkStyle default stroke:#333,stroke-width:2px
```

**Stage Descriptions:**

**🔵 PLANNING PHASE** - Planning and Architecture
- Workspace Detection: Analyze workspace state and project type (ALWAYS)
- Reverse Engineering: Analyze existing codebase (CONDITIONAL - Brownfield only)
- Requirements Analysis: Gather and validate requirements (ALWAYS - Adaptive depth)
- User Stories: Create user stories and personas (all in one pass, `team_size` fixed at 2 — neither is asked); populate the Story Tracker; the generated story set requires explicit human approval (GATE 1) before it pushes to the configured tracker, each story linked to the Parent Epic from `aire-state.md` `## Tracker` (ALWAYS)
- Dependency Graph: Record each story's `requires` dependencies so independent stories can be developed in parallel; write dependency-graph.yml (ALWAYS — right after User Stories)
- Workflow Planning: Create execution plan (ALWAYS)
- Application Design: High-level component identification and service layer design (CONDITIONAL)

**🟢 IMPLEMENTATION PHASE** - Design and Implementation
- Functional Design: Detailed business logic design at the system level (CONDITIONAL, system-level)
- NFR Requirements: Determine NFRs and select tech stack (CONDITIONAL, system-level)
- NFR Design: Incorporate NFR patterns and logical components (CONDITIONAL, system-level)
- Infrastructure Design: Map to actual infrastructure services (CONDITIONAL, system-level)
- 🛑 STOP: mandatory halt after the design stages, before any Code Generation
- Code Generation: Per-**story**, triggered by `dev-implement` only — Story Selection (by Tracker ID) → story branch cut from the Epic branch → Part 1 Planning → Part 2 Generation → unit tests generated + run to `unitTestCoverageMin` coverage (ALWAYS, per-story) → API & Contract Testing Gate (MANDATORY WHEN the story touches an API layer — automated tests against the real endpoints: functional, response-code validation, role-based authorization 401/403, error-response validation, request validation, response contract/schema validation) → Full Regression Gate
- Code Review: Review a story's code, or all stories together, read-only, produce a versioned report (OPTIONAL, `code-review`)
- Remediate: Fix issues from a review report (fix → unit test → green, running only the in-scope story's unit tests), annotate the report in place (OPTIONAL, `remediate`)

**🧪 ve TRACK** - Parallel to Implementation, owned by ve (NOT a Implementation stage at epic or story level)
- Test Plan: Per **story**, triggered by **`/ve-implement`** only — resolves one story, reads its acceptance criteria (the configured tracker / `stories.md`), requirements and design artifacts, and writes **manual test steps** for every applicable test plan (integration, E2E, API, contract, security, performance, accessibility — whichever apply; there is no build-verification artifact) into `.spec/aire-docs/tests/<TICKET-ID>-<title>/`. **Never reads application source code** — it runs while the developer is still writing it. Manual test steps only: no test automation, no test execution; it DOES cut its own `ve/...` branch and raise its own PR to carry the docs (ve-initiated, per story)
- ve Sign-off: Triggered by **`ve-list-work`** on the cycle's integration branch (epic branch for epic cycles, bug/enhancement branch for those cycles) — pulls latest, reports which stories/tickets dev has merged (test these) vs still in development, then asks ve which merged-and-tested items to move to 🧪 Ready for Testing and moves exactly those in the Story Tracker and the configured tracker (ve-initiated)
- Playwright Test Automation (opt-in extension): Triggered by **`/playwright-implement`**, once a story's manual UI test steps exist and both its dev/ve PRs have merged — orchestrates Playwright's own Planner/Generator/Healer agents into executable **UI/browser-only** automation. Never touches Story Tracker or tracker status

**🟡 OPERATIONS PHASE** - Placeholder
- Operations: Placeholder for future deployment and monitoring workflows (PLACEHOLDER)

**Key Principles:**
- Phases execute only when they add value
- Each phase independently evaluated
- PLANNING focuses on "what" and "why"
- IMPLEMENTATION focuses on "how" — Test Plan is ve's parallel track, not a Implementation stage
- OPERATIONS is placeholder for future expansion
- Simple changes may skip conditional PLANNING stages
- Complex changes get full PLANNING and IMPLEMENTATION treatment
---

## 🐞 Bug/Defect Flow (variant)

When `aire-state.md` `## Tracker` records `Workflow Type: bug` (started via `ticket-implement <TICKET-ID>` routed to bug, or the direct keyword `bug-fix <TICKET-ID>`, on an existing Bug/Story ticket in whichever tracker is configured — JIRA/ADO/GITHUB, or LOCAL with no ID at all), the lifecycle is the TRIMMED variant defined in `workflows/bug-fix.md` + `workflows/bug-fix-implement.md` — ONE flow with a single break at design-done — the **ve Handoff Break** (`bug-fix.md` Step 9: analysis + design artifacts committed and pushed on the bug branch, the ve told to pull it and run `/ve-implement <TICKET-ID>`, then a yes/no that continues into the fix in the same session, no second keyword) — NOT the epic flow above:
• ONE branch `bug/<TICKET-ID>-<title>` from the base branch (no epic/story branches) • Impact Analysis + line-level AI-Origin Detection via `agents/defect-provenance-analyst.md` (traces each defective line to its introducing commit; may label the ticket `ai-generated-defect`; resolves the originating story/bug/enhancement ticket and links the bug to it as `is caused by` — automatic, no confirmation; JIRA resolves a typed link at runtime, ADO/GITHUB fall back to a comment, LOCAL notes it locally) • ONE story from the ticket, NO Dependency Graph, no tracker story push • no PR at requirements approval — a single `[BUG]` PR to the base branch at the end • baseline + full regression runs around the fix • ticket stays In Development after the PR — ve transitions it via `ve-list-work` Option B run **on the bug branch, before the archive** (never on the base branch; the base branch's only cycle action is `stitch-delta`) • 🔴 **MANUAL archive** — the operator runs `archive-epic` (→ `aire-archives/bugs/<BUG-ID>-<name>/`) once the ve test-plan PR has merged into the bug branch, and before the `[BUG]` PR merges; the workflow NEVER auto-invokes it.
A resumed session MUST check `Workflow Type` FIRST and follow the bug workflow files when it is `bug`.
