# Skill Renames

Canonical name history. Used by `/claude-toolkit-pull`, `/claude-toolkit-diff`, and
`scripts/install.py` to detect that a destination's old-named skill is the same skill
under its new toolkit name.

Format: `old-name -> new-name` (one per line, in code blocks).

```
using-git-worktrees -> git-using-worktrees
repo-hygiene -> root-directory-hygiene
plan-update -> plan-update-all
draft-commit -> git-draft-commit
draft_commit -> git-draft-commit
log-errors -> errors-log
log_errors -> errors-log
init-standup -> standup-init
init_standup -> standup-init
log-standup -> standup-log
log_standup -> standup-log
prep-standup -> standup-prep
prep_standup -> standup-prep
finalize-standup -> standup-finalize
finalize_standup -> standup-finalize
update-plan -> plan-update-all
update_plan -> plan-update-all
update-all-docs -> docs-update-all
update_all_docs -> docs-update-all
claude-toolkit-update -> claude-toolkit-pull
claude-toolkit-new-skill -> claude-toolkit-push
skill-update-workflow -> claude-toolkit-push
```

## How it's used

When pushing toolkit skills to a destination project, the install script:
1. Looks for an exact-name match in `<dest>/.claude/skills/`.
2. If miss, consults this file: any rename pair `old -> new` where `new` is the toolkit
   name being installed gets matched against `<dest>/.claude/skills/<old>/`.
3. If still no match, falls back to description-field similarity (currently a simple
   normalized-substring match; can be tightened to Jaccard if false positives appear).
4. If a match is found by rename or fuzzy means, the user is told and offered:
   replace-and-rename (delete old, install new) / install-alongside (keep both) / skip.

To add a new rename: append a line in the code block above. The script re-parses on
every run.
