# Rule Catalog

Complete reference for all 18 workspace health rules. Rules are classified by priority and severity.

---

## Claude Hygiene Rules (Priority 1)

These rules directly impact Claude's in-session performance by controlling context load and clarity.

### R-CLAUDE-SIZE
**Rule:** CLAUDE.md file size must be ≤ 200 lines; target 80–150 lines.

**Why:** CLAUDE.md loads at the start of every session. Oversized files bloat context and make navigation harder. The file should be a hub, not a spec.

**Severity:** HIGH if exceeds 200 lines | MEDIUM if 150–200 | OK if under 150

**Fix Tier:** Tier 2 (medium-impact) — requires moving content to external docs, rewriting sections for concision

---

### R-SKILL-NAME
**Rule:** Each skill folder name must exactly match the `name` field in its SKILL.md frontmatter, must be kebab-case, and must be lowercase.

**Why:** Folder names are the public API. Mismatches cause user confusion and make skill lookup fail. Kebab-case is the Claude Code convention.

**Severity:** HIGH — automatic gate rule; blocks enforce CI

**Fix Tier:** Tier 1 (safe-auto-fix) — rename folder to match frontmatter or vice versa

**Examples:** 
- ✅ `workspace-audit` folder, frontmatter `name: workspace-audit`
- ❌ `workspace_audit` folder, frontmatter `name: workspace-audit`
- ❌ `WorkspaceAudit` folder, frontmatter `name: workspace-audit`

---

### R-SKILL-README
**Rule:** No README.md file inside skill folders. Skill docs belong only in SKILL.md.

**Why:** SKILL.md is the single source of truth. A separate README causes duplication, divergence, and confusion.

**Severity:** MEDIUM → Tier 1 fix

**Fix Tier:** Tier 1 (safe-auto-fix) — delete README.md from skill folder

---

### R-SKILL-SIZE
**Rule:** SKILL.md files must be ≤ 500 lines; target 100–250 lines.

**Why:** SKILL.md loads when the skill is activated. Oversized files slow skill loading and reduce usability.

**Severity:** HIGH if exceeds 500 lines | MEDIUM if 300–500 | OK if under 300

**Fix Tier:** Tier 2 (medium-impact) — split into referenced sections or move examples to assets/

---

### R-DUP-INSTR
**Rule:** No duplicate H2 or H3 headings across CLAUDE.md and all `.claude/rules/` files combined.

**Why:** Duplicate section names confuse users, obscure which rules apply where, and make updates hard.

**Severity:** HIGH — easy to drift

**Fix Tier:** Tier 2 (medium-impact) — consolidate or rename sections to be precise

**Examples:**
- ❌ "Workflows" appears in both CLAUDE.md and `.claude/rules/trigger-docs-workflow.md`
- ✅ "Workflows" in CLAUDE.md, "Docs Workflow" in trigger-docs-workflow.md

---

### R-LOCAL-SCOPE
**Rule:** Machine-local or environment-specific files must be gitignored and never committed.

**Specific checks:**
- `.claude/settings.local.json` must be in `.gitignore`
- `.claude/logs/` directory and all `.json`/`.log` files must be in `.gitignore`
- Warn if `settings.local.json` exists and contains stale absolute paths (e.g., dead machine hostnames)

**Why:** Local config files (paths, API keys, temp files) should not be in the repo. Stale paths from old machines are a sign the repo wasn't cleaned up after migration.

**Severity:** HIGH — security and hygiene

**Fix Tier:** Tier 1 (safe-auto-fix) — add to `.gitignore`, optionally delete stale settings file

---

### R-CLAUDE-CONTENT
**Rule:** CLAUDE.md should contain only navigation and high-level summaries, not step-by-step procedures.

**Why:** Detailed procedures bloat CLAUDE.md and belong in skill SKILL.md or referenced docs.

**Severity:** MEDIUM

**Fix Tier:** Tier 2 (medium-impact) — move procedures to `.claude/rules/` or relevant skill SKILL.md

**Examples:**
- ❌ "To run the audit: 1. Create a settings.local.json file 2. Run `python audit_runner.py --root . 3. View output in `findings.json`"
- ✅ "Run `/workspace-audit` to scan the repository." (with procedure in workspace-audit/SKILL.md)

---

## Dependency Hygiene Rules

### R-DEPS-LOCK
**Rule:** Each package ecosystem in use must have a committed lockfile.

**Specifics:**
- `requirements.lock` or `poetry.lock` for Python
- `package-lock.json` or `yarn.lock` for Node.js
- `Gemfile.lock` for Ruby
- `go.sum` for Go

**Why:** Lockfiles ensure reproducible installs and prevent supply chain surprises.

**Severity:** HIGH if ecosystem used but lockfile missing

**Fix Tier:** Tier 3 (high-impact) — requires user to generate lockfile per ecosystem

**Not a violation if:** Project is packages-as-code (e.g., conda environment.yml, Nix flake.lock) and explicitly documents it.

---

### R-SENSITIVE-PATHS
**Rule:** `settings.json` permissions block must cover all sensitive file patterns.

**Specifics:**
- Requires `permissions.deny` block listing patterns for: `.env*`, `*.pem`, `*.key`, `secret*`, `credentials*`, local paths

**Why:** Protects against accidental commits of secrets and API keys.

**Severity:** HIGH — security gate

**Fix Tier:** Tier 2 (medium-impact) — update permissions block with missing patterns

---

## Dependency Audit Rules (Informational)

### R-DEPS-AUDIT
**Rule:** Recommend running `pip audit` or `npm audit` periodically; flag unresolved HIGH vulns as informational.

**Severity:** LOW — informational only

**Fix Tier:** Tier 3 (high-impact) — requires dependency upgrades and testing

---

### R-DEPS-UNUSED
**Rule:** Informational flag on unused imports detected via static analysis.

**Severity:** LOW — informational only

**Fix Tier:** Tier 3 (high-impact) — requires code review and removal

---

## Source Quality Rules (Review Triggers, Never HIGH)

These rules flag code quality patterns for human review. They are **never severity HIGH** and never block enforcement. They are catalog entries; actual severity is LOW or MEDIUM based on context.

### R-FILE-LEN
**Rule:** Flag files exceeding certain line counts as review triggers.

- ≥ 500 LOC: MEDIUM trigger (consider splitting module or extracting utilities)
- 300–500 LOC: LOW trigger (likely fine, but review for cohesion)

**Fix Tier:** Tier 3 (high-impact) — architectural decision

---

### R-FUNC-CPLX
**Rule:** Flag functions exceeding complexity thresholds as review triggers.

- McCabe complexity > 10 or > 60 LOC: MEDIUM trigger (likely needs refactoring)
- McCabe complexity 6–10 or 40–60 LOC: LOW trigger (acceptable but review for clarity)

**Fix Tier:** Tier 3 (high-impact) — requires refactoring and testing

---

### R-ROOT-ALLOW
**Rule:** Catalog entry; usage notes when executing from project root vs. subdir.

---

### R-ROOT-GEN
**Rule:** Catalog entry; notes on scripts that generate files in root vs. structured output dirs.

---

### R-GENERATED-SEP
**Rule:** Catalog entry; recommendation to separate generated files from source.

---

### R-STALE-FILE
**Rule:** Catalog entry; flags files with stale timestamps or dead machine names in paths.

---

### R-WAIVER
**Rule:** Catalog entry; waiver mechanism for baseline violations (enforcement gate).

---

## Summary Table

| Rule ID | Category | Severity | Default Gate | Fix Tier |
|---------|----------|----------|--------------|----------|
| R-CLAUDE-SIZE | Claude | HIGH | Yes | Tier 2 |
| R-SKILL-NAME | Claude | HIGH | Yes | Tier 1 |
| R-SKILL-README | Claude | MEDIUM | No | Tier 1 |
| R-SKILL-SIZE | Claude | HIGH | Yes | Tier 2 |
| R-DUP-INSTR | Claude | HIGH | Yes | Tier 2 |
| R-LOCAL-SCOPE | Claude | HIGH | Yes | Tier 1 |
| R-CLAUDE-CONTENT | Claude | MEDIUM | No | Tier 2 |
| R-DEPS-LOCK | Deps | HIGH | Yes | Tier 3 |
| R-SENSITIVE-PATHS | Deps | HIGH | Yes | Tier 2 |
| R-DEPS-AUDIT | Deps | LOW | No | Tier 3 |
| R-DEPS-UNUSED | Deps | LOW | No | Tier 3 |
| R-FILE-LEN | Source | MEDIUM | No | Tier 3 |
| R-FUNC-CPLX | Source | MEDIUM | No | Tier 3 |
| R-ROOT-ALLOW | Catalog | — | No | — |
| R-ROOT-GEN | Catalog | — | No | — |
| R-GENERATED-SEP | Catalog | — | No | — |
| R-STALE-FILE | Catalog | — | No | — |
| R-WAIVER | Catalog | — | No | — |
