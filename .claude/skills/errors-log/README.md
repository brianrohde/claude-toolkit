# errors-log

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

This skill should be used when the user asks to "log errors", "log tooling issues", or "/errors-log". Scans session conversation history for tool failures, Windows/OneDrive issues, CRLF problems, and encoding errors, then logs them to .claude/logs/tooling-issues.jsonl (source of truth), triggering automatic markdown rebuild.

## Installation

```
cp -r errors-log/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/errors-log/` on 2026-04-22.

## Slash-ref rewrites applied during port

- `/draft-commit\b` -> `/git-draft-commit` (4 occurrences)
- `/log-errors\b` -> `/errors-log` (6 occurrences)
