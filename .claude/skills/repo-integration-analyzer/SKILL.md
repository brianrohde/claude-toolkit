---
name: repo-integration-analyzer
description: Analyze two or more GitHub/forked repositories to identify applicable modules, integration points, and migration paths. Use when evaluating whether to adopt patterns, libraries, or architectural approaches from external projects. Produces structured analysis docs (TOOL_A_TOOL_B_INTEGRATION_ANALYSIS.md) with module breakdown, token costs, and phased implementation plans suitable for any future project. Works across any tech stack (Node/Python/Rust/Go).
version: 1.0.0
---

# Repository Integration Analyzer

Systematically analyze forked repositories to extract reusable patterns and integration opportunities for your current project.

## When to Use This Skill

- Evaluating whether to adopt patterns/libraries from forked repos
- Comparing two+ repositories for cross-project applicability
- Planning incremental integration of external modules
- Documenting why certain patterns are/aren't suitable
- Building decision rationale for architecture reviews

## Core Workflow

### Step 1: Repository Structure Mapping

For each repository, create a directory tree focusing on:
- **Source code structure** (`src/`, `lib/`, `modules/`)
- **Configuration files** (`.json`, `.yaml`, `.toml`)
- **Hook/plugin systems** (`hooks/`, `plugins/`, `.agents/`)
- **Skills/commands** (`skills/`, `.agents/commands/`)
- **Database/storage** (`db/`, `services/`)
- **Testing** (`tests/`, `__tests__/`)

Use `Bash` + `ls`/`find` commands to map directories. Avoid `grep` at this stage—just understand layout.

**Output:** Mental model of repo organization + key directories to investigate.

### Step 2: Deep Module Investigation

For each major module (hook system, database layer, CLI, UI, MCP tools, etc.):

1. **Read CLAUDE.md / README.md** — Understand purpose, dependencies, setup cost
2. **Read architecture docs** — Grasp data flow and design decisions
3. **Examine key files** — Sample implementation (handlers, schemas, services)
4. **Identify dependencies** — What does this module require? (external packages, runtimes, processes)

Focus on:
- What problem does this solve?
- How much setup/configuration is needed?
- Can it be used independently or does it require the full system?
- What other modules does it depend on?

**Output:** Module inventory with "relevance score" (⭐⭐⭐⭐⭐ = must-have, ⭐ = nice-to-have, 0 = not applicable).

### Step 3: Applicability Assessment

For **each relevant module**, ask:

1. **Problem alignment:** Does it solve a real problem in your project?
2. **Integration friction:** How much does it require from the existing project architecture?
3. **Setup cost:** Hours to implement + dependencies required
4. **Maintenance burden:** Is it stable or rapidly evolving?
5. **Cross-project reuse:** Can patterns from this module help other projects?

Organize findings as:
```
| Module | Effort | Benefit | Relevance | File Path |
|--------|--------|---------|-----------|-----------|
| [Name] | X min  | [What it fixes] | ⭐⭐⭐ | path/to/module |
```

### Step 4: Compare Multiple Repos (If Applicable)

If analyzing 2+ repos (e.g., Claude-Mem vs Context-Mode):

1. **List problems each solves** (different angles? overlapping?)
2. **Create comparison table** (setup cost, token savings, maintenance, learning curve)
3. **Recommend priority order** — Which to integrate first? Why?
4. **Identify synergies** — Can they work together? Are they complementary?

### Step 5: Generate Analysis Document

Produce a **single consolidated markdown file** named:

```
{REPO_A}_{REPO_B}_INTEGRATION_ANALYSIS.md
```

Or if single repo:
```
{REPO_NAME}_INTEGRATION_ANALYSIS.md
```

**Structure:**

```markdown
# [Tool A] & [Tool B]: Integration Analysis

**Date:** YYYY-MM-DD
**Status:** Analysis | Ready to Implement | Archived

## Executive Summary
- 2-3 sentences: what you're analyzing, what you recommend

## Repo Comparison
| Aspect | Repo A | Repo B |
|--------|--------|--------|

## Module Breakdown

### Repo A: [Name]

| Module | Effort | Benefit | Relevance | Path |
|--------|--------|---------|-----------|------|

### Repo B: [Name]

| Module | Effort | Benefit | Relevance | Path |
|--------|--------|---------|-----------|------|

## Recommended Integration Path

### Phase 1: [Core feature] (X min)
- What to copy/install
- Expected benefit
- Blockers

### Phase 2: [Next feature] (X min)
- ...

## Token Cost / Performance Impact
| Scenario | Before | After | Saved |
|----------|--------|-------|-------|

## What NOT to Copy
- Reason it doesn't apply
- Better alternative if available

## Reference Files

- Full repo A: `path/to/fork-repo-a/`
- Full repo B: `path/to/fork-repo-b/`
```

## Progressive Disclosure

### Level 1: Metadata (Always Loaded)
- Skill name, description, version
- When to use this skill

### Level 2: Workflow (On Trigger)
- Core 5-step process (you're reading this now)
- Example outputs
- What goes in the analysis doc

### Level 3: Bundled Resources (As Needed)

See `references/` for:
- **template_analysis.md** — Example analysis output (fill-in-the-blanks style)
- **module_checklist.md** — Reusable investigation checklist
- **comparison_matrix.md** — Template for comparing 2+ repos

## Tips & Patterns

### Naming Convention (Critical)

Always use **explicit compound names** for multi-repo analysis:

```
✅ CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md
✅ PYTORCH_LLAMA_INTEGRATION_ANALYSIS.md
❌ INTEGRATION_ANALYSIS.md  ← Don't do this; ambiguous in 03 - R - Resources
```

**Why?** You'll accumulate dozens of analyses over time (para method). Clear names let you scan the folder instantly.

### Save Location

Always save to: `03 - R - Resources/` (or equivalent resources folder in your para setup)

This keeps analyses out of project folders (don't pollute git tree) but discoverable across all projects.

### Dependencies to Watch For

When evaluating setup cost, ask:

- **External runtimes:** Does it need Bun, uv, Python, Docker?
- **System packages:** apt-get/brew installs needed?
- **Port binding:** Does it need a daemon on a specific port?
- **Database:** Does it create schemas? Can they coexist with existing DBs?
- **Environment:** Does it read env vars? Can it be disabled cleanly?

### When to Recommend "Use Both"

If analyzing 2+ repos that solve *different* problems:
- Claude-Mem (persistent cross-session memory) ≠ Context-Mode (in-session context protection)
- They're **complementary**, recommend adopting both in phases

If they solve the *same* problem (competing approaches):
- Compare trade-offs, pick one primary, note secondary value

## Common Pitfalls

### ❌ Mistake 1: Underestimating Setup Cost

"Looks simple" ≠ "is simple." Always test locally first. External processes (daemons, vector DBs) add complexity.

### ❌ Mistake 2: Ignoring Cross-Project Synergies

A pattern in Repo A might be perfect for Repo B even if not immediately applicable. Note these for future reference.

### ❌ Mistake 3: Overfitting to One Project

Repos often solve general problems. Always ask: "Can other projects benefit from this?"

### ❌ Mistake 4: Missing Decision Rationale

Don't just say "not applicable." Explain *why*. Future-you might disagree; good reasoning helps.

## Example: What Good Analysis Looks Like

See `references/example_analysis.md` for a complete worked example (Claude-Mem vs Context-Mode).

## After Analysis: Next Steps

Once you produce the analysis doc:

1. **Commit to git** (in project, if applicable) or **save to Resources folder**
2. **Share with team** if collaborative
3. **Create skills** (if integration involves new workflows)
4. **File implementation tasks** (if planning to adopt)
5. **Tag in memory** (update your MEMORY.md with key findings)

---

**Version History:**
- v1.0.0 — Initial release with 5-step workflow, naming conventions, bundled templates
