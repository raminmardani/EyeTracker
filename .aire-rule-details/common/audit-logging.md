# Audit Logging, Session Identity & Timestamp Accuracy

**Purpose**: the complete contract for `.spec/aire-docs/audit.md` — what is logged, who it is
attributed to, how timestamps are produced, and the entry format.

**Load this file at workflow start.** It is MANDATORY and applies to EVERY workflow, stage, agent and
skill, including those that define their own local audit templates.

---

## 1. Session Identity — approver email, audit.md ONLY, silent, email-only

**CRITICAL**: Every `audit.md` entry MUST carry the operator's **email** in a `**User Email**:` field.
The email is the ONLY identity field — do NOT record, derive, or ask for the user's name. Capture is
**silent** (NO confirmation question) and **tool-free** (no shell commands, no MCP, no external
calls). **`audit.md` is the ONLY place the email is ever recorded.**

**Capture** (no tool calls, no questions, no persistence): read the **session email** LIVE from the
session context the AI environment provides (Claude Code injects the logged-in account's email
automatically) whenever an audit entry is written. Use it AS-IS — it is environment-authenticated,
MUST NOT be confirmed with the user, and MUST NOT be cached in any file.

**Rules**:
- **Email only** — never record a display name anywhere, and never ask the user to confirm the email.
- **Stamp every audit entry** — at every "Wait for Explicit Approval" gate, and at every tracker /
  PR confirmation, this field identifies WHO approved.
- 🔴 **Template precedence — `**User Email**:` can NEVER be dropped.** Workflow-, stage- and
  skill-specific audit templates (dev-implement's TRACKER ITEM format, the bug/enhancement flows,
  `ve-list-work`, error/recovery logs, …) only **ADD** fields to the base format — they never remove
  one. Even when a local template does not show `**User Email**:`, include it, directly after
  `**Timestamp**:`, in every entry written under that template.
- **Attribution, not authentication** — this records who operated the session for the audit trail.
  Non-repudiable records remain the authenticated systems: tracker transitions, GitHub PR actions,
  git commit authorship.

---

## 2. Timestamp Accuracy — ALL timestamps

**CRITICAL**: Every timestamp in an AIRE artifact — `audit.md` `**Timestamp**:`, `aire-state.md`
`Start Date`/`Recorded`, Story Tracker `Start`/`End`/`Recorded`, `dependency-graph.yml`
`generated_at`, `architecture.md` `Generated`, and any other dated field — MUST be sourced from a
**real clock at the moment it is written**, in ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).

🔴 NEVER estimate, hand-write, copy forward, or increment a timestamp.

- **Shell available** (Bash, PowerShell, …): run **EXACTLY ONE** clock command and use its output
  verbatim — `date -u +%Y-%m-%dT%H:%M:%SZ` (Bash) or
  `Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mm:ssZ"` (PowerShell). Do NOT run a second `date` variant,
  and NEVER use a space-separated format like `%Y-%m-%d %H:%M` — the escaped space triggers an
  unnecessary permission prompt.
- **No shell**: use the environment's own real-time clock source; never fabricate a value.
- Applies to EVERY workflow, stage and skill that writes a timestamp.

---

## 3. What gets logged

- **MANDATORY**: EVERY user input — prompts, questions, answers — with a timestamp.
- **MANDATORY**: the user's **COMPLETE RAW INPUT**, exactly as provided. 🔴 Never summarized, never
  paraphrased, never truncated.
- **MANDATORY**: every approval prompt, logged *before* it is presented.
- **MANDATORY**: every user response, logged *after* it is received.
- **MANDATORY**: every stage entry/exit, tracker transition, gate outcome, self-healing attempt, and
  error/recovery event.

🔴 **RECORD WHAT YOU OBSERVED, NEVER WHAT THE RULES SAY SHOULD HAPPEN.** Before writing that an
action succeeded, read the result back from the system that owns it — the PR body, the tracker issue,
the file on disk, the command's exit code. An entry written from the rule ("the PR body carries the
scorecard, because that is what the framework specifies") rather than from the observation is a
**false audit record**, and it is worse than no record: it is the artifact a reviewer trusts when
reconstructing what happened. If verification is impossible, write that it could not be verified.
- Include the stage context on every entry.

---

## 4. File handling

- **Path**: `.spec/aire-docs/audit.md`.
- **Creation**: if it does not exist, create it with an `# Audit Log` header before the first entry.
- **Ordering**: ALWAYS append to the **END**, in strict chronological order (oldest → newest).
  🔴 Never prepend, never reorder, never rewrite an existing entry.
- 🔴 **Append or Edit only.** NEVER use a tool or command that overwrites the whole file — reading the
  file and re-writing it with additions duplicates the entire history.
  - ✅ Read `audit.md`, then append/Edit the new entry.
  - ❌ Rewrite the whole file with previous contents plus additions.

---

## 5. Base entry format

Local templates ADD fields to this; they never remove one.

```markdown
## [Stage Name or Interaction Type]
**Timestamp**: [ISO 8601 — from a real clock, per Section 2]
**User Email**: [current session email — read live; email ONLY, never a name; on approval-flow entries this identifies the approver]
**User Input**: "[Complete raw user input — never summarized]"
**AI Response**: "[AI's response or action taken]"
**Context**: [Stage, action, or decision made]

---
```

### 5.1 Implementation-flow entries add

```markdown
**TRACKER ITEM**: "[Full tracker hyperlink, or the local Story ID]"
**Epic Link**: "[Full Parent Epic URL from ## Tracker in aire-state.md — or "none"]"
**AIRE VERSION**: "[framework version [N], read live from the canonical line in CLAUDE.md]"
```

### 5.2 Self-healing entries add

```markdown
**SH-LOOP**: [SH-LOOP-n] — attempt [n] of 3
**Root cause**: [diagnosis stated BEFORE the change was made]
**Verification**: [exact command re-run] → [result]
```

An unrecorded self-healing attempt is a process violation (Self-Healing Retry Policy, SH-3).
