# Design Reference Grounding (MANDATORY — all workflows, all stages)

## Purpose

A **Design Reference** is any external artifact the user names that describes **what the new work should look like or do** — a UI/HTML prototype folder, a mockup, a wireframe, a Figma/Sketch export, a screenshot, a detailed spec document (`.docx`, `.xlsx`, `.pptx`, `.pdf`), or a reference implementation living outside the repo.

It is **NOT** the same as a Context Project artifact (captured at `planning/workspace-detection.md` Step 4.7), which describes **how the CURRENT system already works**. A design reference describes the **target state**. Both can be present at once.

> **Why this file exists**: a design reference that is *acknowledged but never opened* is worse than one never mentioned — the workflow proceeds with false confidence that it is grounded, generates code that contradicts the design, and the mismatch surfaces only as a defect after the code is written and reviewed. Every rule below exists to close that gap.

## ⛔ This guardrail is AUTOMATIC — it adds no questions, no gates, no checkpoints

**It asks the user nothing, at any stage.** No prompt, no opt-in, no `[Answer]:` tag, no approval checkpoint, no blocking gate, no "confirm before continuing". The framework's existing question set and existing gates are completely unchanged — none are added, none are extended.

This guardrail is **purely reactive and silent**: it fires only when the user *volunteers* a path, document, screenshot, or URL in input they were already giving. What it changes is not what is asked of the user — it is what the model MUST do on its own: register the reference, **actually read it**, and ground design and code against it automatically.

**When something needs the user's attention** — a reference that contradicts an approved artifact, or a capability the design shows that is outside the current scope — you **REPORT it and continue**. State it plainly in the stage's output and log it in `audit.md`. **Do NOT turn it into a question, and do NOT halt the workflow waiting for an answer.** The user can redirect you if they disagree; that is their existing prerogative at the stage's own approval point, not a new gate this guardrail introduces.

## Where the Registry Lives

`.spec/aire-docs/aire-state.md`, section `## Design References`:

```markdown
## Design References
| # | Path / Location | Type | Governs | Read? | Read At Stage |
|---|-----------------|------|---------|-------|---------------|
| 1 | <abs path to prototype> | UI prototype (Angular) | All Workbench components | ✅ | Requirements Analysis |
| 2 | <abs path to spec>.docx | Spec document | Widget + queue detail | ✅ | Requirements Analysis |
```

- **Type**: `UI prototype` / `mockup or screenshot` / `spec document` / `data reference` / `reference implementation`
- **Governs**: which requirements, stories, or components this reference is authoritative for — be specific; `all` is acceptable only when the reference genuinely covers the whole epic
- **Read?**: `✅` only once **DR-2** is satisfied. `⏳` is a **blocking** state, never a resting state.

---

## DR-1 — REGISTER every reference the user volunteers, the moment it is named (MANDATORY)

The registry is created **on first use, not by asking**. Whenever a user's input at **ANY** stage — an epic description, a clarifying-question answer, a request-changes message, a remediation comment, a pasted screenshot — names an external file path, folder path, or URL that describes the target state, you MUST **immediately** add a row to `## Design References` (creating the section if absent) and log it in `audit.md`.

There is **no stage at which references stop being registrable** — a reference volunteered during remediation is registered exactly like one named in the opening request.

**Trigger detection is mechanical, not judgement-based.** Treat as a design reference any user input containing:
- an absolute or relative filesystem path (`D:\...`, `/mnt/...`, `./design/`, `\\share\...`)
- a document filename with a spec-ish extension (`.docx`, `.xlsx`, `.pptx`, `.pdf`, `.fig`, `.sketch`, `.zip`)
- a pasted image / screenshot of intended UI
- a URL to a design tool, prototype, or shared drive

**The answer's framing does NOT matter.** "The design is already built at X", "you can refer to X", "see X for the widget names", "here's how it should look [screenshot]" are all the SAME trigger. A path given as a *statement of fact* is registered exactly like a path given as an *instruction*.

## DR-2 — READ the content. Verifying a path exists is NOT reading it. (MANDATORY)

Marking a reference `Read? ✅` requires opening its **actual content**. The following are explicitly **NOT** sufficient and MUST NOT be recorded as having read the reference:

| ❌ Not reading | ✅ Reading |
|---|---|
| Confirming the path exists on disk | Opening the files and extracting their content |
| Listing folder / component / file **names** | Opening the `.html` / `.ts` / `.tsx` / `.css` source inside those folders |
| Reading a document's table of contents or summary table | Reading the document body end-to-end |
| Viewing a screenshot and noting "it's a dropdown" | Identifying every control, grouping, state, and interaction it shows |

**For a UI prototype specifically**, you MUST open — for every component in scope — the markup, the styles, and the behaviour file (e.g. `*.component.html`, `*.component.ts`, `*.component.css`), and extract:
- the actual **control types** (is it a plain `<select>`, or a searchable grouped combobox? single-select or multi-select checkboxes?)
- **grouping, ordering, labels, icons** actually shown
- **interaction behaviour** (search/filter, click-outside-to-close, keyboard support, empty states)
- **custom CSS classes** used, and whether they exist in the live app's global styles
- any capability present in the prototype that is **outside** the current requirements/ACs — flag it, never silently build it and never silently drop it

Record what was extracted in the stage's own artifact (`requirements.md` grounding notes, `components.md`, or the code-generation plan) — not merely in `audit.md`.

## DR-3 — A binary format is never a reason to defer

`.docx` / `.xlsx` / `.pptx` cannot be opened by the Read tool. This is a **known, solved** problem, not a blocker:

- `.docx` → unzip, read `word/document.xml`, strip tags
- `.xlsx` → unzip, read `xl/sharedStrings.xml` + `xl/worksheets/sheet*.xml`
- `.pptx` → unzip, read `ppt/slides/slide*.xml`
- `.pdf` → read via the Read tool's `pages` parameter

Deferring a reference to a later stage **because of its file format** is a DR-2 violation.

## DR-4 — Read it in the stage where it is named. "Deferred to a later stage" is BANNED as an outcome.

If a user answers a clarifying question by pointing at a document ("the widget names are in `X.docx`"), that answer is **not received** until the document is read. You MUST read it before generating that stage's artifact and before closing the stage.

- ❌ Recording `Q6: C — deferred to reference doc X` and proceeding to write `requirements.md`
- ✅ Reading X **now**, folding its actual content into the answer, and writing `requirements.md` grounded in it

Never present a stage-completion message while a registered reference is still unread — but do not stop and ask about it either: **just read it, then continue**.

## DR-5 — Re-consult automatically before ANY design or code artifact (MANDATORY)

Before generating artifacts at each of these stages, re-open the registered references whose `Governs` covers the scope in hand:

| Stage | What must be re-grounded |
|---|---|
| **Application Design** | Every component in `components.md` — its real structure, controls, and interactions come from the prototype, not from invention |
| **Functional Design** | Interaction flows, states, and validation rules shown in the prototype |
| **Code Generation** (`dev-implement`, every story) | Every component the story builds |
| **`ticket-implement`** (bug / enhancement) | Any component the ticket touches |

The generated artifact (or code-generation plan) MUST state, **per component**, one of exactly two things:

```
Design reference: <path>/<file> — grounded (searchable grouped combobox, multi-select positions, icons)
Design reference: none covers this component — built from ACs only
```

Every component must carry one of those two lines. **"I already looked at that folder in an earlier stage" is NOT grounding** — earlier stages may have read only the parts within *their* scope (see DR-2's folder-names-vs-content distinction).

This is a self-check you perform and satisfy on your own. It is **not** a checkpoint, and it never pauses the workflow or prompts the user.

## DR-6 — Contradictions are REPORTED, not asked about

When a design reference contradicts an already-approved artifact (requirements, stories, ACs, or an earlier design decision), first determine which one wins using **DR-8 (Precedence)** below — the answer is NOT always "the reference". Then:

1. **Apply the DR-8 winner.**
2. **Say so plainly in the stage's output**: what each side said, which one you followed, and why (unreconciled gap vs. recorded decision). One or two lines — a statement, not a question.
3. **Do NOT halt.** Do NOT convert this into an A/B question, an `[Answer]:` tag, or an approval checkpoint. Continue the stage.
4. If the reference won, update the affected AC / `requirements.md` / story text to match what you built, per `common/requirements-traceability.md`, so the artifacts stay truthful — and record it as a reconciliation (DR-8).
5. Log the contradiction and the resolution in `audit.md`.

The user retains full control at the stage's own existing approval point — they can redirect you there. This guardrail adds no new place for them to have to intervene.

**Same rule for out-of-scope capabilities**: when a design reference shows a capability outside the current requirements/ACs, do NOT build it and do NOT silently ignore it — **state that you saw it and excluded it as out of scope**, log it, and **record the exclusion as a reconciliation (DR-8)** so no later stage re-adds it. No question.

## DR-8 — PRECEDENCE: a reconciled framework artifact outranks the raw reference (MANDATORY)

> **Why this rule exists**: DR-5 makes every later stage re-open the raw design reference. Without a precedence rule, Code Generation would re-read the prototype, see something the design stages **deliberately decided against**, and silently reintroduce it — undoing considered decisions (an excluded capability, a reduced scope model, a locally-scoped stylesheet, an accessibility or NFR constraint). That is the exact inverse of the defect DR-1…DR-5 exist to prevent, and it must not be traded for it.

**The test is whether the framework artifact has already CONSIDERED this specific point of the reference.**

| Situation | Winner | Behaviour |
|---|---|---|
| The artifact carries a **recorded reconciliation** covering this point (a deliberate deviation, exclusion, simplification, or constraint) | **The framework artifact** | Follow the artifact. Do **not** re-litigate, do **not** re-report it as a contradiction, do **not** rebuild from the reference. Note in one line that the reference differs here **by prior decision** and continue. |
| The artifact is **silent** on this point — it never saw or never addressed it | **The design reference** | Follow the reference (this is the DR-6 case), amend the artifact to match, and **record the reconciliation**. |
| The artifact **contradicts** the reference with no recorded reason | **The design reference** | Treat as unreconciled: the artifact most likely predates the reference or was written without it. Follow the reference, amend, record. |

**Recording a reconciliation.** Whenever a stage decides *against* what a reference shows — or deliberately narrows, defers, or restyles it — that decision MUST be written where a later stage will find it:

- in the artifact itself (`components.md`, `requirements.md`, the story's ACs, `nfr-design-patterns.md`), stated as a decision with its reason, and
- as a `Reconciled` row in the registry:

```markdown
## Design References
| # | Path / Location | Type | Governs | Read? | Read At Stage |
|---|-----------------|------|---------|-------|---------------|
| 1 | <path to prototype> | UI prototype | All Workbench components | ✅ | Requirements Analysis |

### Reconciliations (decisions taken AGAINST a reference — later stages MUST honour these)
| Ref # | Point in the reference | Decision | Decided At Stage | Recorded |
|-------|------------------------|----------|------------------|----------|
| 1 | Click-to-revert on the theme pill | EXCLUDED — outside ticket scope | Application Design | 2026-08-10T12:40:00Z |
| 1 | Prototype's global `.tip` / `.sec-label` CSS | Scoped to the component, not global | Application Design | 2026-08-10T12:40:00Z |
```

**At every DR-5 re-consult, read the Reconciliations table FIRST.** Any point listed there is settled — the raw reference does not reopen it. Only points *absent* from that table are grounded fresh from the reference.

**Precedence summary (highest first):**
1. A **recorded reconciliation** — a deliberate, traceable decision
2. The **design reference** — on any point no artifact has reconciled
3. The **framework artifact's generic wording** — where no reference covers the point at all

**Never** let a later stage silently reverse an earlier deliberate decision, and **never** let a generic AC restatement suppress a design detail nobody ever considered. DR-8 separates those two cases; everything else in this file assumes it has been applied.

## DR-7 — The registry survives the session

`## Design References` lives in `aire-state.md`, so it is read by every later session, every `dev-implement` run, and every `ticket-implement` run. On resume, read the section and use it — and, as everywhere else, **ask the user nothing** about it.

When a user supplies a reference **late** (e.g. during remediation, after a defect forced it), you MUST still register it, and additionally:
- assess which **already-completed** stories/components it invalidates, and **state that list** in your output and in `audit.md` — a report, not a question
- do not silently limit its application to the story currently in hand

---

## Audit Requirements

Log in `audit.md` at each of these points (base audit format plus the invoking workflow's own template fields):

1. **Registration** — the reference, its type, what it governs, and the complete raw user input that named it
2. **Reading** — what was actually extracted (controls, interactions, contradictions found) — not merely "read the design"
3. **Contradictions** — every DR-6 question asked and the user's complete raw answer
4. **Re-consult** — at Application Design and at each code-generation plan, which references were re-opened for which components

## Violation Examples (observed in real defects)

| Violation | What happened | Rule broken |
|---|---|---|
| Path confirmed to exist; only folder names listed; no file ever opened | Component built as a plain dropdown, while the prototype specified a searchable grouped combobox plus multi-select checkboxes. Found only in post-code-review remediation, after the user re-sent the path with a screenshot. | DR-2, DR-5 |
| Clarifying answer "detail is in `X.docx`" recorded as answered; the doc was read a full stage later | The doc contradicted the approved scope model and story breakdown — forcing a rewrite of requirements, stories, and 21 already-pushed tracker issues | DR-3, DR-4 |
| Design folder named at Requirements, never re-opened at Application Design | `components.md` invented component structure while an authoritative prototype sat unread | DR-5 |
| Late-supplied reference applied only to the story in hand | The prototype covered the whole epic, but only the current story was corrected; the remaining stories carried the same blind spot forward | DR-7 |
