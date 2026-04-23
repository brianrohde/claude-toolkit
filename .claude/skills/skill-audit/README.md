# Skill Audit

Comprehensive audit and comparison of Claude skill ecosystem across global and project-level installations.

## What It Does

Analyzes your entire skill landscape:
- Discovers skills in global directories (`~/.claude/skills/`, `~/.agents/skills/`)
- Audits project-level skills (`.claude/skills/`, `.agents/skills/` per repo)
- Compares metadata (name, description, triggers, dependencies)
- Detects duplicate/similar skills by description similarity (not just names)
- Maps settings.json hooks and environment variable dependencies
- Generates matrix views with progressive disclosure
- Suggests migration paths (promote, consolidate, archive, share)

## Quick Start

### Single Project Audit
```
skill-audit: audit my skills in pta-cbp-parser vs global
```

### Compare Multiple Projects
```
skill-audit: compare skills across ~/project-a, ~/project-b, ~/project-c vs global
```

### Find Duplicates
```
skill-audit: find duplicate or similar skills in my ecosystem
```

### Domain-Specific Audit
```
skill-audit: audit testing-related skills
skill-audit: show all deployment skills globally and in my projects
```

## Output Format

### Level 1: Availability Matrix
Simple table showing which skills exist where:

```
| Skill Name | Global | Project A | Project B | Status |
|---|---|---|---|---|
| skill-x    | [X]    | [X]       |           | SHARED |
| skill-y    | [X]    |           | [X]       | SHARED |
| skill-z    |        | [X]       | [X]       | MULTI_PROJECT |
```

### Level 2: Metadata Summary (on request)
- Brief descriptions
- Sync status (DUPLICATED, SHARED, GLOBAL_ONLY, PROJECT_ONLY, MULTI_PROJECT)
- Trigger examples

### Level 3: Full Details (expandable)
- Complete descriptions
- All triggers (from SKILL.md and settings.json)
- Dependencies (hooks, environment variables)
- File paths
- Last modified dates

## Key Features

### Smart Duplicate Detection
- Compares descriptions using token similarity (75%+ threshold)
- Finds near-duplicates even with different names
- Recommends which version to keep

### Dependency Mapping
- Extracts triggers from SKILL.md frontmatter
- Parses settings.json hooks (PreToolUse, PostToolUse, etc.)
- Shows environment variable requirements
- Warns if dependencies aren't met in target location

### Gap Analysis
- Skills used in 2+ projects but not global → promote candidate
- Global skills unused in any project → archive candidate
- Project-specific but generally useful → share candidate

### Progressive Disclosure
- Default view: Compact matrix, no context bloat
- Expand metadata: Add descriptions and triggers
- Expand full: Show paths, dependencies, dates
- User controls detail level

## Use Cases

### Onboarding New Project
Run audit to see:
- Which global skills apply to your domain
- Which project-specific skills from other repos might be useful
- Where to consolidate vs. where to add project specifics

### Refactoring Skill Ecosystem
Understand:
- What's installed where
- What's redundant (duplicates)
- What's orphaned (global but unused)
- What should be promoted (used in 2+ projects)

### Planning Skill Migrations
- Decide which project-specific skills to promote to global
- Identify consolidation opportunities
- Plan cleanup of outdated skills

### Audit for Quality
- Find outdated or archived skills
- Identify conflicting versions
- Check dependency health

## Example Workflow

```bash
# 1. Audit current project
skill-audit: audit pta-cbp-parser vs global

# 2. Review matrix and notice skill-x is in both global and project
# 3. Expand duplicates section
# 4. See recommendation: consolidate by removing project copy
# 5. Check full details to see if project version has local hooks
# 6. Copy any project-specific config to global version if needed
# 7. Remove redundant project copy
```

## Tips

- Run early in project setup to see applicable global skills
- Run before refactoring to understand impact of moving/deleting
- Compare 2-3 projects to find common patterns and reuse opportunities
- Check settings.json dependencies before moving skills between locations
- Use progressive disclosure to keep terminal output readable
- Export results or save output if building skill governance docs

## How It Works

The auditor:
1. Scans global skill directories
2. Scans specified project directories
3. Extracts metadata from SKILL.md (name, description, frontmatter)
4. Parses settings.json for hook dependencies
5. Checks for environment variable references
6. Compares descriptions to detect similar skills
7. Generates matrix with status labels
8. Produces recommendations based on usage patterns

Similarity scoring uses Python's difflib SequenceMatcher with 75% threshold to avoid false positives.

## Limitations

- Detects skills with SKILL.md only (requirement: valid frontmatter with name field)
- Similarity detection works best for skills with substantial descriptions
- Does not analyze skill implementations, only metadata
- Does not track skill versions or history

## Technical Details

- Python 3.8+
- Uses difflib for similarity scoring
- Parses YAML frontmatter from SKILL.md
- Reads settings.json hooks configuration
- Works with both `.claude/` and `.agents/` skill directories
- Progressive disclosure via markdown tables
