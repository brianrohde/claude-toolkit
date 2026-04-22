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

Groups are defined in `../skills/SKILL_GROUPS.md`. Add or edit groups there;
the install script reads them on every run.

Already-installed skills are skipped (use `/claude-toolkit-pull <name>` to update one).

The script does NOT install hooks or rules -- those need `settings.json` merging
and rule auto-load wiring; install them manually per the install guide at
`../docs/guides/installing-components.md`.

## Future helpers (stubs)

- `promote.sh <project-path> <component-name>` -- diff project copy vs library copy
  (or use the `/claude-toolkit-push` skill, which does this interactively).
