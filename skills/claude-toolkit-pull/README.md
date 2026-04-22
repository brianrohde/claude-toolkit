# claude-toolkit-pull

**Tier**: beta (newly authored 2026-04-22; v0.2.0 added group/destination/fuzzy)

## Purpose

Pull skills, groups, or named components from `claude-toolkit/` into a project. Two modes:

- **Local**: `/claude-toolkit-pull foundational` -> install into the current working directory.
- **Remote**: `/claude-toolkit-pull foundational ~/some-other-repo` -> install into the named project (useful when working from inside the toolkit and fanning out to other projects).

Per-skill, the algorithm checks if the destination already has a corresponding skill via:
1. **Exact name** match.
2. **Known rename** (consults `skills/RENAMES.md`).
3. **Fuzzy match** (description + folder-name token similarity).

For each match it shows a diff and asks `overwrite / replace-and-rename / install-alongside / skip`. Pass `--force-all` to auto-accept.

## Installation

```
cp -r claude-toolkit-pull/ <project>/.claude/skills/
```

Invoke as `/claude-toolkit-pull [target ...] [destination] [--force-all]`.

## Sister skills

- `/claude-toolkit-push` -- promote a project skill TO the toolkit (project -> toolkit).
- `/claude-toolkit-suggestion` -- discover what's available before installing.
- `/claude-toolkit-diff` -- check sync status across all overlapping components.

## Provenance

Authored on 2026-04-22 as part of the toolkit-meta family. Replaces the earlier
single-skill-only `claude-toolkit-update`. v0.2.0 added group/destination/fuzzy support
backed by `scripts/install.py`.

Toolkit path resolved via env var `$CLAUDE_TOOLKIT` / default search (`~/claude-toolkit/`)
/ user prompt -- no hard-coded paths.
