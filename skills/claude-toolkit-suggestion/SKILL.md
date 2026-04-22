---
name: claude-toolkit-suggestion
description: This skill should be used when the user asks "what toolkit skills should I install", "/claude-toolkit-suggestion", "find toolkit skills for this project", or names a keyword (e.g., "/claude-toolkit-suggestion testing"). Scans the claude-toolkit library and recommends which components fit the current project based on its tech stack, file types, existing skills, and an optional keyword. Recommendation only -- does NOT install. Use /claude-toolkit-pull to install a recommended skill.
version: 0.1.0
---

# claude-toolkit-suggestion

## Purpose

Help the user discover which toolkit components are relevant to the current project. The toolkit is a curated library; this skill is the "browse and recommend" surface.

This skill **does not install** anything. It only suggests. To install a suggestion, run `/claude-toolkit-pull <name>` or `/claude-toolkit-push <name>` (depending on direction).

## Trigger

`/claude-toolkit-suggestion [optional keyword]`

Examples:
- `/claude-toolkit-suggestion` -> recommend based on project tech stack alone.
- `/claude-toolkit-suggestion testing` -> filter recommendations to testing-related skills.
- `/claude-toolkit-suggestion vercel` -> show all vercel-* skills with relevance scoring.

## Algorithm

### Step 1: Locate the toolkit
Same resolution as `/claude-toolkit-pull`:
1. `$CLAUDE_TOOLKIT` env var.
2. `~/claude-toolkit/`.
3. `~/.claude-toolkit/`.
4. Ask user.

### Step 2: Profile the project
Gather signals from the current working directory:
- **Package files**: `package.json` (Node/web), `pyproject.toml` / `requirements.txt` (Python), `Cargo.toml` (Rust), `go.mod` (Go).
- **Frameworks**: React (jsx/tsx files, react in deps), Next.js, React Native (expo, react-native deps), Vercel (vercel.json).
- **Workflow**: presence of `.claude/` -> already a Claude project; check `.claude/skills/`, `.claude/hooks/` for already-installed components.
- **Git**: `git remote -v` to see if it's a real repo with collaborators (recommend collab skills).
- **Test infra**: `tests/`, `__tests__/`, `*.test.*`, `*.spec.*`.
- **Standup / supervisor workflow**: `project_updates/` folder presence.

### Step 3: Score each toolkit component
For each skill/hook/rule in the toolkit, compute a relevance score:
- **Hard match** (high): tech stack signal matches skill purpose (e.g., `vercel.json` present + vercel-* skill).
- **Soft match** (medium): adjacent (e.g., React project + react-testing-patterns).
- **Generic match** (low): always-useful (e.g., `git-draft-commit`, `errors-log`, `branch_guard`).
- **Anti-match** (skip): mismatched stack (e.g., suggest `react-*` skills for a pure-Python project).
- **Already installed** (note): skill exists in `<project>/.claude/skills/<name>/` -> mark as installed; suggest `/claude-toolkit-diff` to compare.

If the user passed a keyword, multiply matches that hit the keyword in skill name OR YAML `description:` field.

### Step 4: Group and present
Output as three buckets:

```
=== Strongly recommended (hard matches) ===
- skill-name -- one-line reason -- install: /claude-toolkit-pull skill-name

=== Worth considering (soft matches) ===
- ...

=== Already installed (consider /claude-toolkit-diff to check freshness) ===
- ...
```

Cap each bucket at ~10 entries. If a bucket is empty, omit it.

### Step 5: Suggest next action
End the output with a one-line action recommendation:
- "Install the strongly-recommended skills with `/claude-toolkit-pull <name>` (one at a time)."
- Or, if many overlaps: "Run `/claude-toolkit-diff` first to see which installed skills are stale."

## Output

Structured recommendation list as above. No file modifications. No git operations.

## Failure modes

- **Toolkit not found**: ask user, don't guess.
- **No project signals at all** (e.g., empty dir): fall back to recommending the always-useful core (git-draft-commit, errors-log, branch_guard).
- **Keyword matches nothing**: report no matches; suggest browsing without keyword.
