# check_file_edit

**Tier**: beta (proven in CMT_Codebase + pta-cbp-parser)

## What it does

A `PreToolUse` hook that blocks two classes of dangerous file operations:

1. **Direct `Edit`/`Write` on `.py` files inside OneDrive paths** — these trigger EEXIST mkdir errors and `\b -> \x08` byte corruption. The hook denies the call with a message pointing the user at the safe temp-script pattern.
2. **Any `Edit`/`Write` on `.env` files** — prevents accidental secret leakage. The user must edit `.env` files manually outside Claude Code.

If neither condition matches, the hook exits 0 and the tool call proceeds normally.

## When to use it

- **Any project stored inside OneDrive** (Windows users especially) — primary use case.
- **Any project with `.env` files** — protects secrets even outside OneDrive.
- **Skip it** in projects that live entirely on local disk and have no `.env` files.

## Installation

1. Copy the script into the project:
   ```
   cp check_file_edit.py <project>/.claude/hooks/check_file_edit.py
   ```
2. Open `<project>/.claude/settings.json` and merge the `hooks` block from `settings.snippet.json` into it. The path is **relative to the project root**.
3. Commit both files to the project's repo.

## Configuration

No tunable knobs — the script is intentionally minimal. To adjust the rules, edit the `block_onedrive_py` and `block_env` conditions directly.

If a project needs different rules (e.g., allow `.py` writes in a specific subdirectory), fork the script per-project rather than overgeneralizing the library version.

## Dependencies

- Python 3 (stdlib only: `sys`, `json`)

## Why never register this globally

Per the toolkit's "no globals" principle, register per-project with a relative path. This also lets projects opt out (a scratch repo on local disk doesn't need the OneDrive guard).

## Provenance

Originally written for `CMT_Codebase`. Ported to the toolkit on 2026-04-22.
