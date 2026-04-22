---
name: workspace-cleanup
description: Repository fixer. Applies tiered fixes to audit findings (Tier 1 batch, Tier 2 preview, Tier 3 guidance).
compatibility: any
---

# Workspace Cleanup

Reads workspace health audit findings and applies fixes in three tiers: safe auto-fixes (batch-approvable), medium-impact fixes (per-item approval), and high-impact guidance (interactive, manual).

---

## When to Use

Invoke this skill after running a workspace audit to:
- **Apply Tier 1 auto-fixes** without per-item approval (safe deletions, gitignore updates, folder renames)
- **Preview Tier 2 medium-impact fixes** and approve each one (CLAUDE.md trimming, permissions updates)
- **Get guidance on Tier 3 fixes** that require architectural decisions (lockfile generation, refactoring)

**Trigger phrases:**
- "fix the workspace violations"
- "apply cleanup fixes"
- "show me what can be auto-fixed"
- "preview the fixes"

---

## Fix Tiers

| Tier | Risk | Approval | Examples |
|------|------|----------|----------|
| **1** (safe-auto-fix) | None/trivial | Batch: one "yes" for all | Delete README in skill, add .gitignore entries, rename skill folder to match kebab-case |
| **2** (medium-impact) | Structural but reversible | Per-item: preview + approve each | Trim oversized CLAUDE.md, condense SKILL.md sections, update permissions.deny |
| **3** (high-impact) | Architectural | Interactive: discuss + decide | Generate lockfiles, split long files, refactor complex functions |

---

## How It Works

### Phase 1: Load Findings
- If `--findings` is provided, reads findings JSON (from a previous audit run)
- Otherwise, automatically runs `audit_runner.py` to generate fresh findings

### Phase 2: Categorize by Tier
- Groups findings by `fix_tier` (1, 2, or 3)
- Filters based on `--tier` flag (safe, medium, or all)

### Phase 3: Apply Fixes

**Tier 1 (Safe):** Displays all fixes, asks once for batch approval
```
Tier 1 (Safe Auto-Fix) - 3 findings:
──────────────────────
  [R-SKILL-README] README.md in skill folder should be deleted
  [R-LOCAL-SCOPE] settings.local.json not gitignored
  [R-SKILL-NAME] Skill folder name mismatch

Apply all Tier 1 fixes? [y/N]
```

**Tier 2 (Medium):** Shows preview of each fix, requires per-item approval
```
Tier 2 (Medium-Impact) - 2 findings:
──────────────────────
  [R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines
    Action: Move workflows to .claude/rules/
    Impact: Can reduce file by 20-40 lines

  [R-SENSITIVE-PATHS] permissions.deny missing patterns
    Action: Add [".env*", "*.key", "secret*"]
```

**Tier 3 (High):** Displays guidance and links to manual steps
```
Tier 3 fixes require manual review. See fix-registry.md for details.
```

---

## Running the Script

### Auto-Fix (Audit + Cleanup)

```bash
cd /path/to/repo
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --root .
```

Runs audit automatically, then prompts for each tier.

### From Pre-Generated Findings

```bash
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py \
  --root . \
  --findings findings.json
```

Reads findings from file instead of re-running audit.

### Dry-Run (Preview Only)

```bash
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py \
  --root . \
  --tier safe \
  --dry-run
```

Shows what would be fixed without applying changes.

### Tier Selection

```bash
# Only Tier 1 (safe)
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe --root .

# Only Tier 2 (medium)
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier medium --root .

# All tiers (default)
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --root .
```

### Log Changes

```bash
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py \
  --root . \
  --log cleanup.log
```

Writes changes to cleanup.log in JSON format.

---

## Example Workflow

```bash
# 1. Run full audit and cleanup
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --root .

# Output:
#   Tier 1 (Safe Auto-Fix) - 3 findings:
#   ──────────────────────
#     [R-SKILL-README] README.md in skill folder should be deleted
#     [R-LOCAL-SCOPE] settings.local.json not gitignored
#     [R-SKILL-NAME] Skill folder name mismatch
#
#   Apply all Tier 1 fixes? [y/N] y
#   ✅ Tier 1 fixes applied.
#
#   Tier 2 (Medium-Impact) - 2 findings:
#   ──────────────────────
#   [R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines
#     Action: Move workflows to .claude/rules/
#
#   Tier 2 fixes require manual review. See fix-registry.md for details.

# 2. Commit changes
git add -A
git commit -m "fix: workspace health — apply Tier 1 auto-fixes"

# 3. Follow up on Tier 2
# Edit CLAUDE.md to remove tables and move workflows to .claude/rules/

# 4. Re-run audit to confirm all fixes
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --only-claude
```

---

## Tier 1 Fixers

Implemented and batch-approvable:

### R-SKILL-README: remove-skill-readme
- Deletes all `README.md` files in `.claude/skills/*/`
- SKILL.md is the single source of truth

### R-LOCAL-SCOPE: add-gitignore-entries
- Adds `.claude/settings.local.json` and `.claude/logs/` to `.gitignore`
- Protects machine-local files from accidental commits

### R-SKILL-NAME: fix-skill-name-casing
- Renames skill folders to match kebab-case frontmatter `name` field
- Ensures folder names are the public API

---

## Tier 2 Fixers

Preview-based; require per-item approval:

### R-CLAUDE-SIZE: trim-claude-md
- Suggests moving tables, workflows, and reference content to external docs
- Targets ≤200 lines (prefer 80–150)
- User reviews and approves each suggestion

### R-SKILL-SIZE: trim-skill-md
- Suggests extracting examples, code blocks, and appendices
- Targets ≤500 lines (prefer 100–250)
- User reviews and approves each suggestion

### R-SENSITIVE-PATHS: update-permissions-deny
- Adds missing sensitive patterns (`.env*`, `*.key`, `credentials*`, etc.) to permissions.deny
- User previews changes and approves

---

## Tier 3: Manual Guidance

Requires interactive decision-making:

- **R-CLAUDE-CONTENT**: Move procedures to `.claude/rules/` or skill SKILL.md
- **R-DUP-INSTR**: Consolidate or rename duplicate section headings
- **R-DEPS-LOCK**: Generate and commit ecosystem lockfiles
- **R-DEPS-AUDIT**: Run pip audit / npm audit and address HIGH vulnerabilities
- **R-FILE-LEN**: Split files >500 LOC into smaller, cohesive modules
- **R-FUNC-CPLX**: Refactor functions >60 LOC or McCabe >10

See `.claude/skills/workspace-cleanup/references/fix-registry.md` for details on each fixer.

---

## Troubleshooting

**Q: Tier 2 fixes show but say "requires manual review."**
A: Tier 2 preview-based fixers are partially implemented. Some show suggestions; others (like trim-claude-md) require you to manually edit based on the suggestions shown.

**Q: How do I skip Tier 1 but run Tier 2?**
A: Use `--tier medium`. Tier 1 is the default starting point.

**Q: What if I run cleanup twice?**
A: Safe to re-run. Fixers check for duplicates (e.g., .gitignore entries) and skip if already applied.

**Q: Can I undo fixes?**
A: Yes. Most Tier 1 fixes are reversible via git. Commit before and after running cleanup for easy rollback.

---

## Integration with Enforce Gate

After running cleanup:

```bash
# Apply Tier 1 fixes
python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe --root .

# Verify gate passes
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --format text
# Exit 0 = gate passes, all violations resolved
# Exit 1 = gate fails, Tier 2/3 fixes still needed
```

---

## Change Log

- **2026-04-18**: Initial release. Tier 1 and 2 fixers, safe-auto-fix + preview workflow.
