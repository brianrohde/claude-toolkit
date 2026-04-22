# Rule Catalog

All rules enforced by `/repo-hygiene`. Rules are evaluated in severity order.

## Root Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| ROOT-MD | `.md` file at repo root not on allowlist | HIGH | High if destination folder is unambiguous | Yes |
| ROOT-DUP | Multiple README-like or same-topic files at root | HIGH | Low — canonical selection requires judgment | No |
| ROOT-ASSET | Image, PDF, or report artifact at root | MEDIUM | High for images/screenshots | Yes |

## Placement Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-PLACE | Markdown file in wrong folder for its inferred doc class | MEDIUM | Medium — inferred from filename and content signals | Ask |

## Naming Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-DATE | Time-bound doc missing `YYYY_MM_DD-` filename prefix | MEDIUM | High when doc class is clear from folder | Yes |
| DOC-NAME | Evergreen doc not in `kebab-case.md` | LOW | Medium if no inbound links | Ask |

## Metadata Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-META-ABSENT | Time-bound doc has no YAML front matter | MEDIUM | High when doc class is obvious from folder | Yes |
| DOC-META-FIELDS | YAML present but missing `title`, `type`, `status`, or `created` | MEDIUM | High for obvious fields | Yes |
| DOC-META-TYPE | `type:` value not in controlled vocabulary | LOW | High | Yes |
| DOC-META-STATUS | `status:` value not in controlled vocabulary | LOW | High | Yes |

## Staleness Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-STALE | Doc has `status: deprecated` or `status: archived` but not in `docs/archive/` | MEDIUM | High | Yes |
| DOC-STALE | Dated planning doc older than 90 days with no active owner field | MEDIUM | Medium | Ask |

## Formatting Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-FMT-HEADING | Heading levels skipped (e.g. H1 → H3) | LOW | High (mechanical) | Yes |
| DOC-FMT-FENCE | Code block missing language tag | LOW | High (mechanical) | Yes |
| DOC-FMT-LINK | Absolute internal repo link should be relative | LOW | Medium | Ask |

## Overlap Rules

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| DOC-OVERLAP | Two or more files share the same topic or title | MEDIUM | Low — canonical selection requires judgment | No — report only |

## Exception

| Rule ID | Description | Severity | Auto-fix confidence | Safe auto-apply |
|---------|-------------|----------|---------------------|-----------------|
| EXCEPTION | File violates a rule but is explicitly declared as a repo exception | Informational | N/A | N/A |

---

## Confidence Model

| Level | Meaning | Default action |
|-------|---------|---------------|
| High | Fix is mechanical; destination is unambiguous; no semantic judgment required | Auto-apply with `fix --safe` |
| Medium | Destination is likely correct but could be wrong; no inbound links confirmed | Propose; ask before applying |
| Low | Overlap, ambiguity, or semantic content decision required | Report only; require explicit `apply V…` |

---

## Severity Definitions

| Severity | Meaning |
|----------|---------|
| HIGH | Direct policy violation; root-pollution or canonical-file duplication |
| MEDIUM | Documentation hygiene issue that reduces discoverability or machine-readability |
| LOW | Formatting or naming convention issue; safe to batch-fix |
| Informational | Declared exception; no action needed |
