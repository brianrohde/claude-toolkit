# Fix Registry

Mapping of rules to fixers and the actions they perform.

---

## Tier 1 (Safe Auto-Fix) Fixers

Tier 1 fixes are batch-approvable. One user confirmation applies all fixes.

### Fixer: remove-skill-readme
**Rule:** R-SKILL-README

**What it does:**
- Finds all `README.md` files inside `.claude/skills/*/` directories
- Deletes each file
- Logs deletion

**Can't do:**
- Migrate content from README to SKILL.md (requires human review)
- Preserve if README is crucial (should not happen; SKILL.md is source of truth)

**Example:**
```
Before: .claude/skills/my-skill/README.md (50 lines of documentation)
After:  (file deleted; content should be in SKILL.md)
```

---

### Fixer: add-gitignore-entries
**Rule:** R-LOCAL-SCOPE

**What it does:**
- Checks if `.gitignore` exists
- Adds lines (if not already present):
  ```
  .claude/settings.local.json
  .claude/logs/
  ```
- Commits to `.gitignore`

**Can't do:**
- Delete `.claude/settings.local.json` (contains machine-local data; requires user decision)
- Migrate stale paths to a new machine (requires manual setup)

**Example:**
```
Before: .gitignore (no mention of .claude/)
After:  .gitignore (added .claude/settings.local.json and .claude/logs/)
```

---

### Fixer: fix-skill-name-casing
**Rule:** R-SKILL-NAME

**What it does:**
- Finds skill folders that mismatch frontmatter `name` field (e.g., folder is `MySkill`, name is `my-skill`)
- Renames folder to match kebab-case name
- Updates all internal references (e.g., in CLAUDE.md, other docs)

**Can't do:**
- Ensure CamelCase → kebab-case is correct (e.g., `HTTPServer` → `http-server` vs. `h-t-t-p-server`)
- Fix if name in frontmatter is wrong (requires manual decision)

**Example:**
```
Before: .claude/skills/ExploratoryAnalysis/SKILL.md (frontmatter name: exploratory-analysis)
After:  .claude/skills/exploratory-analysis/SKILL.md (folder renamed to match)
```

---

## Tier 2 (Medium-Impact) Fixers

Tier 2 fixes require per-item preview and approval.

### Fixer: trim-claude-md
**Rule:** R-CLAUDE-SIZE

**What it does:**
- Analyzes CLAUDE.md structure
- Identifies sections that can be moved to external docs or condensed
- Suggests removals or moves (e.g., full table → link + one-liner)
- User previews each suggestion and approves individually

**Can't do:**
- Decide what "concise" means (requires human judgment)
- Rewrite section content (requires editing expertise)
- Know what sections are critical (requires domain knowledge)

**Example:**
```
Before: 
  [Workflows section: 30 lines with 15 table rows]
  [Quick References section: 40 lines listing every doc]

Suggestion 1: Replace Workflows table with link to .claude/rules/
Suggestion 2: Condense Quick References to "see CHEATSHEET.md"

User approves: [Y/N] for each
```

---

### Fixer: trim-skill-md
**Rule:** R-SKILL-SIZE

**What it does:**
- Analyzes SKILL.md sections
- Identifies examples, detailed guides, or reference material that can move to `assets/` or `references/`
- Previews proposed moves
- User approves per item

**Can't do:**
- Decide what is "essential" vs. "reference" (requires author judgment)
- Rewrite condensed content (requires editing)

**Example:**
```
Before: .claude/skills/my-skill/SKILL.md (620 LOC)
  - Overview (20 LOC)
  - When to Use (15 LOC)
  - [10 detailed examples: 200 LOC]
  - [Troubleshooting guide: 150 LOC]
  - Appendix (100 LOC)

Suggestion: Move examples → assets/examples.md, troubleshooting → references/troubleshooting.md
Result: SKILL.md reduced to 170 LOC

User approves: [Y/N]
```

---

### Fixer: update-permissions-deny
**Rule:** R-SENSITIVE-PATHS

**What it does:**
- Reads `settings.json` permissions block
- Identifies missing sensitive patterns (e.g., `.env*`, `*.key`, `secret*`)
- Adds missing patterns to `permissions.deny`
- Shows diff before committing

**Can't do:**
- Identify custom sensitive patterns (e.g., `my_api_key_store.yaml`; requires domain knowledge)
- Ensure coverage is complete (user may know of additional patterns)

**Example:**
```
Before: 
  "permissions": {
    "deny": [".env", "*.pem"]
  }

Adding: ["*.key", "credentials*", "secret*"]

Result:
  "permissions": {
    "deny": [".env", "*.pem", "*.key", "credentials*", "secret*"]
  }

User approves: [Y/N]
```

---

## Tier 3 (High-Impact) Fixers

Tier 3 fixes require interactive case-by-case decisions. No auto-fixer is provided; user must fix manually or discuss with tool.

### Rule: R-CLAUDE-CONTENT
**Guidance:** Move step-by-step procedures out of CLAUDE.md

**Manual steps:**
1. Identify multi-line procedures in CLAUDE.md
2. Move to `.claude/rules/` or relevant skill `SKILL.md`
3. Replace with cross-reference

---

### Rule: R-DEPS-LOCK
**Guidance:** Generate and commit ecosystem lockfiles

**Manual steps:**
1. `pip freeze > requirements.lock` (for Python)
2. `poetry lock` (if using Poetry)
3. `npm ci --package-lock-only` (for Node.js)
4. `git add <lockfile>` and commit

---

### Rule: R-FILE-LEN
**Guidance:** Split long files (>500 LOC)

**Manual steps:**
1. Identify cohesive submodules
2. Extract to separate files
3. Update imports
4. Test thoroughly

---

### Rule: R-FUNC-CPLX
**Guidance:** Refactor complex functions (McCabe >10 or >60 LOC)

**Manual steps:**
1. Run complexity analyzer (e.g., `radon cc <file>`)
2. Break into smaller functions
3. Test edge cases
4. Update docstrings

---

## Registry Summary

| Rule ID | Tier | Fixer Name | Approvable |
|---------|------|-----------|------------|
| R-SKILL-README | 1 | remove-skill-readme | Batch |
| R-LOCAL-SCOPE | 1 | add-gitignore-entries | Batch |
| R-SKILL-NAME | 1 | fix-skill-name-casing | Batch |
| R-CLAUDE-SIZE | 2 | trim-claude-md | Per-item |
| R-SKILL-SIZE | 2 | trim-skill-md | Per-item |
| R-SENSITIVE-PATHS | 2 | update-permissions-deny | Per-item |
| R-CLAUDE-CONTENT | 3 | (manual) | Interactive |
| R-DUP-INSTR | 3 | (manual) | Interactive |
| R-DEPS-LOCK | 3 | (manual) | Interactive |
| R-DEPS-AUDIT | — | (N/A) | — |
| R-DEPS-UNUSED | — | (N/A) | — |
| R-FILE-LEN | — | (N/A) | — |
| R-FUNC-CPLX | — | (N/A) | — |
| R-ROOT-ALLOW | — | (N/A) | — |
| R-ROOT-GEN | — | (N/A) | — |
| R-GENERATED-SEP | — | (N/A) | — |
| R-STALE-FILE | — | (N/A) | — |
| R-WAIVER | — | (N/A) | — |
