---
name: skill-update-workflow
description: This skill should be used when the user asks to "update a skill", "promote skill changes back to toolkit", "diff toolkit skill", or "/skill-update-workflow". Compares a project-local copy of a skill against its canonical version in claude-toolkit, validates cross-references (slash-refs to other skills), and walks the user through promoting general improvements back to the toolkit while keeping project-specific changes local.
version: 0.1.0
---

# skill-update-workflow

## Purpose

Maintain `claude-toolkit/` as the single source of truth for reusable Claude Code components, while letting individual projects iterate on their copies. This skill is the **promotion workflow**: when a project-local edit to a skill has earned the right to flow back to the library, this skill diffs, validates, and applies it.

## When to Use

- **Manual invocation**: Call `/skill-update-workflow <skill-name>` from any project that has a local copy of a toolkit skill.
- **Trigger phrases**: "promote this skill change", "update toolkit skill X", "diff this skill against toolkit".
- **NOT for**: creating brand-new skills (use `/g-s-skill-creator` instead) or for project-specific skills that should never leave the project.

## Algorithm

### Step 1: Locate both copies
- Project copy: `<project>/.claude/skills/<skill-name>/`
- Toolkit copy: `C:/Users/brian/claude-toolkit/skills/<skill-name>/`

If toolkit copy doesn't exist, ask the user whether this skill should be added to the toolkit (different workflow — defer to `/g-s-skill-creator`).

### Step 2: Diff
Run a structured diff between project and toolkit:
- `SKILL.md` (frontmatter + body)
- Any handler scripts (`*.py`, `*.sh`)
- `README.md`

For each diff, classify as:
- **General improvement** — reusable across projects (lift to toolkit)
- **Project-specific** — only makes sense in this project (keep local, don't lift)
- **Bug fix** — almost always lift
- **Ambiguous** — ask the user

### Step 3: Cross-reference validator
Grep the project SKILL.md body for `/<name>` slash-refs. For each ref:
- Confirm the referenced skill exists in `claude-toolkit/skills/`.
- Flag any ref pointing at a renamed or removed skill.
- Suggest the canonical replacement (consult the rename table in the README of this skill).

Known historical renames to check:
- `/draft-commit` -> `/git-draft-commit`
- `/log-errors` / `/log_errors` -> `/errors-log`
- `/init-standup`, `/log-standup`, `/prep-standup`, `/finalize-standup` -> `/standup-init`, `/standup-log`, `/standup-prep`, `/standup-finalize`
- `/update-plan` / `/plan-update` -> `/plan-update-all`
- `/update-all-docs` -> `/docs-update-all`
- `/using-git-worktrees` -> `/git-using-worktrees`
- `/repo-hygiene` -> `/root-directory-hygiene`

### Step 4: Promotion checklist
Before lifting any change to the toolkit, confirm:
- [ ] Change is general, not project-specific.
- [ ] No hard-coded paths to project-specific files/dirs.
- [ ] No references to project-specific tools, branches, or vocabulary.
- [ ] All slash-refs resolve to current canonical names.
- [ ] If the skill's purpose/scope changed, update the YAML `description:` field.
- [ ] Bump the `version:` field if there is one.
- [ ] Update the toolkit README's component index if maturity tier changed (beta -> stable after second-project reuse).

### Step 5: Apply
- Apply lifted changes to `claude-toolkit/skills/<skill-name>/` (use temp-script byte-level write pattern for safety).
- Commit in `claude-toolkit/` with message `feat(<skill-name>): <summary> -- promoted from <project>`.
- Push to `origin/main`.

### Step 6: Reverse-sync (optional)
If other projects also have a copy of this skill, flag them so the user can re-sync. (Future: scripts/install.sh could do this automatically; for now, manual.)

## Output

Report back:
- Files diffed
- Changes lifted to toolkit
- Changes kept local (and why)
- Slash-refs flagged + rewrites suggested
- Toolkit commit hash + push status

## Failure modes

- **Toolkit missing the skill**: defer to `/g-s-skill-creator`.
- **Project copy heavily diverged**: don't auto-lift; surface the divergence and let the user decide what to keep.
- **Slash-ref to a skill that doesn't exist anywhere**: surface as a likely typo or stale ref; do not silently rewrite.
