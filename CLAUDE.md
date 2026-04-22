# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal library of reusable Claude Code components (hooks, skills, rules, agents, helper scripts). Components live under `.claude/` so this repo is itself a valid Claude Code project — skills, hooks, and rules auto-load when you open a session here. Components flow out to consumer projects' own `.claude/` directories via `scripts/install.py`.

Consequence for editing: there is no dev server, no test suite, no build step, and no lint config. Changes are validated either in-place (open a session here and invoke the skill) or by installing into a real project and smoke-testing there (see `docs/guides/installing-components.md`).

## Core model (read before editing)

- **Library → project, never project → library automatically.** `scripts/install.py` copies skills from `.claude/skills/` into a destination project's `.claude/skills/`. Each project owns its copy and may diverge. Promotion back to the library is manual via the `/claude-toolkit-push` skill.
- **Copy, not symlink, for project installs.** This is deliberate — see the "Critical rule" in `docs/guides/installing-components.md`. An absolute-path symlink in a shared settings file is what created the need for this repo.
- **`.claude/skills/SKILL_GROUPS.md` is authoritative** for which skills belong to the `foundational` / `standup` / `webdev` groups. The installer re-parses it on every run — add a skill to a group by editing that file, not the script.
- **`.claude/skills/RENAMES.md` is authoritative** for historical skill renames. The installer consults it to detect that a destination's old-named skill is the same as a toolkit skill under its new name. Every rename must be appended here or the rename-match prompt won't fire.

## Commands

All run from the repo root. There are no tests, builds, or linters.

```bash
# Install skills into a consumer project (interactive if no targets)
python scripts/install.py <project-path> [group-or-skill-name ...]
python scripts/install.py ~/myproject foundational
python scripts/install.py ~/myproject foundational webdev
python scripts/install.py ~/myproject git-commit standup-log
python scripts/install.py ~/myproject foundational --force-all  # skip prompts

# Bash wrapper (Unix)
./scripts/install.sh <project-path> [targets...]
```

The installer does **not** install hooks or rules — those require `settings.json` merging and manual wiring. Follow `docs/guides/installing-components.md` for those.

## Repo layout

```
.claude/
  hooks/     Claude Code hook scripts + settings.snippet.json per hook
  skills/    SKILL.md + handler files per skill (flat — groups are logical)
  rules/     Project-agnostic rule docs (markdown, not executable)
  plans/     Plan/outcome scaffolding (plan_files/, outcome_files/)
.agents/     Custom agent definitions (currently just a README; no agents yet)
docs/        Toolkit documentation
scripts/     install.py + install.sh wrapper
```

Note: hooks, skills, and rules moved under `.claude/` so the repo itself is a valid Claude Code project. Older copies of `scripts/install.py` that hardcode `skills/` (repo-root) will not find anything — the installer needs to look under `.claude/skills/` now. Verify this before trusting a run.

For a browsable list of every component with tier + description, see the component index table in `README.md`.

## Editing conventions

- **Skill folder name must equal the YAML `name:` field in its `SKILL.md`.** The installer relies on this. If you rename a skill folder, also update the frontmatter and add a `old -> new` line to `skills/RENAMES.md`.
- **Each component subfolder gets a `README.md`** stating: what it does, when to use, configuration, dependencies, and a maturity tier (stable / beta / experimental — see the main README).
- **Hooks ship a `settings.snippet.json`** with a **relative path** to the hook script. Never hard-code absolute paths in that snippet — the whole point of this toolkit is to prevent exactly that class of bug.
- **Don't put this repo in OneDrive.** OneDrive's encoding / CRLF / EEXIST behavior corrupts Python files in dependent projects (see README "Cross-machine sync"). Keep it on a plain local drive; sync via GitHub.

## When adding a new skill

1. Create `.claude/skills/<kebab-name>/SKILL.md` with frontmatter `name:` matching the folder.
2. Add a `README.md` with maturity tier and usage.
3. If it belongs in an existing group, append it to that group's bullet list in `.claude/skills/SKILL_GROUPS.md`. If it's general-purpose, add to `foundational`.
4. Update the component index table in `README.md`.
5. If it replaces an older skill, add the rename to `.claude/skills/RENAMES.md`.

## When adding a hook

1. Create `.claude/hooks/<name>/<name>.py` and `.claude/hooks/<name>/settings.snippet.json` (relative path).
2. Add `.claude/hooks/<name>/README.md` with tier, trigger event (PreToolUse / UserPromptSubmit / etc.), and what it blocks or modifies.
3. Add it to the component index in the main `README.md`.
4. Do **not** try to wire it into `scripts/install.py` — hook installation is intentionally manual.
