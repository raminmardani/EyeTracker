# AIRE State — EyeTracker (eval framework smoke test)

**AIRE VERSION**: 1.0
**Workflow Type**: Epic cycle
**Status**: ▶️ Stories generated — awaiting GATE 1 approval

## Tracker
- Type: GITHUB
- Parent Epic: none
- Epic URL: —
- Project Key / Repo / Org: raminmardani/EyeTracker  ✅ CONFIRMED BY USER 2026-09-14T17:35:46Z

## Code Root
- Path: `eye_tracker/` + `main.py` (brownfield — NOT `src/`; tree is never moved)
- Recorded: 2026-09-14T17:12:42Z

## Existing-System Context
- **Workspace type**: brownfield
- **Helix MCP**: connected
- **Source**: atlas+local (partial)
- **Components in scope**: face_mesh, gaze, calibration, tracker, overlay, one_euro, main (7)
- **Atlas coverage**: knowledge graph 7/7 components (commit-exact); deepdive docs 0/7
- **Knowledge graph**: .spec/aire-docs/planning/reverse-engineering/knowledge-graph.md
- **Recorded**: 2026-09-14T17:32:23Z

## Helix MCP Binding
- Provider: `helix` (project .mcp.json)
- Endpoint: https://helix-mcp.3pillarglobal.com/helix-atlas/mcp
- Solution: 704 (EyeTracker) | user 410 | repo raminmardani/EyeTracker @ main
- Graph tools: codebase_cypher_query, codebase_agent_query, graph_change_impact
- Doc tools: list_solution_documents_tool, get_solution_document_tool
- Atlas ingested commit: 745e086f569a7a9d30e0f185bb4f6fc6126a0af2 (zero source drift vs base)


## Branching
- Base Branch: main @ d28991c
- Epic Branch: not yet cut (blocked at the Helix gate)
- 🔒 Push remote deliberately disabled: `DISABLED-no-push-to-real-repo`

## Extension Configuration
- Security Baseline: Enabled = Yes (always mandatory)
- Playwright Test Automation: Enabled = Yes (always mandatory)

## Stage Progress
- [x] Workspace Detection
- [x] 🧭 Helix MCP Gate — bound; coverage PARTIAL
- [ ] Reverse Engineering (existing artifacts found under docs/ — reuse candidate)
- [ ] Requirements Analysis
- [ ] User Stories (GATE 1)
- [ ] Dependency Graph
- [ ] Workflow Planning
- [ ] Application Design
- [ ] System-Level Design stages
- [ ] STOP CHECKPOINT — .evals/ + rubrics + CI pipeline  ← the target of this test

## Story Tracker

| Story | Title | Requires | Tracker ID | Status | PR | Merged | Start | End | Recorded |
|-------|-------|----------|------------|--------|----|--------|-------|-----|----------|
| 1.1 | Unified frame-acceptance envelope | none | — | ⏸️ Awaiting GATE 1 | — | — | | | 2026-09-14 17:48 |
| 1.2 | Frame rejections counted by reason | 1.1 | — | ⏸️ Awaiting GATE 1 | — | — | | | 2026-09-14 17:48 |
| 1.3 | Structured logging replaces print diagnostics | none | — | ⏸️ Awaiting GATE 1 | — | — | | | 2026-09-14 17:48 |

- **team_size**: 2 (fixed) · **ready at start**: 1.1, 1.3
