---
name: plan-update-all
trigger_phrases:
  - "update plan"
  - "log plan outcome"
  - "finalize plan"
  - "plan is done"
  - "plan completed"
  - "document plan outcome"
description: Log and finalize a completed plan by documenting what was completed, adjusted, or dropped. Automatically relocates and renames misplaced plans to conform to the YYYY-MM-DD_<short-slug>.md naming convention.
compatibility:
  tools_required:
    - Read
    - Write
    - Bash
  os: any
  note: Works with both global and project-specific plan directories
---

# Update Plan Skill

Finalize a completed or adjusted plan by logging its outcome and ensuring proper file organization. This skill implements the plan update workflow defined in `.claude/rules/trigger-plan-workflow.md`.

## When to Use

Use this skill **after executing a plan** to document:
- **What was completed** — tasks implemented as originally planned
- **What was adjusted** — changes made during execution (and why)
- **What was dropped** — items deferred, out of scope, or superseded

This creates an audit trail for future reference and allows the plan system to track execution fidelity across your project.

**Typical scenarios:**
- You've finished a refactoring plan and want to log what changed mid-execution
- A multi-phase plan completed with some phases deferred
- A planning session ended with discovered constraints that shifted scope
- You want to close a plan file and create an outcome record

## Invocation

```bash
/plan-update-all-all
/plan-update-all-all <plan-name-or-partial-filename>
/plan-update-all-all YYYY-MM-DD_my-plan-slug
```

If no plan name is provided, Claude searches for recently-touched plans in `.claude/plans/`.

## How It Works

This skill implements a four-step workflow:

### Step 1: Locate the Plan File

The skill searches for your plan in these locations (in order):
1. `<project-root>/.claude/plans/plan_files/` — primary location for new plans
2. `<project-root>/.claude/plans/` — fallback for plans not yet reorganized
3. `~/.claude/plans/` — global plans (if referenced in project context)

### Step 2: Relocate if Misplaced

If a plan is found in the global `~/.claude/plans/` directory, it is moved to the project's `.claude/plans/` directory to keep all project work together.

### Step 3: Rename if Needed

If the filename does not follow the standard naming convention, it is renamed:
- **Format:** `YYYY-MM-DD_<short-slug>.md`
- **Example:** `2026-04-15_system-a-refactor.md`
- **Rules:**
  - Date must be `YYYY-MM-DD` (the plan creation date or today's date)
  - Slug should be 2–4 words, lowercase, hyphenated
  - No spaces or special characters in slug

### Step 4: Append Outcome Section

The skill appends a new `## Outcome` section to the plan file with the structure below.

## Outcome Section Format

Copy and fill this template into your plan file:

```markdown
---

## Outcome

_Completed: YYYY-MM-DD_

### ✅ Completed
- Task or goal that was fully implemented
- Another completed item
- List only items done as originally planned

### 🔄 Adjusted
- **What**: Feature A was split into two phases
  **Why**: Discovered dependency on System B, required sequencing
  **How**: Implemented Phase 1 now, Phase 2 deferred to next sprint

- **What**: API endpoint timeout increased from 5s to 10s
  **Why**: Stress test revealed p99 latencies at 8s under load
  **How**: Tuned timeout and logged issue for infra optimization

### ❌ Dropped
- **What**: Performance profiling with py-spy
  **Why**: Out of scope — superseded by built-in perf metrics
  
- **What**: Backward compatibility layer for v1 clients
  **Why**: No active v1 users; deferred to next major release

### Notes
- The refactor surfaced three schema inconsistencies (logged as GH issues #42–44)
- Team agreed on revised naming convention mid-execution (see linked PR)
- Next iteration should front-load dependency analysis
```

**Omit sections if there is nothing to record.** For example, if a plan executed perfectly with no adjustments or dropped items, only include the `✅ Completed` section.

## File Locations and Conventions

### Directory Structure

All plan files live in the **project's own directory**:

```
<project-root>/
├── .claude/
│   ├── plans/
│   │   ├── plan_files/          # New plans (YYYY-MM-DD_<slug>.md)
│   │   ├── outcome_files/       # Outcomes linked to plan_files/
│   │   └── README.md            # Plan system documentation
```

### Naming Conventions

- **Plan files:** `YYYY-MM-DD_<short-slug>.md`
- **Outcome files:** `YYYY-MM-DD_<short-slug>.md` (mirrors plan filename in `outcome_files/` directory)
- **Slug guidelines:**
  - 2–4 words maximum
  - Lowercase only
  - Hyphens to separate words
  - No spaces, underscores, or special characters
  - Examples: `system-a-refactor`, `thesis-chapter-3-draft`, `code-review-process`

### Example Plan Lifecycle

1. **Created:** `2026-04-10_system-refactor.md` in `.claude/plans/plan_files/`
2. **Executed:** You run the plan over 3 days, discover adjustments
3. **Logged:** You run `/plan-update-all-all system-refactor`
4. **Result:** Plan file gains `## Outcome` section; a mirrored outcome entry is created at `.claude/plans/outcome_files/2026-04-10_system-refactor.md`

## Common Workflows

### Workflow: Quick Plan Completion

You've just finished a small focused plan with no surprises:

```
/plan-update-all-all my-plan-name
```

Skill will:
1. Locate and open `my-plan-name` 
2. Ask you to confirm the outcome summary
3. Append `## Outcome` with `✅ Completed` items only
4. Save and notify you of the updated file location

### Workflow: Complex Multi-Phase Execution

You've completed a plan with significant adjustments and dropped phases:

```
/plan-update-all-all YYYY-MM-DD_big-refactor
```

Skill will:
1. Locate the plan file
2. Guide you through each section (Completed, Adjusted, Dropped)
3. Help you articulate **What**, **Why**, and **How** for each adjustment
4. Append the full `## Outcome` section
5. Create an outcome mirror file in `outcome_files/`

## Integration with Project Workflow

This skill connects to:
- **`.claude/rules/trigger-plan-workflow.md`** — Plan creation, naming, and outcome documentation standards
- **`docs/project-state.md`** — Frozen decisions and plan execution context
- **`/git-draft-commit`** skill — Uses outcome files to generate accurate commit messages

## Examples

### Example 1: Simple Plan with All Completed

**Plan file:** `.claude/plans/plan_files/2026-04-10_add-logging.md`

**Original plan:** Add structured logging to three modules

**Outcome appended:**

```markdown
## Outcome

_Completed: 2026-04-12_

### ✅ Completed
- Added structured logging to auth module
- Added structured logging to database module
- Added structured logging to cache module
- Updated log configuration documentation
```

### Example 2: Complex Plan with Adjustments

**Plan file:** `.claude/plans/plan_files/2026-04-05_thesis-chapter-2-draft.md`

**Original plan:** Write 3000 words on methodology, 2000 words on data sources, outline results section

**Outcome appended:**

```markdown
## Outcome

_Completed: 2026-04-14_

### ✅ Completed
- Wrote 3200 words on methodology (exceeded target for clarity)
- Wrote 2000 words on data sources as planned
- Supervisor feedback integrated throughout

### 🔄 Adjusted
- **What**: Results section outline expanded to full draft (1500 words)
  **Why**: Discovered early that outline alone wouldn't capture nuance needed for supervisor review
  **How**: Drafted full section instead of outline; saves revision cycle

- **What**: Added 4-figure diagram set for methodology
  **Why**: Supervisor requested visual explanation of experimental design
  **How**: Created figures using Mermaid; embedded in chapter

### ❌ Dropped
- **What**: Peer review round before supervisor submission
  **Why**: Schedule compression; supervisor offered inline feedback instead
  **How**: Submitted directly to supervisor with TODOs marked for revision

### Notes
- Supervisor approved methodology approach in live feedback session (2026-04-13)
- Results section will require one more revision cycle post-supervisor feedback
- Next chapter planning should budget extra time for figures
```

## Tips for Effective Outcomes

1. **Be specific:** "Fixed bug" → "Fixed race condition in cache invalidation by adding mutex lock"
2. **Link decisions:** "Changed approach" → link to the GitHub issue, PR, or decision doc that prompted the change
3. **Note surprises:** Document unexpected discoveries; they inform future planning
4. **Track deferred work:** Dropped items should reference where they'll be picked up (GitHub issue, future sprint, etc.)
5. **Use the Notes section:** Add meta-commentary for your future self — what did you learn about your planning process?

## Troubleshooting

**Plan file not found:**
- Check that the plan name or partial filename matches your file
- Verify the file exists in `.claude/plans/plan_files/` or `.claude/plans/`
- Provide the full filename if partial match fails

**Filename needs renaming:**
- The skill will suggest a rename to `YYYY-MM-DD_<slug>.md` format
- You can accept the suggestion or provide a custom slug

**Outcome section already exists:**
- If the plan already has a `## Outcome` section, the skill will ask whether to append or update
- Choose update to replace with a new outcome summary
- Choose append to add additional phases/iterations

---

**Related:** `.claude/rules/trigger-plan-workflow.md` | `/git-draft-commit` | `docs/project-state.md`
