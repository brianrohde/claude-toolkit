---
trigger: "codebase_navigation|file_lookup|where_is|find_the|how_.*_connect"
priority: "high"
---

# Repository Map Reference

**Always consult this first** when answering questions about file locations, module responsibilities, or how components fit together.

## Quick Links

- **Primary reference:** [repository_map.md](../../docs/dev/repository_map.md) — complete file-to-purpose mapping
- **Thesis workflow:** [CLAUDE.md](../../CLAUDE.md) — session entry point and workflow phases
- **Architecture:** [docs/architecture.md](../../docs/architecture.md) — System A/B architecture decisions
- **Compliance:** [thesis/thesis-context/formal-requirements/cbs_guidelines_notes.md](../../thesis/thesis-context/formal-requirements/cbs_guidelines_notes.md) — CBS thesis requirements

## When to Use This Rule

This rule **auto-loads** when your prompt matches patterns like:
- "where is the X module?"
- "what does Y file do?"
- "which file handles Z?"
- "how do System A and System B connect?"
- "find the agent for..."

**Default behavior:** Consult `repository_map.md` **before** exploring with Glob/Grep. This prevents unnecessary file searches and ensures consistent mental models.

## Map Update Ceremony

The map should be updated whenever:
- Files are moved or renamed
- Module responsibilities change
- New agents or sections are added
- New phases are completed

**Include in session end workflow:** Add "update repository_map.md" as an explicit task when repo structure changes.
