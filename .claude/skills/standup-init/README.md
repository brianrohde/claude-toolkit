# standup-init

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

Initialize a new standup draft for the next supervisor meeting. Automatically carries over unchecked tasks, backlog items, and performance snapshots. Trigger phrases include "init standup", "initialize standup", "start new standup", "next meeting prep", "/standup_done", or immediately after a supervisor meeting concludes. Use this skill to prepare the next meeting's task structure by archiving the completed meeting and setting up fresh PRIMARY and SECONDARY task sections.

## Installation

```
cp -r standup-init/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/standup-init/` on 2026-04-22.

## Slash-ref rewrites applied during port

- `/draft-commit\b` -> `/git-draft-commit` (3 occurrences)
- `/init-standup\b` -> `/standup-init` (7 occurrences)
- `/log-standup\b` -> `/standup-log` (7 occurrences)
