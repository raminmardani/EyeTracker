# Extensions — Loading and Enforcement

**Purpose**: how AIRE discovers, loads and enforces the rule extensions under `extensions/`, without
paying the context cost of rules the project never opted into.

**Load this file at workflow start**, together with the `*.opt-in.md` scan it describes.

---

## 1. Loading process (context-optimized)

**CRITICAL**: at workflow start, scan `extensions/` recursively but load ONLY the lightweight opt-in
files — NOT the full rule files. Full rule files are loaded on demand, after the user opts in.

1. List every subdirectory under `extensions/` (e.g. `extensions/compliance/`).
2. In each, load ONLY `*.opt-in.md` — these carry the extension's opt-in prompt. The corresponding
   rules file is derived by convention: strip `.opt-in.md`, append `.md`
   (`resiliency-baseline.opt-in.md` → `resiliency-baseline.md`).
3. Do NOT load a full rule file (e.g. `resiliency-baseline.md`) at this stage.

## 2. Deferred rule loading

- During **Requirements Analysis**, present the opt-in prompts from the loaded `*.opt-in.md` files.
- **Opts IN** → load that extension's rules file at that point.
- **Opts OUT** → the full rules file is never loaded, saving context.
- An extension with **no** matching `*.opt-in.md` is **always enforced** — load its rules file
  immediately at workflow start.

## 3. Always-mandatory extensions (never asked, never opt-out)

| Extension | Rule file | Behaviour |
|---|---|---|
| **Security Baseline** | `extensions/security/baseline/security-baseline.md` | Loaded at workflow start for EVERY project and enforced as **blocking**. 🔴 NEVER ask whether security rules apply, and ignore any legacy opt-out recorded in `## Extension Configuration`. |
| **Playwright Test Automation** | `extensions/testing/playwright-automation/playwright-automation.md` | Loaded at workflow start; record `Enabled = Yes` in `## Extension Configuration`. |

## 4. Enforcement (applies only to loaded/enabled extensions)

- Extension rules are **hard constraints**, not optional guidance.
- At each stage, evaluate which extension rules are applicable, based on the stage's purpose, the
  artifacts being produced, and the context of the work — enforce only the relevant ones.
- A rule that is not applicable to the current stage is marked **N/A** in the compliance summary.
  That is not a blocking finding.
- Non-compliance with any **applicable, enabled** extension rule is a **blocking finding** — do NOT
  present stage completion until it is resolved.
- When presenting stage completion, include a compliance summary: compliant / non-compliant / N/A per
  rule, with a brief rationale for each N/A determination.

## 5. Conditional enforcement

Extensions may be conditionally enabled or disabled. The opt-in mechanism lives in
`planning/requirements-analysis.md`. **Before enforcing any extension at ANY stage**, check its
`Enabled` status in `.spec/aire-docs/aire-state.md` under `## Extension Configuration`. Skip disabled
extensions and log the skip in `audit.md`. Default to **enforced** when no configuration exists.
