# skill-update-workflow

**Tier**: beta (newly authored 2026-04-22, not yet reused)

## Purpose

The promotion workflow that keeps `claude-toolkit/` as the single source of truth. When you iterate on a project's local copy of a toolkit skill and the change deserves to flow back to the library, run this skill.

It diffs project copy vs toolkit copy, validates cross-references (slash-refs), classifies changes as general/project-specific/bug-fix, and applies lifted changes to the toolkit with a structured commit.

## Installation

```
cp -r skill-update-workflow/ <project>/.claude/skills/
```

Then commit to the project's repo. Invoke as `/skill-update-workflow <skill-name>`.

## Provenance

Authored on 2026-04-22 as part of the toolkit migration. Designed to formalize the promotion step that the toolkit's philosophy depends on but had no enforcement mechanism.
