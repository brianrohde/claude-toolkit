---
name: workspace-enforce
description: CI gate for workspace health. Blocks merge if high-severity violations are unwaived.
compatibility: any
---

# Workspace Enforce

Repository health enforcement gate for CI/pre-commit. Exits non-zero if violations are found, with waiver support for planned fixes.

---

## When to Use

Invoke this skill in:
- **CI workflows** (GitHub Actions, GitLab CI, etc.) to block merges with health violations
- **Pre-commit hooks** to gate local commits
- **Pre-merge gates** to enforce standards before PRs reach main

**Trigger phrases:**
- "check if repository passes health gate"
- "enforce workspace standards"
- "run the CI gate"
- "validate for merge"

---

## How It Works

### Phase 1: Run Audit
Automatically runs all audit checks (Claude, Deps, optional Source).

### Phase 2: Load Waivers
Reads `.claude/audit-waivers.json` and checks expiry for each violation.

### Phase 3: Filter by Gate Rules
Compares findings against `gate_rules` (default: Claude + Deps HIGH severity rules).

### Phase 4: Exit Code
- **Exit 0**: No unwaived violations; merge is allowed
- **Exit 1**: Unwaived violations; merge is blocked
- **Exit 2**: Script error (bad args, missing file, I/O error)

---

## Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| **0** | PASS ✅ | All violations waived or resolved |
| **1** | FAIL ❌ | Unwaived violations; gate blocks merge |
| **2** | ERROR | Script execution error |

---

## Default Gate Rules

By default, the following HIGH-severity rules block the gate:

```
R-CLAUDE-SIZE       # CLAUDE.md must be ≤ 200 lines
R-SKILL-NAME        # Skill folder name must match frontmatter name
R-SKILL-README      # No README.md in skill folders
R-SKILL-SIZE        # SKILL.md must be ≤ 500 lines
R-LOCAL-SCOPE       # settings.local.json must be gitignored
R-DEPS-LOCK         # Lockfiles must be committed per ecosystem
R-SENSITIVE-PATHS   # permissions.deny must cover sensitive patterns
```

Medium and Low severity rules are informational only and do not block by default.

---

## Running the Gate

### Basic Gate Check

```bash
cd /path/to/repo
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root .
```

Output: Human-readable text report.

**Exit code:** 0 (pass) or 1 (fail).

### JSON Output (for CI Integration)

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --format json
```

Output: Structured JSON with violations, waivers, exit code.

### With Waivers File

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --waivers .claude/audit-waivers.json
```

### Custom Gate Rules

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --gate-rules "R-CLAUDE-SIZE,R-SKILL-NAME,R-FILE-LEN"
```

### Include Source Quality Rules

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --include-source
```

Adds `R-FILE-LEN` and `R-FUNC-CPLX` to the gate (normally informational).

### Exit on Fail

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --exit-on-fail
```

Exits non-zero if any unwaived violations. Useful in CI.

---

## Output Format

### Text Report

```
================================================================================
WORKSPACE HEALTH ENFORCEMENT GATE
Repository: /path/to/repo
Gate Rules: R-CLAUDE-SIZE, R-SKILL-NAME, ...
Waivers File: .claude/audit-waivers.json
================================================================================

GATE VIOLATIONS (2 unwaived):
────────────────────────────────────────────────────────────────────────────

[R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines (found 247)
  File: CLAUDE.md
  Severity: HIGH
  Waived: NO — violation blocks gate

[R-LOCAL-SCOPE] settings.local.json not gitignored
  File: .claude/settings.local.json
  Severity: HIGH
  Waived: NO — violation blocks gate


GATE VIOLATIONS WAIVED (1):
────────────────────────────────────────────────────────────────────────────

[R-SKILL-SIZE] SKILL.md exceeds 500 lines (found 523)
  File: .claude/skills/my-skill/SKILL.md
  Waived: YES (Temporary waiver while refactoring large skill)


RESULT: FAIL ❌
────────────────────────────────────────────────────────────────────────────
Unwaived violations: 2
Gate will block merge until all unwaived violations are resolved.

================================================================================
```

### JSON Output

```json
{
  "timestamp": "2026-04-18T10:30:45.123456",
  "repository": "/path/to/repo",
  "gate_rules": ["R-CLAUDE-SIZE", "R-SKILL-NAME", ...],
  "waivers_file": ".claude/audit-waivers.json",
  "exit_code": 1,
  "status": "FAIL",
  "violations": {
    "unwaived": [
      {
        "rule_id": "R-CLAUDE-SIZE",
        "severity": "HIGH",
        "file": "CLAUDE.md",
        "message": "CLAUDE.md exceeds 200 lines (found 247)",
        "waived": false
      },
      ...
    ],
    "waived": [
      {
        "rule_id": "R-SKILL-SIZE",
        "severity": "HIGH",
        "file": ".claude/skills/my-skill/SKILL.md",
        "waived": true,
        "waiver_reason": "Temporary waiver while refactoring"
      }
    ]
  },
  "summary": {
    "total_unwaived": 2,
    "total_waived": 1,
    "gate_blocks_merge": true
  }
}
```

---

## Waivers

Temporarily suppress violations with expiring waivers in `.claude/audit-waivers.json`:

```json
{
  "R-CLAUDE-SIZE": [
    {
      "rule_id": "R-CLAUDE-SIZE",
      "reason": "CLAUDE.md refactor in progress (PR #45); moving workflows to .claude/rules/",
      "expires": "2026-04-25",
      "issue_tracker": "https://github.com/myorg/myrepo/pull/45",
      "owner": "alice@example.com"
    }
  ]
}
```

**Field definitions:**
- `rule_id`: Must match a rule from rule-catalog.md
- `reason`: Why violation is temporarily acceptable
- `expires`: Date waiver expires (YYYY-MM-DD); encourages action
- `issue_tracker`: Optional; link to tracking issue/PR
- `owner`: Optional; person responsible for fix

**Behavior:**
- If `expires` date has passed, waiver is ignored and violation blocks gate
- Expired waivers are flagged in the output with a warning

See `.claude/skills/workspace-enforce/references/waiver-schema.md` for full details and examples.

---

## CI Integration

### GitHub Actions

```yaml
name: Workspace Health Gate
on: [pull_request]
jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --exit-on-fail
        name: Check workspace health
```

### GitLab CI

```yaml
workspace-health:
  stage: test
  script:
    - python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root . --exit-on-fail
  only:
    - merge_requests
```

### Pre-commit Hook (Windows-Safe)

```bash
#!/bin/bash
# .git/hooks/pre-commit
python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --exit-on-fail

if [ $? -ne 0 ]; then
  echo "❌ Workspace health gate failed. Run cleanup or add waivers before committing."
  exit 1
fi
```

Or use Python for better Windows compatibility:

```python
#!/usr/bin/env python3
# .git/hooks/pre-commit
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
enforce = root / '.claude' / 'skills' / 'workspace-enforce' / 'scripts' / 'enforce_runner.py'

result = subprocess.run([sys.executable, str(enforce), '--root', str(root), '--exit-on-fail'], cwd=root)
sys.exit(result.returncode)
```

---

## Workflow: New Violation During Development

1. **Developer commits code** → pre-commit hook runs gate
2. **Gate fails** → dev sees violation and takes action:
   - Option A: Fix violation immediately (apply cleanup fixes)
   - Option B: Waive for planned fix (add to `.claude/audit-waivers.json`)
3. **If waived:** Revert commit, update waivers file, commit again
4. **If fixed:** Verify gate passes, push to main

Example waiver workflow:

```bash
# 1. Gate fails on CLAUDE.md size
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root .
# → FAIL: R-CLAUDE-SIZE violation

# 2. Add waiver to .claude/audit-waivers.json
cat > .claude/audit-waivers.json <<EOF
{
  "R-CLAUDE-SIZE": [
    {
      "rule_id": "R-CLAUDE-SIZE",
      "reason": "CLAUDE.md refactor scheduled for this sprint",
      "expires": "2026-04-25",
      "issue_tracker": null,
      "owner": "me@example.com"
    }
  ]
}
EOF

# 3. Gate now passes
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root .
# → PASS ✅

# 4. Commit
git add -A
git commit -m "ci: add waiver for CLAUDE.md refactor (expires 2026-04-25)"

# 5. Later: fix CLAUDE.md and remove waiver
# ... edit CLAUDE.md ...
git rm .claude/audit-waivers.json  # or update with no entries
git commit -m "refactor: condense CLAUDE.md to 120 lines"
```

---

## Troubleshooting

**Q: Gate blocks merge but I don't see violations in the output.**
A: Check for expired waivers. Run with `--format json` to see full details and expiry dates.

**Q: How do I bypass the gate for emergency fixes?**
A: Add a waiver with a short expiry (e.g., same day), fix the violation, then remove the waiver.

**Q: Can I change the default gate rules?**
A: Yes, use `--gate-rules` to override. Or modify `DEFAULT_GATE_RULES` in `enforce_runner.py` and rebuild the skill.

**Q: Why is the gate checking source quality rules I didn't ask for?**
A: By default, source quality rules (R-FILE-LEN, R-FUNC-CPLX) are informational only and don't block the gate. Use `--include-source` to add them to the gate.

---

## Resources

- **Rule Catalog**: `.claude/skills/workspace-audit/references/rule-catalog.md` — all 18 rules
- **Waiver Schema**: `.claude/skills/workspace-enforce/references/waiver-schema.md` — full waiver format and examples
- **Audit Tool**: `.claude/skills/workspace-audit/SKILL.md` — how to run the audit
- **Cleanup Tool**: `.claude/skills/workspace-cleanup/SKILL.md` — how to fix violations

---

## Change Log

- **2026-04-18**: Initial release. 7 default gate rules, waiver support, CI-friendly JSON output.
