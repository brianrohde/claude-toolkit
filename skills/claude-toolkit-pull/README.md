# claude-toolkit-pull

**Tier**: beta (newly authored 2026-04-22)

## Purpose

Sync a project's local copy of a toolkit component (skill / hook / rule) with the canonical version in `claude-toolkit/`. Library -> project direction.

## Installation

```
cp -r claude-toolkit-pull/ <project>/.claude/skills/
```

Invoke as `/claude-toolkit-pull [optional component-name]`.

## Sister skills

- `/claude-toolkit-suggestion` -- discover what's available before installing.
- `/claude-toolkit-diff` -- check sync status across all overlapping components.
- `/claude-toolkit-push` -- promote a project skill TO the toolkit (reverse direction).
- `/claude-toolkit-push` -- update an existing toolkit skill from project edits.

## Provenance

Authored on 2026-04-22 as part of the toolkit-meta family. Toolkit path resolved via env var / default search / user prompt -- no hard-coded paths.
