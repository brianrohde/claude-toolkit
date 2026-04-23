# claude-toolkit-sync-status

**Tier**: beta

## Purpose

Read-only multi-repo audit: compares any number of destination repos against the toolkit and reports IN_SYNC / TOOLKIT_NEWER / PROJECT_NEWER / DIVERGED plus one-sided components. Bulk companion to `/claude-toolkit-diff` (which is single-project).

## When to use

- You maintain several projects that share toolkit skills and want a quick dashboard.
- You want to decide where to run `/claude-toolkit-pull` vs `/claude-toolkit-push` without opening every repo.
- You want to confirm a pull actually landed everywhere you expected.

## Dependencies

- Python 3.8+
- `git` on PATH (used for last-commit timestamps to decide newer side)
- The toolkit itself (located via `$CLAUDE_TOOLKIT` or the script's own repo root)

## Invocation

```
python <toolkit>/scripts/sync_status.py <repo-path> [<repo-path> ...] [--type skills|hooks|rules]
```

No arguments -> audits the current directory.

## Provenance

Extracted from an inline diff helper on 2026-04-23.
