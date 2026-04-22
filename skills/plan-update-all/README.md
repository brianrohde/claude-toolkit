# plan-update-all

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Log and finalize a completed plan by documenting what was completed, adjusted, or dropped. Automatically relocates and renames misplaced plans to conform to the YYYY-MM-DD_<short-slug>.md naming convention.

## Installation

```
cp -r plan-update-all/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/plan-update/` on 2026-04-22.

Renamed during port: `plan-update` -> `plan-update-all` (category-first convention).

## Slash-ref rewrites applied during port

- `/draft-commit\b` -> `/git-draft-commit` (2 occurrences)
- `/update-plan\b` -> `/plan-update-all` (6 occurrences)
- `/plan-update\b` -> `/plan-update-all` (6 occurrences)
