# git-worktree-merge

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Review and merge a worktree branch back to main. Handles diff review, overlap detection, GitHub PR guidance, and post-merge cleanup. Delegate this skill when the user says "merge", "merge back to main", "complete worktree", or "push and merge".

## Installation

```
cp -r git-worktree-merge/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/git-worktree-merge/` on 2026-04-22.
