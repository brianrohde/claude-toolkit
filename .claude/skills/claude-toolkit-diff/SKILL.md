---
name: claude-toolkit-diff
description: This skill should be used when the user asks "what skills are out of sync with toolkit", "/claude-toolkit-diff", "compare project skills to toolkit", "check toolkit freshness". Compares every skill, hook, and rule that exists in BOTH the current project and the claude-toolkit library, reports which side is newer (or whether they have diverged in incompatible ways), and recommends per-component sync direction.
version: 0.1.0
---

# claude-toolkit-diff

## Purpose

Audit synchronization status between the project's local Claude Code components and the canonical toolkit. Surface stale copies, project-local improvements that should be promoted, and divergences that need manual reconciliation.

This skill is **read-only** -- it never writes. It tells you what action to take. The follow-up actions are:
- `/claude-toolkit-pull <name>` -- pull toolkit version into project (project copy was stale).
- `/claude-toolkit-push <name>` -- promote project edits back to toolkit (toolkit was stale).
- Manual reconciliation -- both sides edited; merge required.

## Trigger

`/claude-toolkit-diff` (no arguments)

Optional flag in the user's prompt: `--type=skills|hooks|rules` to scope the comparison.

## Algorithm

### Step 1: Locate the toolkit
Standard resolution (env var -> default paths -> ask).

### Step 2: Enumerate overlap
For each subtree (`skills/`, `hooks/`, `rules/`):
- List components in `<toolkit>/<type>/`.
- List components in `<project>/.claude/<type>/`.
- Intersection = the overlap set to compare.

Skip components present only on one side (those are handled by `/claude-toolkit-pull` for toolkit-only or `/claude-toolkit-push` for project-only -- mention them in a separate "Project-only" / "Toolkit-only" appendix).

### Step 3: Per-component comparison
For each overlapping component, compute three signals:

1. **Content equality** (byte-level): identical files, identical tree -> mark `IN_SYNC`.
2. **One-sided newer** (only one side modified relative to last shared state):
   - Compare git mtime of the toolkit copy vs project copy via `git log -1 --format=%at -- <path>`.
   - If only one side has commits since the other's mtime: that side is newer -> `TOOLKIT_NEWER` or `PROJECT_NEWER`.
3. **Divergent** (both sides edited since last sync, content differs): mark `DIVERGED`.

For each component, also report:
- File count delta (added / removed / modified).
- Any slash-refs in the project copy that point at renamed/removed skills (cross-ref staleness).

### Step 4: Group output

```
=== IN_SYNC (n) ===
- skill-a, skill-b, ...    [no action needed]

=== TOOLKIT_NEWER (n) -- project is stale ===
- skill-c -- toolkit ahead by 2 commits, last toolkit edit YYYY-MM-DD -- run /claude-toolkit-pull skill-c
- ...

=== PROJECT_NEWER (n) -- improvements waiting to promote ===
- skill-d -- project ahead, last project edit YYYY-MM-DD -- run /claude-toolkit-push skill-d
- ...

=== DIVERGED (n) -- manual reconciliation needed ===
- skill-e -- both sides edited; show file-by-file diff and ask user
- ...

=== Cross-reference staleness ===
- skill-f references /old-name (not in toolkit) -- canonical is /new-name

=== APPENDIX: Project-only ===
- skill-x -- consider /claude-toolkit-push skill-x

=== APPENDIX: Toolkit-only ===
- skill-y -- consider /claude-toolkit-pull skill-y
```

### Step 5: No mutations
Do not stage, commit, or modify anything. End with the summary and recommended commands.

## Output

Structured grouped report as above. Final line: total components in each bucket.

## Failure modes

- **Toolkit not found**: ask user, don't guess.
- **Not in a project with `.claude/`**: report nothing-to-compare; suggest running `/claude-toolkit-suggestion` to bootstrap.
- **No git history on toolkit or project**: fall back to file mtimes; flag the comparison as low-confidence.
- **Mixed line endings (CRLF vs LF)**: normalize before byte-equality check; do not flag as a difference.
