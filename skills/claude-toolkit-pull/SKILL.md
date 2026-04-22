---
name: claude-toolkit-pull
description: This skill should be used when the user asks to "update toolkit skill", "pull latest from toolkit", "refresh toolkit copy", "/claude-toolkit-pull", or names a specific toolkit skill (e.g., "/claude-toolkit-pull git-using-worktrees"). Pulls the canonical version of a skill (or hook/rule) from the claude-toolkit library into the current project, overwriting the project's local copy. The opposite direction of /claude-toolkit-push.
version: 0.1.0
---

# claude-toolkit-pull (formerly claude-toolkit-pull)

## Purpose

Pull (sync down) a project's local copy of a toolkit component with the canonical version in `claude-toolkit/`. Use when:
- The toolkit version has been improved and the project should adopt the change.
- The project's copy was accidentally modified and you want to reset it.
- A new project hasn't yet pulled the component at all.

This is the **library -> project** direction. For the reverse, see `/claude-toolkit-push` (first-time promotion) or `/claude-toolkit-push` (diff-and-promote existing).

## Trigger

`/claude-toolkit-pull [optional component-name]`

Examples:
- `/claude-toolkit-pull` -> ask the user which component to update; offer a list of project-installed components.
- `/claude-toolkit-pull git-using-worktrees` -> update only that skill.
- `/claude-toolkit-pull branch_guard` -> update the hook.

## Algorithm

### Step 1: Locate the toolkit
Resolve toolkit root in this order:
1. `$CLAUDE_TOOLKIT` env var.
2. `~/claude-toolkit/` (Unix) or `%USERPROFILE%/claude-toolkit/` (Windows).
3. `~/.claude-toolkit/`.
4. Ask the user for the path.

Verify the chosen path contains `skills/`, `hooks/`, and `rules/` subdirs. If not, ask the user.

### Step 2: Resolve the component
- If user passed a name, find it in the toolkit (`skills/<name>/`, `hooks/<name>/`, or `rules/<name>/`).
- If no name given, list all components currently installed in `<project>/.claude/{skills,hooks,rules}/` that ALSO exist in the toolkit, and ask the user which to update.
- If the requested component doesn't exist in the toolkit, fail with a clear message and suggest `/claude-toolkit-suggestion` to discover what's available.

### Step 3: Show the diff
Before overwriting, show the user a summary:
- Files that will change (added / modified / removed).
- Any **project-local edits that will be lost** -- this is the critical warning.
- Slash-refs in the new version that may need updating in other project skills (cross-reference impact).

### Step 4: Confirm
Pause for explicit user confirmation unless they passed a `--force` flag in their prompt. Default is interactive.

### Step 5: Apply
Use the byte-level temp-script copy pattern (Windows/OneDrive safe):
1. Write a temp `.py` script to `$TEMP/toolkit_update_<name>.py`.
2. Script reads source bytes from toolkit, writes to project, preserving subdir structure.
3. Run it via Bash.

For hooks: also remind the user to merge `settings.snippet.json` into `<project>/.claude/settings.json` if not already present.

### Step 6: Stage in git
- `git add <project>/.claude/<type>/<name>/`
- Suggest a commit message: `chore(toolkit): update <name> from claude-toolkit`.
- Do NOT auto-commit -- let the user review.

## Output

Report:
- Toolkit path used
- Component updated
- Files added / modified / removed
- Any project-local changes that were overwritten (with paths to backups if you made them)
- Suggested commit message
- Any cross-reference warnings for other project skills

## Failure modes

- **Toolkit not found**: ask user, don't guess.
- **Component not in toolkit**: suggest `/claude-toolkit-suggestion` and `/claude-toolkit-push`.
- **Project copy heavily diverged**: surface the divergence; recommend running `/claude-toolkit-push` first to promote any general improvements before overwriting.
- **Hook update without settings.json change**: warn the user that the snippet may need merging.
