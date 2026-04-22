---
name: standup-finalize
description: Clean and finalize the standup draft for supervisor delivery, removing internal Claude notes and archiving the source. Triggers on: "finalize standup", "clean up standup", "prepare standup for delivery", "send standup to supervisor"
trigger_phrases:
  - finalize standup
  - clean up standup
  - prepare standup for delivery
  - send standup to supervisor
  - finalize the standup
  - ready standup for supervisor
compatibility:
  required_tools:
    - Read
    - Write
    - Grep
  optional_tools: []
  cwd_requirement: absolute paths preferred
---

# Finalize Standup

**Purpose**: Clean and finalize the standup draft document for supervisor delivery by removing internal Claude meta-notes and archiving the source with all notes intact.

This skill implements the finalize standup workflow from `.claude/rules/trigger-standup-workflow.md`, ensuring supervisor-ready documentation while preserving internal decision records.

---

## When to Use

- **After a standup meeting cycle**: You've completed work items, updated `standup_draft.md` with post-meeting notes and progress, and want to deliver a clean report to your supervisor
- **End of a project phase**: You need to produce a formal, finalized update document showing all completed work without internal Claude comments
- **Regular supervisor check-ins**: You want to transform the working draft into a professional, clean meeting summary
- **Before archiving work**: You're moving to a new sprint or phase and need a permanent, clean record of work completed

Do NOT use this skill if:
- You haven't yet updated `standup_draft.md` with post-meeting work
- You want to preserve the draft in its current state (use `/standup-init` only)
- You need to make edits to the draft before finalizing (edit `project_updates/standup_draft.md` first)

---

## Usage

Invoke in chat:

```
/standup-finalize
```

Or use trigger phrases in conversation:
- "finalize standup"
- "clean up standup"
- "prepare standup for delivery"
- "ready the standup for my supervisor"

---

## How It Works

The skill executes the following steps:

### Step 1: Read Draft

Reads `project_updates/standup_draft.md`, which contains:
- Pre-meeting status and goals
- Work completed during the session
- Post-meeting notes and decisions
- Internal Claude meta-notes (marked with `_(... Claude ...)_` patterns)

### Step 2: Strip Meta-Notes

Removes all internal Claude annotations using a Grep-based cleanup:
- Pattern: `_(... Claude ...)_` or similar meta-comment blocks
- Preserves: All work descriptions, status updates, progress, and substantive content
- Result: Clean, professional content ready for supervisor review

### Step 3: Overwrite Meeting File

Writes the cleaned content to a timestamped meeting document:
- **File**: `project_updates/YYYY-MM-DD_HH-MM_update_meeting_N.md`
- **Purpose**: This becomes the final supervisor copy with full Progress Log and all post-meeting updates
- **Note**: This file replaces the pre-meeting skeleton version with the comprehensive final version

Example filename: `project_updates/2026-04-15_14-32_update_meeting_1.md`

### Step 4: Archive Source

Writes the **unmodified** `standup_draft.md` (with all meta-notes intact) to:
- **File**: `project_updates/standup_draft_archive.md`
- **Purpose**: Permanent backup and historical record of internal decision-making
- **Usage**: Serves as the carry-over source when `/standup-init` starts the next meeting cycle

---

## Output

### Files Created/Modified

**Supervisor Copy** (clean, professional):
```
project_updates/YYYY-MM-DD_HH-MM_update_meeting_N.md
```
- Contains: All work completed, status updates, progress notes
- Excludes: Internal Claude meta-notes
- Recipients: Your supervisor (delivered as the formal meeting summary)

**Archive Copy** (internal record):
```
project_updates/standup_draft_archive.md
```
- Contains: Verbatim `standup_draft.md` with all meta-notes and internal annotations
- Excludes: Nothing (everything preserved)
- Recipients: Stored locally for session history and carry-over to next `/standup-init`

### Workflow Continuity

After finalization:
- `project_updates/standup_draft.md` **remains unchanged** in the working directory
- The draft is ready for the next cycle: when you run `/standup-init`, it uses the archive as the carry-over source
- No action required — the skill handles file movement and cleanup automatically

---

## Data Flow Diagram

```
standup_draft.md (working, with meta-notes)
    ↓
    [Strip meta-notes]
    ↓
project_updates/YYYY-MM-DD_HH-MM_update_meeting_N.md
    (supervisor copy, clean)
    
standup_draft.md (original)
    ↓
    [Archive verbatim]
    ↓
project_updates/standup_draft_archive.md
    (historical record, all notes preserved)
```

---

## Important Notes

- **Draft is preserved**: The original `standup_draft.md` is not modified; archiving copies it, not moves it
- **Supervisor transparency**: The final meeting document shows all work done with full Progress Log and decision history (without meta-notes)
- **No re-running**: Finalize once per cycle; `/standup-init` handles prep for the next meeting
- **File naming**: Meeting files are named with timestamp and sequential counter (N) to prevent overwrites
- **Carry-over**: The archive file (`standup_draft_archive.md`) is automatically used by `/standup-init` for the next session's context

---

## Example Session

**Before finalization:**
```
project_updates/standup_draft.md
├─ Pre-meeting status
├─ Completed work items
├─ _(Claude: Noted decision to refactor parser)_
├─ Progress notes
└─ _(Claude: Meta-note about session flow)_
```

**After finalization:**
```
project_updates/2026-04-15_14-32_update_meeting_1.md ← Sent to supervisor
├─ Pre-meeting status (clean)
├─ Completed work items (clean)
├─ Progress notes (clean)
└─ Full Progress Log

project_updates/standup_draft_archive.md ← Internal archive
├─ [Same as original draft with all meta-notes]
```

---

## Related Skills

- **`/standup-init`** — Initialize a new standup draft for the next meeting cycle (reads the archive created by this skill)
- **`/standup-log`** — Log new standup entries manually to the draft between meetings
- **`/git-draft-commit`** — Generate a git commit message from session work (often run in parallel with finalization)

---

## Troubleshooting

**Problem**: "File not found" when trying to finalize
- **Check**: Does `project_updates/standup_draft.md` exist? Create it first with `/standup-init` if missing.

**Problem**: Meta-notes not being stripped
- **Check**: Verify meta-note format matches `_(... Claude ...)_`. If your notes use different syntax, update the Grep pattern in the skill.

**Problem**: Supervisor file overwritten unexpectedly
- **Note**: This is intentional — finalization replaces the pre-meeting skeleton with the complete final version. Archive backups are preserved in `standup_draft_archive.md`.

**Problem**: Want to edit before finalizing
- **Solution**: Edit `project_updates/standup_draft.md` directly before running this skill. Changes will be reflected in the supervisor copy.

---

## Implementation Notes

The skill uses:
- **Read**: Load `project_updates/standup_draft.md` and any archive files
- **Grep**: Pattern-match and remove meta-notes (`_(... Claude ...)_`)
- **Write**: Output cleaned content to meeting file and archive to backup

All file paths use absolute paths to avoid cwd ambiguity in the Claude Code execution environment.

---

**Last Updated**: 2026-04-15
**Related Rules**: [trigger-standup-workflow.md](../.claude/rules/trigger-standup-workflow.md)
