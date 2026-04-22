---
paths:
  - "**"
---

# Plan Workflow

**Auto-mirroring enabled**: Write plans to `~/.claude/plans/` → hook auto-mirrors to `.claude/plans/plan_files/YYYY-MM-DD_<slug>.md` with timestamps.

**Plan format**: Plans auto-include YAML frontmatter:
```yaml
---
created: 2026-04-15 14:32:18
updated: 2026-04-15 15:45:22
---
# Plan Title
[content]
```

**After execution**: Manually create outcome file at `.claude/plans/outcome_files/YYYY-MM-DD_<slug>.md`:
```
# Outcome: <Title>
_Plan: plan_files/YYYY-MM-DD_<slug>.md_
_Created: YYYY-MM-DD HH:MM:SS_
_Completed: YYYY-MM-DD HH:MM:SS_

### ✅ Completed
- [what was done]

### 🔄 Adjusted
- **What**: [change] **Why**: [reason] **How**: [done instead]

### ❌ Dropped
- **What**: [item] **Why**: [reason]
```

**Rule**: No outcome file = plan not completed (instant visual check).
