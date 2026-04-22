---
name: workspace-audit
description: Read-only repository health auditor. Scans for Claude hygiene, dependency, and source quality violations.
compatibility: any
---

# Workspace Audit

Scans a repository against 18 workspace health rules and reports violations and findings. Read-only; no changes made to the repository.

---

## When to Use

Invoke this skill when you need to:
- **Validate repository health** before merging or releasing
- **Identify Claude-specific hygiene issues** (CLAUDE.md size, skill names, skill file sizes)
- **Detect dependency problems** (missing lockfiles, unsecured sensitive paths)
- **Review source quality** (long files, complex functions) as hints for refactoring
- **Export findings as JSON** for CI integration or downstream tools

**Trigger phrases:**
- "audit the repository"
- "check workspace health"
- "scan for violations"
- "validate repository standards"

---

## How It Works

The audit runs in four stages:

### 1. Claude Hygiene Checks (Priority 1)
Validates Claude Code standards: CLAUDE.md/SKILL.md sizes, skill name consistency (kebab-case), forbidden README files in skill folders, no step-by-step procedures in CLAUDE.md, local config gitignore.

**Rules:**
- R-CLAUDE-SIZE, R-SKILL-NAME, R-SKILL-README, R-SKILL-SIZE, R-DUP-INSTR, R-LOCAL-SCOPE, R-CLAUDE-CONTENT

### 2. Dependency Hygiene Checks
Detects missing lockfiles per ecosystem, validates permissions block covers sensitive paths, suggests periodic audits.

**Rules:**
- R-DEPS-LOCK, R-SENSITIVE-PATHS, R-DEPS-AUDIT, R-DEPS-UNUSED

### 3. Source Quality Checks (Review Triggers)
Flags long files (≥500 LOC) and complex functions (>60 LOC, McCabe >10) as suggestions for refactoring. Never HIGH severity; never block enforcement.

**Rules:**
- R-FILE-LEN, R-FUNC-CPLX

### 4. Catalog Entries
Documents standards for edge cases: root directory allowance, generated file separation, stale file detection, waiver mechanism.

---

## Running the Script

### Basic Audit (All Checks)

```bash
cd /path/to/repo
python .claude/skills/workspace-audit/scripts/audit_runner.py --root .
```

Output: Human-readable report with violations and findings.

### By Category

```bash
# Claude hygiene only
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --only-claude

# Dependency checks only
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --only-deps

# Source quality only
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --only-source
```

### JSON Output

```bash
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --json
```

Output: JSON array of finding dicts (suitable for piping to cleanup or CI).

### Save to File

```bash
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --json --output findings.json
```

---

## Output Format

### Text Report

```
================================================================================
WORKSPACE HEALTH AUDIT
Root: /path/to/repo
================================================================================

VIOLATIONS (4 HIGH, gate will fail):
────────────────────────────────────

[R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines (found 247)
  File: CLAUDE.md
  Severity: HIGH | Fix Tier: Tier 2
  CLAUDE.md loads at every session start. Current: 247 lines.
  [detail omitted for brevity]

[more violations...]

FINDINGS (2 MEDIUM, 0 LOW, optional):
────────────────────────────────────

[R-SKILL-README] README.md in skill folder should be deleted
  File: .claude/skills/my-skill/README.md
  Severity: MEDIUM | Fix Tier: Tier 1
  [detail]

SUMMARY:
───────
Total violations: 4 (4 HIGH, 0 MEDIUM)
Total findings: 2 (0 HIGH, 2 MEDIUM, 0 LOW)
Gate status: FAIL ❌

To apply Tier 1 auto-fixes:
  python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe

================================================================================
```

### JSON Format

```json
[
  {
    "rule_id": "R-CLAUDE-SIZE",
    "severity": "HIGH",
    "fix_tier": 2,
    "category": "Claude",
    "file": "CLAUDE.md",
    "line": null,
    "message": "CLAUDE.md exceeds 200 lines (found 247)",
    "detail": "...",
    "is_violation": true
  },
  ...
]
```

---

## Resources

- **Rule Catalog**: `.claude/skills/workspace-audit/references/rule-catalog.md` — all 18 rules with severity, fix tier, rationale
- **Output Format**: `.claude/skills/workspace-audit/references/output-format.md` — finding dict schema and examples
- **Cleanup Workflow**: `.claude/skills/workspace-cleanup/SKILL.md` — how to apply fixes
- **Enforcement Gate**: `.claude/skills/workspace-enforce/SKILL.md` — CI integration and waivers

---

## Common Patterns

### Integrate into CI

```yaml
# .github/workflows/health-gate.yml
name: Workspace Health Gate
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --format text
```

### Local Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --format text
[ $? -eq 0 ] || exit 1
```

### Scheduled Audits

Run audit weekly and report violations to a dashboard or Slack:

```bash
python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --json | \
  curl -X POST https://your-webhook.example.com -d @-
```

---

## Troubleshooting

**Q: How do I run this if checks modules are in workspace-audit?**
A: The audit_runner.py imports checks_*.py from the same directory. Ensure you run it from the `.claude/skills/workspace-audit/scripts/` directory or add it to sys.path.

**Q: Can I customize the rules or thresholds?**
A: Not yet. Edit `checks_claude.py`, `checks_deps.py`, or `checks_source.py` directly to change thresholds (e.g., CLAUDE.md line limit) or add new checks.

**Q: What if my project uses a non-standard lockfile or config?**
A: Add checks to `checks_deps.py` for your ecosystem. The audit catalog (`rule-catalog.md`) documents what patterns are expected.

**Q: How often should I run the audit?**
A: Before merges, releases, or as part of CI. Weekly scheduled runs help catch drift early.

---

## Change Log

- **2026-04-18**: Initial release. 18 rules, 3 categories (Claude, Deps, Source), read-only audit.
