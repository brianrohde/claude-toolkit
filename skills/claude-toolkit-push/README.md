# claude-toolkit-push

**Tier**: beta (newly authored 2026-04-22)

## Purpose

Promote a project-local component to the claude-toolkit library. Auto-detects:
- **NEW** (component doesn't exist in toolkit yet) -> first-time promotion with project-specific reference scrubbing.
- **UPDATE** (component already in toolkit) -> shows diff, requires user confirmation, then overwrites.

Mirrors `git push` semantics. Project -> toolkit direction.

## Installation

```
cp -r claude-toolkit-push/ <project>/.claude/skills/
```

Invoke as `/claude-toolkit-push [optional component-name]`.

## Sister skills

- `/claude-toolkit-pull` -- pull a toolkit component into a project (toolkit -> project).
- `/claude-toolkit-suggestion` -- discover what's available in the toolkit.
- `/claude-toolkit-diff` -- check sync status across all overlapping components.

## Provenance

Authored on 2026-04-22 as part of the toolkit-meta family. Replaces the earlier
`claude-toolkit-push` (NEW-only) and `claude-toolkit-push` (UPDATE-only) skills,
which were merged into this single bidirectional `git push`-style tool.

Toolkit path resolved via env var `$CLAUDE_TOOLKIT` / default search (`~/claude-toolkit/`)
/ user prompt -- no hard-coded paths.
