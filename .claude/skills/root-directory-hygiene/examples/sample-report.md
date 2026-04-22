# Sample Report — `/repo-hygiene analyze`

Example output from auditing the CMT_Codebase root on 2026-04-20.

---

```
═══════════════════════════════════════════════════
 REPO-HYGIENE REPORT
 Scope:      all
 Policy:     default
 Date:       2026-04-20
═══════════════════════════════════════════════════

COMPLIANCE:  non-compliant
SCORE:       54 / 100

STATUS SUMMARY
  Root:      fail   (3 HIGH violations)
  Docs:      warn   (4 MEDIUM violations)
  Metadata:  warn   (2 MEDIUM violations)

───────────────────────────────────────────────────
VIOLATIONS
───────────────────────────────────────────────────

[V001] HIGH    | ROOT-MD
  File:        ZOTERO_QUICK_REFERENCE.md
  Problem:     Root Markdown not on allowlist
  Fix:         move → docs/reference/zotero-quick-reference.md
  Confidence:  high
  Auto-apply:  yes

[V002] HIGH    | ROOT-MD
  File:        SKILL_ACTIVATION_SUMMARY.md
  Problem:     Root Markdown not on allowlist
  Fix:         move → docs/reference/skill-activation-summary.md
  Confidence:  high
  Auto-apply:  yes

[V003] HIGH    | ROOT-MD
  File:        2026_04_18-17_58-INTEGRATION_AUDIT_AND_HANDOVER.md
  Problem:     Root Markdown not on allowlist; appears to be a handover doc
  Fix:         move → docs/handover/2026_04_18-integration_audit_and_handover.md
  Confidence:  high
  Auto-apply:  yes

[V004] MEDIUM  | DOC-META-ABSENT
  File:        docs/ZOTERO_SETUP_GUIDE.md
  Problem:     Guides folder doc has no YAML front matter (type/status/created missing)
  Fix:         insert YAML front matter block (type: guide, status: active)
  Confidence:  high
  Auto-apply:  yes

[V005] MEDIUM  | DOC-DATE
  File:        docs/planning/some-plan.md  (hypothetical)
  Problem:     Planning doc missing YYYY_MM_DD- filename prefix
  Fix:         rename → docs/planning/2026_04_20-some_plan.md
  Confidence:  high
  Auto-apply:  yes

[V006] MEDIUM  | DOC-PLACE
  File:        docs/ZOTERO_SETUP_GUIDE.md
  Problem:     Setup guide not in docs/guides/ subfolder
  Fix:         move → docs/guides/zotero-setup.md
  Confidence:  medium
  Auto-apply:  ask

[V007] MEDIUM  | DOC-STALE
  File:        docs/notes/old-meeting.md  (hypothetical, dated > 90 days, no owner)
  Problem:     Dated note older than 90 days with no active owner declared
  Fix:         move → docs/archive/old-meeting.md; set status: archived
  Confidence:  medium
  Auto-apply:  ask

[V008] LOW     | DOC-FMT-FENCE
  File:        docs/architecture.md
  Problem:     2 code blocks missing language tag
  Fix:         add language identifier to fenced code blocks
  Confidence:  high
  Auto-apply:  yes

───────────────────────────────────────────────────
PROPOSED TARGET STRUCTURE
───────────────────────────────────────────────────

  docs/
  ├── guides/
  │   ├── zotero-setup.md           ← moved from docs/ZOTERO_SETUP_GUIDE.md
  ├── reference/
  │   ├── zotero-quick-reference.md ← moved from root
  │   └── skill-activation-summary.md ← moved from root
  ├── explanation/
  ├── planning/
  ├── handover/
  │   └── 2026_04_18-integration_audit_and_handover.md ← moved from root
  ├── notes/
  ├── archive/
  └── assets/
      └── images/

───────────────────────────────────────────────────
FIX PLAN
───────────────────────────────────────────────────

  [V001] move ZOTERO_QUICK_REFERENCE.md
              → docs/reference/zotero-quick-reference.md
         rewrite inbound links if any

  [V002] move SKILL_ACTIVATION_SUMMARY.md
              → docs/reference/skill-activation-summary.md
         update CLAUDE.md reference link

  [V003] move 2026_04_18-17_58-INTEGRATION_AUDIT_AND_HANDOVER.md
              → docs/handover/2026_04_18-integration_audit_and_handover.md

  [V004] insert YAML front matter in docs/ZOTERO_SETUP_GUIDE.md:
         ---
         title: Zotero Setup Guide
         type: guide
         status: active
         created: 2026-04-XX
         ---

  [V005] rename docs/planning/some-plan.md
              → docs/planning/2026_04_20-some_plan.md

  [V006] PENDING CONFIRMATION — move docs/ZOTERO_SETUP_GUIDE.md
              → docs/guides/zotero-setup.md
         (medium confidence — confirm before applying)

  [V007] PENDING CONFIRMATION — archive docs/notes/old-meeting.md
         (stale doc — confirm before moving)

  [V008] add language tags to 2 code fences in docs/architecture.md

───────────────────────────────────────────────────
SAFETY NOTES
───────────────────────────────────────────────────

  Auto-fixable (high confidence):  V001, V002, V003, V004, V005, V008
  Requires confirmation:           V006, V007

  To apply safe fixes:  /repo-hygiene fix --safe
  To apply all:         /repo-hygiene apply V001,V002,V003,V004,V005,V006,V007,V008

═══════════════════════════════════════════════════
```
