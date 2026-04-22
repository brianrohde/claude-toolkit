---
name: standup-log
description: |
  Append a timestamped session entry to the standup draft, classifying work as PRIMARY 
  (thesis deliverables) or SECONDARY (infrastructure/tooling). Maintains date/priority/time 
  hierarchy for session work tracking.
trigger_phrases:
  - log standup
  - log session to standup
  - add to standup
  - record progress
  - standup entry
  - append standup
  - log this session
compatibility:
  required_tools:
    - Read (read existing standup_draft.md)
    - Write (append new entries)
    - Bash (get current timestamp, verify file paths)
  file_dependencies:
    - project_updates/standup_draft.md (created if missing)
  models:
    - haiku (default, sufficient for timestamp logic)
  environment:
    - Windows/Unix compatible
    - Date format: YYYY-MM-DD, Time format: HH-MM-SS
---

# Log Standup

Record your completed work from this session into the project's progress log, maintaining 
a disciplined, timestamped history of what was accomplished.

## When to Use

- **End of each work session** — Record what was done toward thesis deliverables
- **Mid-session breakpoints** — If switching between major tasks (e.g., writing → infrastructure)
- **Before git commits** — Standup entries pair with commit messages to document intent
- **Progress tracking** — Build a session-by-session record visible to supervisors and reviewers
- **Context switching** — When returning to a project later, your standup log explains continuity

## Usage

```
/standup-log
```

The skill will:
1. Review your session to determine what was accomplished
2. Classify work as PRIMARY (thesis-focused) or SECONDARY (tooling/infrastructure)
3. Append a timestamped entry to `project_updates/standup_draft.md`
4. Maintain proper date/priority/time ordering

## How It Works

This skill implements the session logging workflow for the CBS Master Thesis project:

### Step 1: Reconstruct Session Work
Review the conversation context to understand what was accomplished:
- What files were read, edited, or created?
- Were thesis sections updated?
- Did you solve infrastructure/tooling problems?
- Were new features or agents added?

### Step 2: Determine Priority Classification

**PRIMARY** — Thesis writing deliverables (count these first):
- Chapter or section drafting/editing (Chapters 1–7)
- Literature synthesis and integration
- Figure drafts or appendices
- Research questions refinement
- Methodology decision documentation
- Results/analysis updates

**SECONDARY** — Infrastructure, tooling, and agent work (track after PRIMARY):
- Agent code creation or fixes
- Repository restructuring
- Skill development or updates
- Documentation/README updates
- Git workflow improvements
- Configuration or environment setup

### Step 3: Get Current Time

The skill captures the current time in `HH-MM-SS` format (24-hour, UTC if applicable).

### Step 4: Append to Progress Log

Insert the entry under the correct date and priority section in `project_updates/standup_draft.md`.

## Entry Format & Structure

Entries use a **hierarchical structure**: date → priority → time.

### Standard Hierarchy

```
## Progress Log

### YYYY-MM-DD                           ← Create once per day; reuse if exists
#### [PRIMARY]                           ← Include if primary work done this session
##### HH-MM-SS — <Session Title>
- <specific accomplishment, 1–2 lines>
- <another accomplishment, 1–2 lines>

#### [SECONDARY]                         ← Include only if secondary work done
##### HH-MM-SS — <Session Title>
- <infrastructure change or fix, 1–2 lines>
```

### Complete Example

```
## Progress Log

### 2026-04-15
#### [PRIMARY]
##### 10-30-15 — Methodology chapter outline review
- Expanded Section 3.2 (Data Collection) with ethics checklist
- Drafted 3 paragraphs on informed consent procedures
- Integrated CBS compliance feedback into architecture diagram

#### [SECONDARY]
##### 11-45-22 — Repository refactoring
- Moved Chapter 2 outline to new thesis/sections/ directory
- Updated repository_map.md to reflect file moves
- Fixed git pre-commit hook to skip .pyc files

### 2026-04-14
#### [PRIMARY]
##### 14-20-08 — Literature synthesis session
- Added 7 new papers to References section (APA 7)
- Cross-referenced papers with Research Questions v2
- Drafted bullets for Chapter 5 (System A/B Comparison)

##### 16-55-33 — Results chapter prep
- Created outline for Chapter 6 with 5 main subsections
- Identified 3 gaps needing additional experimentation
```

## Ordering Rules

**Date headings** (`### YYYY-MM-DD`):
- **Descending order** — most recent date at the top of the log
- New dates are added above existing dates

**Priority sections** (`#### [PRIMARY]` / `#### [SECONDARY]`):
- **PRIMARY always before SECONDARY** within a date
- Create only if work exists in that category that day

**Time entries** (`##### HH-MM-SS`):
- **Ascending order** — earliest timestamp first within a priority group
- Timestamps reflect when work started or when session was logged

## Content Guidelines

### Be Specific
- ✅ "Updated Section 2.1 (Background) with 2 new paragraphs on data ethics"
- ❌ "Did some writing"

- ✅ "Fixed git hook to skip OneDrive cache files"
- ❌ "Infrastructure work"

### Keep Bullets Tight
- 1–2 lines per bullet
- Focus on "what changed" not "how it was done"
- Name the specific chapter, section, file, or agent affected

### Naming Conventions

**Session titles** (`<Session Title>`):
- Use sentence case
- Examples: "Methodology chapter refinement", "Literature integration", "Agent debugging"
- Optional: Include the task type in parentheses for clarity
  - (writing), (research), (refactoring), (bug fix), (documentation)

**Accomplishment bullets**:
- Start with verb: "Added", "Updated", "Fixed", "Created", "Reviewed", "Drafted", "Integrated"
- Include file/section name: "Chapter 3", "repository_map.md", "System A agent"
- One concept per bullet

## Rules & Constraints

### Classification Rules
- **PRIMARY** = thesis writing deliverables (chapters, literature synthesis, figures, research contribution)
- **SECONDARY** = infrastructure, tooling, agent code, configuration — **only after PRIMARY tasks logged**
  - Exception: If a tooling issue blocks thesis writing, it may be logged as PRIMARY
- Never omit or combine priorities incorrectly

### File Management
- File path: `project_updates/standup_draft.md` (relative to repository root)
- Created automatically if missing (populated with header)
- Plain Markdown format, UTF-8 encoding
- No binary or special characters in timestamps

### Time Format
- Must be 24-hour format: `HH-MM-SS` (00:00:00 to 23:59:59)
- Must be hyphen-separated (not colons) to avoid Markdown heading conflicts
- Example: `15-30-45` (3:30:45 PM)

### Deduplication
- Never log the same accomplishment twice in the same session
- If re-running the skill in the same minute, append new entries rather than duplicating

## Example Workflow

**Scenario:** You've spent 2 hours writing and another 30 minutes fixing a bug in an agent.

**Reconstruction:**
- Hours 1–2: Drafted Section 4.1 on System A methodology, reviewed supervisor feedback, added citations
- Minutes 31–45: Fixed agent error handling in system_b_agent.py

**Classification:**
- PRIMARY: Section writing + citations
- SECONDARY: Agent bug fix

**Entry logged:**
```
### 2026-04-15
#### [PRIMARY]
##### 14-15-30 — System A methodology section
- Drafted 4 paragraphs for Section 4.1 (System A Design)
- Reviewed and incorporated supervisor feedback on clarity
- Added 3 APA-formatted citations to Section 4.1

#### [SECONDARY]
##### 16-45-12 — System B agent error handling fix
- Fixed null-pointer exception in error recovery path (system_b_agent.py)
- Added unit test coverage for edge case
```

## Skill Behavior

When invoked, the skill will:

1. **Prompt for session summary** — Ask you to briefly describe what was done
2. **Classify work** — Determine PRIMARY vs SECONDARY tasks from your description
3. **Verify file exists** — Create `project_updates/standup_draft.md` if needed
4. **Read current content** — Load existing entries to maintain proper ordering
5. **Insert entry** — Add timestamped entry under correct date and priority section
6. **Verify ordering** — Ensure dates descend, times ascend within priority groups
7. **Write updated file** — Save the modified standup file
8. **Confirm** — Show you the entry that was added

## Integration Points

- **Git commit workflow**: Standup entries provide context for commit messages
- **Thesis structuring**: Entries track which sections/chapters were modified
- **Session review**: End-of-session logs feed into supervisor check-ins
- **Repository map**: Entries reference files/modules in the `docs/dev/repository_map.md`

## Troubleshooting

**"Can't find project_updates/ directory"**
- The skill creates it if missing along with `standup_draft.md`

**"My entry appeared in the wrong priority section"**
- Verify you classified the work correctly (PRIMARY = thesis content, SECONDARY = tooling)
- Re-run the skill to add a corrected entry

**"Timestamps look wrong"**
- Ensure your system clock is accurate
- Timestamps are logged in HH-MM-SS (24-hour) format

**"I logged the same work twice"**
- Each run creates a new entry; if you need to edit, manually remove the duplicate from `standup_draft.md`
- Timestamps help identify duplicates (same time = likely duplicate)

## See Also

- [CLAUDE.md](../../CLAUDE.md) — Thesis workflow entry point
- [docs/project-state.md](../../docs/project-state.md) — Current project milestones and frozen decisions
- [docs/dev/repository_map.md](../../docs/dev/repository_map.md) — File-to-purpose mapping
