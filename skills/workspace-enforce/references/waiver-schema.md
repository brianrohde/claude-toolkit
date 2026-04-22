# Waiver Schema and Examples

How to waive (temporarily suppress) violations for planned fixes.

---

## Waiver File Location and Format

**File:** `.claude/audit-waivers.json` (in repo root)

**Format:** JSON dict mapping `rule_id` to a waiver list:

```json
{
  "R-CLAUDE-SIZE": [
    {
      "rule_id": "R-CLAUDE-SIZE",
      "reason": "Refactoring CLAUDE.md for concision; scheduled for Tier 2 fix",
      "expires": "2026-05-01",
      "issue_tracker": "https://github.com/yourorg/repo/issues/123",
      "owner": "alice@example.com"
    }
  ],
  "R-SKILL-SIZE": [
    {
      "rule_id": "R-SKILL-SIZE",
      "reason": "my-skill SKILL.md split across multiple sections; will be refactored into assets/",
      "expires": "2026-04-30",
      "issue_tracker": null,
      "owner": "bob@example.com"
    }
  ]
}
```

---

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | string | Yes | Must match a rule from rule-catalog.md (e.g., `R-CLAUDE-SIZE`) |
| `reason` | string | Yes | Why violation is temporarily acceptable; short explanation of planned fix |
| `expires` | string (YYYY-MM-DD) | Yes | Date waiver expires (becomes unwaived again); encourages action |
| `issue_tracker` | string (URL) \| null | No | Link to issue or PR tracking the fix; null if no tracker |
| `owner` | string (email) | No | Person responsible for fixing; helps track accountability |

---

## Behavior

When `enforce_runner.py --format json` is run:

1. **Audit** checks for violations against gate rules
2. **Load waivers** from `.claude/audit-waivers.json`
3. **Match**: For each violation, check if `rule_id` is in waivers
4. **Expire check**: If `expires` date has passed, violation is **unwaived** (and error logged)
5. **Report**: Separate `unwaived` vs. `waived` violations in JSON output
6. **Exit**: Exit 1 if any unwaived violations; exit 0 if all waived or no violations

---

## Example Scenarios

### Scenario 1: Planned Fix with Expiry

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

**Behavior:**
- Until 2026-04-25, gate will **PASS** even if CLAUDE.md is >200 lines
- On 2026-04-25 and after, gate will **FAIL** until violation is fixed or waiver is renewed

---

### Scenario 2: Multiple Waivers (Same Rule)

```json
{
  "R-FILE-LEN": [
    {
      "rule_id": "R-FILE-LEN",
      "reason": "src/model/inference.py (742 LOC) — architectural refactor planned Q3",
      "expires": "2026-07-01",
      "issue_tracker": "https://github.com/myorg/myrepo/issues/198",
      "owner": "charlie@example.com"
    },
    {
      "rule_id": "R-FILE-LEN",
      "reason": "src/util/helpers.py (610 LOC) — utility extraction scheduled",
      "expires": "2026-05-15",
      "issue_tracker": null,
      "owner": "dave@example.com"
    }
  ]
}
```

**Behavior:**
- Both violations are waived until their respective expiry dates
- If you want to waive a specific file, list it in `reason` for human readability

---

### Scenario 3: Empty Waivers (No Violations Waived)

```json
{}
```

All violations are active; gate enforces all rules.

---

## Best Practices

1. **Keep waivers short-lived**: Always set an expiry date ≤ 2 weeks from creation. This forces progress on planned fixes.

2. **Link to tracker**: If you have an issue or PR, include the URL so readers know the fix is tracked.

3. **Ownership**: Assign an owner so it's clear who is responsible.

4. **Reason clarity**: Write reasons that would make sense to someone reviewing the waivers in a month. Example:
   - ✅ "CLAUDE.md refactor in progress (PR #45); moving workflows to .claude/rules/"
   - ❌ "TODO"
   - ❌ "large file"

5. **Audit regularly**: Run `enforce_runner.py` weekly to catch expired waivers before CI blocks merges.

---

## Expired Waiver Behavior

If a waiver has expired (today > `expires` date):

1. `enforce_runner.py` logs a **warning** with the expired rule and owner
2. The violation is treated as **unwaived**
3. Gate will **FAIL**
4. User must either:
   - **Fix the violation** (remove finding)
   - **Renew the waiver** (update `expires` date in `.claude/audit-waivers.json`)

Example output when expired:

```
⚠️  Expired waiver: R-CLAUDE-SIZE (expired 2026-04-24, waived by alice@example.com)
    Reason: "CLAUDE.md refactor in progress (PR #45)"
    Action: Fix violation or renew waiver in .claude/audit-waivers.json
```

---

## Enforcement: No Waivers for Source Quality Rules

Source quality rules (R-FILE-LEN, R-FUNC-CPLX) are **never in gate_rules** by default, so waivers have no effect on enforcement gates.

If you use `--gate-rules "R-FILE-LEN,R-FUNC-CPLX"` to add them to the gate, then waivers **will** apply.

```bash
# Normally, source quality rules are informational only:
python enforce_runner.py --root . --format text
# → R-FILE-LEN violations are shown but don't fail gate

# But if you add them to gate:
python enforce_runner.py --root . --gate-rules "R-CLAUDE-SIZE,R-SKILL-NAME,R-FILE-LEN"
# → R-FILE-LEN violations now fail gate unless waived
```
