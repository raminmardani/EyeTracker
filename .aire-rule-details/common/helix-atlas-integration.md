# Helix MCP ↔ Atlas Integration — Reuse Existing-System Truth, Never Re-Derive It

**Purpose**: AIRE does not re-discover a system it already has documentation for. **Atlas** holds the
existing-system truth for brownfield estates — a **knowledge graph** of the system and **deepdive
`.md` documents** per component/domain. The **Helix MCP server** is how AIRE reaches Atlas.

**The rule in one line**: when the work touches an existing system, Atlas is the source of the
reverse-engineering truth and AIRE consumes it; AIRE generates that truth locally **only** when Atlas
is genuinely unavailable, and says so out loud when it does.

**Load this file when**: Workspace Detection runs, Reverse Engineering is being considered, a
migration/modernisation is detected, or any stage needs existing-system context.

---

## 1. When Helix is REQUIRED (blocking) vs OPTIONAL

| Situation | Helix MCP |
|---|---|
| **Brownfield** — existing code detected in the workspace | 🔴 **REQUIRED** — prompt to connect and HALT |
| **Migration / modernisation / re-platform** — stated by the user or inferred from the Epic | 🔴 **REQUIRED** — prompt to connect and HALT |
| **Integration with an existing system** the workspace does not contain | 🔴 **REQUIRED** — prompt to connect and HALT |
| **Greenfield**, no existing system referenced anywhere | ⚪ **OPTIONAL** — never prompt, never block |

**Migration/brownfield detection signals** (any one is enough):
- Workspace Detection classified the workspace **brownfield**.
- The Epic / ticket / user request contains: *migrate, migration, modernise/modernize, re-platform,
  replatform, port, legacy, rewrite, refactor <existing system>, strangler, lift and shift, upgrade
  from, replace <system>, integrate with <existing system>*.
- The user names a system that is not in this workspace as something to build against.

---

## 2. Discovery — never hardcode, always resolve at runtime

🔴 **Do NOT assume tool names.** Deployments differ. Resolve the server and its tools at the moment
you need them.

**Resolution order:**

1. **Enumerate the connected MCP servers and their tools** available in this session (the host lists
   them; use the tool-discovery mechanism the session provides).
2. **Match a Helix/Atlas provider** — a server or tool whose name or description contains any of:
   `helix`, `atlas`, `knowledge graph`, `knowledge-graph`, `deepdive`, `deep dive`, `codebase graph`.
3. **Classify the matched tools by capability**, by what their descriptions say they do:
   - **GRAPH** — queries the knowledge graph (entities, components, relationships, call paths, data flows)
   - **DOCS** — lists/fetches deepdive `.md` documents
   - **SEARCH** — free-text search across the indexed estate
4. **Record the binding** in `aire-state.md` (Section 6) so later stages and later sessions reuse it without
   re-discovering.

**If matching is ambiguous** (several plausible servers): list what you found and ask the user which
one is Helix. Do not guess — pulling architecture truth from the wrong system is worse than pausing.

### TOOL BINDING — fill in on first successful discovery

Write the resolved binding into `aire-state.md`. Never invent values for it.

```markdown
## Helix MCP Binding
- **Server**: <resolved MCP server name>
- **Graph tool(s)**: <tool name(s)> — <one-line purpose>
- **Docs tool(s)**: <tool name(s)> — <one-line purpose>
- **Search tool(s)**: <tool name(s)> — <one-line purpose>
- **Estate / workspace id**: <the Atlas workspace or repo identifier queried>
- **Resolved**: <ISO 8601 timestamp>
```

---

## 3. The connect gate (blocking)

When Helix is REQUIRED (Section 1) and no Helix provider resolves, **HALT**. Do not fall back to local
reverse engineering without the user's explicit instruction — silently re-deriving what Atlas already
holds produces a second, divergent source of truth, which is the exact failure this integration
exists to prevent.

Emit **verbatim**, substituting the bracketed values:

```
🧭 HELIX MCP REQUIRED — connect Atlas to continue

   This is a [brownfield workspace | migration | integration with an existing system].
   AIRE reuses Atlas's existing-system truth instead of re-deriving it:
     • the knowledge graph  → the system's real components, dependencies and data flows
     • the deepdive docs    → per-component architecture and behaviour, already reviewed

   No Helix MCP server is connected in this session, so that truth is unavailable.

   ➡️ To connect: add the Helix MCP server to this project's `.mcp.json` (or your Claude Code MCP
      configuration) and restart the session. Then re-run this command — AIRE resumes here.

❓ How do you want to proceed?
   A) 🔌 I'll connect Helix now — stop, and I will re-run once it's connected. (Recommended)
   B) 📄 Point me at exported Atlas docs — give a local path to the deepdive .md files and/or a
         knowledge-graph export; AIRE reads them from disk instead of the MCP.
   C) ⚠️ Proceed WITHOUT Atlas — AIRE generates reverse-engineering artifacts locally from the code
         in this workspace. Slower, limited to what is in this repo, and it will NOT reflect the wider
         estate. This choice is recorded in aire-state.md and audit.md.

[Answer]:
```

- **A** → HALT. Log the halt in `audit.md`. Nothing else runs.
- **B** → read the supplied path, treat those files exactly as Section 4 treats MCP-fetched docs, and record
  `Source: local-export (<path>)` in the provenance block.
- **C** → record `Source: local-generation (Atlas unavailable — user approved)` in the provenance
  block, in `aire-state.md`, and in `audit.md`, then run the normal
  `planning/reverse-engineering.md` stage. 🔴 Every downstream artifact derived this way carries the
  line *"Existing-system context derived locally; Atlas was not consulted."*

🔴 Log the prompt and the raw user response in `audit.md`. This is a real decision with downstream
consequences and it must be attributable.

---

## 4. What to pull, and where it lands

Once a Helix provider is bound, pull **before** any planning stage that needs system context — that
is, before Reverse Engineering is even considered, and before Requirements Analysis reads its inputs.

| Pull | Via | Lands in | Replaces |
|---|---|---|---|
| **Knowledge graph** — components, ownership, dependencies, call paths, data stores, integration points | GRAPH tool | `.spec/aire-docs/planning/reverse-engineering/knowledge-graph.md` — **once per cycle**, never per work unit | Manual dependency discovery |
| **Deepdive docs** for every component the work touches | DOCS tool | `.spec/aire-docs/planning/reverse-engineering/` — one file per component, original filenames preserved | Locally generated RE artifacts |
| **Targeted answers** — a specific contract, schema, or flow a stage needs | SEARCH / GRAPH | Quoted inline in the consuming artifact, with the citation | Guessing |

### 4.1 Scoping the pull — pull what the work touches, not the whole estate

🔴 **Never dump the entire estate.** Resolve scope in this order and pull only that:
1. The components named in the Epic / ticket / requirements.
2. Their **direct** dependencies and dependents from the graph (one hop).
3. Any component that owns a data store or contract the work will read or write.

Record the scope you resolved and why. If a later stage needs a component outside the pulled scope,
pull it then — incrementally — and note the extension.

### 4.2 Provenance block — MANDATORY on every artifact sourced from Atlas

Every file written from Atlas content opens with this block. An Atlas-derived document without
provenance is indistinguishable from an AI-invented one, which destroys its value as truth.

```markdown
> **Source**: Atlas via Helix MCP
> **Server / tool**: <server> · <tool>
> **Estate**: <estate or repo identifier>
> **Scope pulled**: <components and the rule that selected them>
> **Fetched**: <ISO 8601 timestamp>
> **Freshness**: <Atlas's own last-indexed timestamp, if it exposes one — else "not reported">
```

### 4.3 🔴 Never edit Atlas content to make it fit

Atlas documents are **read-only inputs**. Copy them faithfully. If Atlas contradicts an assumption in
the Epic, the requirements, or a design artifact, that contradiction is a **finding to surface**, not
a discrepancy to smooth over:

> ⚠️ **Atlas conflict** — `<component>`: Atlas states `<X>`; `<artifact>` assumes `<Y>`.
> Proceeding on Atlas (existing-system truth wins) and amending `<artifact>` to match.
> Recorded in audit.md.

Follow Atlas, amend the AIRE-side artifact to stay truthful, say so plainly, log it. Never the reverse
— never rewrite an Atlas document to agree with a plan.

---

## 5. Effect on the Reverse Engineering stage

`planning/reverse-engineering.md` becomes **conditional on Atlas availability**:

| Atlas state | Reverse Engineering stage |
|---|---|
| Deepdive docs cover **every** component in scope | ⏭️ **SKIPPED.** Atlas docs ARE the artifacts. Record `Source: atlas` and the coverage list. Announce the skip and what it saved. |
| Atlas covers **some** components | 🔀 **PARTIAL.** Consume Atlas for what it covers; generate locally **only** for the gaps. Every locally generated file says so in its provenance block. |
| Atlas unavailable, user chose option C | ▶️ **FULL local generation**, exactly as before, with the "Atlas was not consulted" banner on every artifact. |

Record which branch was taken in `aire-state.md` and `audit.md`. Announce it — the user needs to know
whether they are reading reviewed estate truth or a fresh AI derivation.

---

## 6. State recorded in `aire-state.md`

```markdown
## Existing-System Context
- **Workspace type**: brownfield | greenfield | migration
- **Helix MCP**: connected | not connected | declined by user
- **Source**: atlas | atlas+local (partial) | local-export | local-generation
- **Components in scope**: <list>
- **Atlas coverage**: <n of m components covered by deepdive docs>
- **Knowledge graph**: .spec/aire-docs/planning/reverse-engineering/knowledge-graph.md
- **Recorded**: <ISO 8601 timestamp>
```

---

## 7. Downstream consumers — who reads Atlas content and for what

| Stage / artifact | Uses |
|---|---|
| Requirements Analysis | Knowledge graph + deepdives to ground scope and spot impacted components the Epic omitted |
| User Stories | Component boundaries from the graph to keep stories independently implementable |
| Dependency Graph | Real inter-component dependencies from the graph — not guessed from story titles |
| `.spec/architecture.md` | Existing architecture is the **starting state**; the design records the delta from it |
| `.evals/rubrics/architecture-rubric.json` | Fallback chain link 3 — derive criteria from Atlas truth when no design stage ran |
| Code Generation | Real signatures, error shapes and conventions of the code being changed |

🔴 **A stage that needs existing-system context and has none must say so** — not proceed on
assumption. "I don't have Atlas coverage for `<component>`" is a valid, required output.
