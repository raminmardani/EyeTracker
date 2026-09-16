# Development Handoff Message

**Purpose**: the verbatim message presented at the 🛑 MANDATORY STOP checkpoint in `CLAUDE.md`
(after the system-level design stages complete or are skipped, before any Code Generation). This is
the moment the workflow hands off to development and ve.

**Load and emit this** at Step 4 of the STOP CHECKPOINT. Emit the block below **verbatim**, with
every placeholder substituted from real values — never ship an unsubstituted placeholder. Then
**HALT** and wait for the user to type `dev-implement`.

```markdown
# ✅ Design Done — Ready to Build

📚 **[N] user stories created** during Planning.
[IF stories were pushed to the configured tracker:]
🔗 **On [TRACKER TYPE] [PROJECT_KEY / org-repo / org-project]** — stories [TICKET-101 … TICKET-1NN][, all linked to Parent Epic [EPIC-ID] — include this clause ONLY if `## Tracker` records an Epic (not `none`)].
[IF Type: LOCAL, or stories were NOT pushed:]
📍 Tracked locally only (not pushed to an external tracker).

🌊 Dependency Graph: [M] stories are ready to start now (no unfinished prerequisites).
🧩 Design stages: [list which ran vs were skipped].
🌿 Epic branch: `[epic-branch]` — design artifacts **committed and pushed** ([commit hash]).

> **🚀 <u>**DEV — use the keyword `dev-implement`**</u>**
> 1️⃣  Stay on / switch to the epic branch `[epic-branch]` and pull the latest.
> 2️⃣  Type **`dev-implement`** and pick a story (by Story ID / number, or Tracker ID).
>     Run it **once per story** — it cuts `story/N.M-…` from the epic branch.

> **🧪 <u>**ve — use the skill `/ve-implement`**</u>** (in parallel, starting now)
> ve does **not** wait for development — no dev code, branch, PR or merge is needed.
> 1️⃣  `git fetch origin && git checkout [epic-branch] && git pull --ff-only`
> 2️⃣  Type **`/ve-implement <story-ID or Tracker ID>`** — once per story.
>     It cuts `ve/<TICKET-ID>-<title>` from this branch, writes the MANUAL test steps to
>     `.spec/aire-docs/tests/<TICKET-ID>-<title>/` from the story's acceptance criteria, and raises
>     its own PR back into `[epic-branch]`.

🔴 Type `dev-implement` / `/ve-implement` EXACTLY as shown — do not describe what you want in your
   own words. Any other phrasing is not a framework trigger and the workflow will not advance.
```

- **[N]** = total stories. Show the tracker line only if stories were pushed (Tracker ID column populated); Epic ID from `## Tracker`. Otherwise show the local-only line.
- Substitute `[epic-branch]` and the commit hash with real values from `## Branching` / the Step 3 commit — never ship a placeholder.
- Log this handoff in audit.md.
