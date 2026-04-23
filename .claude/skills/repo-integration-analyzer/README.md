# Repo Integration Analyzer Skill

A custom Claude Code skill for systematically analyzing GitHub/forked repositories to identify applicable modules, integration points, and migration paths.

## Purpose

When evaluating whether to adopt patterns, libraries, or architectural approaches from external projects (especially forked repos), this skill provides:

1. **Structured investigation workflow** — 5-step process to analyze any repository
2. **Reusable templates** — Checklists and comparison matrices (bundled)
3. **Clear naming conventions** — Avoid generic "INTEGRATION_ANALYSIS.md" files in your resources folder
4. **Phased implementation plans** — Know exactly what to integrate and in what order

## Quick Start

### For evaluating a single repo:

```
I'm evaluating fork-context-mode for integration into pta-cbp-parser.
Can you analyze the repository and tell me which modules are worth adopting?
```

Claude will:
1. Map the repository structure
2. Deep-dive into each major module
3. Assess applicability to your project
4. Produce a `CONTEXT_MODE_INTEGRATION_ANALYSIS.md` file

### For comparing two repos:

```
Compare fork-claude-mem and fork-context-mode. 
Which should I prioritize for my multi-project workflow?
Can they work together?
```

Claude will:
1. Analyze both repos
2. Create a comparison matrix
3. Recommend integration order (or pick one)
4. Produce a `CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md` file

## File Structure

```
repo-integration-analyzer/
├── SKILL.md                     ← Main skill definition (you're using this)
├── README.md                    ← This file
└── references/                  ← Bundled templates
    ├── MODULE_CHECKLIST.md      ← Investigation checklist (fill in per module)
    ├── COMPARISON_MATRIX.md     ← Side-by-side repo comparison
    └── EXAMPLE_ANALYSIS.md      ← Worked example (Claude-Mem vs Context-Mode)
```

## Key Concepts

### Module Relevance Scoring

Each module is scored ⭐ to ⭐⭐⭐⭐⭐:

- ⭐⭐⭐⭐⭐ = Must integrate immediately
- ⭐⭐⭐⭐ = High priority
- ⭐⭐⭐ = Medium priority
- ⭐⭐ = Low priority
- ⭐ = Reference only

### Naming Convention (Critical!)

Always name analysis documents explicitly:

```
✅ CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md
✅ PYTORCH_LLAMA_INTEGRATION_ANALYSIS.md
❌ INTEGRATION_ANALYSIS.md  ← Too generic
```

**Why?** Your `03 - R - Resources/` folder will accumulate dozens of analyses. Explicit names let you scan instantly.

### Output Location

Always save to: `03 - R - Resources/` (or equivalent in your para setup)

This keeps analyses out of project git trees but discoverable across all projects.

## Example Workflow

**User asks:**
> "I forked claude-mem and context-mode. Which is more applicable to pta-cbp-parser?"

**Skill does:**

1. **Map both repos** — Directory structure, main modules
2. **Deep-dive investigation** — Read CLAUDE.md, architecture docs, sample code
3. **Assessment** — Problem alignment, setup cost, cross-project value
4. **Comparison** — Side-by-side module inventory
5. **Recommendation** — Phased implementation plan

**Produces:**
- `CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md` saved to Resources folder
- Clear phasing: "Install Context-Mode first (5 min), then Claude-Mem (30 min)"
- Token cost analysis, blocker identification, cross-project applicability

---

## Using the Bundled References

### MODULE_CHECKLIST.md

Use when investigating a single module in detail. Includes:
- Purpose & location
- Dependencies (runtimes, packages, ports)
- Integration analysis (setup cost, learning curve)
- Relevance scoring
- Implementation plan

**Example:** Investigating Claude-Mem's "SDKAgent" module? Fill out one checklist per module.

### COMPARISON_MATRIX.md

Use when evaluating 2+ repos side-by-side. Includes:
- Setup comparison table
- Problem scope analysis
- Architecture & design comparison
- Token cost breakdown
- Module inventory for each repo
- Final recommendation (pick one vs use both vs neither)

**Example:** "Should I use Claude-Mem or Context-Mode?" → Use this to score both.

### EXAMPLE_ANALYSIS.md

A fully worked example (Claude-Mem vs Context-Mode) showing:
- Executive summary format
- Module breakdown with real relevance scores
- Real-world scenario showing how they work together
- Token cost calculations
- Phased implementation plan
- Decision rationale section

**Use as a template** for your own analyses.

---

## Tips for Success

### ✅ Do's

- **Be explicit with naming:** `PYTORCH_LLAMA_...` not `INTEGRATION_...`
- **Assess cross-project value:** Can other projects benefit from this pattern?
- **Document decision rationale:** Why you chose Option A over Option B
- **Phased implementation:** Break into 5-10 min chunks vs one big lift
- **Save to Resources:** Not in project folders; available across all projects

### ❌ Don'ts

- **Don't underestimate setup cost:** "Looks simple" ≠ "is simple"
- **Don't ignore dependencies:** External processes, vector DBs, system packages all add complexity
- **Don't skip the decision section:** Future-you will ask "why did we choose this?"
- **Don't use generic names:** INTEGRATION_ANALYSIS.md becomes meaningless after you have 5 of them

---

## Migrating to New Projects

Once you have a working integration analysis, it's portable to other projects:

1. **Copy the skill** → `new-project/.agents/skills/repo-integration-analyzer/`
2. **Re-run the workflow** → Same repo might apply differently in new context
3. **Reference your past analysis** → "We evaluated this in pta-cbp-parser; here's what we found"
4. **Build team knowledge** → Share analyses across team members

---

## Version History

- **v1.0.0** — Initial release
  - 5-step workflow
  - 3 bundled reference templates
  - Naming conventions + output location guidance
  - Explicit relevance scoring system

---

## Integration with Other Skills

This skill pairs well with:

- **skill-creator** — Use after analysis to turn findings into new skills
- **skill-development** — Use to document patterns as reusable workflows
- **command-development** — Use to build CLI tools around integrated modules

---

**Created:** 2026-04-17  
**Author:** Claude Code (Custom Skill for Brian's Multi-Project Workflow)
