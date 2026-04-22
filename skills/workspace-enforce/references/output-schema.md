# Enforce Runner Output Schema

Machine-readable exit codes and JSON output format for CI integration.

---

## Exit Codes

| Exit Code | Meaning | When |
|-----------|---------|------|
| **0** | PASS | No violations found, or all violations waived |
| **1** | FAIL | Violations found and not waived; gate blocks merge |
| **2** | ERROR | Script execution error (bad args, missing waivers file, I/O error) |

---

## Text Output Format

Default output (human-readable):

```
================================================================================
WORKSPACE HEALTH ENFORCEMENT GATE
Repository: /path/to/repo
Timestamp: 2026-04-18T10:30:45Z
Gate Rules: R-CLAUDE-SIZE, R-SKILL-NAME, R-SKILL-README, R-SKILL-SIZE, R-LOCAL-SCOPE, R-DEPS-LOCK, R-SENSITIVE-PATHS
Waivers File: .claude/audit-waivers.json
================================================================================

GATE VIOLATIONS (2 unwaived):
────────────────────────────────────────────────────────────────────────────

[R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines (found 247)
  File: CLAUDE.md
  Severity: HIGH | Fix Tier: Tier 2
  Waived: NO — violation blocks gate
  Waiver deadline: N/A

[R-LOCAL-SCOPE] settings.local.json not gitignored
  File: .claude/settings.local.json
  Severity: HIGH | Fix Tier: Tier 1
  Waived: NO — violation blocks gate
  Waiver deadline: N/A


GATE VIOLATIONS WAIVED (1):
────────────────────────────────────────────────────────────────────────────

[R-SKILL-SIZE] SKILL.md file exceeds 500 lines (found 523)
  File: .claude/skills/my-skill/SKILL.md
  Waived: YES (expires 2026-05-01 per .claude/audit-waivers.json)
  Reason: "Temporary waiver while refactoring large skill; scheduled for Tier 2 fix by May 1"


RESULT: FAIL ❌
────────────────────────────────────────────────────────────────────────────
Unwaived violations: 2
Gate will block merge until all unwaived violations are resolved.

To see all findings (including source quality LOW/MEDIUM):
  python .claude/skills/workspace-audit/scripts/audit_runner.py --root . --json

To apply Tier 1 auto-fixes:
  python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe

================================================================================
```

---

## JSON Output Format

With `--format json`, output is a single JSON object:

```json
{
  "timestamp": "2026-04-18T10:30:45Z",
  "repository": "/path/to/repo",
  "gate_rules": ["R-CLAUDE-SIZE", "R-SKILL-NAME", "R-SKILL-README", "R-SKILL-SIZE", "R-LOCAL-SCOPE", "R-DEPS-LOCK", "R-SENSITIVE-PATHS"],
  "waivers_file": ".claude/audit-waivers.json",
  "exit_code": 1,
  "status": "FAIL",
  "violations": {
    "unwaived": [
      {
        "rule_id": "R-CLAUDE-SIZE",
        "severity": "HIGH",
        "file": "CLAUDE.md",
        "line": null,
        "message": "CLAUDE.md exceeds 200 lines (found 247)",
        "is_violation": true,
        "waived": false
      },
      {
        "rule_id": "R-LOCAL-SCOPE",
        "severity": "HIGH",
        "file": ".claude/settings.local.json",
        "line": null,
        "message": "settings.local.json not gitignored",
        "is_violation": true,
        "waived": false
      }
    ],
    "waived": [
      {
        "rule_id": "R-SKILL-SIZE",
        "severity": "HIGH",
        "file": ".claude/skills/my-skill/SKILL.md",
        "line": null,
        "message": "SKILL.md file exceeds 500 lines (found 523)",
        "is_violation": true,
        "waived": true,
        "waiver_reason": "Temporary waiver while refactoring large skill; scheduled for Tier 2 fix by May 1",
        "waiver_expires": "2026-05-01"
      }
    ]
  },
  "summary": {
    "total_unwaived": 2,
    "total_waived": 1,
    "total_violations": 3,
    "gate_blocks_merge": true
  }
}
```

---

## Pre-commit Hook Integration (Windows)

Example `.git/hooks/pre-commit` (shell script):

```bash
#!/bin/sh
# Enforce gate before commit

python .claude/skills/workspace-enforce/scripts/enforce_runner.py \
  --root . \
  --format text \
  --exit-on-fail

if [ $? -ne 0 ]; then
  echo "❌ Workspace health gate failed. Run cleanup or add waivers before committing."
  exit 1
fi

exit 0
```

**Windows note**: Git on Windows uses bash in a MinGW environment. The above script should work, but Windows users can also use a `.husky/pre-commit` (Node.js hook manager) or a Python hook wrapper for better portability.

**Safe pattern for Python pre-commit setup:**

```python
# .git/hooks/pre-commit (Python wrapper)
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent
enforce_script = root / '.claude' / 'skills' / 'workspace-enforce' / 'scripts' / 'enforce_runner.py'

result = subprocess.run(
    [sys.executable, str(enforce_script), '--root', str(root), '--format', 'text'],
    cwd=str(root)
)

if result.returncode != 0:
    print("❌ Workspace health gate failed. Run cleanup before committing.")
    sys.exit(1)

sys.exit(0)
```

---

## Gate Rules (Default)

Default gate rules that block CI:

```
R-CLAUDE-SIZE       # CLAUDE.md must be ≤ 200 lines
R-SKILL-NAME        # Skill folder name must match frontmatter name
R-SKILL-README      # No README.md in skill folders
R-SKILL-SIZE        # SKILL.md must be ≤ 500 lines
R-LOCAL-SCOPE       # settings.local.json must be gitignored
R-DEPS-LOCK         # Lockfiles must be committed per ecosystem
R-SENSITIVE-PATHS   # permissions.deny must cover sensitive patterns
```

These can be overridden via `--gate-rules` flag or `enforce_runner.py --gate-rules "R-CLAUDE-SIZE,R-SKILL-NAME"`
