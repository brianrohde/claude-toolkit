---
name: claude-toolkit-pull
description: This skill should be used when the user asks to "pull from toolkit", "install toolkit skills", "/claude-toolkit-pull", or names a toolkit skill, group, or destination repo (e.g., "/claude-toolkit-pull foundational" or "/claude-toolkit-pull foundational ~/some-other-repo"). Pulls one or more skills (or a named group from skills/SKILL_GROUPS.md) from the claude-toolkit library into a project. By default targets the current project; if a destination path is given, targets that repo instead. Per-skill diff + fuzzy rename detection + confirm before overwrite. Opposite of /claude-toolkit-push.
version: 0.2.0
---

# claude-toolkit-pull

## Purpose

Pull (sync down) one or more components from `claude-toolkit/` into a project. Two modes:

1. **Local mode** (no destination arg): install into the current working directory's `.claude/skills/`.
2. **Remote mode** (destination path given): install into `<destination>/.claude/skills/` -- useful when working from inside the toolkit and fanning out to other projects, or when you want to refresh a project from a session anywhere.

Per-skill, the algorithm checks if the destination already has a corresponding skill via three matching strategies (exact name -> known rename -> fuzzy description), shows a diff, and asks the user what to do. Opposite direction of `/claude-toolkit-push`.

## Trigger

`/claude-toolkit-pull [target ...] [destination-path] [--force-all]`

Where `target` is a group name from `skills/SKILL_GROUPS.md` (e.g., `foundational`, `webdev`, `standup`) or an individual skill folder name. Multiple targets allowed. The last positional arg is treated as a destination path if it looks like a path (contains `/` or `\\` or starts with `~`) and exists as a directory.

Examples:
- `/claude-toolkit-pull` -> interactive: list groups, ask which to install into current project.
- `/claude-toolkit-pull foundational` -> install foundational group into current project.
- `/claude-toolkit-pull git-commit` -> install one named skill into current project.
- `/claude-toolkit-pull foundational ~/myproject` -> install foundational group into the named repo.
- `/claude-toolkit-pull foundational webdev ~/myproject` -> multiple groups, named destination.
- `/claude-toolkit-pull foundational ~/myproject --force-all` -> auto-accept all overwrite prompts.

## Algorithm

This skill primarily delegates to `scripts/install.py` in the toolkit, which implements the matching + diff + prompt logic. The skill's job is to:
1. Resolve the toolkit path.
2. Resolve the destination (current dir, or the path arg).
3. Resolve targets (groups / skill names).
4. Invoke `install.py` and surface its output to the user.
5. Stage results for git review.

### Step 1: Locate the toolkit
1. `$CLAUDE_TOOLKIT` env var.
2. `~/claude-toolkit/`.
3. `~/.claude-toolkit/`.
4. Ask the user.

### Step 2: Resolve destination
- If the user's argv last token is a path (contains a separator or `~`) and exists, that is the destination.
- Otherwise, destination = current working directory.
- The destination must be a directory; create `<destination>/.claude/skills/` if missing.

### Step 3: Resolve targets
- Each token that is not the destination is a target.
- A target may be a group name (from `<toolkit>/skills/SKILL_GROUPS.md`) or a skill name.
- Groups expand to their skill list; skills resolve directly.
- Deduplicate while preserving order.
- If the user passed nothing, list groups interactively.

### Step 4: Per-skill matching (handled by install.py)
For each toolkit skill `<name>`:
1. **Exact match**: `<destination>/.claude/skills/<name>/` exists.
2. **Rename match**: consult `<toolkit>/skills/RENAMES.md` for any `old -> <name>` pair where `<destination>/.claude/skills/<old>/` exists.
3. **Fuzzy match**: compare YAML `description:` fields and folder-name token sets across all destination skills; treat as a candidate match if Jaccard similarity (0.4 * name + 0.6 * description) >= 0.5.

### Step 5: Per-skill prompt
For each skill the script categorizes:
- **No match** -> install cleanly.
- **Exact match, identical** -> skip (already in sync).
- **Exact match, differs** -> show diff; ask `overwrite / skip`.
- **Rename match** -> tell user `<old> <-> <name>`; ask `replace-and-rename / install-alongside / skip`.
- **Fuzzy match** -> tell user the candidate + similarity; ask `install-alongside / replace-and-rename / skip`. Suggest the user add the rename pair to `RENAMES.md` if they confirm it's the same skill.

`--force-all` auto-accepts: overwrite for exact-differs, replace for rename matches, install-alongside for fuzzy matches.

### Step 6: Report + stage in git
After install.py finishes, surface its summary:
- Added (clean) / Replaced (exact) / Renamed-replaced (rename or fuzzy) / Kept alongside / Skipped / Failed.
- For renamed-replaced, list the `old -> new` pairs explicitly.

Then suggest:
```
cd <destination>
git status
git add .claude/skills/
git commit -m "chore: sync skills from claude-toolkit"
```

Do NOT auto-commit -- let the user review.

## Concrete usage examples

### Refresh CMT_Codebase with the latest foundational skills
You suspect CMT has outdated toolkit-meta skills (e.g., still `claude-toolkit-update` instead of `claude-toolkit-pull`, still `using-git-worktrees` instead of `git-using-worktrees`):

```
/claude-toolkit-pull foundational "C:/Users/brian/OneDrive/.../CMT_Codebase"
```

Per-skill the script will:
- Detect `using-git-worktrees` in CMT and offer rename-replace to `git-using-worktrees`.
- Detect `claude-toolkit-update` (if still present) and offer rename-replace to `claude-toolkit-pull`.
- Install missing toolkit-meta skills cleanly (`claude-toolkit-push`, `claude-toolkit-suggestion`, `claude-toolkit-diff`).
- Show diffs for any other skill where CMT and toolkit have drifted.

### Install webdev skills into a fresh React project
```
/claude-toolkit-pull webdev ~/my-react-app
```

### Install one skill, current project, no prompts
```
/claude-toolkit-pull git-draft-commit --force-all
```

## Output

Surface the install.py summary verbatim plus the suggested `git status` / `git add` / `git commit` commands.

## Failure modes

- **Toolkit not found**: ask user, do not guess.
- **Destination not a directory**: ask user.
- **Unknown target (not a group, not a skill)**: warn but continue with valid targets.
- **install.py errors**: surface its stderr.
- **Hook target without settings.json merge**: this skill installs SKILLS only. To install a hook, copy the folder manually and merge `settings.snippet.json` -- see `docs/guides/installing-components.md`.
