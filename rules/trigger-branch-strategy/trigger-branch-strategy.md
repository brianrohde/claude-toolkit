# Branch Strategy Rule

**Reference**: [docs/reference/GIT_BRANCH_STRATEGY.md](../../docs/reference/GIT_BRANCH_STRATEGY.md)

## Core principle

Every Claude Code session should work on a dedicated branch, not on `main`.
`main` is reserved for stable, reviewed, merged work — not active development.

## Layer A — Deterministic hook (primary)

A `UserPromptSubmit` hook fires on every opening message and runs
`.claude/hooks/branch_guard.py`. That script:

1. Reads the user's prompt text
2. Runs `git branch --show-current`
3. If on a **feature branch** → injects `✓ branch: <name>` and passes through
4. If on **`main`** → extracts topic keywords from the prompt, derives a
   suggested branch name using the naming convention below, and injects a
   structured interactive choice block that Claude must present to the user
   **before answering their question**

The hook is registered in `~/.claude/settings.json` (global, not in repo).

### Branch mismatch detection (used by `/draft-git-commit`)

`branch_guard.py` exports `extract_keywords`, `pick_prefix`, `slugify`, and
`branch_matches_topic` for use by the draft-git-commit skill. At commit time,
the skill re-derives the session topic and checks the current branch using
two-level matching:

| Level | Condition | Result |
|-------|-----------|--------|
| **Strict** | prefix matches AND ≥1 keyword in slug | Proceed silently |
| **Loose** | ≥1 keyword anywhere in branch name | Proceed, note loose match |
| **None** | Neither condition met | Flag mismatch, ask user to resolve |

## Layer B — Rule fallback (backup)

If the hook output is somehow absent, Claude must still perform the branch
check manually at the start of any session where git work is expected:

```bash
git branch --show-current
```

- **Feature branch** → proceed normally
- **`main`** → present the interactive choice block below before doing anything else

## Interactive choice block (present verbatim when on `main`)

```
You're on `main`. Before we start, let's move to a branch.

Suggested: `<prefix>/<slug>`

  [1] Create and switch to `<prefix>/<slug>`  →  git checkout -b <prefix>/<slug>
  [2] Use a different name (type it)
  [3] Stay on `main` (only if you're merging completed work)

Which would you like?
```

After the user responds:
- **[1]** → run `git checkout -b <suggested>`, confirm success, then answer their question
- **[2]** → use the name they provide, run `git checkout -b <name>`, confirm, then answer
- **[3]** → ask "Are you sure? This is only recommended for merge/integration work." — if confirmed, note you're on `main` and proceed

## Branch naming convention

```
session/<topic>          # general chat / exploratory work
thesis/<chapter-topic>   # thesis content changes
data/<dataset-topic>     # data scripts or pipeline
config/<tool-topic>      # settings, tooling, integrations
chore/<cleanup-topic>    # refactoring, reorganization
```

## When committing on `main` IS allowed

- User is explicitly integrating/merging completed branch work into `main`
- User has reviewed the changes and confirms the commit is intentional
- The commit is a merge commit, not new feature work

## Committing on a feature branch

On a feature branch, `git add -A` is safe — the branch is isolated by design.
The draft-git-commit skill and all git workflows can proceed without restriction.

## Merging back to `main`

```bash
git checkout main
git merge <branch-name>     # or open a PR on GitHub
```

Before merging, review the diff:
```bash
git diff main..<branch-name>
```
