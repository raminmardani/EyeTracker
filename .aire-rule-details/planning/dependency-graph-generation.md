# Dependency Graph Generation (Planning — immediately after User Stories)

**Purpose**: Analyse story dependencies. Each story gets a `requires` list; stories whose prerequisites are all Done have no dependencies on each other and can be implemented in parallel by different developers. `Requires` is stamped onto every story in the Story Tracker and in `stories.md`. The graph is computed for the fixed `team_size` of **2** developers (never asked — see Step 2).

**Always executes** right after User Stories. Produces `.spec/aire-docs/planning/dependency-graph.yml` and records each story's `Requires` in the Story Tracker.

## Execution Steps

1. **MANDATORY**: Log start of Dependency Graph stage in audit.md
2. **Reuse `team_size` from `aire-state.md`** — it is the fixed framework default `2`, recorded by User Stories Part 1 without prompting. 🔴 **NEVER ask the user for a team size here** (or anywhere else): the graph aims for at least **2** independent stories being available at any time where the architecture allows, so no developer is idle waiting on another's in-progress work. If the value is missing from state for any reason, write `team_size: 2` and continue — do not prompt.
3. **Determine story dependencies — 🤖 AUTOMATIC, INFERRED. Do NOT ask the user.** For each story, derive its `requires` from the approved story set itself: the acceptance criteria, the files/components each story creates vs consumes, and the **TRUE-PARALLELISM RULES** below (R1 seed files, R2 compile/runtime need, R3 mocks, R4 no narrative chains, R5 parallelism target). Every inferred edge MUST be justifiable in one line ("1.3 requires 1.1 — needs the `User` entity to exist at compile time"); record that justification per edge in the `## Dependency Graph` section so the user can audit the reasoning in the announcement. Never ask "which stories must be Done before Story N.M?" — the stories were just generated, approved at GATE 1, and pushed to the configured tracker, and they contain everything needed to infer this.
4. **Update every story** in `.spec/aire-docs/planning/user-stories/stories.md` and the Story Tracker in `aire-state.md` with its `Requires` list
5. **Write `.spec/aire-docs/planning/dependency-graph.yml`** (see schema below)
6. **Add `## Dependency Graph` section to `.spec/aire-docs/aire-state.md`** containing:
   - Mermaid `graph TD` of the dependency chain
   - Ready-stories summary: which stories have no prerequisites and can start immediately, and which are blocked by what

7. **Announce and proceed — 🤖 AUTOMATIC, no approval gate.** The graph is derived from the generated story set, and it is **enforced later by two live machine gates** (`dev-implement`'s Doability Gate and the branch-cut dependency-merge check), so a wrong edge cannot silently cause bad work — it surfaces at story pick. Show the graph and summary as an **announcement**:
   ```
   📊 Dependency Graph complete (auto-generated — no approval needed).
   - Total stories: K  |  Immediately startable (no prerequisites): M
   - team_size: N  (target: ≥ N independent stories available at a time)
   - Inferred edges: [story → requires, with the one-line justification for each]

   Proceeding to Workflow Planning. (Tell me any time if an edge is wrong and I'll revise the graph.)
   ```
   **Do NOT ask "Proceed? (yes / revise graph)" and do NOT block.** If the user volunteers a correction, apply it and re-announce — that is an interrupt, not a gate.
8. **MANDATORY**: Log in audit.md that the graph was generated and auto-approved, with the complete inferred edge list + justifications; log verbatim any correction the user volunteers afterwards

## TRUE-PARALLELISM RULES (apply when computing `requires`)

- **R1 Seed story**: If a file doesn't exist yet and is needed by 2+ stories, one seed story must create it first; all others `requires` that seed — prevents unmergeable git conflicts
- **R2 Contract rule**: A story only `requires` another when it needs that story's **code to exist at compile/run time**, not merely its API shape
- **R3 Mock rule**: A frontend/consumer story MAY drop a `requires` edge when its tests use mocks/stubs AND a separate integration story verifies real wiring
- **R4 No artificial chains**: Don't add `requires` for narrative ordering — only for genuine runtime/compile-time dependencies
- **R5 Parallelism target**: Aim for at least `team_size` independent stories being available at any time where the architecture allows

## `.spec/aire-docs/planning/dependency-graph.yml` Schema

```yaml
version: 1
generated_at: YYYY-MM-DD
team_size: 2

shared_files:
  - package.json          # files touched by 2+ stories — may cause merge conflicts
  - src/routes.ts

stories:
  - id: "1.1"
    title: Story title
    tracker_id: LOCAL     # updated to the real key/number/ID after the tracker push (Part 3 of User Stories)
    requires: []          # story IDs that must be Done before this starts
    enables: ["1.2"]      # reverse edges (informational only)
```

## Story Tracker Table Format

Create/update in `aire-state.md` under `## Story Tracker` after this stage:

| Story | Title   | Requires | Tracker ID | Status         | PR         | Merged | Start      | End        | Recorded           |
|-------|---------|----------|------------|----------------|------------|--------|------------|------------|--------------------|
| 1.1   | [Title] | none     | —          | 🟢 Ready for Development | —          | —      |            |            | [YYYY-MM-DD HH:MM] |

- **Requires**: Assigned by this Dependency Graph stage.
- **Tracker ID**: Populated from Part 3 of User Stories (the tracker push; each pushed story is linked to the Parent Epic in `## Tracker`). The value is a Jira key, an ADO work item ID, a GitHub issue number, or `LOCAL` when `## Tracker` records `Type: LOCAL` (no external push).
- **PR**: The story's Pull Request URL, recorded by `dev-implement` when the PR is raised (Section D). `—` until a PR exists.
- **Merged**: `no` once the PR is raised, `yes` once the PR is confirmed merged into the epic branch, `—` before a PR exists. A story moves to 🧪 Ready for Testing ONLY when this becomes `yes` (checked via `gh pr view` by the `ve-list-work` skill, which promotes it once ve has tested it).
- **Start**: Timestamp when story moves to 🔵 In Development.
- **End**: Timestamp when story moves to 🧪 Ready for Testing (i.e. when its PR is merged).
- **Recorded**: Timestamp of the last tracker update for this row.
