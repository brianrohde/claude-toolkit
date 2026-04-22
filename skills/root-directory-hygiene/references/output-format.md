# Output Format

Canonical schema for the structured report emitted by `/repo-hygiene analyze` and `/repo-hygiene plan`.

---

## Full Report Schema

```
═══════════════════════════════════════════════════
 REPO-HYGIENE REPORT
 Scope:      root | docs | all
 Policy:     default
 Date:       YYYY-MM-DD
═══════════════════════════════════════════════════

COMPLIANCE:  compliant | conditionally-compliant | non-compliant
SCORE:       0–100  (100 = fully compliant)

STATUS SUMMARY
  Root:      pass | warn | fail
  Docs:      pass | warn | fail
  Metadata:  pass | warn | fail

───────────────────────────────────────────────────
VIOLATIONS
───────────────────────────────────────────────────

[V001] HIGH    | ROOT-MD
  File:        CHANGELOG.md
  Problem:     Root Markdown not on allowlist
  Fix:         move → docs/archive/CHANGELOG.md
  Confidence:  high
  Auto-apply:  yes

[V002] MEDIUM  | DOC-DATE
  File:        docs/planning/release-plan.md
  Problem:     Time-bound doc missing YYYY_MM_DD- filename prefix
  Fix:         rename → docs/planning/2026_04_19-release_plan.md
  Confidence:  high
  Auto-apply:  yes

[V003] MEDIUM  | DOC-META-ABSENT
  File:        docs/guides/zotero-setup.md
  Problem:     No YAML front matter; evergreen guide — not required
  Fix:         skip (evergreen docs exempt from metadata requirement)
  Confidence:  high
  Auto-apply:  n/a

[V004] MEDIUM  | DOC-OVERLAP
  Files:       docs/planning/plan-a.md ↔ docs/planning/plan-b.md
  Problem:     Both files cover the same topic
  Fix:         Requires human review — not auto-applied
  Confidence:  low
  Auto-apply:  no

───────────────────────────────────────────────────
PROPOSED TARGET STRUCTURE
───────────────────────────────────────────────────

  docs/
  ├── guides/          ← how-to, setup, runbooks
  ├── reference/       ← CLI, API, config, quick-reference
  ├── explanation/     ← architecture, design rationale
  ├── tutorials/       ← walkthroughs, demos
  ├── decisions/       ← ADRs, design decisions
  ├── planning/        ← plans, RFCs, migration docs
  ├── handover/        ← internal handover docs
  ├── notes/           ← meeting notes, session logs
  ├── archive/         ← deprecated / superseded docs
  └── assets/
      └── images/      ← shared diagrams and screenshots

───────────────────────────────────────────────────
FIX PLAN
───────────────────────────────────────────────────

  [V001] move CHANGELOG.md → docs/archive/CHANGELOG.md
         update inbound links if any

  [V002] rename docs/planning/release-plan.md
              → docs/planning/2026_04_19-release_plan.md

  [V004] SKIPPED — overlap requires human review
         To apply: /repo-hygiene apply V004 after deciding canonical doc

───────────────────────────────────────────────────
SAFETY NOTES
───────────────────────────────────────────────────

  Auto-fixable (high confidence):  V001, V002
  Requires confirmation:           V004
  Skipped (exempt):                V003

  To apply safe fixes:  /repo-hygiene fix --safe
  To apply specific:    /repo-hygiene apply V001,V002

═══════════════════════════════════════════════════
```

---

## Field Definitions

### Header block

| Field | Values | Description |
|-------|--------|-------------|
| `Scope` | `root`, `docs`, `all` | Which areas were audited |
| `Policy` | `default` | Policy variant used |
| `Date` | `YYYY-MM-DD` | Date of the audit run |

### Status summary

| Field | Values | Threshold |
|-------|--------|-----------|
| `Compliance` | `compliant`, `conditionally-compliant`, `non-compliant` | `compliant` = 0 violations; `conditionally-compliant` = MEDIUM/LOW only; `non-compliant` = any HIGH |
| `Score` | 0–100 | 100 = zero violations; each HIGH −20, MEDIUM −10, LOW −3 |
| `Root` | `pass`, `warn`, `fail` | `fail` if any HIGH ROOT-* violation; `warn` if any MEDIUM |
| `Docs` | `pass`, `warn`, `fail` | `fail` if any HIGH DOC-* violation; `warn` if any MEDIUM |
| `Metadata` | `pass`, `warn`, `fail` | `fail` if any HIGH DOC-META-* violation; `warn` if MEDIUM |

### Violation entry

| Field | Description |
|-------|-------------|
| `[V{NNN}]` | Sequential violation ID for this audit run; use in `apply` subcommand |
| Severity | `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| Rule ID | From `references/rule-catalog.md` |
| `File` | Repo-relative path |
| `Problem` | Human-readable description of the violation |
| `Fix` | Proposed action |
| `Confidence` | `high`, `medium`, `low` |
| `Auto-apply` | `yes` = included in `fix --safe`; `no` = requires explicit `apply V…`; `n/a` = exempt |

### Fix plan entry

One line per violation ID. States the exact operation: `move`, `rename`, `insert metadata`, `archive`, `rewrite links`, or `SKIPPED`.

### Safety notes block

Three groups:
- **Auto-fixable**: IDs where `fix --safe` will act
- **Requires confirmation**: IDs where `apply V…` is needed
- **Skipped**: IDs that are exempt or informational

---

## Post-Fix Report (after `fix --safe` or `apply`)

Same schema as above, re-run after changes, prefixed with:

```
═══════════════════════════════════════════════════
 POST-FIX AUDIT
 Applied fixes: V001, V002
 Skipped:       V004 (requires confirmation)
═══════════════════════════════════════════════════
```

Then the full report as normal. Violations resolved by the applied fixes should no longer appear.
