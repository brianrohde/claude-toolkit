# claude-toolkit-suggestion

**Tier**: beta (newly authored 2026-04-22)

## Purpose

Recommend which toolkit components fit the current project based on its tech stack, file types, and existing skills. Optional keyword filter. Read-only -- does not install.

## Installation

```
cp -r claude-toolkit-suggestion/ <project>/.claude/skills/
```

Invoke as `/claude-toolkit-suggestion [optional keyword]`.

## Sister skills

- `/claude-toolkit-update` -- pull a toolkit component into a project (library -> project).
- `/claude-toolkit-suggestion` -- discover what's available in the toolkit.
- `/claude-toolkit-diff` -- check sync status across all overlapping components.
- `/claude-toolkit-new-skill` -- promote a project skill TO the toolkit (first-time).
- `/skill-update-workflow` -- update an EXISTING toolkit skill from project edits.

## Provenance

Authored on 2026-04-22 as part of the toolkit-meta family. Toolkit path resolved via env var `$CLAUDE_TOOLKIT` / default search (`~/claude-toolkit/`) / user prompt -- no hard-coded paths.
