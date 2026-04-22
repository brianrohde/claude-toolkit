# branch_guard

**Tier**: beta (proven in CMT_Codebase, not yet reused elsewhere)

## What it does

A `UserPromptSubmit` hook that:

- **On `main`**: extracts keywords from the user's prompt, suggests a branch name with a sensible prefix (`thesis/`, `data/`, `config/`, `chore/`, or `session/`), and injects an interactive choice into Claude's system prompt — Claude then offers the user [1] create suggested branch, [2] custom name, [3] stay on main.
- **On any feature branch**: injects a brief confirmation note (`Git branch: <name> -- proceed normally.`) and passes through.
- **No git repo / detached HEAD**: silently no-ops.

The goal: keep `main` clean and deployable, especially in collaborative repos where multiple people (or parallel Claude agents / worktrees) may be working at once.

## When to use it

- **Collaborative repos** (multiple humans, or human + agents in worktrees) — primary use case.
- **Solo repos** where you still want a forcing function to avoid accidental commits to `main`.
- **Skip it** in scratch / experimental repos where committing straight to main is fine.

## Installation

1. Copy the script into the project:
   ```
   cp branch_guard.py <project>/.claude/hooks/branch_guard.py
   ```
2. Open `<project>/.claude/settings.json` and merge the `hooks` block from `settings.snippet.json` (below) into it. The path is **relative to the project root** — Claude Code runs hooks from the project's working directory, so `.claude/hooks/branch_guard.py` resolves correctly.
3. Commit both files to the project's repo.

## Configuration

The script has two project-tunable knobs near the top of the file:

- **`STOPWORDS`** — words ignored when extracting keywords from a prompt. The default list is generic English; usually fine to leave alone.
- **`PREFIX_KEYWORDS`** — vocabulary that maps prompt keywords to branch prefixes. The defaults (`thesis`, `data`, `config`, `chore`, `session`) are biased toward research / thesis work. **Override these per project** — for a web app you'd want `feat`, `fix`, `refactor`, etc.

To customize: edit the project's copy of `branch_guard.py` directly. The library copy stays generic.

## Dependencies

- Python 3 (uses `subprocess`, `json`, `re`, `sys` — all stdlib)
- `git` on PATH

## Public functions

These are importable by other scripts (e.g. a `draft-git-commit` mismatch checker that wants to verify the current branch matches the commit topic):

- `extract_keywords(text, n=6) -> list[str]`
- `pick_prefix(keywords) -> str`
- `slugify(keywords, max_words=3) -> str`
- `branch_matches_topic(branch, topic_keywords, topic_prefix) -> dict` — returns `{match, method, reason}` with `method` being `"strict"`, `"loose"`, or `"none"`.

## Why never register this globally

The original install lived in `~/.claude/settings.json` with a hard-coded absolute path to the CMT_Codebase copy. When the file was moved/renamed, every Claude Code session in every project broke with `[Errno 2] No such file or directory`. Always register per-project with a relative path.

## Provenance

Originally written for `CMT_Codebase` (MSc thesis project). Ported to the toolkit on 2026-04-22.
