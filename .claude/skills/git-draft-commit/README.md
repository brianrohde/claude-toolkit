# git-draft-commit

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Generate a ready-to-paste git commit message from the current session. Trigger whenever the user mentions committing changes, preparing a git message, or wants to submit work. Includes worktree awareness, commit discipline check, optional trailers, draft PR reminder, and session summary. Works in any git repo — collaborative features activate automatically when a multi-person context is detected.

## Installation

```
cp -r git-draft-commit/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/git-draft-commit/` on 2026-04-22.
