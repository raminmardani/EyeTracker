# Reverse Engineering

**Purpose**: Analyze existing codebase and generate comprehensive design artifacts

**Execute when**: Brownfield project detected (existing code found in workspace)

**Skip when**: Greenfield project (no existing code)

**Rerun behavior**: Rerun is controlled by workspace-detection.md. If existing reverse engineering artifacts are found and are still current, they are loaded and reverse engineering is skipped. If artifacts are stale (older than the codebase's last significant modification) or the user explicitly requests a rerun, reverse engineering executes again to ensure artifacts reflect current code state

## Monorepo Handling — Root-Level, Single Pass

**CRITICAL**: In a monorepo (multiple modules/packages under one workspace root), reverse engineering executes **ONCE at the workspace root**, covering ALL modules in a single pass:

- **One artifact set**: All artifacts are generated at `.spec/aire-docs/planning/reverse-engineering/` (the ROOT reverse engineering documents). NEVER generate separate per-module reverse engineering document sets.
- **Module detail lives inside the root docs**: each module/package gets its own component-level sections within `business-overview.md`, `architecture.md`, `code-structure.md`, `component-inventory.md`, and `dependencies.md`.
- **All modules reuse the root artifacts**: every downstream stage (Requirements Analysis, User Stories, design stages, `dev-implement`), regardless of which module a story touches, loads the SAME root artifacts. Do NOT re-run reverse engineering per module or per story.
- **Keeping root docs current**: changes introduced by an epic's development are captured as **delta reverse engineering artifacts** (by the `archive-epic` skill, on the epic branch) and **stitched into the root documents** after the epic PR merges (by the `stitch-delta` skill, on the base branch) — see "Delta Reverse Engineering & Stitching" below.

## Standalone Invocation — `reverse-engineering-root` Skill

This stage can also be invoked standalone (outside the main workflow) via the **`reverse-engineering-root`** skill:

- **When**: (a) upfront, before starting a new epic cycle, to create the root artifacts once for all modules; (b) **RECOMMENDED: post release cycle**, after `archive-epic` has archived the previous epic, to regenerate fresh root artifacts from the released codebase.
- **Mode differences in standalone runs**:
  - If `.spec/aire-docs/` does not exist yet, create the minimal structure (`.spec/aire-docs/planning/reverse-engineering/`, `audit.md` with an `# Audit Log` header) before Step 1.
  - Execute Steps 1–12 exactly as written. In Step 12, replace the "proceed to **Requirements Analysis**" option with "✅ **Approve & Finish** — artifacts are ready for all modules to use"; the skill ends after approval (Step 13).
  - If artifacts already exist, this is a refresh: regenerate all artifacts against the current code state and update the timestamp file. Remove any stale `delta/` subfolder — its contents were already stitched and archived by `archive-epic`; a leftover delta must never be stitched twice.
- Log the standalone invocation and completion in `.spec/aire-docs/audit.md` as with any stage.

## Context Project Folder (root, human-curated — scaffolded here)

As its **very first step** (before Step 1, in BOTH the inline stage and the standalone `reverse-engineering-root` skill), this stage ensures a **`.spec/context-project/existing-knowledge/` folder exists** (inside `.spec/`, a sibling of `.spec/aire-docs/`):

- **Check first, create only if missing**: test whether `.spec/context-project/existing-knowledge/` already exists. **If it already exists** (e.g. left by an earlier run, or already curated by the team) — **reuse it AS-IS**: do NOT recreate, empty, overwrite, or delete it or anything under it. **Only if it is absent**, create an empty `.spec/context-project/existing-knowledge/` folder. **Do NOT create a README inside it** — humans curate its contents.
- **What it is for**: a human-authored home for **knowledge about the CURRENT project** — how the existing system works, where things live, what each module does (e.g. an `interview.md` explaining a module's behavior and layout). This is context about what already exists, NOT requirements for the new work (those come from the Epic). The framework never auto-populates it.
- **Convention**: one subfolder per repo module, named **exactly** after the module (e.g. for a repo `ALIX_DX` containing `ALIX.BMS`, create `.spec/context-project/existing-knowledge/ALIX.BMS/` and place its `interview.md` etc. there).
- **How it is used**: it is read **only when the user opts in** at workflow start (Workspace Detection asks "Are there any context-project artifacts I should use for this task?") and **only at the exact path the user pastes** — Requirements Analysis and Workflow Planning then consult that path as background context about the existing system. Nothing under `.spec/context-project/existing-knowledge/` is auto-scanned.

When writing the reverse engineering artifacts, note in `code-structure.md` (or the workspace-layout section of `architecture.md`) that a `.spec/context-project/existing-knowledge/` folder is present and is used as human-curated context input to the AIRE workflow — so it is not mistaken for application source.

## Accuracy Rules — Apply to ALL Artifact Writing

These rules govern BOTH root artifact generation (Steps 2–9 below, including standalone `reverse-engineering-root` runs) AND delta generation/stitching at release end — every reverse engineering document, whichever path writes it:

- **🔴 Ground truth is the code at HEAD, not documents**: before writing ANY factual claim into an artifact (a file/export/route exists, a convention is followed, an element is unused/removed, a token/pattern is used), verify it by reading or grepping the actual code. Prior documents — story summaries, design docs, earlier baselines — record *intent* or *past state*; NEVER treat them as evidence about the current code.
- **🔴 Measured facts must be measured**: every quantitative claim (test totals, pass/fail counts, file counts, page counts, import counts, coverage) MUST be produced by running the real command at writing time — e.g. run the test suite and copy its reported `Tests N passed (M)` totals; use `grep -rl ... | wc -l` for file counts. NEVER sum, estimate, or carry numbers forward from other documents. Where practical, record the command next to the figure so the next run can reproduce the measurement.

A regenerated baseline is only the "highest-fidelity correction" if these rules were followed while writing it — they are not optional in any path.

## Step 1: Multi-Package Discovery

### 1.1 Scan Workspace
- All packages (not just mentioned ones)
- Package relationships via config files
- Package types: Application, CDK/Infrastructure, Models, Clients, Tests

### 1.2 Understand the Business Context
- The core business that the system is implementing overall
- The business overview of every package
- List of Business Transactions that are implemented in the system

### 1.3 Infrastructure Discovery
- CDK packages (package.json with CDK dependencies)
- Terraform (.tf files)
- CloudFormation (.yaml/.json templates)
- Deployment scripts

### 1.4 Build System Discovery
- Build systems: Brazil, Maven, Gradle, npm
- Config files for build-system declarations
- Build dependencies between packages

### 1.5 Service Architecture Discovery
- Lambda functions (handlers, triggers)
- Container services (Docker/ECS configs)
- API definitions (Smithy models, OpenAPI specs)
- Data stores (DynamoDB, S3, etc.)

### 1.6 Code Quality Analysis
- Programming languages and frameworks
- Test coverage indicators
- Linting configurations
- CI/CD pipelines

## Step 2: Generate Business Overview Documentation

Create `.spec/aire-docs/planning/reverse-engineering/business-overview.md`:

```markdown
# Business Overview

## Business Context Diagram
[Mermaid diagram showing the Business Context]

## Business Description
- **Business Description**: [Overall Business description of what the system does]
- **Business Transactions**: [List of Business Transactions that the system implements and their descriptions]
- **Business Dictionary**: [Business dictionary terms that the system follows and their meaning]

## Component Level Business Descriptions
### [Package/Component Name]
- **Purpose**: [What it does from the business perspective]
- **Responsibilities**: [Key responsibilities]
```

## Step 3: Generate Architecture Documentation

Create `.spec/aire-docs/planning/reverse-engineering/architecture.md`:

```markdown
# System Architecture

## System Overview
[High-level description of the system]

## Architecture Diagram
[Mermaid diagram showing all packages, services, data stores, relationships]

## Component Descriptions
### [Package/Component Name]
- **Purpose**: [What it does]
- **Responsibilities**: [Key responsibilities]
- **Dependencies**: [What it depends on]
- **Type**: [Application/Infrastructure/Model/Client/Test]

## Data Flow
[Mermaid sequence diagram of key workflows]

## Integration Points
- **External APIs**: [List with purposes]
- **Databases**: [List with purposes]
- **Third-party Services**: [List with purposes]

## Infrastructure Components
- **CDK Stacks**: [List with purposes]
- **Deployment Model**: [Description]
- **Networking**: [VPC, subnets, security groups]
```

## Step 4: Generate Code Structure Documentation

Create `.spec/aire-docs/planning/reverse-engineering/code-structure.md`:

```markdown
# Code Structure

## Build System
- **Type**: [Maven/Gradle/npm/Brazil]
- **Configuration**: [Key build files and settings]

## Key Classes/Modules
[Mermaid class diagram or module hierarchy]

### Existing Files Inventory
[List all source files with their purposes - these are candidates for modification in brownfield projects]

**Example format**:
- `[path/to/file]` - [Purpose/responsibility]

## Design Patterns
### [Pattern Name]
- **Location**: [Where used]
- **Purpose**: [Why used]
- **Implementation**: [How implemented]

## Critical Dependencies
### [Dependency Name]
- **Version**: [Version number]
- **Usage**: [How and where used]
- **Purpose**: [Why needed]
```

## Step 5: Generate API Documentation

Create `.spec/aire-docs/planning/reverse-engineering/api-documentation.md`:

```markdown
# API Documentation

## REST APIs
### [Endpoint Name]
- **Method**: [GET/POST/PUT/DELETE]
- **Path**: [/api/path]
- **Purpose**: [What it does]
- **Request**: [Request format]
- **Response**: [Response format]

## Internal APIs
### [Interface/Class Name]
- **Methods**: [List with signatures]
- **Parameters**: [Parameter descriptions]
- **Return Types**: [Return type descriptions]

## Data Models
### [Model Name]
- **Fields**: [Field descriptions]
- **Relationships**: [Related models]
- **Validation**: [Validation rules]
```

## Step 6: Generate Component Inventory

Create `.spec/aire-docs/planning/reverse-engineering/component-inventory.md`:

```markdown
# Component Inventory

## Application Packages
- [Package name] - [Purpose]

## Infrastructure Packages
- [Package name] - [CDK/Terraform] - [Purpose]

## Shared Packages
- [Package name] - [Models/Utilities/Clients] - [Purpose]

## Test Packages
- [Package name] - [Integration/Load/Unit] - [Purpose]

## Total Count
- **Total Packages**: [Number]
- **Application**: [Number]
- **Infrastructure**: [Number]
- **Shared**: [Number]
- **Test**: [Number]
```

## Step 7: Generate Technology Stack Documentation

Create `.spec/aire-docs/planning/reverse-engineering/technology-stack.md`:

```markdown
# Technology Stack

## Programming Languages
- [Language] - [Version] - [Usage]

## Frameworks
- [Framework] - [Version] - [Purpose]

## Infrastructure
- [Service] - [Purpose]

## Build Tools
- [Tool] - [Version] - [Purpose]

## Testing Tools
- [Tool] - [Version] - [Purpose]
```

## Step 8: Generate Dependencies Documentation

Create `.spec/aire-docs/planning/reverse-engineering/dependencies.md`:

```markdown
# Dependencies

## Internal Dependencies
[Mermaid diagram showing package dependencies]

### [Package A] depends on [Package B]
- **Type**: [Compile/Runtime/Test]
- **Reason**: [Why dependency exists]

## External Dependencies
### [Dependency Name]
- **Version**: [Version]
- **Purpose**: [Why used]
- **License**: [License type]
```

## Step 9: Generate Code Quality Assessment

Create `.spec/aire-docs/planning/reverse-engineering/code-quality-assessment.md`:

```markdown
# Code Quality Assessment

## Test Coverage
- **Overall**: [Percentage or Good/Fair/Poor/None]
- **Unit Tests**: [Status]
- **Integration Tests**: [Status]

## Code Quality Indicators
- **Linting**: [Configured/Not configured]
- **Code Style**: [Consistent/Inconsistent]
- **Documentation**: [Good/Fair/Poor]

## Technical Debt
- [Issue description and location]

## Patterns and Anti-patterns
- **Good Patterns**: [List]
- **Anti-patterns**: [List with locations]
```

## Step 10: Create Timestamp File

Create `.spec/aire-docs/planning/reverse-engineering/reverse-engineering-timestamp.md`:

```markdown
# Reverse Engineering Metadata

**Analysis Date**: [ISO timestamp]
**Analyzer**: aire
**Workspace**: [Workspace path]
**Analyzed At Commit**: [git HEAD SHA at analysis time, or N/A if not a git repo]
**Total Files Analyzed**: [Number]

## Artifacts Generated
- [x] business-overview.md
- [x] architecture.md
- [x] code-structure.md
- [x] api-documentation.md
- [x] component-inventory.md
- [x] technology-stack.md
- [x] dependencies.md
- [x] code-quality-assessment.md
```

## Step 11: Update State Tracking

Update `.spec/aire-docs/aire-state.md`:

```markdown
## Reverse Engineering Status
- [x] Reverse Engineering - Completed on [timestamp]
- **Artifacts Location**: .spec/aire-docs/planning/reverse-engineering/
```

## Step 12: Present Completion Message to User

```markdown
# 🔍 Reverse Engineering Complete

[AI-generated summary of key findings from analysis in the form of bullet points]

> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the reverse engineering artifacts at: `.spec/aire-docs/planning/reverse-engineering/`

> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the reverse engineering analysis if required
> ✅ **Approve & Continue** - Approve analysis and proceed to **Requirements Analysis**
```

## Step 13: Wait for User Approval

- **MANDATORY**: Do not proceed until user explicitly approves
- **MANDATORY**: Log user's response in audit.md with complete raw input

---

## Delta Reverse Engineering & Stitching (End of Release Cycle)

**Purpose**: Keep the root reverse engineering documents current without a full re-analysis. The changes an epic's development introduced are captured as a **delta** and **stitched into the root documents**. Split across two skills — NOT during the normal Planning pass above:

- **Delta Generation** — executed by the **`archive-epic`** skill on the epic branch at the end of a release cycle (see `agents/archive-epic-agent.md`). The delta rides the epic's PR to the base branch.
- **Stitching** — executed by the **`stitch-delta`** skill on the BASE branch, AFTER the epic PR merges (see `agents/stitch-delta-agent.md`). Root docs are NEVER stitched on epic branches: with N parallel epics, per-branch stitching would put N divergent versions of the same root docs into N PRs — guaranteed merge conflicts. Epic-namespaced delta folders + post-merge stitching on current main make conflicts impossible by implementation.

### Delta Generation

Analyze what changed since the root artifacts were produced, using (in priority order):
1. **Git history**: `git log --name-status <analyzed_at_commit>..HEAD` (fall back to `git log --since="<Analysis Date>"` if no commit SHA was recorded)
2. **Story summaries**: `.spec/aire-docs/implementation/code/story-*-summary.md`
3. **Story Tracker** in `aire-state.md` (which stories shipped) and design artifacts under `.spec/aire-docs/implementation/design/`

**🔴 The Accuracy Rules (top of this file) apply in full here.** Delta-specific emphasis: sources 2–3 above record *intent*; the codebase at HEAD is the *source of truth*. Claims about **pre-existing** code ("follows the existing X convention", "pages already import Y") MUST be verified against the existing code itself — NEVER inferred from the epic's own documents, which describe only what the epic did. Every figure is re-measured at delta-generation time — never carried forward from story summaries or the baseline documents.

Write the delta artifacts to the **epic-namespaced** folder `.spec/aire-docs/planning/reverse-engineering/delta/<EPIC-ID>-<epic-name-slug>/` (🔴 MANDATORY — namespacing is what lets N parallel epics' deltas coexist without merge conflicts; never write directly under `delta/`, never touch another epic's folder):

- `delta-summary.md` — epic key/name, date range, commits covered, stories covered, and a per-root-document list of additions/modifications/removals
- One `delta-<artifact>.md` per affected root document (e.g., `delta-architecture.md`, `delta-api-documentation.md`) containing ONLY the changed sections, written in the same section format as the corresponding root document

### Stitching Rules

**Executed ONLY by the `stitch-delta` skill on the base branch post-merge.** Before stitching, check the ledger `.spec/aire-docs/planning/reverse-engineering/stitch-epic.md` — a delta recorded there is already stitched and MUST be skipped (idempotency). Pending deltas are stitched one at a time, in the order their folders landed on the base branch.

Merge each `delta-<artifact>.md` into its root document, section by section:

- **New elements** (components, endpoints, models, dependencies, transactions): ADD as new sections in the matching format
- **Modified elements**: UPDATE the existing section in place — never duplicate a section
- **Removed elements**: DELETE the section (note the removal in `delta-summary.md`)
- **Diagrams**: regenerate affected Mermaid diagrams to include the changes; VALIDATE syntax per `common/content-validation.md` before writing
- **Recount derived metrics**: the "only touch delta-identified sections" rule protects prose, but it lets codebase-wide statistics in OTHER sections go stale (e.g. "imported by N of M pages", "~K files with hardcoded colours"). After section-merging, scan ALL root documents for counts/statistics, re-run each measurement against HEAD, and update stale values — noting each recount in `delta-summary.md`
- 🔴 NEVER blind-overwrite a whole root document during stitching — only touch sections the delta identifies (derived-metric recounts above are the one exception)
- 🔴 NEVER stitch without recording the operation (below)

### Record the Stitch

Record EACH stitched delta in TWO places, immediately after stitching it (before starting the next delta):

1. **The ledger** — append a row to `.spec/aire-docs/planning/reverse-engineering/stitch-epic.md` (create with header if missing; header and column definitions per `agents/stitch-delta-agent.md` — `Cycle` is `epic` or `bug`, `Tracker Item` is the cycle's tracker ID, in whichever tracker was configured for it):

```markdown
| Cycle | Tracker Item | Delta Folder | Stitched At | Commit Range | Documents Updated |
|-------|--------------|--------------|-------------|--------------|-------------------|
| epic  | [EPIC-ID]    | delta/<EPIC-ID>-<epic-name-slug>/ | [ISO timestamp] | [commit range] | [documents updated] |
| bug   | [BUG-ID]     | delta/<BUG-ID>-<slug>/            | [ISO timestamp] | [commit range] | [documents updated] |
```

If an existing ledger still uses the old format (`| Epic | Delta Folder | ... |`), migrate it first per the migration rule in `agents/stitch-delta-agent.md` Step 2.

2. **Stitch History** — append to `reverse-engineering-timestamp.md`:

```markdown
## Stitch History
- **[ISO timestamp]** — Epic [EPIC-KEY] ([Epic name]) delta stitched. Commits: [range]. Documents updated: [list]
```

After the last pending delta, update **Analyzed At Commit** to the current `HEAD` SHA (the root docs now reflect this commit). Log the stitch in audit.md. 🔴 NEVER stitch a delta whose ledger row already exists.

> **Post-release recommendation**: after `archive-epic` completes, run the **`reverse-engineering-root`** skill to fully regenerate the root artifacts from the released codebase. Stitching keeps documents usable between cycles; a full post-release regeneration is the highest-fidelity baseline for the next epic.
