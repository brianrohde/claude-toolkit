---
paths:
  - "**"
---

# Tooling Issues Workflow

**Purpose**: `.claude/logs/tooling-issues.jsonl` is the source of truth for Windows/OneDrive/tooling problems. `docs/tooling-issues.md` is rebuilt from JSONL.

## Authority & Flow
1. **JSONL is authoritative**: `.claude/logs/tooling-issues.jsonl` contains all issues with consistent schema
2. **Markdown is derived**: `docs/tooling-issues.md` is rebuilt from JSONL (never edit manually)
3. **Schema**: Each JSONL entry has `issue_num, category, symptom_short, symptom, cause, solution, timestamp`

## Triggers
When Brian says: `update tooling`, `log tooling issue`, `tooling update`, `add tooling issue` → invoke `/log_errors` skill to extract and append to JSONL. Then rebuild markdown.

## Record When
- Tool failed (Write, Edit, Bash, python -c, etc.) non-obviously
- Windows/OneDrive/CRLF/encoding caused silent error
- Workaround or safe pattern replaces naive approach
- Environment constraint affects future plans
- New symptom/better fix for existing issue

## Don't Record
- Business logic bugs
- One-off data quality issues
- Python stdlib obvious errors

## Adding to JSONL
Use `/log_errors` skill. It will:
1. Scan conversation for error→solution sequences
2. Create new entry with next available `issue_num`
3. Deduplicate via `symptom_short` field
4. Append to `.claude/logs/tooling-issues.jsonl`
5. Trigger markdown rebuild

## JSONL Entry Format
```json
{
  "timestamp": "2026-04-17T18:53:53.123456+00:00",
  "issue_num": 33,
  "category": "Category/Subcategory",
  "symptom_short": "abbreviated key 3-5 words",
  "symptom": "Full description of what went wrong",
  "cause": "Why this happens",
  "solution": "How to fix or avoid it"
}
```

## Markdown Format (Auto-Generated)
Do NOT edit markdown manually. It regenerates from JSONL.

## Cheatsheet Rule
When adding new category: update `docs/CHEATSHEET.md` reference to tooling-issues too.
