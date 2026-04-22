# workspace-enforce

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## Purpose

CI gate for workspace health. Blocks merge if high-severity violations are unwaived.

## Installation

```
cp -r workspace-enforce/ <project>/.claude/skills/
```

Then commit to the project's repo.

## Provenance

Ported from `CMT_Codebase/.claude/skills/workspace-enforce/` on 2026-04-22.
