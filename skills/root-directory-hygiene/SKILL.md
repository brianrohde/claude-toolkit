---
name: root-directory-hygiene
description: >
  Repository root and Markdown documentation hygiene auditor.
  Analyzes the repo root against a minimal-root policy and audits
  Markdown files for correct folder placement, filename format,
  and YAML front matter completeness.
  Trigger: /root-directory-hygiene analyze | plan | fix --safe | apply V001,V002
compatibility: any
---

# repo-hygiene

Audit repository root cleanliness and Markdown documentation hygiene. Emits a structured compliance report, proposes a remediation plan, and applies only approved or explicitly safe fixes.

## When to Use

- Root directory has accumulated non-canonical Markdown or asset files
- Documentation files lack YAML front matter, correct naming, or correct folder placement
- Before a handover or major collaboration — confirm docs are discoverable and well-typed
- After a sprint or session — catch docs created in root that should live in `docs/`
- Periodic hygiene check on any project

## Subcommand Interface

```
/root-directory-hygiene analyze              # audit only — no changes
/root-directory-hygiene analyze --scope root # root files only
/root-directory-hygiene analyze --scope docs # markdown files only
/root-directory-hygiene plan                 # audit + full remediation plan
/root-directory-hygiene fix --safe           # apply high-confidence safe fixes only
/root-directory-hygiene apply V003,V007      # apply specific violation IDs
```

Default when no subcommand given: `analyze`.

---

## Workflow

### Step 1 — Discover

Use Glob and Read to gather:
- All files at repo root: `Glob("*")`
- All Markdown files: `Glob("**/*.md")`
- Detect repo type from root contents: Python (`pyproject.toml`), JS/TS (`package.json`), monorepo (`pnpm-workspace.yaml`/`turbo.json`), docs-heavy (`mkdocs.yml`/`docusaurus.config.*`), or plain
- Detect docs tooling: MkDocs, Docusaurus, Sphinx (`conf.py`), or none

### Step 2 — Classify root files

For every file at the repo root, assign one classification using the allowlist in `references/root-allowlist.md`:

| Class | Meaning |
|-------|---------|
| `required` | Must be present |
| `allowed` | Permitted when the repo actually uses it |
| `discouraged` | Should move to `docs/`; emit WARN |
| `forbidden` | Must not be in root; emit violation |
| `exception` | Explicitly declared exception — informational only |

### Step 3 — Classify Markdown files

For each `.md` file, evaluate all rules from `references/rule-catalog.md`. Key checks:

**Root rules**
- `ROOT-MD` (HIGH): `.md` at root not on allowlist → propose move to correct `docs/` subfolder
- `ROOT-DUP` (HIGH): multiple README-like or same-topic root docs
- `ROOT-ASSET` (MEDIUM): image/export at root

**Placement rules**
- `DOC-PLACE` (MEDIUM): file in wrong folder for its inferred doc class (use folder taxonomy in `references/doc-taxonomy.md`)

**Naming rules**
- `DOC-DATE` (MEDIUM): time-bound doc (plan, handover, note, ADR, RFC, postmortem, migration) missing `YYYY_MM_DD-` prefix
- `DOC-NAME` (LOW): evergreen doc not in `kebab-case.md`

**Metadata rules**
- `DOC-META-ABSENT` (MEDIUM): time-bound doc has no YAML front matter at all
- `DOC-META-FIELDS` (MEDIUM): YAML present but missing required fields (`title`, `type`, `status`, `created`)
- `DOC-META-TYPE` (LOW): `type:` value not in controlled vocabulary
- `DOC-META-STATUS` (LOW): `status:` value not in controlled vocabulary

**Staleness rules**
- `DOC-STALE` (MEDIUM): `status: deprecated` or `status: archived` but not in `docs/archive/`; or dated plan older than 90 days with no active owner

**Formatting rules** (LOW severity, auto-fixable)
- `DOC-FMT-HEADING`: heading levels skipped (e.g. H1 → H3)
- `DOC-FMT-FENCE`: code block missing language tag
- `DOC-FMT-LINK`: absolute internal repo link (should be relative)

**Overlap**
- `DOC-OVERLAP` (MEDIUM): two or more files share the same topic/title — report only, do not auto-fix

### Step 4 — Produce structured report

Emit the report using the schema in `references/output-format.md`:

```
Compliance: compliant | conditionally-compliant | non-compliant
Policy variant: default
Summary score: 0–100
Root status: pass | warn | fail
Docs status: pass | warn | fail
Metadata status: pass | warn | fail

Violations:
- [V001] HIGH    | ROOT-MD        | CHANGELOG.md → move to docs/archive/        | confidence: high
- [V002] MEDIUM  | DOC-DATE       | docs/planning/release-plan.md → rename to 2026_04_19-release_plan.md | confidence: high
- [V003] MEDIUM  | DOC-META-ABSENT| docs/guides/zotero-setup.md → insert YAML front matter | confidence: high
- [V004] MEDIUM  | DOC-OVERLAP    | docs/planning/plan-a.md ↔ docs/planning/plan-b.md share topic | confidence: low

Proposed target structure:
  docs/guides/
  docs/planning/
  docs/decisions/
  docs/handover/
  docs/notes/
  docs/reference/
  docs/explanation/
  docs/archive/
  docs/assets/images/

Proposed fix plan:
- [V001] move CHANGELOG.md → docs/archive/CHANGELOG.md; update inbound links
- [V002] rename docs/planning/release-plan.md → docs/planning/2026_04_19-release_plan.md
- [V003] insert YAML front matter block in docs/guides/zotero-setup.md
- [V004] SKIPPED — overlap requires human review

Safety notes:
- V001, V002, V003: auto-fixable (high confidence)
- V004: requires confirmation — not auto-applied
```

### Step 5 — Apply (mode-gated)

| Mode | Behaviour |
|------|-----------|
| `analyze` | Emit report only. No file changes. |
| `plan` | Emit report + full remediation plan. No file changes. |
| `fix --safe` | Apply HIGH-confidence mechanical fixes only. After each move: rewrite relative links in affected files. Re-run audit. Emit post-fix report. Suggest `git stash` before bulk changes. |
| `apply V…` | Apply only the named violation IDs. Same safety protocol as `fix --safe`. |

**Safety invariants (never break these):**
- Prefer move over delete — never delete files
- Never apply `DOC-OVERLAP` fixes automatically
- Never archive or delete without explicit approval
- After any move, update relative internal links in affected files
- Re-run the audit after applying changes and show the post-fix report
- If confidence is medium or low, report and ask — do not apply

---

## YAML Front Matter Schema

Required for all **time-bound** docs (plans, handovers, notes, ADRs, RFCs, postmortems, migration plans):

```yaml
---
title: Clear canonical title
type: guide | decision | handover | plan | reference | note | adr | postmortem | rfc
status: draft | active | deprecated | archived
owner: person-or-team          # recommended
created: YYYY-MM-DD
updated: YYYY-MM-DD            # update whenever content changes
tags:                          # optional
  - topic
supersedes: path-or-id         # optional
superseded_by: path-or-id      # optional
review_by: YYYY-MM-DD          # optional — for time-sensitive docs
---
```

**Evergreen docs** (README, CONTRIBUTING, stable guides, reference pages): YAML front matter is not required. Git history is the authoritative provenance record.

---

## Filename Convention

| Doc class | Format | Example |
|-----------|--------|---------|
| Time-bound (plan, handover, note, ADR, RFC, postmortem, migration) | `YYYY_MM_DD-slug_with_underscores.md` | `2026_04_19-handover_system_b.md` |
| Evergreen (guide, reference, explanation, tutorial) | `kebab-case.md` | `zotero-setup.md` |
| Root special files | Exact conventional name | `README.md`, `CONTRIBUTING.md` |

**Why `YYYY_MM_DD-slug`**: On Windows, double-clicking in a filename selects hyphen-separated tokens. Underscores inside the date block and inside the slug mean one double-click selects the whole date, one selects the whole title — two clean units.

---

## References

- `references/rule-catalog.md` — all rule IDs, severity, confidence, auto-apply status
- `references/root-allowlist.md` — canonical root allowlist/denylist with rationale
- `references/doc-taxonomy.md` — folder taxonomy, type vocabulary, filename rules
- `references/output-format.md` — full structured report schema
- `examples/sample-report.md` — example output from a real analyze run
