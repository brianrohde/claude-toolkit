# Output Format Reference

Schema and examples for audit runner output.

---

## Finding Dictionary Schema

Each finding is a dict with the following structure:

```python
{
    'rule_id': str,              # e.g., 'R-CLAUDE-SIZE'
    'severity': str,             # 'HIGH', 'MEDIUM', 'LOW'
    'fix_tier': int,             # 1, 2, or 3
    'category': str,             # 'Claude', 'Deps', 'Source', 'Catalog'
    'file': str,                 # absolute or relative path; None if repo-wide
    'line': int | None,          # line number if applicable; None if file-wide
    'message': str,              # one-line human summary
    'detail': str | None,        # multiline explanation, fix suggestions, examples
    'is_violation': bool         # True if severity HIGH and in gate_rules; else False
}
```

---

## Example Findings

### Claude Hygiene: CLAUDE.md Oversized

```python
{
    'rule_id': 'R-CLAUDE-SIZE',
    'severity': 'HIGH',
    'fix_tier': 2,
    'category': 'Claude',
    'file': 'CLAUDE.md',
    'line': None,
    'message': 'CLAUDE.md exceeds 200 lines (found 247)',
    'detail': '''CLAUDE.md is oversized and loads at every session start.
Target: 80–150 lines. Current: 247 lines.

Recommendation:
1. Move detailed workflows to .claude/rules/ or skill SKILL.md files
2. Trim table entries to one-line summaries
3. Replace multi-paragraph sections with links to external docs

See CLAUDE.md structure targets in workspace-audit rule-catalog.md.''',
    'is_violation': True
}
```

### Claude Hygiene: Skill Name Mismatch

```python
{
    'rule_id': 'R-SKILL-NAME',
    'severity': 'HIGH',
    'fix_tier': 1,
    'category': 'Claude',
    'file': '.claude/skills/my_skill/SKILL.md',
    'line': 2,
    'message': 'Skill folder name "my_skill" does not match frontmatter name "my-skill"',
    'detail': '''Folder names are the public API. Mismatches cause lookup failure and user confusion.

Folder: .claude/skills/my_skill/
Frontmatter name: my-skill

Fix: Rename folder to .claude/skills/my-skill/ (kebab-case, lowercase).''',
    'is_violation': True
}
```

### Claude Hygiene: README in Skill Folder

```python
{
    'rule_id': 'R-SKILL-README',
    'severity': 'MEDIUM',
    'fix_tier': 1,
    'category': 'Claude',
    'file': '.claude/skills/my-skill/README.md',
    'line': None,
    'message': 'README.md found in skill folder; should be deleted',
    'detail': '''SKILL.md is the single source of truth for skill documentation.
A separate README causes duplication and divergence.

Action: Delete .claude/skills/my-skill/README.md''',
    'is_violation': False
}
```

### Dependency Hygiene: Missing Lockfile

```python
{
    'rule_id': 'R-DEPS-LOCK',
    'severity': 'HIGH',
    'fix_tier': 3,
    'category': 'Deps',
    'file': None,
    'line': None,
    'message': 'Python ecosystem detected but no lockfile committed (no requirements.lock or poetry.lock)',
    'detail': '''Found setup.py or requirements.txt but no lockfile.
Lockfiles ensure reproducible installs and prevent supply chain surprises.

To fix:
1. If using pip: pip freeze > requirements.lock && git add requirements.lock
2. If using poetry: poetry lock && git add poetry.lock
3. If using conda: conda env export > environment.lock.yml && git add environment.lock.yml

Re-run audit after committing.''',
    'is_violation': True
}
```

### Local Scope: Stale settings.local.json

```python
{
    'rule_id': 'R-LOCAL-SCOPE',
    'severity': 'HIGH',
    'fix_tier': 1,
    'category': 'Claude',
    'file': '.claude/settings.local.json',
    'line': None,
    'message': 'settings.local.json exists with stale paths (dead machine "oldmachine.local")',
    'detail': '''settings.local.json should not be committed and should be gitignored.
Additionally, the file contains stale absolute paths from a previous machine:

Stale entries:
- /mnt/oldmachine.local/... (machine no longer available)
- C:\\dead_drive\\... (unreachable)

Action:
1. Delete .claude/settings.local.json (it's machine-local, not repo config)
2. Add .claude/settings.local.json to .gitignore
3. Add .claude/logs/ to .gitignore if not present

After committing the .gitignore change, this finding will clear.''',
    'is_violation': True
}
```

### Source Quality: File Too Long

```python
{
    'rule_id': 'R-FILE-LEN',
    'severity': 'MEDIUM',
    'fix_tier': 3,
    'category': 'Source',
    'file': 'src/agent/orchestrator.py',
    'line': None,
    'message': 'File exceeds 500 LOC (found 742); consider splitting or extracting utilities',
    'detail': '''Long files are harder to review and test. Breaking into smaller modules improves cohesion.

Current: 742 LOC
Threshold for MEDIUM trigger: 500 LOC

Suggestion: Extract utility functions or dispatcher logic into separate modules.

This is a review trigger; fix is optional unless multiple triggers accumulate.''',
    'is_violation': False
}
```

---

## Report Template

Audit output combines all findings in a human-readable report:

```
================================================================================
WORKSPACE HEALTH AUDIT
Root: /path/to/repo
Timestamp: 2026-04-18T10:30:45Z
================================================================================

VIOLATIONS (4 HIGH, gate will fail):
─────────────────────────────────────────────────────────────────────────────

[R-CLAUDE-SIZE] CLAUDE.md exceeds 200 lines (found 247)
  File: CLAUDE.md
  Severity: HIGH | Fix Tier: Tier 2
  Recommendation: Move workflows to .claude/rules/ or reduce table entries

[R-SKILL-NAME] Skill folder name mismatch: folder="my_skill" vs name="my-skill"
  File: .claude/skills/my_skill/SKILL.md:2
  Severity: HIGH | Fix Tier: Tier 1
  Recommendation: Rename folder to .claude/skills/my-skill/

[R-LOCAL-SCOPE] settings.local.json not gitignored; contains stale paths
  File: .claude/settings.local.json
  Severity: HIGH | Fix Tier: Tier 1
  Recommendation: Add .claude/settings.local.json to .gitignore; delete stale file

[R-DEPS-LOCK] Python ecosystem detected but no lockfile committed
  File: (repo-wide)
  Severity: HIGH | Fix Tier: Tier 3
  Recommendation: Run `pip freeze > requirements.lock` and commit


FINDINGS (2 MEDIUM, 0 LOW, optional):
─────────────────────────────────────────────────────────────────────────────

[R-SKILL-README] README.md in skill folder should be deleted
  File: .claude/skills/my-skill/README.md
  Severity: MEDIUM | Fix Tier: Tier 1
  Recommendation: Delete file; use SKILL.md as single source of truth

[R-FILE-LEN] src/agent/orchestrator.py exceeds 500 LOC (found 742)
  File: src/agent/orchestrator.py
  Severity: MEDIUM | Fix Tier: Tier 3
  Recommendation: Consider splitting module into smaller units


SUMMARY:
────────────────────────────────────────────────────────────────────────────
Total violations: 4 (4 HIGH, 0 MEDIUM)
Total findings: 2 (0 HIGH, 2 MEDIUM, 0 LOW)
Gate status: FAIL (violations present)

To apply Tier 1 auto-fixes:
  python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe

To see all findings in JSON:
  python .claude/skills/workspace-audit/scripts/audit_runner.py --json

================================================================================
```

---

## JSON Output Schema

When `--json` flag is used, audit outputs a JSON array of finding dicts:

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

This JSON is suitable for piping to cleanup runner, CI gates, or external tools.
