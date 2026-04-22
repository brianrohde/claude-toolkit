# Skill Groups

This file is the source of truth for which skills belong to which group.
Used by `scripts/install.py` to install named groups in bulk.

Skills live flat in `skills/<name>/` -- this file is purely a logical grouping.
A skill may appear in multiple groups (rare).

## foundational

The "install everywhere" set. Toolkit-meta + git workflow + plan/docs hygiene + workspace
auditing. Install these in any new Claude Code project.

- claude-toolkit-pull
- claude-toolkit-push
- claude-toolkit-suggestion
- claude-toolkit-diff
- git-commit
- git-draft-commit
- git-using-worktrees
- git-worktree-merge
- plan-update-all
- root-directory-hygiene
- test-codebase-integrity
- workspace-audit
- workspace-cleanup
- workspace-enforce
- errors-log
- docs-update-all

## standup

Standup / supervisor-meeting workflow. Install in projects with a recurring stakeholder
update cadence.

- standup-init
- standup-log
- standup-prep
- standup-finalize

## webdev

Vercel / React / TypeScript web-dev guidance. Install in web frontend / fullstack projects.

- deploy-to-vercel
- vercel-cli-with-tokens
- vercel-composition-patterns
- vercel-react-best-practices
- vercel-react-native-skills
- vercel-react-view-transitions
- react-testing-patterns
- typescript-advanced-types
- webapp-testing
- web-design-guidelines

## How to extend

To add a new group, append a `## <group-name>` section here with a bulleted list of skill
names. The install script picks them up automatically. To add a skill to an existing group,
just append it to the group's bullet list.
