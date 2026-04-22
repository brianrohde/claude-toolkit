---
name: docs-update-all
description: >
  Comprehensive documentation sync workflow that reviews the current session and 
  updates all affected project documents in validated order. Ensures thesis sections, 
  compliance records, CLAUDE.md, cheatsheet, README files, plans, and rules stay 
  synchronized with codebase changes.
---

# Update All Docs

Synchronize all living project documentation after completing significant work, structural changes, or documentation passes. This skill implements the complete docs-workflow from `.claude/rules/trigger-docs-workflow.md`.

---

## Quick Start

```
/docs-update-all
```

**No arguments required.** The skill auto-detects what changed this session and updates only affected documents.

---

## When to Use This Skill

Use `/docs-update-all` when you:

- **Complete major work**: After finishing a chapter, refactoring session, or feature implementation
- **Change project structure**: After moving files, renaming modules, or reorganizing directories
- **Update frozen decisions**: After making architectural or process decisions that need recording
- **Add new rules or conventions**: After establishing new trigger phrases, formatting standards, or workflows
- **Before committing**: To ensure documentation matches the code about to be committed
- **After running compliance checks**: When CBS requirements validation or integrity gates produce new findings
- **After editing CLAUDE.md or rules**: To cascade changes to all dependent documents
- **At session end**: As part of wrap-up workflow to log all session outputs

**Do NOT use** if only reading or exploring code without making changes.

---

## Trigger Phrases

The skill activates when you use any of these phrases:

- `update all docs`
- `update documentation`
- `sync docs`
- `refresh all project docs`
- `documentation pass`
- `docs sync`
- `update the docs`

---

## Compatibility

**Required tools:**
- `Read` — Load document contents for review and updates
- `Write` — Persist updated documents to disk
- `Grep` — Search for stale references across files

**File system access required:**
- Read: `docs/`, `.claude/rules/`, `.claude/plans/`, `project_updates/`
- Write: All of the above locations

**Git integration:**
- Does not require git operations; complements `git status` and `/git-draft-commit`
- Works on any branch; output can be committed separately

---

## How It Works

The skill processes documents in this strict order, updating only those affected by this session:

### Phase 1: Session Record — `project_updates/standup_draft.md`

**When to update:**
- Code was written, refactored, or deleted
- Configuration or tooling was modified
- Workflow or rule changes were made
- New findings or blockers were documented

**Action:** Append session changes to standup draft with timestamp and summary.

**Example entry:**
```
## 2026-04-15 14:30 — Docs Workflow Expansion (30min)
- Rewrote update-all-docs.md with trigger phrases, compatibility section
- Added "When to use" guidance and expanded examples
- Updated repository_map reference in trigger-docs-workflow.md
```

---

### Phase 2: Thesis Sections — `thesis/thesis-writing/sections-drafts/`

**When to update:**
- Bullet points were expanded with new content
- Outline structure was changed (renumbered, reorganized, or split)
- New subsections were added to a chapter stub
- Prose was converted from draft bullets (mark as approved ✅)

**Action:** Update affected section files with new bullets, mark prose passages with status.

**Files checked:**
- `thesis/thesis-writing/sections-drafts/00_abstract.md`
- `thesis/thesis-writing/sections-drafts/01_introduction.md`
- `thesis/thesis-writing/sections-drafts/02_literature_review.md`
- `thesis/thesis-writing/sections-drafts/03_methodology.md`
- `thesis/thesis-writing/sections-drafts/04_system_a.md` through `13_*.md` (all system sections)

**Example output:**
```
✅ 01_introduction.md — expanded RQ definitions (5 new bullets)
⏭️  02_literature_review.md — skipped (no new citations added)
```

---

### Phase 3: Compliance — `thesis/thesis-context/formal-requirements/`

**When to update:**
- CBS compliance checks ran (with pass/fail/review results)
- Integrity gate produced findings
- New compliance notes or exceptions were documented
- Requirements mapping was revised

**Action:** Update compliance tracking files with check results and sign-off.

**Files checked:**
- `thesis/thesis-context/formal-requirements/cbs_guidelines_notes.md`
- `thesis/thesis-context/formal-requirements/compliance.md`
- `thesis/thesis-context/formal-requirements/compliance_report_20260315.md`

**Example output:**
```
✅ cbs_guidelines_notes.md — added 2026-04-15 check results
⏭️  compliance_checklist.md — skipped (no checks run this session)
```

---

### Phase 3.5: Tooling Issues — `docs/tooling-issues.md`

**When to update:**
- Tool failures were encountered and fixed (Write, Edit, Bash, pip, venv)
- Windows/OneDrive/CRLF bugs were debugged and workarounds applied
- Environment constraints (Python version, package compatibility) were discovered
- LaTeX, Pandoc, or build system issues were resolved
- Package installation or dependency conflicts occurred

**Action:** Add new issue entry to the registry with symptom, cause, solution, and key lesson learned.

**Files checked:**
- `docs/tooling-issues.md` (main registry)

**Issue format:**
```markdown
## Issue N: <short title>
**Symptom**: <failure appearance>
**Cause**: <root cause>
**Solution**: <safe pattern or fix>
**Key lesson**: <rule to carry forward>
```

**Example output:**
```
✅ tooling-issues.md — added Issue 5 (LangGraph venv corruption)
⏭️  tooling-issues.md — skipped (no tool failures this session)
```

---

### Phase 5: CLAUDE.md — Project Hub

**When to update:**
- New module or function was added
- Project structure or phase changed
- New rule file was created or referenced
- Frozen decision was made
- Workflow commands changed
- Quick references became stale

**Action:** Update navigation structure, frozen decisions, Quick Start order, and workflow table.

**Example output:**
```
✅ CLAUDE.md — added new /docs-update-all workflow description
```

---

### Phase 6: CHEATSHEET.md — Command Reference

**When to update:**
- CLI flags or command syntax changed
- Trigger phrases were added or renamed
- Make commands were added or updated
- Workflow recipes changed
- New shell aliases or shortcuts were created

**Action:** Update command table, add new recipes, mark deprecated items.

**Example output:**
```
✅ CHEATSHEET.md — added /docs-update-all trigger phrase list
```

---

### Phase 7: README.md — Setup & Overview

**When to update:**
- Installation or setup steps changed
- Major architecture was refactored
- User-facing behavior changed
- Dependencies were added/removed
- Project scope shifted

**Action:** Update setup section, architecture diagram (if applicable), feature list.

**Example output:**
```
⏭️  README.md — skipped (no user-facing changes)
```

---

### Phase 8: README_builder.md — Builder Agent Docs

**When to update:**
- Builder agent behavior or capabilities changed
- New builder-specific commands were added
- Architecture of the builder layer was refactored
- Builder usage patterns were documented

**Action:** Update agent capabilities, usage examples, integration notes.

**Example output:**
```
⏭️  README_builder.md — skipped (no builder changes)
```

---

### Phase 9: Plan Files — `.claude/plans/`

**When to update:**
- Plan was actively discussed, executed, or partially implemented
- New plan was created
- Plan title or structure was changed
- Plan file was moved to `YYYY-MM-DD_<short-slug>.md` format

**Action:** Append `## Outcome` section to executed plans; move misplaced plans to correct naming convention.

**Plan format (outcome):**
```markdown
## Outcome

**Status:** Completed / Partially completed / Abandoned

**Timestamp:** 2026-04-15 14:30 (completed)

### ✅ Completed
- Rewrote update-all-docs.md with improved trigger phrases
- Added compatibility and "When to use" sections

### 🔄 Adjusted
- **What:** Extended line count to 400-500 instead of 350
  **Why:** Better documentation requires more space
  **How:** Expanded all sections with examples and clearer guidance

### ❌ Dropped
- None this session
```

**Example output:**
```
✅ 2026-04-15_docs-workflow-refresh.md — appended Outcome section
✅ 2026-04-14_integration-safety-audit.md — moved from global to plans/
⏭️  2026-04-13_*.md — skipped (plan still in progress)
```

---

### Phase 10: Rules — `.claude/rules/`

**When to update:**
- Rule trigger phrases were changed
- File paths or references in rules became stale
- New rule was created
- Rule behavior was modified

**Action:** Review all `.claude/rules/*.md` files for stale references; update file paths, trigger examples, and deprecated patterns.

**Files reviewed:**
- `context-token-optimization.md`
- `one-off-execution.md`
- `repository-map-reference.md`
- `tooling-issues-workflow.md`
- `trigger-docs-workflow.md`
- `trigger-git-commit-workflow.md`
- `trigger-plan-workflow.md`
- Any other `.md` files in `.claude/rules/`

**Example output:**
```
✅ trigger-docs-workflow.md — updated to reference expanded update-all-docs.md
⏭️  context-token-optimization.md — skipped (no stale refs found)
```

---

## Output Format

After processing all ten phases, the skill produces a summary table:

```
=== Documentation Sync Summary ===

📝 Docs Updated:
  ✅ standup_draft.md — session work logged
  ✅ thesis sections — 01_introduction.md, 03_methodology.md updated
  ⏭️  compliance — skipped (no checks run)
  ✅ tooling-issues.md — added Issue 5 (LangGraph venv corruption)
  ✅ CLAUDE.md — workflow table updated
  ✅ CHEATSHEET.md — new trigger phrases added
  ⏭️  README.md — skipped (no user-facing changes)
  ⏭️  README_builder.md — skipped
  ✅ plans — 1 outcome appended, 2 files moved
  ✅ rules — 2 stale references fixed

📊 Total: 7 updated, 3 skipped
⏱️  Completed in 3 min 45 sec
🔗 Ready to stage for commit: git add docs/ .claude/ project_updates/ CLAUDE.md CHEATSHEET.md README.md
```

---

## Workflow Integration

This skill is part of the **Thesis Production System** and works alongside:

- **`/git-draft-commit`** — Generates commit messages from session + standup records
- **`/write-section`** — Converts bullets to prose (outputs feed into Phase 2)
- **`/update-outline`** — Modifies thesis structure (triggering Phase 2 updates)
- **`/standup-log`** — Manual standup logging (feeds Phase 1)

**Typical flow:**
```
1. /write-section 02_lit_review
   ↓ (outputs approved prose)
2. /docs-update-all
   ↓ (syncs all docs)
3. /git-draft-commit
   ↓ (stages files)
4. git push
```

---

## Common Issues & Solutions

**Q: "Skill says 'no changes detected' but I did work"**
- The skill may not have access to in-memory context. Manually mention what changed: "I updated thesis intro and added two new papers."

**Q: "Updated documents but got 'write permission denied'"**
- Check file permissions in `project_updates/`, `docs/`, `.claude/`. Ensure write access on your machine.

**Q: "Plan file not moved to correct naming format"**
- Plans must follow `YYYY-MM-DD_<slug>.md` naming. The skill auto-renames during Phase 8.

**Q: "CLAUDE.md Quick Start order doesn't match my workflow"**
- Edit CLAUDE.md manually to reorder, then `/docs-update-all` will preserve that order.

---

## Notes & Best Practices

- **Run before committing**: Use `/docs-update-all` → `/git-draft-commit` → `git add` → `git push` workflow
- **Skip full sync on minor edits**: You can manually edit single files (e.g., CHEATSHEET.md) without invoking this skill
- **Combine with standup**: This skill auto-includes standup entries from `project_updates/standup_draft.md`
- **Plan outcomes are manual**: The skill appends the outcome section; you provide the content via `/standup-log` or manual entry

---

## See Also

- `.claude/rules/trigger-docs-workflow.md` — Complete workflow spec
- `CLAUDE.md` — Project navigation hub
- `docs/dev/repository_map.md` — File and module inventory
- `/git-draft-commit` — Generate commit messages from updated docs
- `/write-section` — Thesis writing workflow that feeds docs updates
