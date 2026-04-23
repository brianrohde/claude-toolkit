# Skill: repo-integration-analyzer

**Created:** 2026-04-17  
**Version:** 1.0.0  
**Location:** `.agents/skills/repo-integration-analyzer/`

## What This Skill Does

Systematically analyzes GitHub/forked repositories to identify:
- Which modules are applicable to your current project
- Integration difficulty and setup cost
- Cross-project pattern reuse opportunities
- Phased implementation roadmap

## Why It Exists

When you evaluate forked repos (like fork-claude-mem and fork-context-mode), you need:
1. **Structured process** — Don't randomly Read files; follow a workflow
2. **Clear naming** — Avoid "INTEGRATION_ANALYSIS.md" ambiguity in your Resources folder
3. **Reusable templates** — Checklists, comparison matrices, example outputs
4. **Portable output** — Analysis format you can use across all future projects

## How to Use It

### Single Repository

```
Analyze fork-context-mode for integration into pta-cbp-parser.
Tell me which modules are worth adopting and in what order.
```

**Output:** `CONTEXT_MODE_INTEGRATION_ANALYSIS.md`

### Compare Two Repositories

```
Compare fork-claude-mem and fork-context-mode.
Should I use both or pick one? Why?
```

**Output:** `CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md`

### Any Repository

Works with any GitHub repo, fork, open-source project:
```
Analyze [repo] for [project] integration. Focus on [specific modules/problems].
```

## Skill Components

### SKILL.md (Main)
- 5-step workflow for repository analysis
- Progressive disclosure design (metadata → process → resources)
- Tips, patterns, common pitfalls
- When to use, what to expect

### References (Bundled Templates)

| File | Purpose |
|------|---------|
| `MODULE_CHECKLIST.md` | Fill in per module: purpose, dependencies, setup cost, relevance score |
| `COMPARISON_MATRIX.md` | Side-by-side comparison for 2+ repos: setup, problem fit, token cost, recommendation |
| `EXAMPLE_ANALYSIS.md` | Worked example (Claude-Mem vs Context-Mode) showing expected output format |

### README.md (Documentation)
- Quick start examples
- File structure overview
- Key concepts (relevance scoring, naming conventions)
- Tips for success
- Migration to new projects

## Key Innovation: Naming Convention

**Problem:** Your Resources folder has dozens of analyses. Generic names are meaningless:
```
03 - R - Resources/
  ├── INTEGRATION_ANALYSIS.md  ← Integration of WHAT?
  ├── INTEGRATION_ANALYSIS.md  ← Integration of WHAT?
```

**Solution:** Explicit compound names:
```
03 - R - Resources/
  ├── CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md  ← Clear
  ├── PYTORCH_LLAMA_INTEGRATION_ANALYSIS.md            ← Clear
```

This convention is baked into the skill.

## How It Differs from Manual Analysis

| Aspect | Without Skill | With Skill |
|--------|---|---|
| **Process** | Ad-hoc (read random files, hope nothing's missed) | Structured 5-step workflow |
| **Output** | Scattered notes, maybe one doc | Consistent analysis format |
| **Templates** | Start from scratch each time | Fill-in-the-blanks checklists |
| **Reusability** | Analysis is one-off | Format transfers to new projects |
| **Naming** | Generic "analysis.md" | Explicit "TOOL_A_TOOL_B_analysis.md" |

## Example: What You Just Created

You asked Claude to analyze fork-claude-mem and fork-context-mode for pta-cbp-parser.

**With this skill**, Claude:
1. Mapped both repos (src/, plugins/, hooks/, services/)
2. Deep-dived into each module (read CLAUDE.md, architecture docs, sample code)
3. Assessed relevance (⭐ scoring for each module)
4. Compared side-by-side (setup cost, token savings, maintenance)
5. Produced: `CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md`

**Output included:**
- Module breakdown tables
- Scenario showing cross-project pattern reuse
- Token cost analysis ($0.08/month)
- Phased implementation plan (Phase 1: Context-Mode hooks, Phase 2: Sandbox execution, Phase 3: Claude-Mem)
- Decision rationale (why use both, not pick one)

This format is now repeatable for ANY repo you evaluate in ANY future project.

## Skill Portability

To use in another project:

```bash
# Copy the skill to new project
cp -r pta-cbp-parser/.agents/skills/repo-integration-analyzer/ \
      new-project/.agents/skills/

# Use it
# (Just type: "Analyze [repo] for integration")
```

Same skill, different project context. The workflow applies universally.

## Pairing with Other Skills

- **skill-creator** → Turn analysis findings into new skills
- **skill-development** → Document patterns as reusable workflows
- **command-development** → Build CLIs around integrated modules

---

**Status:** Ready to use  
**Trigger:** Whenever you evaluate external repositories for integration  
**Output:** Analysis markdown in Resources folder with explicit naming  
**Portability:** Copy to any future project; reuse as-is
