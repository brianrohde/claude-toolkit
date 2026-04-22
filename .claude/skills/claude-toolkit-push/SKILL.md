---
name: claude-toolkit-push
description: This skill should be used when the user asks to "push skill to toolkit", "promote skill to toolkit", "/claude-toolkit-push", or names a project skill (e.g., "/claude-toolkit-push my-skill"). Pushes a project-local component (skill / hook / rule) up to the claude-toolkit library. Auto-detects whether this is a NEW component (first-time promotion) or an UPDATE to an existing toolkit component (shows diff, asks user to confirm, then overwrites). Project -> toolkit direction. The opposite of /claude-toolkit-pull.
version: 0.1.0
---

# claude-toolkit-push

## Purpose

Promote a project-local component to the toolkit library. Mirrors `git push` semantics:

- If the component **does not exist** in the toolkit yet -> first-time promotion. Scrub project-specific references, write a generic README, commit, push.
- If the component **already exists** in the toolkit -> show the diff, ask the user to confirm, then overwrite. Like a force-push but with a mandatory diff review step.

This is the **project -> toolkit** direction. For the reverse (pull a toolkit component into a project), use `/claude-toolkit-pull`.

## Trigger

`/claude-toolkit-push [optional component-name]`

Examples:
- `/claude-toolkit-push` -> ask which project component to push; offer a list.
- `/claude-toolkit-push my-cool-skill` -> push that skill (auto-detects new vs update).
- `/claude-toolkit-push branch_guard` -> works for hooks too (auto-detects type by location).

## Algorithm

### Step 1: Locate the toolkit
Resolve in this order:
1. `$CLAUDE_TOOLKIT` env var.
2. `~/claude-toolkit/` (Unix) or `%USERPROFILE%/claude-toolkit/` (Windows).
3. `~/.claude-toolkit/`.
4. Ask the user.

Verify the chosen path is a git repo with `skills/`, `hooks/`, `rules/` subdirs.

### Step 2: Resolve the source component
- If user passed a name, find it in `<project>/.claude/{skills,hooks,rules}/<name>/`.
- If no name, list all project components and ask which to push.
- Auto-detect type from location.

### Step 3: Detect mode (NEW vs UPDATE)
- If `<toolkit>/<type>/<name>/` does not exist -> mode = NEW.
- If it exists -> mode = UPDATE.

### Step 4: Generality audit (NEW mode only)
Scan the source for project-specific references that must be scrubbed:

- **Project name / domain**: e.g., specific project names, domain terms, supervisor / stakeholder vocabulary, document types.
- **Project-specific paths**: hard-coded absolute paths; project-specific subdirs the toolkit cannot assume exist.
- **Hard-coded user paths**: `C:/Users/<user>/...`, `/home/<user>/...`, OneDrive paths.
- **Project-specific tool names**: scripts that exist only in the source project.
- **Stale slash-refs**: refs to skills not in the toolkit's canonical name list.

For each flagged item, show the user the line and ask: rewrite generically / drop / keep (rare).

Apply rewrites to the destination files only -- never modify the project source.

### Step 5: Diff + confirm (UPDATE mode only)
Show a structured diff between project copy and toolkit copy:
- Files that will change (added / modified / removed).
- Per-file unified diff (or summary if very large).
- Any toolkit-side edits that will be **overwritten** -- this is the critical warning. If the toolkit has commits the project copy does not, the user is force-pushing over toolkit improvements; halt and recommend `/claude-toolkit-diff` to investigate before continuing.
- Cross-reference impact: slash-refs that other toolkit skills make to this one, and whether the new content breaks them.

Pause for explicit user confirmation. Default is interactive -- only auto-proceed if the user passed a `--force` flag in their prompt.

### Step 6: Copy
Use the byte-level temp-script copy pattern (Windows/OneDrive safe):
1. Write a temp `.py` script.
2. Copy source tree to `<toolkit>/<type>/<name>/`.
3. For NEW mode, apply Step 4 rewrites to destination.
4. For UPDATE mode, copy source as-is (rewrites should already be in source if needed).

### Step 7: Write / refresh README (NEW mode only)
Create `<toolkit>/<type>/<name>/README.md` with title, tier (`beta`), generic purpose, install command, provenance.

For UPDATE mode, leave the existing toolkit README in place unless the user explicitly asks to refresh it.

### Step 8: Update toolkit indexes (NEW mode only)
Add a row to root `claude-toolkit/README.md` and `<toolkit>/<type>/README.md`.

For UPDATE mode, only refresh the index if the description changed materially.

### Step 9: Commit and push
In the toolkit directory:
- `git add` the affected paths.
- Commit message: `feat(<type>): add <name> -- promoted from <project>` (NEW) or `feat(<type>): update <name> from <project>` (UPDATE).
- `git push origin main`.

### Step 10: Suggest follow-up
- NEW: skill is now at tier `beta`. Bump to `stable` after second-project reuse. Other projects can install via `/claude-toolkit-pull <name>`.
- UPDATE: other projects with this skill installed should run `/claude-toolkit-pull <name>` to receive the update; or run `/claude-toolkit-diff` first to check for local edits.

## Output

Report:
- Mode (NEW or UPDATE)
- Source path / destination path
- For NEW: generality rewrites applied
- For UPDATE: diff summary + what the user confirmed to overwrite
- Files written
- Toolkit commit hash + push status
- Suggested next steps for downstream projects

## Failure modes

- **Toolkit not found / not a git repo**: ask user; do not initialize one without permission.
- **Push fails (no auth, no remote)**: leave the commit local; tell the user to push manually.
- **UPDATE mode + toolkit has unmerged commits**: halt; recommend `/claude-toolkit-diff` to reconcile first.
- **NEW mode + user wants to keep project-specific refs**: warn that the toolkit copy will not be project-agnostic; require explicit override.
