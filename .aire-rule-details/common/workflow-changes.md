# Mid-Workflow Changes and Stage Management

## Overview

Users may request changes to the execution plan or stage execution during the workflow. This document provides guidance on handling these requests safely and effectively.

---

## Types of Mid-Workflow Changes

### 1. Adding a Skipped Stage

**Scenario**: User wants to add a stage that was originally skipped

**Example**: "Actually, I want to add user stories even though we skipped that stage"

**Handling**:
1. **Confirm Request**: "You want to add User Stories stage. This will create user stories and personas. Confirm?"
2. **Check Dependencies**: Verify all prerequisite stages are complete
3. **Update Execution Plan**: Add stage to `execution-plan.md` with rationale
4. **Update State**: Mark stage as "PENDING" in `aire-state.md`
5. **Execute Stage**: Follow normal stage execution process
6. **Log Change**: Document in `audit.md` with timestamp and reason

**Considerations**:
- May need to update later stages that could benefit from new artifacts
- Existing artifacts may need revision to incorporate new information
- Timeline will be extended

---

### 2. Skipping a Planned Stage

**Scenario**: User wants to skip a stage that was planned to execute

**Example**: "Let's skip the NFR Design stage for now"

**Handling**:
1. **Confirm Request**: "You want to skip NFR Design. This means no NFR patterns or logical components will be incorporated. Confirm?"
2. **Warn About Impact**: Explain what will be missing and potential consequences
3. **Get Explicit Confirmation**: User must explicitly confirm understanding of impact
4. **Update Execution Plan**: Mark stage as "SKIPPED" with reason
5. **Update State**: Mark stage as "SKIPPED" in `aire-state.md`
6. **Adjust Later Stages**: Note that later stages may need manual setup
7. **Log Change**: Document in `audit.md` with timestamp and reason

**Considerations**:
- Later stages may fail or require manual intervention
- User accepts responsibility for missing artifacts
- Can be added back later if needed

---

### 3. Restarting Current Stage

**Scenario**: User is unhappy with current stage results and wants to redo it

**Example**: "I don't like these user stories. Can we start over?"

**Handling**:
1. **Understand Concern**: "What specifically would you like to change about the stories?"
2. **Offer Options**:
   - **Option A**: Modify existing artifacts (faster, preserves some work)
   - **Option B**: Complete restart (clean slate, more time)
3. **If Restart Chosen**:
   - Archive existing artifacts: `{artifact}.backup.{timestamp}`
   - Reset stage checkboxes in plan file
   - Mark stage as "IN PROGRESS" in `aire-state.md`
   - Clear stage completion status
   - Re-execute from beginning
4. **Log Change**: Document reason for restart and what will change

**Considerations**:
- Existing work will be lost (but backed up)
- May need to redo dependent stages
- Timeline will be extended

---

### 4. Restarting Previous Stage

**Scenario**: User wants to go back and redo a completed stage

**Example**: "I want to change the architectural decision we made earlier"

**Handling**:
1. **Assess Impact**: Identify all stages that depend on the stage to be restarted
2. **Warn User**: "Restarting Application Design will require redoing: the system-level design stages and Code Generation. Confirm?"
3. **Get Explicit Confirmation**: User must understand full impact
4. **If Confirmed**:
   - Archive all affected artifacts
   - Reset all affected stages in `aire-state.md`
   - Clear checkboxes in all affected plan files
   - Return to the stage to restart
   - Re-execute from that point forward
5. **Log Change**: Document full impact and reason for restart

**Considerations**:
- Significant rework required
- All dependent stages must be redone
- Timeline will be significantly extended
- Consider if modification is better than restart

---

### 5. Changing Stage Depth

**Scenario**: User wants to change the depth level of current or upcoming stage

**Example**: "Let's do a comprehensive requirements analysis instead of standard"

**Handling**:
1. **Confirm Request**: "You want to change Requirements Analysis from Standard to Comprehensive depth. This will be more thorough but take longer. Confirm?"
2. **Update Execution Plan**: Change depth level in `workflow-planning.md`
3. **Adjust Approach**: Follow comprehensive depth guidelines for the stage
4. **Update Estimates**: Inform user of new timeline estimate
5. **Log Change**: Document depth change and reason

**Considerations**:
- More depth = more time but better quality
- Less depth = faster but may miss details
- Can only change before or during stage, not after completion

---

### 6. Pausing Workflow

**Scenario**: User needs to pause and resume later

**Example**: "I need to stop for now and continue tomorrow"

**Handling**:
1. **Complete Current Step**: Finish the current step in progress if possible
2. **Update Checkboxes**: Mark all completed steps with [x]
3. **Update State**: Ensure `aire-state.md` reflects current status
4. **Log Pause**: Document pause point in `audit.md`
5. **Provide Resume Instructions**: "When you return, I'll detect your existing project and offer to continue from: [current stage, current step]"

**On Resume**:
1. **Detect Existing Project**: Check for `aire-state.md`
2. **Load Context**: Read all artifacts from completed stages
3. **Show Status**: Display current stage and next step
4. **Offer Options**: Continue where left off or review previous work
5. **Log Resume**: Document resume point in `audit.md`

---

### 7. Changing Architectural Decision

**Scenario**: User wants to change from monolith to microservices (or vice versa)

**Example**: "Actually, let's do microservices instead of a monolith"

**Handling**:
1. **Assess Current Progress**: Determine how far into workflow
2. **Explain Impact**: 
   - If before the Implementation design stages: Minimal impact, just update decision
   - If after the Implementation design stages: Must redo the system-level design stages
   - If after Code Generation: Significant rework required
3. **Recommend Approach**:
   - Early in workflow: Restart from Application Design stage
   - Late in workflow: Consider if modification is feasible vs. restart
4. **Get Confirmation**: User must understand full scope of change
5. **Execute Change**: Follow restart procedures for affected stages

**Considerations**:
- Architectural changes have cascading effects
- Earlier in workflow = easier to change
- Later in workflow = consider cost vs. benefit

---

### 8. Changing the Service/Component Decomposition

**Scenario**: User wants to change how the system is decomposed after Application Design / the design stages

**Example**: "We need to split the Payment service into Payment and Billing"

**Handling**:
1. **Assess Impact**: Determine which parts have completed design/code (check the Story Tracker)
2. **Explain Consequences**:
   - Adding a service/module: extend Application Design and the system-level design artifacts
   - Removing one: redistribute functionality; affected stories may need re-implementation
   - Splitting one: redo the affected design sections and re-implement affected stories
3. **Update Design Artifacts**:
   - Modify `.spec/aire-docs/planning/application-design/` artifacts (incl. code organization strategy)
   - Update the affected system-level design artifacts under `.spec/aire-docs/implementation/design/`
4. **Reset Affected Stories**: Mark affected stories as needing (re)implementation via `dev-implement`
5. **Execute Changes**: Re-run the affected design stages, then `dev-implement` per affected story

**Considerations**:
- Affects all downstream stages for the changed areas
- May shift story dependencies — re-run the Dependency Graph if `requires` change
- Timeline impact depends on how many stories are affected

---

### 9. Adding/Removing Stories (re-run Dependency Graph)

**Scenario**: User wants to add, remove, or split stories after the Dependency Graph has been built

**Example**: "We need to split the Payment story into Payment and Billing"

**Handling**:
1. **Assess Impact**: Check the Story Tracker for which stories are already implemented (`🧪 Ready for Testing`) vs `🔵 In Development` vs `🟢 Ready for Development`.
2. **Explain Consequences**:
   - Adding story: plan and implement the new story (and map its `requires` dependencies)
   - Removing story: redistribute its functionality to other stories or drop it
   - Splitting story: implement both resulting stories
3. **Update Story Artifacts**:
   - Modify `.spec/aire-docs/planning/user-stories/stories.md`
   - Update the `## Story Tracker` in `.spec/aire-docs/aire-state.md`
   - **Re-run the Dependency Graph stage** to reassign `requires`, and rewrite `dependency-graph.yml`
   - If the story has a non-LOCAL Tracker ID, apply the **Tracker Sync Rule** (confirm-first, per `common/tracker-sync.md` Section 4); new/split stories pushed to the tracker must be linked to the **Parent Epic** recorded in `aire-state.md` `## Tracker`
4. **Reset Affected Stories**: Mark affected stories as needing (re)implementation via `dev-implement`
5. **Execute Changes**: Follow the normal per-story Code Generation process (`dev-implement`) for affected stories

**Considerations**:
- Re-running the Dependency Graph may change `requires` for downstream stories
- Verify the Doability Gate still holds for any in-progress stories
- Keep the Story Tracker and the configured tracker in sync throughout

---

## General Guidelines for Handling Changes

### Before Making Changes

1. **Understand the Request**: Ask clarifying questions about what user wants to change and why
2. **Assess Impact**: Identify all affected stages, artifacts, and dependencies
3. **Explain Consequences**: Clearly communicate what will need to be redone and timeline impact
4. **Offer Alternatives**: Sometimes modification is better than restart
5. **Get Explicit Confirmation**: User must understand and accept the impact

### During Changes

1. **Archive Existing Work**: Always backup before making destructive changes
2. **Update All Tracking**: Keep `aire-state.md`, plan files, and `audit.md` in sync
3. **Communicate Progress**: Keep user informed about what's happening
4. **Validate Changes**: Ensure changes are consistent across all artifacts
5. **Test Continuity**: Verify workflow can continue smoothly after changes

### After Changes

1. **Verify Consistency**: Check that all artifacts are aligned with changes
2. **Update Documentation**: Ensure all references are updated
3. **Log Completely**: Document full change history in `audit.md`
4. **Confirm with User**: Verify changes meet user's expectations
5. **Resume Workflow**: Continue with normal execution from new state

---

## Change Request Decision Tree

```
User requests change
    |
    ├─ Is it current stage?
    |   ├─ Yes: Can modify or restart current stage
    |   └─ No: Go to next question
    |
    ├─ Is it a completed stage?
    |   ├─ Yes: Assess impact on dependent stages
    |   |   ├─ Low impact: Modify and update dependents
    |   |   └─ High impact: Recommend restart from that stage
    |   └─ No: Go to next question
    |
    ├─ Is it adding a skipped stage?
    |   ├─ Yes: Check prerequisites, add to plan, execute
    |   └─ No: Go to next question
    |
    ├─ Is it skipping a planned stage?
    |   ├─ Yes: Warn about impact, get confirmation, skip
    |   └─ No: Go to next question
    |
    └─ Is it changing depth level?
        ├─ Yes: Update plan, adjust approach
        └─ No: Clarify request with user
```

---

## Logging Requirements

### Change Request Log Format

```markdown
## Change Request - [Stage Name]
**Timestamp**: [ISO timestamp]
**User Email**: [current session email — read live from the session context]
**Request**: [What user wants to change]
**Current State**: [Where we are in workflow]
**Impact Assessment**: [What will be affected]
**User Confirmation**: [User's explicit confirmation]
**Action Taken**: [What was done]
**Artifacts Affected**: [List of files changed/reset]

---
```

---

## Best Practices

1. **Always Confirm**: Never make destructive changes without explicit user confirmation
2. **Explain Impact**: Users need to understand consequences before deciding
3. **Offer Options**: Sometimes there are multiple ways to handle a change
4. **Archive First**: Always backup before making destructive changes
5. **Update Everything**: Keep all tracking files in sync
6. **Log Thoroughly**: Document all changes for audit trail
7. **Validate After**: Ensure workflow can continue smoothly
8. **Be Flexible**: Workflow should adapt to user needs, not force rigid process
