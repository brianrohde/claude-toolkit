---
name: standup-init
description: Initialize a new standup draft for the next supervisor meeting. Automatically carries over unchecked tasks, backlog items, and performance snapshots. Trigger phrases include "init standup", "initialize standup", "start new standup", "next meeting prep", "/standup_done", or immediately after a supervisor meeting concludes. Use this skill to prepare the next meeting's task structure by archiving the completed meeting and setting up fresh PRIMARY and SECONDARY task sections.
compatibility:
  tools: [Read, Write]
  requires: project_updates directory with standup infrastructure files (standup_draft.md, standup_draft_archive.md, standup_draft_formatting.md)
  tested_on: CBS Master Thesis CMT project
---

# Initialize Standup Draft

Prepare for the next supervisor meeting by creating a fresh standup draft that carries over pending work from the current meeting.

## When to use this skill

Invoke this skill when:
- **Immediately after a supervisor meeting ends** — You've logged your deliverables and next steps, and it's time to prep for Meeting N+1
- **User says "init standup"** — Shorthand to start a fresh meeting draft
- **User says "initialize standup"** — More explicit form of the same request
- **User says "start new standup"** — Beginning of a new meeting cycle
- **User says "next meeting prep"** — Prepping for the upcoming supervisor meeting
- **User says "/standup_done"** — Alias indicating the current meeting is logged and ready to move forward
- **Session context indicates a supervisor meeting just concluded** — Automatic opportunity to initialize the next draft

This skill is designed as a **post-meeting ritual**: it archives the completed meeting's work, extracts reusable context, and initializes a clean slate for the next meeting cycle.

## Why use this skill

Your supervisor meetings follow a predictable cycle: deliver on committed items, review progress, identify blockers, and agree on next deliverables. Most of the next meeting's work depends on what you **didn't finish** or what new items you committed to in the **current** meeting.

This skill:
- **Preserves continuity** — Carries all unchecked tasks so nothing falls through cracks
- **Reduces manual setup** — Auto-scaffolds the meeting structure from a template
- **Maintains performance history** — Builds cumulative snapshots of progress across all meetings
- **Prevents data loss** — Archives the current meeting before overwriting the draft

## How it works

This skill implements the standup initialization workflow and executes these steps in order:

### Step 1: Pre-flight checks
Verify that all three standup infrastructure files exist:
- `project_updates/standup_draft.md` — Current meeting's live log
- `project_updates/standup_draft_archive.md` — Historical record of all prior meetings
- `project_updates/standup_draft_formatting.md` — Template for meeting structure

If any file is missing, stop with an informative error. Do not proceed.

### Step 2: Read template
Load `standup_draft_formatting.md` as the structural base. This contains the gold-standard formatting (headers, subsection layout, example table formats) that will be reused verbatim in the new draft.

### Step 3: Read archive and extract carryover
Load `standup_draft_archive.md` and extract carryover content:
- All **unchecked PRIMARY tasks** (items marked `- [ ]`, including sub-items)
- All **unchecked SECONDARY tasks** (items marked `- [ ]`, including sub-items)
- All **backlog items** (unless explicitly marked for removal)
- The complete **Performance Snapshot table** (copy verbatim — it accumulates across all meetings)

Do NOT carry over:
- Checked items (`- [x]` or completed tasks)
- Progress Log entries (start fresh each meeting)
- Non-Technical Summary (start blank each meeting)

### Step 4: Determine meeting number
Read the meeting number from the archive header (e.g., "## Meeting 3"). Increment by 1 (e.g., "## Meeting 4").

### Step 5: Compose new draft
Combine:
1. Template structure (headers, section layout)
2. Carried-over PRIMARY tasks (sorted to top of PRIMARY section)
3. Carried-over SECONDARY tasks (sorted to top of SECONDARY section)
4. Carried-over backlog items
5. Carried-over Performance Snapshot table
6. Empty Progress Log section
7. Empty Non-Technical Summary section

### Step 6: Write and confirm
Overwrite `project_updates/standup_draft.md` with the new draft.

Output confirmation message:
```
✓ Initialized project_updates/standup_draft.md for Meeting N+1.
  Carried over X PRIMARY tasks, Y SECONDARY tasks, Z backlog items.
  Archive preserved at project_updates/standup_draft_archive.md.
```

## Carry-over rules in detail

### PRIMARY tasks
- **Definition**: High-priority deliverables committed to the supervisor
- **Carry-over rule**: All items marked `- [ ]` (unchecked), including nested sub-items
- **Drop rule**: All items marked `- [x]` (completed)
- **Example**:
  ```
  ## PRIMARY
  - [ ] Finish System A integration (carries over if unchecked)
    - [ ] Resolve pipeline config issue (carries over if unchecked)
    - [x] Deploy to staging (dropped — already completed)
  ```

### SECONDARY tasks
- **Definition**: Secondary or exploratory work; lower priority than PRIMARY
- **Carry-over rule**: All items marked `- [ ]` (unchecked), including nested sub-items
- **Drop rule**: All items marked `- [x]` (completed)
- **Example**:
  ```
  ## SECONDARY
  - [ ] Experiment with new hyperparameter (carries over)
  - [x] Document findings (dropped — done)
  ```

### Backlog items
- **Definition**: Future work, nice-to-haves, or long-term goals
- **Carry-over rule**: Carry all items **unless** you explicitly mark them for removal in the current meeting
- **Removal pattern**: Items removed by the supervisor or you during the meeting are documented but not carried
- **Example**:
  ```
  ## BACKLOG
  - [ ] Explore reinforcement learning approach
  - [ ] Write literature review chapter 4
  → All carry over unless explicitly dropped
  ```

### Performance Snapshot
- **Definition**: A table tracking metrics, progress indicators, and KPIs across meetings
- **Carry-over rule**: Copy the **entire table verbatim** — it accumulates across all meetings
- **Interpretation**: Each meeting adds a new row; previous rows remain unchanged
- **Example**:
  ```
  | Meeting | Task Completion | Papers Read | Lines Written | Notes |
  |---------|-----------------|-------------|---------------|-------|
  | 1       | 6/8 (75%)       | 4           | 250           | Good start |
  | 2       | 7/8 (87%)       | 3           | 180           | Demo blockers |
  | 3       | 8/8 (100%)      | 5           | 420           | On track |
  → All three rows persist in Meeting 4's draft
  ```

### Progress Log
- **Definition**: Session-by-session work log (created during the meeting, not carried)
- **Carry-over rule**: **Do NOT carry over** — start with an empty Progress Log section
- **Why**: Each meeting cycle has a fresh work log; archiving the prior log preserves it in the archive

### Non-Technical Summary
- **Definition**: Plain-language summary of achievements, blockers, and next steps
- **Carry-over rule**: **Do NOT carry over** — start with a blank section
- **Why**: Summaries are specific to each meeting; the prior summary is archived

## Input and customization

### Automatic input
The skill reads carrover items from the archive automatically.

### Custom input (optional)
If you dictate new PRIMARY tasks immediately after invoking the skill, they are inserted at the **top** of the PRIMARY section, above any carried-over items. Example:

**User says:** "Init standup. New tasks: Fix System B logging config, Review supervisor feedback."

**Result:**
```
## PRIMARY
- [ ] Fix System B logging config (NEW)
- [ ] Review supervisor feedback (NEW)
- [ ] Complete System A integration (CARRIED OVER)
  - [ ] Resolve pipeline config issue (CARRIED OVER)
```

## Output

The skill outputs:
1. A confirmation message with counts (X PRIMARY tasks, Y SECONDARY tasks, Z backlog items)
2. Confirmation that the archive file was preserved
3. The file path where the new draft was written: `project_updates/standup_draft.md`

Example:
```
✓ Initialized project_updates/standup_draft.md for Meeting 4.
  Carried over 5 PRIMARY tasks, 3 SECONDARY tasks, 2 backlog items.
  Archive preserved at project_updates/standup_draft_archive.md (Meeting 1-3 history).
```

## Integration with project workflow

This skill is part of the CBS Master Thesis standup system:

- **`/standup-log`** — Log session work and meeting results (run during/after a meeting)
- **`/standup-init`** — Prepare for the next meeting by archiving and resetting (run after logging is complete)
- **`/git-draft-commit`** — Bundle standup notes into git commits (run when ready to commit)

The three skills form a cycle: **Log → Initialize → Commit → Log again**.

## Troubleshooting

### "standup_draft.md not found"
The standup infrastructure hasn't been set up yet. Create these files in `project_updates/`:
1. `standup_draft.md` — Initialize with meeting headers
2. `standup_draft_archive.md` — Initialize with an empty header
3. `standup_draft_formatting.md` — Copy a template from a prior project or create manually

### "No unchecked tasks to carry over"
This is fine — your previous meeting was fully completed. The new draft will have empty PRIMARY and SECONDARY sections, ready for new work.

### "Archive is lost or corrupted"
The skill stops before overwriting. Restore from git or a backup. Never overwrite the archive without a backup.

## Files involved

| File | Purpose | Modified? |
|------|---------|-----------|
| `project_updates/standup_draft.md` | Live meeting log for Meeting N+1 | ✓ Overwritten |
| `project_updates/standup_draft_archive.md` | Historical record (Meetings 1 through N) | ✗ Read only |
| `project_updates/standup_draft_formatting.md` | Structural template | ✗ Read only |

## Detailed carry-over example

Here's a concrete example showing what carries over from one meeting to the next.

### Meeting 3's final state (before init-standup)
```
## Meeting 3

### PRIMARY
- [x] Deploy System A to production
  - [x] Test endpoint response times
  - [ ] Monitor logs for 24 hours
- [ ] Integrate System B with data pipeline
  - [ ] Fix credential handling
  - [ ] Write integration tests
- [ ] Prepare presentation slides

### SECONDARY
- [ ] Experiment with new loss function
- [x] Refactor config loader

### BACKLOG
- [ ] Explore adversarial training methods
- [ ] Write chapter 4 literature review
- [ ] Benchmark against baseline model

### Performance Snapshot
| Meeting | Task Completion | Papers Read | Lines Written | Notes |
|---------|-----------------|-------------|---------------|-------|
| 1       | 6/8 (75%)       | 4           | 250           | Initial setup |
| 2       | 7/9 (77%)       | 3           | 180           | Debugging delays |
| 3       | 8/10 (80%)      | 5           | 420           | System A demo done |
```

### Meeting 4's state (after init-standup)
```
## Meeting 4

### PRIMARY
- [ ] Monitor logs for 24 hours
- [ ] Integrate System B with data pipeline
  - [ ] Fix credential handling
  - [ ] Write integration tests
- [ ] Prepare presentation slides

### SECONDARY
- [ ] Experiment with new loss function

### BACKLOG
- [ ] Explore adversarial training methods
- [ ] Write chapter 4 literature review
- [ ] Benchmark against baseline model

### Performance Snapshot
| Meeting | Task Completion | Papers Read | Lines Written | Notes |
|---------|-----------------|-------------|---------------|-------|
| 1       | 6/8 (75%)       | 4           | 250           | Initial setup |
| 2       | 7/9 (77%)       | 3           | 180           | Debugging delays |
| 3       | 8/10 (80%)      | 5           | 420           | System A demo done |

### Progress Log
(empty, ready for Meeting 4 work)

### Non-Technical Summary
(empty, ready for Meeting 4 summary)
```

**What changed:**
- `- [x] Deploy System A...` dropped (was completed)
- `- [ ] Monitor logs...` carried (was unchecked)
- All PRIMARY and SECONDARY unchecked items carried verbatim
- All backlog items carried (none explicitly dropped)
- Performance Snapshot row for Meeting 3 preserved; ready to add Meeting 4 row
- Progress Log and Non-Technical Summary cleared

## Advanced: Handling meeting structure changes

### Adding new sections mid-meeting
If you add a new section to the meeting draft (e.g., "EXPERIMENTS" or "RISKS"), the skill carries it over on the next init if items in that section are unchecked. Example:

**Meeting 3 draft (custom section):**
```
### EXPERIMENTS
- [ ] Test new attention mechanism
- [x] Benchmark Transformer v2
```

**Meeting 4 draft (after init-standup):**
```
### EXPERIMENTS
- [ ] Test new attention mechanism
```

The checked item drops; the unchecked item carries.

### Supervisor-requested removals
If during Meeting 3, your supervisor explicitly says "remove the adversarial training item from backlog", you manually delete it from standup_draft.md **before** calling init-standup. When init-standup runs, it only carries items that exist in the archive, so removed items don't reappear.

## Common patterns and best practices

### Pattern 1: High-velocity week
You complete 80% of your work. Call init-standup:
- Most of your PRIMARY and SECONDARY sections clear
- A few unchecked items carry over
- You start the new meeting with a short "housekeeping" phase, then pivot to fresh deliverables

### Pattern 2: Blocked work
You're blocked on a dependency. Call init-standup:
- All PRIMARY items carry (they're not done, they're waiting)
- Unchecked SECONDARY items carry (you couldn't get to them)
- You start the new meeting with blocker discussion
- Once unblocked, you have a ready-to-resume list

### Pattern 3: Scope creep
Your supervisor adds new tasks during the meeting. Example:

**User says:** "Init standup. New tasks from supervisor: Data augmentation pipeline review, Finalize abstract."

**Result:**
```
### PRIMARY
- [ ] Data augmentation pipeline review (NEW from supervisor)
- [ ] Finalize abstract (NEW from supervisor)
- [ ] Monitor logs for 24 hours (CARRIED OVER)
```

The new tasks appear first, making them obvious anchors for the meeting.

### Pattern 4: Backlog evolution
Over three meetings, your backlog grows as ideas accumulate. init-standup preserves all backlog items. You can then:
- Prioritize them with your supervisor during the next meeting
- Explicitly drop items that no longer make sense
- Promote items to PRIMARY when ready

## Example: Complete multi-meeting cycle

### Week 1: Meeting 1
```
User: /standup-log → Records kickoff tasks
User: /standup-init → Prepares Meeting 2 (empty PRIMARY, fresh start)
```

### Week 2: Meeting 2
```
User: Completes first set of deliverables
User: /standup-log → Records progress, feedback
User: /standup-init → Prepares Meeting 3 with carried-over items
```

### Week 3: Meeting 3
```
User: Works through carried-over items, completes most
User: /standup-log → Records near-complete status
User: /standup-init → Prepares Meeting 4 with remaining items
```

### Week 4: Meeting 4
```
User: Finishes last items, supervisor assigns new sprint
User: /standup-log → Records completion + new deliverables
User: /standup-init → Prepares Meeting 5 with fresh tasks
```

## Integration with version control

The standup system is designed to live **outside** git commits. However, when you're ready to commit work:

**Workflow:**
```
1. /standup-log → Update standup_draft.md during/after meeting
2. /standup-init → Prepare next meeting
3. Work session → Update standup_draft.md with progress
4. /git-draft-commit → Extracts standup notes into conventional commit
5. git add, git commit → Commit the code (not standup files, typically)
```

This keeps:
- **Standup files** as living project documentation (not committed per-session)
- **Git commits** focused on code changes with context from standup notes
- **Meeting history** separate from code history (easier to review meeting outcomes independently)

## Security and data safety

### Pre-flight file checks
Before making any modifications, init-standup verifies that:
- All three infrastructure files exist and are readable
- Archive file is not empty (has prior meeting history)
- Draft file is not corrupted (valid Markdown)

If any check fails, the skill stops without touching any files.

### Backup strategy
Because init-standup overwrites standup_draft.md, the archive file (standup_draft_archive.md) is the source of truth. Always:
- Commit the archive to git regularly (weekly)
- Never manually edit the archive (let the system manage it)
- Test init-standup in a dry-run on a copy if unsure

### Recovery procedure
If you accidentally overwrite standup_draft.md:
1. Restore standup_draft_archive.md from git history
2. Re-run init-standup to recreate the draft

## Example workflow

**Session 1: Supervisor Meeting (Meeting 3)**
```
User: "Log today's work to standup" → /standup-log
Claude: Records deliverables, blockers, next steps
Result: standup_draft.md updated with Meeting 3 details
```

**Session 2: After logging is done**
```
User: "Init standup" → /standup-init
Claude: Archives Meeting 3, prepares for Meeting 4
Result: standup_draft.md refreshed with unchecked items from Meeting 3
```

**Session 3: Work session**
```
User: Completes tasks, logs progress to standup_draft.md
```

**Session 4: Ready to commit**
```
User: "Prepare a commit message" → /git-draft-commit
Claude: Includes standup notes in commit message
Result: Ready-to-paste conventional commit
```
