# Code Generation - Detailed Steps

## Overview
Code Generation is **per-story** and is triggered ONLY by the **`dev-implement`** keyword (orchestrated by `workflows/dev-implement.md`). It runs after the system-level design stages and the 🛑 STOP CHECKPOINT. It has two parts, preceded by Story Selection:
- **Step 0 - Story Selection (MANDATORY)**: identify WHICH story to implement (by Tracker ID or Story ID), run the Doability Gate, move it from `🟢 Ready for Development` to `🔵 In Development`
- **Part 1 - Planning**: Create detailed code generation plan — implementation steps per layer, ending with the mandatory **Unit Test & Coverage** step
- **Part 2 - Generation**: Execute the announced plan to generate code and artifacts, then generate + RUN unit tests until coverage is ≥90% (Step 11a — same run), then — **when this story touches an API layer** — generate + RUN the API & Contract Testing Gate (Step 11a.5 — same run), then run the FULL repo regression suite and diff it against the pre-change baseline (Step 11b — same run), then run the Static Eval Gate D1–D7 and diff it against the pre-change static baseline (Step 11c — same run)

**Extensions**: test-mandating extensions (e.g., Property-Based Testing) apply — their required tests are included in the Unit Test & Coverage step per the extension's scope.

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

**Audit entries**: EVERY audit.md entry written during this stage (plan approval prompts/responses, per-step generation logs, coverage evidence, completion) MUST include the `**TRACKER ITEM**:` field — the story's Tracker ID as a clickable link, or the local Story ID when `Tracker ID = —` — AND the `**Epic Link**:` field — the full Parent Epic URL as a clickable link, read from `## Tracker` in `.spec/aire-docs/aire-state.md`, or `none` when no Epic is recorded. See the Audit Entry Format in `workflows/dev-implement.md`.

**Note on design context**: The system-level design artifacts (functional/NFR/infrastructure under `.spec/aire-docs/implementation/design/`) apply to every story. Code for each story is written into the application structure documented in Application Design (or, if Application Design was skipped, per the structure patterns in Critical Rules below).

## Prerequisites
- System-level design stages complete (functional/NFR/infrastructure as applicable)
- Dependency Graph exists (`.spec/aire-docs/planning/dependency-graph.yml`) and the `## Story Tracker` exists in `aire-state.md`
- The story selected via `dev-implement` has passed the Doability Gate (all `requires` are `🧪 Ready for Testing`)
- The story branch is active, cut from the epic branch AFTER the dependency-merge check passed (`common/branching-strategy.md` Section 3). If any prerequisite story's branch is NOT yet merged into the epic branch, code generation MUST NOT start — the workflow has already warned and stopped (Case B): the user must merge the prerequisite's PR into the epic branch first and re-run `dev-implement`

---

# PART 1: PLANNING

## Step 0: Story Selection (MANDATORY)
- [ ] Load and execute all steps from `implementation/story-selection.md` — it asks which story, runs the Doability Gate, and moves the story from `🟢 Ready for Development` to `🔵 In Development` automatically (tracker + local Story Tracker updated without asking, transition verified for non-LOCAL). Do NOT restate that logic here.
- [ ] Carry the resolved story (ID, title, acceptance criteria, Tracker ID/link) into the planning steps below.

## Step 1: Analyze Story & Design Context
- [ ] Read the selected story and its acceptance criteria from `.spec/aire-docs/planning/user-stories/stories.md`
- [ ] **Read `.spec/aire-docs/planning/requirements/requirements.md` and resolve the story's `Covers` REQ-IDs** — the requirement text itself (not just the story's AC restatement) is MANDATORY planning input; an AC set that understates its requirement never caps the plan (`common/requirements-traceability.md` Rule 5)
- [ ] **Fallback coverage verification**: if `aire-state.md` carries NO `Requirements coverage verified post-design` record, run `common/requirements-traceability.md` Rule 4 now (silent, blocking) before planning proceeds — the thread must never reach code generation unverified
- [ ] Read the system-level design artifacts (functional-design, nfr-design, infrastructure-design under `.spec/aire-docs/implementation/design/`)
- [ ] Read `## Context References` in `aire-state.md`. **IF `Use References: Yes`**, load all listed reference paths — UX wireframes/mockups dictate the exact UI to build (layouts, controls, interactions); API specs dictate the exact endpoints and data shapes. When generating code, implement what the references show — they are authoritative for visual/structural fidelity alongside the acceptance criteria.
- [ ] Identify the story's dependencies and interfaces (from the Dependency Graph `requires`/`enables`)
- [ ] Validate the story is ready for code generation (Doability Gate passed in Step 0)

### Step 1.5: 📐 RE-CONSULT the Design References (MANDATORY — automatic, ask the user nothing)

**Load `common/design-reference-grounding.md`** and read `## Design References` in `.spec/aire-docs/aire-state.md`.

**This step adds NO question, NO gate, and NO checkpoint to code generation.** It runs silently as part of analysing story context. This phase has NO approval gate at all (the former GATE 2 plan approval is removed) — this step adds none either.

- [ ] **FIRST, read the `### Reconciliations` table** in `## Design References` (rule **DR-8**). Every point listed there is a **settled decision taken deliberately against the reference** by an earlier design stage — an excluded capability, a narrowed scope, a locally-scoped stylesheet, an NFR or accessibility constraint. **Those points are closed: follow the framework artifact, NOT the raw reference, and do not re-report them as contradictions.** The design docs the framework generated are the reconciled source of truth wherever they have actually considered a point.
- [ ] **Re-open** every reference whose `Governs` covers a component THIS story builds or modifies, and ground **only the points the reconciliations table does NOT settle**. A fresh read for THIS story's scope is required — *"it was read at Requirements Analysis / Application Design"* does not count, because those stages read only what was in their own scope.
- [ ] For a UI prototype, open the real `*.component.html` / `*.ts` / `*.css` (or equivalent) for this story's components and extract: actual control types (plain `<select>` vs searchable grouped combobox; single- vs multi-select), grouping/ordering, labels and icons, interaction behaviour (search/filter, click-outside-to-close, keyboard, empty states), and custom CSS classes — checking whether those classes exist in the live app's global styles.
- [ ] **On any remaining difference, apply DR-8 precedence — do NOT blanket-prefer the reference:**
   - **Reconciled** (the artifact recorded a decision on this point) → **follow the artifact**; note in one line that the reference differs here by prior decision. **Never reintroduce something a design stage deliberately excluded.**
   - **Unreconciled** (no artifact ever addressed this point — the AC is simply generic or silent) → **follow the reference**, state plainly in the plan what the AC said versus what the design shows, amend the AC / `requirements.md` / the tracker item per `common/requirements-traceability.md`, and record the reconciliation.
   - Either way: **do NOT stop, do NOT ask an A/B question** — the user reviews it at the existing GATE 2 like everything else in the plan.
- [ ] A capability the prototype shows that is **outside** this story's ACs → check the reconciliations table first: if it is already recorded as excluded, honour that silently. If it is new, note in the plan that you saw it and excluded it as out of scope, and record the reconciliation so no later story re-adds it. Never silently build it, never silently drop it, never ask about it.
- [ ] Any reference still `Read? ⏳` — read it now (DR-2/DR-3/DR-4) and carry on.
- [ ] Log in `audit.md` which references were re-opened, for which components, what was extracted, and any deviation reported.

**The plan (Step 2) states, for EVERY component it creates or changes, exactly one of:**

```
Design reference: <path>/<file> — grounded (<what the reference actually specifies>)
Design reference: none covers this component — built from ACs only
```

This is your own self-check while writing the plan — satisfy it yourself before announcing the plan.

## Step 2: Create Detailed Story Code Generation Plan
- [ ] Read workspace root and project type from `.spec/aire-docs/aire-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never .spec/aire-docs/)
- [ ] Create explicit steps for implementing this story:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Summary
  - API Layer Generation
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - **Unit Test & Coverage** — generate unit tests for ALL new/changed code, run them, measure coverage, and iterate until ≥90% (Step 11a — MANDATORY, always the step after implementation)
  - **API & Contract Testing Gate** — when this story adds/changes an API endpoint (i.e. the plan includes an API Layer Generation step above), generate automated tests against the actual endpoints, run them, and iterate until every applicable checklist item passes (Step 11a.5 — MANDATORY WHEN APPLICABLE, always the step after Step 11a; N/A when no API layer is touched)
  - **Full Regression vs Baseline** — re-run the ENTIRE repo suite (including any API & Contract tests from Step 11a.5) and diff against the baseline captured at the Story Branch checkpoint; any NEW failure is fixed in the same run (Step 11b — MANDATORY, always the step after Step 11a / Step 11a.5)
  - **Static Eval Gate (D1–D7)** — lint, type check, SAST, dependency vulnerabilities, licences, complexity, secrets; diffed against the static baseline captured at the Story Branch checkpoint; any NEW finding is fixed in the same run (Step 11c — MANDATORY, always the step after Step 11b)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] **Tag EVERY implementation step with the REQ-ID(s) and acceptance criteria it implements** — e.g., `Step 3: Order validation service (REQ-F-03, AC-1, AC-2)` (`common/requirements-traceability.md` Rule 5)
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Story Implementation Context
- [ ] For this story, include:
  - The story's acceptance criteria and the intake brief context (`epic-brief.md`, if present)
  - Dependencies on other stories (`requires`/`enables` from the Dependency Graph)
  - Expected interfaces and contracts (from Application Design, if it ran)
  - Database entities this story owns or touches
  - Service/component boundaries and responsibilities (from Application Design)

## Step 4: Create Story Plan Document
- [ ] Save complete plan as `.spec/aire-docs/implementation/plans/story-{N.M}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include story context and dependencies
- [ ] Include story traceability
- [ ] **Trace completeness self-check (MANDATORY — automatic, blocking, BEFORE the plan is announced)**: verify every REQ-ID in the story's `Covers` AND every acceptance criterion appears in ≥1 tagged plan step. A REQ/AC with no plan step is a blocking gap — extend the plan and re-check (no user prompt). Include the trace summary (REQ/AC → plan steps) in the plan document (`common/requirements-traceability.md` Rule 5)
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Story Plan
- [ ] Provide summary of the story code generation plan to the user
- [ ] Highlight the implementation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log the Finalized Plan (🤖 no approval prompt)
- [ ] **There is NO plan-approval gate.** The plan is finalized, announced and executed in the same run — never ask "Approve this plan?" (the former GATE 2 is removed).
- [ ] Log the finalized plan with timestamp in `.spec/aire-docs/audit.md` under a **plain heading** — e.g. `## Code Generation Part 1 — Plan Finalized (auto-approved, no gate) (Story N.M)`. **The word "GATE" must NOT appear in any heading written by this stage.**
- [ ] Include the path to the complete story code generation plan, the step count, and the REQ/AC trace summary
- [ ] Include the `**TRACKER ITEM**:` field (story's Tracker ID link, or local Story ID) and the `**Epic Link**:` field (full Parent Epic URL from `## Tracker` in aire-state.md, or `none`)


## Step 7: Announce and Proceed (no wait)
- [ ] Present the plan summary as an **announcement**, then proceed straight to Part 2 (Generation) — do NOT wait for a response
- [ ] If the user volunteers changes to the plan (now or mid-generation), apply them, update the plan document, announce the revision, log it, and continue — an interrupt, not a gate

## Step 8: (removed — there is no approval response to record)
- [ ] Superseded by Step 6's auto-approval note. Any user-volunteered plan change is logged as an ordinary interaction with their complete raw input, under a plain (non-"GATE") heading.

## Step 9: Update Progress
- [ ] Mark Code Generation Part 1 (Planning) complete in `aire-state.md`

---

# PART 2: GENERATION

## Step 10: Load Story Code Generation Plan
- [ ] Read the complete plan from `.spec/aire-docs/implementation/plans/story-{N.M}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (story, dependencies, design artifacts)

## Step 11: Execute Current Step
- [ ] Verify target directory from plan — code goes to the resolved code root, never to `.spec/`
- [ ] **Brownfield only**: Check if target file exists
- [ ] If this step is the **Unit Test & Coverage** step, execute Step 11a in full (mandatory — tests are generated, RUN, and iterated to `unitTestCoverageMin` coverage in this same run, never deferred to ve or a later session).
- [ ] If this step is the **Behavioural Test Gate**, execute the 🥒 Gherkin gate in full per `common/behavior-spec.md` Section 4.3 — implement the step definitions in `tests/behavior/steps/` against the app's public surface, RUN every scenario in this unit's `<work-unit>.feature`, and iterate (max 3 attempts) until all pass and every `@AC` tag is executed. 🔴 Fix the code, never the scenario.
- [ ] If this step is the **API & Contract Testing Gate**, execute Step 11a.5 in full (mandatory WHEN this story's plan includes an API Layer Generation step — tests are generated, RUN, and iterated until every applicable checklist item passes in this same run, never deferred to ve or a later session).
- [ ] Generate exactly what the current step describes:
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: the resolved code root (`src/` by default) per project structure
  - **Unit tests**: `tests/unit/` · **Gherkin step definitions**: `tests/behavior/steps/`
  - **Documentation**: `.spec/aire-docs/implementation/code/` (markdown + evidence only)
  - **Build/Config Files**: workspace root (they belong there by tooling convention)
  - 🔴 **Never** a source file under `.spec/`
- [ ] Follow the story's acceptance criteria
- [ ] Respect dependencies and interfaces

## Step 11a: Unit Test & Coverage Step (MANDATORY — after implementation, the `unitTestCoverageMin` threshold, same run)
Runs ONCE per story, immediately after all implementation steps are complete (business logic, API, repository, frontend):
- [ ] **Generate unit tests** covering ALL of the story's new/changed code — happy paths, edge cases, error scenarios, per acceptance criterion
- [ ] **RUN the tests** with the project's test runner; fix any failures (whether in the tests or defects they expose in the implementation) until 100% of tests pass
- [ ] **Measure coverage** on the story's new/changed code using the stack's standard coverage tool (e.g., jest `--coverage`, pytest-cov, JaCoCo)
- [ ] **Iterate until the threshold is met**: if coverage is below `unitTestCoverageMin` (`.evals/config.json`), identify the uncovered lines/branches, add or adjust tests, and re-run — repeat WITHIN THIS SAME RUN until coverage is ≥90%. Do not defer the gap to ve or a later session
- [ ] If the threshold is genuinely unreachable (e.g., untestable generated boilerplate), surface the gap to the user with the measured %, the uncovered code, and the reason — never silently accept below-target coverage
- [ ] **Capture PROOF artifacts (MANDATORY — durable, verifiable evidence, not just a text claim)**: from the FINAL passing test run, save the actual tool output to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/`:
  - [ ] **`unit-test-run.log`** — the raw, unedited stdout/stderr of the final test-runner invocation (the run that shows X/X passing). Do NOT hand-transcribe or summarize it — capture the real output (e.g., `npm test -- --coverage > unit-test-run.log 2>&1`, `pytest --cov ... | tee unit-test-run.log`)
  - [ ] **`coverage-report.*`** — the coverage tool's own machine-readable report from the same run. **This file is MANDATORY, not best-effort.** You MUST invoke the runner with the flags that emit a real report file — do NOT rely on the terminal summary alone:
    - **Node/JS (jest, nyc, vitest)**: enable coverage reporters so `coverage/lcov.info` (and/or `coverage-final.json`, HTML) is produced — e.g., `jest --coverage --coverageReporters=lcov --coverageReporters=json-summary`
    - **Python (pytest-cov)**: `pytest --cov=<pkg> --cov-report=xml --cov-report=html` → `coverage.xml` (+ `htmlcov/`)
    - **Java (JaCoCo)**: the `jacoco.xml`/HTML report from the build
    - **Any other stack**: use that stack's standard coverage-report flag to emit a machine-readable file (lcov / xml / json / HTML)
    Copy the emitted report into the evidence folder so it survives independent of the build workspace. **🔴 GATE FAILURE — if the stack HAS coverage-report tooling but no report file is produced and stored, the Unit Test & Coverage gate is NOT satisfied: STOP and surface it to the user (the terminal summary in `unit-test-run.log` alone is NOT sufficient proof).**
    - **⚠️ Narrow exception — only when the stack has NO coverage-report tooling at all**: if the language/test stack genuinely provides no way to emit a machine-readable coverage report (after actually checking for the standard tool), this is a **documented, surfaced exception — NOT a silent skip**. Record in `evidence-manifest.md` which coverage tool(s) were checked and why none is available, keep the mandatory `unit-test-run.log`, and explicitly surface the exception to the user for acknowledgment. This exception NEVER applies when a coverage tool exists for the stack (Python/pytest-cov, JS/jest·nyc·vitest, Java/JaCoCo, Go `-coverprofile`, .NET coverlet, etc.) — there the report file remains strictly mandatory.
  - [ ] **`evidence-manifest.md`** — a short manifest recording: the exact command(s) run, the test runner + coverage tool used, tests passing (X/X), the measured coverage % on the story's new/changed code, and a relative-path link to each artifact above
- [ ] **Cite the proof, not just the numbers**: in the story summary and audit.md, record tests passing (X/X) and the measured coverage %, AND link the evidence folder path `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/`. The numbers reported downstream (completion message, Code Review, PR/tracker comment) MUST match these saved artifacts

## Step 11a.5: 🔌 API & Contract Testing Gate (MANDATORY WHEN APPLICABLE — after Step 11a, same run)

**Purpose**: the Unit Test & Coverage gate (Step 11a) proves the story's code paths are exercised, but it does not prove the story's API is *callable correctly from the outside* — right status codes, right auth semantics, right error shape, right request/response schema. This step closes that gap with **automated, dev-executed API tests plus schema/contract validation** for every endpoint this story adds or changes.

### Applicability (automatic — no question asked)
- **Applies** to this story IF its code-generation plan (Step 2) includes an **API Layer Generation** step — i.e., the story adds or changes an API-visible endpoint/route/controller/handler.
- **N/A** if the plan has no API Layer Generation step. State this explicitly — `API & Contract Testing: N/A — no API layer touched by this story` — in the plan and in `evidence-manifest.md` (see below), and skip straight to Step 11b.
- Applicability is decided at the STORY level (does *this story* touch the API layer), not the whole application.

### Scope — the checklist (for EVERY new/changed endpoint this story touches)
Generate automated tests that call the actual endpoint (in-process test client — e.g. supertest, httpx/TestClient, RestAssured, MockMvc — or a spun-up test server; whichever is the stack's standard integration-test mechanism) and assert:
1. **Functional / happy path** — the documented success behavior per acceptance criterion, end to end through the real endpoint.
2. **Response Code Validation** — the correct HTTP status code for every documented success AND failure path (2xx variants, 4xx, 5xx as applicable) — not just 200-on-success.
3. **Authorization Testing — role-based access** — for every endpoint requiring auth: an unauthenticated request → `401`; an authenticated request with an insufficient role/permission → `403`; an authenticated request with the correct role → success. **401 and 403 must be distinguished correctly — never collapse them into one behavior.** N/A only for a genuinely unauthenticated/public endpoint (state why).
4. **Error Response Validation** — every documented error condition returns the codebase's/design docs' standard error envelope/format AND the correct error code — assert the error *schema*, not just the status code.
5. **Request Validation (inbound contract)** — required fields, data types, and enum constraints on the request payload are enforced: a missing required field, a wrong type, or an invalid enum value each produce the expected validation error. N/A only for an endpoint with no request body (state why).
6. **Response Contract Validation (outbound contract)** — the response payload matches its declared schema/contract (from Application Design, an OpenAPI/DTO/interface definition, or the API's own schema): required fields present, correct types, enum values within the declared set.

This is "API Testing along with Contract Testing" as **ONE gate**: functional behavior AND schema/contract compliance of both the request and the response. It is schema/contract validation of THIS service's own API — not consumer-driven cross-service contract testing (e.g. Pact); that remains out of scope unless the project already practices it elsewhere.

### Mechanics (mirrors the Unit Test & Coverage gate)
- [ ] **Generate** the tests per the checklist above for every new/changed endpoint.
- [ ] **RUN** them with the project's standard test runner / API-testing library (reuse the unit-test runner if it can drive HTTP/in-process calls, e.g. jest+supertest, pytest+httpx, JUnit+RestAssured).
- [ ] **Iterate within the SAME run** until every applicable checklist item passes — fix defects the tests expose in the implementation (never weaken the assertion to force a pass).
- [ ] **Pass criterion**: every new/changed endpoint has a passing test for EACH applicable checklist item. An item is inapplicable only when it genuinely does not apply to that endpoint (e.g., a public endpoint skips Authorization Testing, a GET with no body skips Request Validation) — state why per endpoint in the evidence manifest.
- [ ] If a checklist item genuinely cannot be satisfied (e.g., the stack defines no schema/contract to validate the response against), surface this to the user explicitly with the reason — never silently skip it.
- [ ] **Capture PROOF artifacts** to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/`:
  - [ ] **`api-contract-test-run.log`** — the raw, unedited stdout/stderr of the final passing run.
  - [ ] **`api-contract-test-report.*`** — the test runner's own machine-readable report from the same run. **This file is MANDATORY, not best-effort.** You MUST invoke the runner with the flags/plugin that emit a real report file — do NOT rely on the raw log alone:
    - **Node/JS (jest)**: `jest --json --outputFile=api-contract-test-report.json` (built into jest, no extra package needed) — or `jest-junit` for JUnit XML if the project already uses it
    - **Python (pytest)**: `pytest --junitxml=api-contract-test-report.xml` (built into pytest, no plugin needed)
    - **Java (JUnit/RestAssured/MockMvc)**: the `TEST-*.xml` JUnit report Surefire/Gradle already emits (`target/surefire-reports/` or `build/test-results/test/`) — copy it into the evidence folder
    - **Go**: `go test -json ./... > api-contract-test-report.json` (built into `go test`) — or `gotestsum --junitfile=...`
    - **.NET**: `dotnet test --logger "trx;LogFileName=api-contract-test-report.trx"` (or `--logger junit`)
    - **Any other stack**: use that stack's standard test-report flag/plugin to emit a machine-readable file (JUnit XML / JSON)
    Copy the emitted report into the evidence folder so it survives independent of the build workspace. **🔴 GATE FAILURE — if the stack's test runner supports a machine-readable report but none is produced and stored, the API & Contract Testing Gate is NOT satisfied: STOP and surface it to the user (the raw log in `api-contract-test-run.log` alone is NOT sufficient proof).**
    - **⚠️ Narrow exception — only when the runner genuinely has NO way to emit a machine-readable report at all** (after actually checking for the standard flag/plugin above): this is a **documented, surfaced exception — NOT a silent skip**. Record in `evidence-manifest.md` which report mechanism(s) were checked and why none is available, keep the mandatory `api-contract-test-run.log`, and explicitly surface the exception to the user for acknowledgment. This exception NEVER applies to the common stacks above (pytest, jest, JUnit/Surefire/Gradle, `go test -json`, dotnet trx) — there the report file remains strictly mandatory.
  - [ ] **`evidence-manifest.md`** — a per-endpoint checklist table: endpoint + method, each of the 6 checklist items → ✅ Pass / N/A + one-line reason, and the overall tests-passing count.
- [ ] **Cite the proof, not just a claim**: in the story summary, Code Review, and PR/tracker comment, reference `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/` — the numbers reported downstream MUST match these saved artifacts.

## Step 11b: Full Regression checkpoint (MANDATORY — after Step 11a and Step 11a.5, same run)
The coverage gate in Step 11a is scoped to the story's NEW/changed code. It cannot detect assertions this story invalidated in **pre-existing shared test files** — that is what this step is for. Where Step 11a.5 applied, its new API & Contract tests are now part of the repo suite and are included in this regression run going forward.
- [ ] **Re-run the ENTIRE repo test suite** (all pre-existing tests + this story's new tests) and save the raw output to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/full-regression.log`
- [ ] **Diff against `baseline-regression.log`** captured on the story branch before any code was generated (`workflows/dev-implement.md` Step 1.5 Item 4.5)
- [ ] **NEW failures (green at baseline, red now)** — **this story broke them, so this story fixes them.** Fix them within THIS SAME run (no user prompt), then re-run and re-diff, iterating until the diff is clean. Fix each according to what actually broke:
  - **Obsolete expectation** — behaviour legitimately changed, the assertion encodes the old contract → **update the assertion** (keep the test; it still guards real behaviour)
  - **Genuinely dead** — exercises a code path this story removed → **delete it** after confirming the new tests cover the replacement path
  - **Real regression** — the test is correct and the implementation broke it → **fix the implementation, never the test**
- [ ] 🔴 **NEVER delete, skip, or weaken a failing test merely to turn the suite green** — that discards the guard and hides real regressions while the coverage gate still reports ≥90% on new code
- [ ] **Failures already red at baseline** → not this story's doing. They are already logged in `baseline-regression.log`; ignore them and do not block/fix on them.
- [ ] **Record in `evidence-manifest.md`**: baseline vs post-change pass/fail counts, and each NEW failure with what broke and how it was fixed
- [ ] Proceed to Code Review only once the diff is clean (zero NEW failures, ignore the old failures from baseline run)

## Step 11c: 🔎 Static Eval Gate — D1–D7 (MANDATORY — after Step 11b, same run)

The test gates prove the code **behaves** correctly. They say nothing about whether it lints, type-checks, imports safely, or is licence-clean. This step closes that gap with **deterministic, zero-token checks**, gated on the **delta** against the baseline captured before generation.

- [ ] Run **D1–D7** per `common/eval-framework.md` Section 2 — lint, type check, SAST, dependency vulnerabilities, licences, cyclomatic complexity on changed functions, secret scan of the diff — using whatever tooling the repo already has (Section 2.2 covers detection and the `N/A` exception)
- [ ] Save the raw output to `.spec/aire-docs/implementation/code/eval-evidence/story-[N.M]/static/`
- [ ] **Diff against the baseline** captured before any code was generated (`workflows/dev-implement.md` Step 1.5 Item 4.6, in `static/baseline/`)
- [ ] **NEW findings above the `.evals/config.json` thresholds, on files this story changed** → **this story introduced them, so this story fixes them** in THIS SAME run (no user prompt), then re-run and re-diff until the diff is clean
- [ ] 🔴 **NEVER suppress a finding to pass the gate** — no blanket `eslint-disable`, no `# nosec`, no `# type: ignore`, no ignore-list entry, no widening `disallowedLicenses`. That is the exact analogue of deleting a failing test to make the suite green and is equally forbidden. **Fix the code.**
- [ ] **Findings already present at baseline** → pre-existing debt, not this story's. Logged under `static/baseline/`; ignore them and do not block on them
- [ ] Write `eval.json` + `eval-summary.md` per `common/eval-framework.md` Section 6 — `verdict` is `PASS` only if every entry under `gates` is `PASS` or `N/A`
- [ ] Proceed to Code Review only once the diff is clean

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the code generation plan
- [ ] **Story Tracker**: ensure the story being implemented is `🔵 In Development` with a `Start` date; update `Recorded` to the current timestamp in `.spec/aire-docs/aire-state.md`
- [ ] Update `.spec/aire-docs/aire-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Continue or Complete Generation
- [ ] If more steps remain, return to Step 10
- [ ] If all steps complete, proceed to present completion message

## Step 14: Present Completion Message
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete - Story [N.M]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `.spec/aire-docs/implementation/code/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> ✅ Code generation is complete. An **automated Code Review now runs for this story** — you are not
> asked for anything. If it reports findings they are **remediated automatically** and re-reviewed
> until the verdict is clean; then the commit, push and PR happen on their own.

---
```

## Step 15: Hand Off to Automated Code Review (no user gate here)

🔴 **GUARDRAIL — "Code Review" and "Remediate" here are WORKFLOW RULE FILES, NOT Claude skills.** They are executed by `Read`ing and following `workflows/code-review.md` / `workflows/remediate.md` (which pull detailed steps from `implementation/code-review.md` / `implementation/remediate.md`). There is **NO** Claude skill named `code-review` or `remediate` — **NEVER** invoke one via the Skill tool. The only review that IS a skill is **`pr-review`** (post-PR, AUTO MODE, as-is).

- **When invoked via `dev-implement`** (the normal path): do NOT stop for a "Request Changes / Continue" choice. Immediately hand control back to `workflows/dev-implement.md` **Post-Code-Generation Automation**, which auto-runs Code Review, audits the full log, and then routes on the verdict itself — a clean verdict goes straight to commit/push/PR, and any finding is fixed by the automatic remediate loop. No approval is requested at any point.
- **When invoked standalone** (code generation only, not under `dev-implement`): present the completion announcement and wait for the user to either request changes or confirm; do not auto-run downstream workflows.

## Step 16: Record Approval & Story Status (Confirm-First)
> **When invoked via `dev-implement`** (the normal path): do NOT change the status here. The story stays `🔵 In Development` through code generation, the automated Code Review, any Remediate loop, the PR raise (Section D — which only STORES the PR URL and sets `Merged=no`), and the auto PR review
- Log approval in audit.md with timestamp
- Record the user's approval response with timestamp
- **Post-implementation status — standalone code-generation only** (NOT under `dev-implement`): the story remains `🔵 In Development`.
  ```
  ✅ Story [N.M] implemented (tests [X/X] passing, coverage [Z]%).
  ❓ Mark story 🧪 Ready for Testing now? (yes — set Ready for Testing + End date / no — keep In Development)
  ```
  - On yes: update the `## Story Tracker` — **Status** → `🧪 Ready for Testing`, **End** timestamp, **Recorded** timestamp.
  - If the story has a non-LOCAL Tracker ID, apply the **Tracker Sync Rule** (confirm-first, per `common/tracker-sync.md` Section 4): transition the tracker issue to the state/label that mirrors Ready for Testing, verify it landed, add a comment with evidence (tests X/X passing, coverage %).
  - If the story is local-only (`Tracker ID = —`), update only the local tracker.
- **NEVER update the tracker without explicit user confirmation in this turn.**
- **The ONLY valid Story Tracker statuses are `🟢 Ready for Development`, `🔵 In Development`, and `🧪 Ready for Testing`.**

---

## Critical Rules

### Code Location Rules — 🔴 `src/` IS THE ONLY CODE ROOT

Full layout: `common/directory-structure.md`. The four roots and what belongs in each:

| Root | Contents |
|---|---|
| **`src/`** | ALL application code — greenfield AND brownfield |
| **`tests/`** | `unit/` · `behavior/` (🥒 Gherkin step definitions) · `e2e/` (Playwright) |
| **`.spec/`** | Specs + docs ONLY. 🔴 Never a source file. |
| **`.evals/`** | `config.json`, `rubrics/`, `scripts/` |

- **Read the code root from `aire-state.md` `## Code Root`** before generating. If the block is
  absent, the root is `src/`.
- 🔴 **Never write application code outside the resolved code root**, and never into `.spec/`.

**Structure patterns by project type** (all *inside* the code root):
- **Greenfield (default)**: `src/` for code, `tests/` for tests, `config/` for configuration
- **Greenfield, multiple services (per Application Design)**: `src/{service-name}/`, `tests/unit/{service-name}/`
- **Greenfield, modular monolith (per Application Design)**: `src/{module-name}/`, `tests/unit/{module-name}/`
- **Brownfield**: use the EXISTING structure under the recorded code root (e.g. `src/main/java/`,
  `packages/api/src/`). 🔴 Never mass-move an existing tree into `src/` — that produces an
  unreviewable diff and breaks every import. Record the real root once and treat it as `src/` for the
  whole cycle (`common/directory-structure.md` — Brownfield reconciliation).
- **Brownfield with no discernible code root** (files loose at the repo root): create `src/`, put
  **only new** code there, record it, and leave the existing files alone.

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- **REQ-ID THREAD**: load requirements.md + the story's `Covers` REQ-IDs as planning input, tag every step with the REQ/AC it implements, and pass the trace completeness self-check (every covered REQ-ID and every AC in ≥1 step) before the plan is announced — per `common/requirements-traceability.md` Rule 5
- Document story context and dependencies
- NO approval before generation — the plan is announced and executed (there is no plan gate)

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the story plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark the story's plan steps [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when the story's `requires` dependencies are `🧪 Ready for Testing` (Doability Gate)
- 🔴 **SQL RESERVED-WORD GUARDRAIL**: when generating any SQL (queries, migrations, stored procedures), never use a target-dialect reserved keyword (e.g., in T-SQL: `key`, `order`, `date`, `user`, `identity`, `year`, `percent`, `session`, `open`, `close`) as an unquoted column/table alias or identifier. Always bracket/quote any alias that could collide (`AS [Order]` in T-SQL, backticks in MySQL, double quotes in Postgres), or simply pick a non-colliding alias name.
- 🔴 **ANGULAR/JS ASYNC SCOPE GUARDRAIL**: when generating Angular (or any JS/TS) code with async callbacks, always use arrow functions for `.subscribe()`, `.then()`, `.pipe()` operator, and other async callbacks inside a class, so `this` correctly resolves to the enclosing component/service/directive instance — never a plain `function() {...}` callback in that position. Always unsubscribe from long-lived Observables in `ngOnDestroy` (`Subscription.unsubscribe()`, `takeUntil(this.destroy$)`, or the `async` pipe) so a callback never fires against a destroyed component instance. Never shadow an outer-scope variable name inside a nested/chained API-call callback — give inner-scope variables from chained calls distinct names.

### Unit Test & Coverage Rules (MANDATORY — every story)
- 🔴 **TESTS AFTER IMPLEMENTATION, SAME RUN**: Once the story's implementation is complete, ALWAYS execute Step 11a — generate unit tests, RUN them, and iterate to the coverage target before the story is announced complete
- 🔴 **COVERAGE GATE (threshold from `.evals/config.json`)**: measure coverage on the story's new/changed code; below target → add/adjust tests and re-run within the same run until met (or surface the gap to the user with the measured % and a reason).
- 🔴 **PROOF ARTIFACTS (MANDATORY)**: from the FINAL passing run, save the raw runner output (`unit-test-run.log`), the coverage tool's **machine-readable report file** (`coverage-report.*` — lcov/xml/json/HTML), and an `evidence-manifest.md` to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/`. Evidence is the actual tool output, NOT a hand-written claim. **The coverage-report file is MANDATORY whenever the stack has coverage tooling** — run the tool with the flags that emit it (`--cov-report=xml`, `--coverageReporters=lcov`, JaCoCo report, etc.); a terminal summary alone does NOT satisfy the gate. Only when the stack genuinely has NO coverage-report tooling is the file waived — a documented, user-surfaced exception recorded in `evidence-manifest.md`, never a silent skip. Every X/X-passing and coverage-% figure reported downstream (completion message, Code Review, PR/tracker comment) MUST match these saved artifacts.

  | Metric | Target | Scope |
  |--------|--------|-------|
  | Unit Test Coverage | `unitTestCoverageMin` | All new/changed code for the story |

### API & Contract Testing Rules (MANDATORY WHEN the story touches an API layer)
- 🔴 **APPLICABILITY IS PLAN-DERIVED, AUTOMATIC**: if the story's plan includes an API Layer Generation step, this gate is MANDATORY — never skip it and never ask the user whether it applies. If the plan has no API Layer Generation step, it is N/A — state that explicitly, do not silently omit the section.
- 🔴 **ONE GATE, SIX CHECKLIST ITEMS**: functional/happy-path, response-code validation, role-based authorization (401 vs 403), error-response validation (standard format + codes), request validation (required fields/types/enums), and response contract validation (schema compliance) — generated as automated tests against the REAL endpoints, RUN, and iterated to a full pass in the SAME run as implementation, never deferred to ve or a later session.
- 🔴 **PROOF ARTIFACTS (MANDATORY)**: `api-contract-test-run.log`, the **mandatory machine-readable** `api-contract-test-report.*` (JUnit XML/JSON — run the tool with the report-emitting flag/plugin, e.g. `pytest --junitxml=...`, `jest --json --outputFile=...`; a raw log alone does NOT satisfy the gate whenever the runner supports a report), and `evidence-manifest.md` (per-endpoint checklist table) to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/`. Only a genuinely reportless runner (documented, surfaced exception) waives the report file. Every X/X-passing figure reported downstream MUST match these saved artifacts.
- 🔴 **NEVER weaken a checklist assertion to force a pass** — a genuinely inapplicable item is marked N/A with a stated reason, not silently dropped or asserted away.
- 🔴 This gate is **separate from and does not replace** ve's `/ve-implement` MANUAL API/Contract test *steps* (`.spec/aire-docs/tests/<TICKET-ID>-<title>/api-test-steps.md` / `contract-test-steps.md`) — those remain ve's independent black-box design/validation layer.

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Story Selection completed (Step 0) and the implemented story recorded in the Story Tracker
- Complete code generation plan created and approved
- All steps in the code generation plan marked [x]
- The selected story implemented according to plan
- All code generated, with unit tests generated AND executed after implementation (Step 11a)
- Unit test coverage ≥ `unitTestCoverageMin` for all new/changed code (measured and iterated to target in the same run)
- **Proof artifacts saved** to `.spec/aire-docs/implementation/code/unit-test-evidence/story-[N.M]/` — `unit-test-run.log` (raw runner output), `coverage-report.*` (the coverage tool's **mandatory** machine-readable report: lcov/xml/json/HTML), and `evidence-manifest.md` — with the reported X/X passing + coverage % matching those artifacts. Missing the coverage-report file = gate not satisfied
- **API & Contract Testing Gate applied when the story touches an API layer** — every new/changed endpoint has a passing automated test for each applicable checklist item (functional, response code, role-based authorization, error-response validation, request validation, response contract validation), with proof artifacts saved to `.spec/aire-docs/implementation/code/api-contract-test-evidence/story-[N.M]/`; explicitly marked N/A (with reason) when the story touches no API layer
- Post-implementation Story Tracker update applied (status + timestamps); tracker phase prompt presented and applied if confirmed for non-LOCAL tracked stories
- Deployment artifacts generated
- Story ready for build and verification
