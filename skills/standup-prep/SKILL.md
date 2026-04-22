---
name: standup-prep
description: |
  Prepares the standup draft for supervisor meetings by drafting the Non-Technical Summary and producing a clean presentation-ready copy. Triggered by: "prep standup", "prepare standup", "prepare for standup", "get ready for supervisor meeting", "before supervisor meeting".
compatibility:
  required_tools:
    - Read
    - Write
    - Grep
  input_files:
    - project_updates/standup_draft.md
  output_files:
    - project_updates/YYYY-MM-DD_HH-MM_update_meeting_N.md (presentation-ready copy)
---

# Prep Standup

Prepares the standup draft for the supervisor meeting by drafting the Non-Technical Summary and producing a clean presentation-ready copy.

## Trigger Phrases

Use this skill with any of these commands:

- `/standup-prep`
- "prep standup"
- "prepare standup"
- "prepare for standup"
- "get ready for supervisor meeting"
- "before supervisor meeting"

## When to Use

Run this skill **just before your supervisor meeting** to finalize the standup document for presentation. It transforms your working `standup_draft.md` (which contains meta-notes and internal tracking) into a clean, professional document suitable for discussion with your CBS thesis supervisor.

**Typical workflow:**
1. Throughout the week: maintain `standup_draft.md` with updates, blockers, and meta-notes
2. Before the meeting: run `/standup-prep`
3. During the meeting: optionally edit the output file in real-time, or take notes directly in `standup_draft.md`
4. After the meeting: run `/standup-finalize` to create the final supervisor copy with post-meeting edits

## How It Works

This skill implements the pre-meeting preparation workflow in four steps:

### Step 1: Read Source Document

Read `project_updates/standup_draft.md` to gather all current progress, blockers, and task status.

### Step 2: Draft Non-Technical Summary

Claude writes a concise, supervisor-friendly summary suitable for a non-technical CBS thesis supervisor. This summary should:

- **Highlight key accomplishments** since the last meeting (1-2 sentences max per item)
- **Mention major blockers or risks** (e.g., data access delays, architectural decisions pending approval, external dependencies)
- **Keep to 3-5 bullet points** — only the most important points
- **Use clear, non-technical language** — avoid jargon; explain technical terms if unavoidable
- **Frame progress in thesis context** — connect weekly work to thesis objectives and milestones
- **Be honest about setbacks** — supervisors appreciate transparency about delays or pivots

The Non-Technical Summary is written directly into `standup_draft.md` under a section titled `## Non-Technical Summary Draft` (or appended to existing draft if section exists).

**Tone guidance:**
- Professional but conversational
- Assume the supervisor is intelligent but not a specialist in your technical domain
- Focus on "what we accomplished and why it matters" rather than "how we built it"
- Use dates for clarity (e.g., "this week we..." or "since 2026-04-08...")

### Step 3: Strip Meta-Notes and Create Finalized Copy

Remove all internal Claude notes and metadata to produce a clean presentation document:

- **Delete** all lines matching `_(... Claude ...)_` patterns (internal notes)
- **Delete** lines 2-3 of the header (the "Updated incrementally..." and "Manual trigger..." lines)
- **Preserve** the Non-Technical Summary, all Progress Log entries, Task Status, and Blockers sections
- **Write** the cleaned content to `project_updates/YYYY-MM-DD_HH-MM_update_meeting_N.md`

The output filename uses:
- `YYYY-MM-DD` = today's date
- `HH-MM` = current time (24-hour format)
- `N` = the meeting number (increment from previous meetings)

Example: `project_updates/2026-04-15_14-30_update_meeting_5.md`

### Step 4: Confirm Readiness

Report that the presentation-ready document is created and located at the output path. Provide the user with:

- Full path to the new document
- Confirmation of the meeting number
- Reminder about the meeting workflow (edit during meeting, finalize after)
- Next steps (`/standup-finalize` after the meeting)

## Important Workflow Notes

**`standup_draft.md` is the source of truth:**
- This skill does NOT modify `standup_draft.md` — it retains all meta-notes
- All internal tracking (Claude notes, timestamps, incremental updates) stays in the draft
- If changes are needed, always edit `standup_draft.md` afterward, then re-run `/standup-prep` to regenerate the presentation copy

**Output document is presentation-ready:**
- The `YYYY-MM-DD_HH-MM_update_meeting_N.md` file is clean and ready to show or discuss in the meeting
- It contains the full Progress Log so supervisors see all activity since the last meeting
- It includes the Non-Technical Summary for quick context-setting

**During the meeting:**
- Brian can edit the output file directly if needed (e.g., to mark items as discussed)
- Or, make changes to `standup_draft.md` during/after the meeting (new to-dos, clarifications, etc.)

**After the meeting:**
- Run `/standup-finalize` which will create the final version including any post-meeting edits from `standup_draft.md`
- This ensures the final document reflects what was actually discussed and decided

## Example Workflow

```
Monday-Thursday: Maintain standup_draft.md
  - Add daily progress bullets
  - Note blockers and decisions
  - Include meta-notes and timestamps

Friday 9:50 AM (before 10 AM meeting):
  /standup-prep
  → Reads standup_draft.md
  → Drafts Non-Technical Summary
  → Creates 2026-04-15_09-55_update_meeting_5.md (clean, ready to present)

Friday 10:00-10:30 AM (during meeting):
  - Share the prep document
  - Discuss progress, blockers, next steps
  - Optionally take notes in the output file or in standup_draft.md

Friday 10:35 AM (after meeting):
  - Edit standup_draft.md with any final notes from the meeting
  /standup-finalize
  → Creates final archived copy with all post-meeting updates
```

## Related Skills

- **`/standup-finalize`** — Run after the supervisor meeting to create the final archived copy with any post-meeting edits
- **`/standup-log`** — Log a quick standup entry at the end of a session (e.g., "added 200 lines to System A agent")

## Common Questions

**Q: Can I edit the output file during the meeting?**
A: Yes. Brian can edit the presentation document in real-time during the meeting, or note changes in `standup_draft.md` afterward. Either way, run `/standup-finalize` after the meeting.

**Q: What if the Non-Technical Summary isn't quite right?**
A: Edit the summary directly in `standup_draft.md` under `## Non-Technical Summary Draft`, then re-run `/standup-prep` to regenerate the presentation copy.

**Q: Should I delete the output files after the meeting?**
A: No. Keep them as a meeting record. They are named with timestamps so new meetings won't overwrite old ones.

**Q: Can I use this skill more than once before a meeting?**
A: Yes. Each run creates a new timestamped file. The last one you create before the meeting is the one to use. Old timestamped files can be kept as a record of what was prepared.
