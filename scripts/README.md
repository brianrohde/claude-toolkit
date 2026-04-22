# Scripts

Helpers for working with the toolkit itself.

## install.py / install.sh

Bulk-install skills from the toolkit into a project's `.claude/skills/`.

```
# install a group
python install.py ~/myproject foundational

# install multiple groups
python install.py ~/myproject foundational webdev

# install named skills only
python install.py ~/myproject git-commit standup-log

# interactive (lists groups, asks)
python install.py ~/myproject

# bash wrapper (Unix)
./install.sh ~/myproject foundational
```

Groups are defined in `../.claude/skills/SKILL_GROUPS.md`. Add or edit groups there;
the install script reads them on every run.

## Per-skill matching

For each toolkit skill, the script looks for a corresponding skill in the destination via three strategies:

1. **Exact name match** (`<dest>/.claude/skills/<name>/`).
2. **Known rename** (consults `../.claude/skills/RENAMES.md`). Catches cases like the destination still having `using-git-worktrees` while the toolkit now ships `git-using-worktrees`.
3. **Fuzzy match** (compares YAML `description:` and folder-name token sets; threshold ~0.5 weighted Jaccard). Catches accidental description-similar skills under different names.

Per match kind, the script prompts:
- Exact + identical -> skip silently.
- Exact + differs -> overwrite / skip.
- Rename match -> replace-and-rename (delete old, install new) / install-alongside / skip.
- Fuzzy match -> install-alongside / replace-and-rename / skip (also suggests adding the pair to `RENAMES.md` if confirmed).
- No match -> install cleanly.

Pass `--force-all` to auto-accept (overwrite for exact-differs, replace for rename matches, install-alongside for fuzzy matches). Use with care.

## Adding a known rename

Edit `../.claude/skills/RENAMES.md` and append a line `old-name -> new-name` inside the code block. The script reparses on every run.

The script does NOT install hooks or rules -- those need `settings.json` merging
and rule auto-load wiring; install them manually per the install guide at
`../docs/guides/installing-components.md`.

## Future helpers (stubs)

- `promote.sh <project-path> <component-name>` -- diff project copy vs library copy
  (or use the `/claude-toolkit-push` skill, which does this interactively).
