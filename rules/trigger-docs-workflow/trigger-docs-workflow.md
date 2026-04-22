---
paths:
  - "**"
---

# Docs Workflow

**Trigger**: `/docs-update-all` reviews session and updates relevant documents in order.

**Order**: 
1. Thesis sections (`thesis/thesis-writing/sections-drafts/`) — if bullet/outline changes
2. Compliance (`thesis/thesis-context/formal-requirements/`) — if checks ran
3. CLAUDE.md — if structure/rules changed
4. CHEATSHEET.md — if commands/triggers changed
5. README.md — if setup/behavior changed
6. Plans (`plan_files/`) — if plan executed (append Outcome section)
7. Rules (`.claude/rules/`) — if references staled

**Output**: List what was updated and what was skipped (with reason).

See `.claude/skills/docs-update-all/SKILL.md` for implementation.
