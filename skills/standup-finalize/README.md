# standup-finalize

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Clean and finalize the standup draft for supervisor delivery, removing internal Claude notes and archiving the source. Triggers on: "finalize standup", "clean up standup", "prepare standup for delivery", "send standup to supervisor

## Installation

```
cp -r standup-finalize/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/standup-finalize/` on 2026-04-22.

## Slash-ref rewrites applied during port

- `/draft-commit\b` -> `/git-draft-commit` (1 occurrences)
- `/init-standup\b` -> `/standup-init` (8 occurrences)
- `/log-standup\b` -> `/standup-log` (1 occurrences)
- `/finalize-standup\b` -> `/standup-finalize` (1 occurrences)
