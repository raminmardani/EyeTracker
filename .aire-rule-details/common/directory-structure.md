# Directory Structure

**Purpose**: the canonical layout of an AIRE workspace — where application code goes, where specs go,
where documentation goes, and where every stage/skill writes its artifacts.

**Load this file when**: creating any file or folder whose location isn't already fixed by the rule
file you are following, or when you need to locate an existing artifact by convention.

---

## The four roots

An AIRE workspace has exactly four top-level roots that AIRE owns. Everything AIRE writes goes into
one of them. Nothing AIRE writes goes anywhere else.

| Root | Holds | Rule |
|---|---|---|
| `src/` | **ALL application source code** | Greenfield AND brownfield. Never code outside it. |
| `tests/` | All test code: `tests/unit/`, `tests/behavior/` (Gherkin), `tests/e2e/` (Playwright) | Mirrors `src/` structure under `tests/unit/`. |
| `.spec/` | The specs AIRE writes and the docs AIRE writes | The agent's source of truth for WHAT to build. |
| `.evals/` | Thresholds, rubrics and eval runner scripts | The agent's source of truth for WHETHER it built it right. |

Plus one generated integration point: `.github/workflows/` — the CI pipeline AIRE **generates for
this specific project** (see `common/ci-pipeline-generation.md`).

---

## Full layout

```text
<WORKSPACE-ROOT>/
│
├── src/                                  # 💻 ALL APPLICATION CODE — greenfield and brownfield
│   └── [stack-idiomatic structure]       #    layout per code-generation.md; NEVER outside src/
│
├── tests/                                 # 🧪 ALL TEST CODE — never under .spec/
│   ├── unit/                              #    Unit tests (jest / pytest / go test / JUnit)
│   ├── behavior/                          # 🥒 Gherkin execution layer
│   │   ├── test_<work-unit>.py            #    loader — points the runner at the .feature file
│   │   └── steps/                         #    step definitions binding Gherkin to src/
│   └── e2e/                               # 🎭 tests/e2e/ — Playwright, UI projects only
│       ├── seed.spec.ts                   #    ONE shared seed, inside testDir
│       └── <story-slug>/                  #    Generator output, one folder per story
│
├── .spec/                                # 📐 SPECS + DOCUMENTATION — never code
│   ├── architecture.md                   # 🏛️ ONCE per cycle. The system design + Section 10 Verifiable
│   │                                     #    Constraints that derive the blocking J1 rubric.
│   │                                     #    🔴 NEVER one per story.
│   ├── behavior.feature                  # 🥒 ONCE per cycle. Cross-story journeys, @REQ tagged.
│   │                                     #    What the B3 tier runs on the last work unit.
│   ├── context-project/                  # 👤 HUMAN-CURATED INPUT — two subfolders, nothing else.
│   │   ├── existing-knowledge/           #    HUMAN-AUTHORED — how the CURRENT system works:
│   │   │                                 #    module notes, interview.md, where things live.
│   │   │                                 #    Brownfield only; empty on greenfield.
│   │   └── new-references/               #    HUMAN-SUPPLIED — what to BUILD: wireframes,
│   │                                     #    mockups, UI/API specs, architecture diagrams.
│   │                                     #    Greenfield AND brownfield.
│   └── aire-docs/                        # 📄 DOCUMENTATION ONLY
│       ├── planning/                     # 🔵 PLANNING PHASE
│       │   ├── plans/
│       │   ├── reverse-engineering/      #    Brownfield — REUSED FROM ATLAS when Helix MCP is bound
│       │   │   └── knowledge-graph.md    #    once per cycle, never per work unit
│       │   ├── requirements/             #    epic-brief.md, requirements.md
│       │   ├── user-stories/             #    stories.md, personas.md
│       │   ├── application-design/
│       │   └── dependency-graph.yml
│       ├── implementation/               # 🟢 IMPLEMENTATION PHASE
│       │   ├── plans/
│       │   ├── design/                   #    functional / nfr-requirements / nfr-design / infrastructure
│       │   ├── code/
│       │   │   ├── behavior/             # 🥒 ONE .feature per work unit — the only per-unit spec
│       │   │   │   ├── story-1.1.feature
│       │   │   │   ├── story-1.2.feature
│       │   │   │   └── bug-PROJ-123.feature
│       │   │   ├── unit-test-evidence/
│       │   │   ├── behavior-test-evidence/       # per unit: b1/ b2/ b3/
│       │   │   ├── api-contract-test-evidence/
│       │   │   └── eval-evidence/                # eval.json, eval-summary.md, static/, judge/
│       │   └── reviews/
│       ├── tests/                        # 🧪 ve Test Plan — one folder per work unit
│       ├── code-security-reviews/
│       ├── operations/
│       ├── aire-state.md
│       └── audit.md
│
├── .evals/                                # 🎯 EVAL FRAMEWORK — created on the cycle branch if missing
│   ├── config.json                        #    ALL thresholds. The ONLY place a number lives.
│   ├── rubrics/
│   │   ├── architecture-rubric.json       #    derived from .spec/architecture.md every cycle
│   │   └── security-rubric.json           #    OWASP-based, created once
│   ├── behavior/                          # 📦 Gherkin container — same image locally and in CI
│   │   ├── Containerfile                  #    🔴 must be PROVEN to build at bootstrap
│   │   └── run.sh                         #    THE entry point: run.sh <b1|b2|b3>
│   └── scripts/                           #    generated per project, committed, executable
│       ├── run-static-evals.*             #    D1–D7 baseline diff — local AND CI call this
│       ├── run-evals.*                    #    J1/J2 judge via the Claude Code CLI
│       └── auto-fix-agent.*               #    CI self-repair driver
│
├── .github/workflows/
│   └── agentic-eval-pipeline.yml         # ⚙️ GENERATED for this project by ci-pipeline-generation.md
│
├── .aire-rule-details/                   # 📕 THE FRAMEWORK ITSELF (this directory)
│   ├── aire-workflow.md                  #    End-to-end flow diagrams for every cycle type
│   ├── common/                           #    Cross-cutting rules loaded by every stage
│   ├── planning/                         #    🔵 Planning-phase stage rules
│   ├── implementation/                   #    🟢 Implementation-phase stage rules
│   ├── workflows/                        #    Keyword-triggered workflows (dev-implement, …)
│   ├── agents/                           #    Sub-agent procedures
│   ├── extensions/                       #    Opt-in and mandatory rule extensions
│   └── operations/
│
├── aire-archives/                        # 📦 Closed release cycles (archive-epic skill)
│   └── epics|bugs|enhancements/<ID>-<name>/
│       ├── .spec/                        #    EXACT MIRROR of the live .spec/ at cycle close —
│       │                                 #    aire-docs, every work-unit bundle, context-project,
│       │                                 #    new-references. One `cp -R`, no unpacking.
│       └── archive-manifest.md
│
├── playwright.config.*                   # Only when the Playwright extension is enabled
├── .mcp.json                             # MCP servers — incl. the Helix MCP for Atlas access
└── CLAUDE.md                             # Repo guardrails — the agent reads this first
```

---

## 🔴 CRITICAL PLACEMENT RULES

1. **ALL application code lives in `src/`.** Greenfield and brownfield alike. If a brownfield repo
   keeps its code somewhere else, see "Brownfield reconciliation" below — never silently write new
   code into a second location.
2. **`.spec/` is documentation and specification only.** Never a `.ts`, `.py`, `.java` or any other
   source file. It holds four things: **`architecture.md`** and **`behavior.feature`** at its root
   (each written ONCE per cycle after the design stages — 🔴 never one per story), `aire-docs/`, and
   **`context-project/`** — the single human-curated input folder, which has exactly two subfolders:
   `existing-knowledge/` (how the CURRENT system works) and `new-references/` (wireframes, mockups,
   API specs defining the target). 🔴 There is no `context-references/` at the top level — both live
   inside `context-project/`. The framework **creates the folders and reads them only at a path the
   user explicitly supplies** — it never auto-populates them and never auto-scans them. They are
   cross-cycle: `archive-epic`'s option-A reset preserves them in place. The one apparent exception, `<work-unit>.feature`, is a *specification* written in
   Gherkin; its executable step definitions live in `tests/behavior/steps/`.
3. **`.spec/architecture.md` is the architecture source of truth, and there is exactly one.**
   🔴 A work unit never gets its own architecture document — it reads the relevant section of this
   one. The blocking J1 rubric is derived from its Section 10 and from nothing else.
3b. **One `.feature` per work unit is the ONLY per-unit spec file**, under
   `.spec/aire-docs/implementation/code/behavior/`. No per-story requirements, architecture,
   constraints or knowledge-graph documents — that information is already authoritative in
   `stories.md`, `requirements.md`, `architecture.md` and `.evals/config.json`, and copying it per
   story only creates something that can drift.
4. **Test code lives in `tests/`, never in `src/`** unless the stack's own convention is co-location
   (Go `_test.go`, Rust `#[cfg(test)]`), in which case follow the stack.
5. **Evidence is not documentation.** Raw tool output goes under
   `.spec/aire-docs/implementation/code/*-evidence/`, never into a design or requirements document.
6. **Never write outside these roots.** No stray files at the workspace root; no code in
   `.spec/`; no docs in `src/`.

---

## 🔴 ARTIFACT OWNERSHIP — create if missing, never regenerate

**This table is the single authority on which branch writes each generated artifact, and what to do
when it is absent.**

**The rule in one line: if it exists, use it as-is. If it does not exist, create it on the cycle
branch. Nothing is ever pushed to the base branch.**

| Path | Written on | If MISSING |
|---|---|---|
| `.github/workflows/agentic-eval-pipeline.yml` | cycle branch | **Create it** (deterministically) |
| `.evals/config.json` | cycle branch | **Create it** |
| `.evals/scripts/**` | cycle branch | **Create it** |
| `.evals/behavior/**` (Containerfile, run.sh) | cycle branch | **Create it** |
| `.evals/rubrics/security-rubric.json` | cycle branch | **Create it** |
| `.evals/rubrics/architecture-rubric.json` | cycle branch | Derive from `.spec/architecture.md` Section 10 |
| `.spec/**` | cycle branch | Generate during the cycle |
| `src/**`, `tests/**` | work-unit branch | Generate during code generation |

**"Cycle branch"** = the epic branch for an epic cycle, the bug branch for a bug cycle, the
enhancement branch for an enhancement cycle.

### Why nothing is pushed to base

**GitHub runs a `pull_request` workflow from the HEAD branch, not the base.** So the pipeline only
has to exist on the branch raising the PR:

| PR | Head branch has the workflow because | CI runs? |
|---|---|---|
| story → epic | story branches are cut from the epic branch | ✅ |
| ve → epic/bug/enh | cut from the cycle branch | ✅ |
| epic → main | the epic branch created it | ✅ |
| bug → main | the bug cycle created it on the bug branch | ✅ |
| enh → main | the enhancement cycle created it on the enhancement branch | ✅ |

**Base ends up with it anyway, for free** — the cycle's own PR diff includes
`.github/workflows/agentic-eval-pipeline.yml` and `.evals/**`, so merging the cycle lands them on
base. The next cycle then branches from base, finds them present, and leaves them alone.

🔴 **Never push these files directly to the base branch, and never raise a separate `[CI]` PR for
them.** They ride in with the cycle that created them.

### The two rules that make this conflict-free

**1. 🔴 PRESENT → USE AS-IS. Never regenerate, never "refresh", never "upgrade".**
If the file exists — created earlier in this cycle, or inherited by branching from base — it is
correct by definition. The repo's own standards win. Regenerating an existing file is what produces
merge conflicts, and it is forbidden regardless of how stale the file looks. To *change* one
deliberately, do it as an explicit, announced edit and say why.

**2. 🔴 MISSING → CREATE IT on the cycle branch, then move on.**
An absent bootstrap artifact is **never a reason to halt the cycle**. Generate it from the canonical
template, commit it with the cycle's other artifacts, and continue. The gates work immediately.

🔴 **Never stop a cycle because base has not been bootstrapped.** The framework's job is to create
that infrastructure, not to wait for it.

### 🔴 Why concurrent cycles do not collide: DETERMINISM

Two cycles running against an unbootstrapped base will both create these files, and both will merge
into base. That is safe **only if both produce byte-identical content**, so generation must be
deterministic:

- **No timestamps, run ids, hostnames or absolute paths** anywhere in the file.
- **Stable ordering** — JSON keys in the canonical order shown in the template, arrays sorted.
- **Values from fixed sources only** — the template, and facts read from the repo (detected stack,
  resolved code root). Never a value that varies between two runs on the same repo.
- **Two-space JSON indent**, trailing newline, LF endings.

A file generated twice from the same repo state must be identical. If it is not, that is a defect in
the generator — fix the non-determinism rather than restricting who may write the file.

### One thing that IS a repo setting, not a file

If the team wants "CI must pass before merge" **enforced**, that is GitHub **branch protection** with
the job name as a required check — configured once on the repository, not something any branch can
carry. Name it in the completion announcement so the user can set it; do not attempt it automatically.

---

## Brownfield reconciliation — when existing code is not in `src/`

Detected at Workspace Detection. Do **not** mass-move an existing tree; that produces an
unreviewable diff and breaks every import in the repo.

| Situation | What to do |
|---|---|
| Existing code already in `src/` | Nothing to do. Continue. |
| Existing code in a single other root (`app/`, `lib/`, `server/`) | **Record it** in `aire-state.md` under `## Code Root` and treat that directory as `src/` for the whole cycle. Announce it. Every rule that says `src/` means the recorded root. |
| Monorepo with several package roots | Record each in `## Code Root` as a list. New code goes into the package the work unit belongs to, at that package's own `src/`. |
| No discernible code root (files loose at repo root) | Create `src/`, put **only new** code there, and record it. Leave existing files alone. |

🔴 Record the decision once, in `aire-state.md`, and never re-derive it per story — an inconsistent
code root across stories is worse than a non-standard one.

```markdown
## Code Root
- **Type**: single | monorepo | new
- **Path(s)**: src/ | app/ | packages/api/src, packages/web/src
- **Recorded**: 2026-08-26T10:14:00Z
- **Note**: existing tree left in place; `src/` semantics map to `app/` for this repo
```
