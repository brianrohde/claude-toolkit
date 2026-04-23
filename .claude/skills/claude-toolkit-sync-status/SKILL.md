---
name: claude-toolkit-sync-status
description: This skill should be used when the user asks to "check sync status", "compare repos to toolkit", "/claude-toolkit-sync-status", or names one or more repo paths to audit against the claude-toolkit. Runs scripts/sync_status.py to produce a read-only IN_SYNC / TOOLKIT_NEWER / PROJECT_NEWER / DIVERGED report across skills, hooks, and rules for one or more destination repos. Byte-level comparison with CRLF normalization; uses git mtimes to decide which side is newer. Does not mutate anything -- recommends /claude-toolkit-pull or /claude-toolkit-push as follow-ups.
---

# claude-toolkit-sync-status

## Purpose

Read-only multi-repo audit of synchronization state between one or more destination projects and the canonical `claude-toolkit`. Reports per-subtree (`skills`, `hooks`, `rules`) which components are in sync, which side is ahead, which have diverged, and what exists only on one side.

This is the bulk companion to `/claude-toolkit-diff`. `/claude-toolkit-diff` focuses on the current project; this skill accepts any number of explicit repo paths and runs the same comparison against each.

## Trigger

`/claude-toolkit-sync-status [repo-path ...] [--type skills|hooks|rules]`

Examples:
- `/claude-toolkit-sync-status` -- audit current directory.
- `/claude-toolkit-sync-status C:\dev\thesis-manifold` -- audit one repo.
- `/claude-toolkit-sync-status C:\dev\thesis-manifold C:\dev\pta-cbp-parser` -- audit multiple.
- `/claude-toolkit-sync-status --type skills C:\dev\thesis-manifold` -- scope to skills only.

## Algorithm

Delegates to `<toolkit>/scripts/sync_status.py`. The script:

1. Resolves the toolkit via `$CLAUDE_TOOLKIT` or script location.
2. For each repo + subtree (`skills`, `hooks`, `rules`):
   - Enumerates component folders on both sides.
   - For overlapping components, computes a byte-level tree hash with CRLF -> LF normalization.
   - If hashes differ, consults `git log -1 --format=%at --` on both sides to decide which copy is newer. Buckets: `TOOLKIT_NEWER`, `PROJECT_NEWER`, `DIVERGED` (only when both git mtimes are absent).
   - Lists toolkit-only and project-only components separately.
3. Prints one block per repo.

Does not touch the filesystem beyond reads. Does not modify git state.

## Output shape

```
========== <repo-name> vs toolkit ==========
toolkit: <path>
repo:    <path>

--- skills ---
IN_SYNC        (n): ...
TOOLKIT_NEWER  (n): ...
PROJECT_NEWER  (n): ...
DIVERGED       (n): ...
Toolkit-only   (n): ...
Project-only   (n): ...

--- hooks ---
(same)

--- rules ---
(same)
```

## Recommended follow-ups

- `TOOLKIT_NEWER` entry -> `/claude-toolkit-pull <name> <repo>` to refresh.
- `PROJECT_NEWER` entry -> `/claude-toolkit-push <name>` from the repo to promote.
- `DIVERGED` entry -> open both files manually and reconcile.
- `Project-only` entry -> candidate for `/claude-toolkit-push` if general-purpose.
- `Toolkit-only` entry -> candidate for `/claude-toolkit-pull` if relevant.

## Failure modes

- Toolkit not found -> ask user, don't guess.
- Repo missing `.claude/` -> skipped with a note.
- No git history on a side -> comparison is low-confidence (falls back to "whichever has any git mtime").
- Mixed line endings -> normalized before byte check; not flagged.

## Invocation

```
python <toolkit>/scripts/sync_status.py <repo-path> [<repo-path> ...] [--type skills|hooks|rules]
```
