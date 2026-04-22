# Documentation Taxonomy

Folder structure, doc-type vocabulary, and filename conventions for all Markdown files outside the repo root.

---

## Approved Folder Taxonomy

| Folder | Doc types that belong here | Filename format |
|--------|---------------------------|-----------------|
| `docs/guides/` | How-to procedures, setup guides, runbooks, troubleshooting | `kebab-case.md` |
| `docs/reference/` | CLI options, config schemas, API notes, quick-reference sheets | `kebab-case.md` |
| `docs/explanation/` | Architecture overviews, design rationale, tradeoff discussions, roadmaps | `kebab-case.md` |
| `docs/tutorials/` | Learning walkthroughs, end-to-end demos, getting-started guides | `kebab-case.md` |
| `docs/decisions/` | Architecture decision records (ADRs), technology decisions, design decisions | `YYYY_MM_DD-decision-slug.md` |
| `docs/planning/` | Implementation plans, rollout plans, RFCs, migration plans, project plans | `YYYY_MM_DD-plan-slug.md` |
| `docs/handover/` | Internal handover docs for teammates or Claude instances getting up to speed | `YYYY_MM_DD-handover-slug.md` |
| `docs/notes/` | Meeting notes, session logs, research notes, discovery notes, audit notes | `YYYY_MM_DD-note-slug.md` |
| `docs/archive/` | Deprecated, superseded, or expired docs of any class | Preserve original stem; keep date prefix if present |
| `docs/assets/images/` | Shared images and diagrams referenced by docs | `kebab-case.{png,jpg,svg}` |

**Minimum viable tree** for a small repo: `docs/guides/`, `docs/reference/`, `docs/planning/`, `docs/archive/`. Add other folders when you have content for them.

---

## Doc-Type Controlled Vocabulary

Use these values for the `type:` field in YAML front matter. The skill flags any value not in this list as `DOC-META-TYPE`.

| Value | Use for |
|-------|---------|
| `guide` | How-to procedure, setup guide, runbook |
| `reference` | CLI/API/config/schema reference, quick-reference sheet |
| `explanation` | Architecture, design rationale, conceptual overview |
| `tutorial` | Learning walkthrough, end-to-end demo |
| `decision` | ADR, design decision, technology choice |
| `plan` | Implementation plan, rollout plan, project plan, RFC |
| `handover` | Internal handover doc |
| `note` | Meeting note, session log, research note, discovery note |
| `postmortem` | Incident review, retrospective |
| `rfc` | Request for comment (use `plan` as an alternative for lightweight RFCs) |
| `adr` | Architecture decision record (subset of `decision`; use when ADR numbering is enforced) |

---

## Status Controlled Vocabulary

Use these values for the `status:` field. The skill flags any value not in this list as `DOC-META-STATUS`.

| Value | Meaning |
|-------|---------|
| `draft` | Work in progress; not yet authoritative |
| `active` | Current, authoritative, maintained |
| `deprecated` | Superseded or no longer recommended; should be archived |
| `archived` | No longer maintained; moved to `docs/archive/` |

---

## Filename Convention Details

### Time-bound docs — `YYYY_MM_DD-slug_with_underscores.md`

All docs in: `docs/decisions/`, `docs/planning/`, `docs/handover/`, `docs/notes/`, plus any postmortem or RFC.

**Format rules:**
- Date portion: `YYYY_MM_DD` — underscores between year, month, day
- Separator between date and slug: single hyphen `-`
- Slug: `lowercase_words_with_underscores`
- No double hyphens, no spaces, no CamelCase

**Examples:**
```
2026_04_19-handover_system_b.md
2026_04_19-plan_data_pipeline_v2.md
2026_04_17-meeting_notes_supervisor.md
2026_03_15-decision_use_polars.md
2026_01_10-postmortem_api_outage.md
```

**Why this format**: On Windows, double-clicking in a filename selects hyphen-separated tokens. Using underscores within `2026_04_19` means one double-click selects the whole date block; one double-click on the slug selects the whole title — two clean, selectable units in File Explorer and rename inputs.

### Evergreen docs — `kebab-case.md`

All docs in: `docs/guides/`, `docs/reference/`, `docs/explanation/`, `docs/tutorials/`.

**Format rules:**
- Lowercase, words separated by hyphens
- No underscores, no spaces, no uppercase

**Examples:**
```
zotero-setup.md
api-reference.md
system-b-architecture.md
getting-started.md
```

### Root special files — exact conventional names

```
README.md
CONTRIBUTING.md
CHANGELOG.md
SECURITY.md
CODE_OF_CONDUCT.md
SUPPORT.md
CODEOWNERS
CITATION.cff
```

---

## Inferring Doc Class from Path

When the skill cannot determine a doc's class from its YAML `type:` field, it infers from folder:

| Folder | Inferred class | Time-bound? |
|--------|---------------|-------------|
| `docs/guides/` | `guide` | No |
| `docs/reference/` | `reference` | No |
| `docs/explanation/` | `explanation` | No |
| `docs/tutorials/` | `tutorial` | No |
| `docs/decisions/` | `decision` | Yes |
| `docs/planning/` | `plan` | Yes |
| `docs/handover/` | `handover` | Yes |
| `docs/notes/` | `note` | Yes |
| `docs/archive/` | (preserve original) | Conditional |
| Root (allowed) | (no type required) | No |
| Root (discouraged/forbidden) | Use content signals | Depends |

If a doc is in `docs/` but not in a recognised subfolder, treat as `DOC-PLACE` violation and suggest the best-fit folder.
