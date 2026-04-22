# git-commit

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Execute a git commit from an approved draft message. Handles staging, PowerShell-safe commit command, and post-commit checklist. Always verify worktree isolation before committing. Pairs with /git-draft-commit (message generation) and /git-using-worktrees (workspace setup).

## Installation

```
cp -r git-commit/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/git-commit/` on 2026-04-22.

## Slash-ref rewrites applied during port

- `/using-git-worktrees\b` -> `/git-using-worktrees` (4 occurrences)
