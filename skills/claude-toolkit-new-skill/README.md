# claude-toolkit-new-skill

**Tier**: beta (newly authored 2026-04-22)

## Purpose

Promote a project-local component to the toolkit as a brand-new entry. Scrubs project-specific references, writes a generic README, commits, and pushes. Use for first-time promotion only.

## Installation

```
cp -r claude-toolkit-new-skill/ <project>/.claude/skills/
```

Invoke as `/claude-toolkit-new-skill [optional component-name]`.

## Sister skills

- `/claude-toolkit-update` -- pull a toolkit component into a project (library -> project).
- `/claude-toolkit-suggestion` -- discover what's available in the toolkit.
- `/claude-toolkit-diff` -- check sync status across all overlapping components.
- `/claude-toolkit-new-skill` -- promote a project skill TO the toolkit (first-time).
- `/skill-update-workflow` -- update an EXISTING toolkit skill from project edits.

## Provenance

Authored on 2026-04-22 as part of the toolkit-meta family. Toolkit path resolved via env var `$CLAUDE_TOOLKIT` / default search (`~/claude-toolkit/`) / user prompt -- no hard-coded paths.
