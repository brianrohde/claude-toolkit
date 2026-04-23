---
name: skill-audit
description: |
  Comprehensive audit of Claude skill ecosystem across global and project-level installations. Use this skill whenever you need to understand your skill distribution, find gaps, identify duplicates with different names, detect unused skills, plan migrations, or evaluate whether to create new project-specific skills vs reusing global ones. Compares ~/.claude/skills/ + ~/.agents/skills/ against one or more project repositories, generates matrix views of availability, detects description-based duplicates, checks settings.json dependencies, and recommends migration paths. Essential for skill governance, onboarding new projects, and maintaining a coherent skill ecosystem.
compatibility: |
  - Python 3.8+
  - difflib (stdlib)
  - json, os, pathlib (stdlib)
---

# Skill Audit: Comprehensive Skill Ecosystem Comparator

## What This Skill Does

Provides visibility into your Claude skill ecosystem:
1. **Discovers** all skills in global directories (`~/.claude/skills/`, `~/.agents/skills/`) and project directories (`.claude/skills/`, `.agents/skills/`)
2. **Analyzes** metadata (name, description, triggers, dependencies) from SKILL.md frontmatter and settings.json
3. **Detects duplicates** by comparing descriptions using similarity scoring (not just by name)
4. **Generates a matrix view** showing which skills exist where, with progressive disclosure
5. **Suggests migrations** (e.g., "Skill X is in Project A—consider copying to Project B")
6. **Identifies gaps** (e.g., "Global skill Y isn't used in any project")
7. **Checks dependencies** (settings.json hooks, triggers, environment variables)

## When to Use

Invoke this skill when you:
- **Onboard a new project** — See which global skills apply, which other projects have relevant skills
- **Refactor your skill ecosystem** — Understand what's installed where and what's redundant
- **Plan skill migrations** — Decide whether to promote project-specific skills to global or vice versa
- **Audit for quality** — Find outdated, unused, or duplicated skills
- **Compare repositories** — See how skill usage differs across projects

## How to Use

### Basic Audit (Single Repository)
```
skill-audit: audit my skills in ~/project-name [vs global]
```
Shows:
- All skills in the project (`.claude/skills/` + `.agents/skills/`)
- All global skills
- Comparison matrix
- Recommendations

### Compare Multiple Repositories
```
skill-audit: compare skills across projects A, B, C [vs global]
```
Shows:
- Skills in each project
- Gaps and overlaps
- Migration suggestions

### Detailed Duplicate Detection
```
skill-audit: find duplicate or similar skills in my ecosystem
```
Compares descriptions across all installed skills to find near-duplicates.

### Focus on a Specific Domain
```
skill-audit: audit testing-related skills in my ecosystem
```
Filters to skills matching a keyword or pattern.

## Output Format

### Matrix View (Progressive Disclosure)

**Level 1: Availability Matrix** (always shown)
```
| Skill Name          | Global | Project A | Project B | Status      |
|---|---|---|---|---|
| react-testing       | ✓      | ✓         | ✗         | Duplicated  |
| deploy-to-vercel    | ✓      | ✗         | ✗         | Global only |
| tariff-field-insp   | ✗      | ✓         | ✓         | Shared proj |
```

**Level 2: Metadata Summary** (on request)
- Name, sync status (duplicated/unique/global-only/project-only)
- Brief description (one-liner)
- Location(s) where installed

**Level 3: Full Details** (on click/expand)
- Full description
- Triggers (from SKILL.md frontmatter or detected from settings.json)
- Dependencies (hooks, environment variables)
- Path(s) where installed

### Migration Recommendations

Shown at the bottom:
```
## Migration Suggestions

- **Promote to global**: tariff-field-insp is used in 2+ projects → move to ~/.agents/skills/
- **Consolidate**: react-testing exists in both global and Project A → remove redundant copy
- **Share**: log-errors is project-specific but relevant to Project B → copy to Project B
- **Archive**: old-skill hasn't been updated in 6+ months → consider removing
```

### Duplicate Detection Report

When near-duplicates found (similarity > 75%):
```
## Similar Skills Detected

- **react-testing** ↔ **testing-react** (90% similar)
  Description: "React component and hook testing patterns with Testing Library and Vitest"
  Recommend: Keep react-testing (more recent), remove testing-react
```

## Key Features

### Smart Duplicate Detection
- Compares descriptions using token-based similarity (not just substring matching)
- Shows similarity score and recommends which to keep
- Highlights naming variations (e.g., "test-react" vs "react-testing")

### Dependency Mapping
- Extracts triggers from SKILL.md YAML frontmatter
- Parses settings.json hooks (PreToolUse, PostToolUse, etc.)
- Shows which skills require environment variables or external tools
- Warns if dependencies aren't met

### Gap Analysis
- Shows skills that exist only globally (no project uses them)
- Shows skills unique to one project that might be useful elsewhere
- Identifies "orphaned" skills (no recent activity)

### Progressive Disclosure
- **Default**: Simple matrix with status
- **Expand metadata**: Add description + triggers
- **Expand full**: Show paths, dependencies, last modified date
- No context bloat — user controls detail level

## Example Workflow

1. Run basic audit: `skill-audit: audit pta-cbp-parser vs global`
2. Review matrix view and migration suggestions
3. Expand "duplicates" section to see which to consolidate
4. Expand a specific skill to see triggers and dependencies
5. Copy recommended skills to/from projects based on findings

## Tips

- Run at project creation to see what global skills apply
- Run before refactoring to understand impact of moving/deleting a skill
- Compare 2-3 projects at once to find common patterns
- Use progressive disclosure to keep output readable (don't dump all details upfront)
- Check settings.json dependencies before moving a skill — you may need to migrate configuration too
