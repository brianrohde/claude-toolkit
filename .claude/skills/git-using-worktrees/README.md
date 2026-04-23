# git-using-worktrees

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Use when starting a new Claude Code session that needs isolation — creates a git worktree under worktrees/ with the project branch naming convention, safety checks, and branch mismatch detection. Pairs with /git-draft-commit for cleanup and audit.

## Installation

```
cp -r git-using-worktrees/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/using-git-worktrees/` on 2026-04-22.

Renamed during port: `using-git-worktrees` -> `git-using-worktrees` (category-first convention).

## Slash-ref rewrites applied during port

- `/draft-commit\b` -> `/git-draft-commit` (6 occurrences)
