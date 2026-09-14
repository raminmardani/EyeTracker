# Session Continuity Templates

## Welcome Back Prompt Template
When a user returns to continue work on an existing aire project, present this prompt:

```markdown
**Welcome back! I can see you have an existing aire project in progress.**

Based on your aire-state.md, here's your current status:
- **Project**: [project-name]
- **Current Phase**: [PLANNING/IMPLEMENTATION/OPERATIONS]
- **Current Stage**: [Stage Name]
- **Last Completed**: [Last completed step]
- **Next Step**: [Next step to work on]
- **Recording approvals as**: [current session email — read live from the session context; email only, no name]

**What would you like to work on today?**

A) Continue where you left off ([Next step description])

B) Review a previous stage ([Show available stages])

[Answer]: 
```

## MANDATORY: Session Continuity Instructions
1. **Always read aire-state.md first** when detecting existing project
2. **Resolve the Session Identity** (silent, email-only, tool-free — per the Session Identity Capture rules in the root workflow file): read the current session email LIVE from the environment context. NO confirmation question and NO stored state — the email is recorded ONLY in audit.md, NEVER in aire-state.md (do not create or update a `## Session Identity` section; if an older run left one, ignore it).
   All audit.md entries in this session carry `**User Email**:` with the current session email — at every approval flow this field records who approved. A different developer resuming the project automatically logs under their own email. Email only; never record a name.
3. **Parse current status** from the workflow file to populate the prompt
4. **MANDATORY: Load Previous Stage Artifacts** - Before resuming any stage, automatically read all relevant artifacts from previous stages:
   - **Reverse Engineering**: Read architecture.md, code-structure.md, api-documentation.md
   - **Requirements Analysis**: Read requirements.md, requirement-verification-questions.md
   - **User Stories**: Read stories.md, personas.md, story-generation-plan.md, the `## Story Tracker` in aire-state.md (statuses, requires, Tracker IDs), AND the `## Tracker` section in aire-state.md (Type, Parent Epic ID/URL, Project Key / Repo / Org) — required so a resumed session can still link pushed stories to the Parent Epic provided at workflow start, and knows which tracker to dispatch to without re-asking
   - **Dependency Graph**: Read `.spec/aire-docs/planning/dependency-graph.yml` (`requires`/`enables`) and the `## Dependency Graph` section in aire-state.md
   - **Application Design**: Read application-design artifacts (components.md, component-methods.md, services.md)
   - **Implementation Design**: System-level design artifacts live under `.spec/aire-docs/implementation/design/` in
     `functional-design/`, `nfr-requirements/`, `nfr-design/`, and `infrastructure-design/`
     subdirectories. On resume, load whichever of these exist. The exact files in each
     subdirectory are enumerated by the corresponding implementation stage rules.
   - **At the STOP CHECKPOINT / Code Generation (`dev-implement`)**: If aire-state.md shows `Design complete — awaiting dev-implement`, remind the user to type `dev-implement` to build a story. On resuming a `dev-implement` session, read the Story Tracker + dependency-graph.yml to recompute the currently ready stories, and re-check the Doability Gate before continuing any in-progress story.
   - **Code Stages**: Read all code files, plans, the Story Tracker, dependency-graph.yml, AND all previous artifacts
5. **Smart Context Loading by Stage**:
   - **Early Stages (Workspace Detection, Reverse Engineering)**: Load workspace analysis
   - **Requirements/Stories**: Load reverse engineering + requirements artifacts
   - **Design Stages**: Load requirements + stories + architecture + design artifacts
   - **Code Stages**: Load ALL artifacts + existing code files
6. **Adapt options** based on architectural choice and current phase
7. **Show specific next steps** rather than generic descriptions
8. **Log the continuity prompt** in audit.md with timestamp
9. **Context Summary**: After loading artifacts, provide brief summary of what was loaded for user awareness
10. **Asking questions**: ALWAYS ask clarification or user feedback questions by placing them in .md files. DO NOT place the multiple-choice questions in-line in the chat session.

## Error Handling
If artifacts are missing or corrupted during session resumption, see [error-handling.md](error-handling.md) for guidance on recovery procedures. 