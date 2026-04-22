# Plan: User-global skill installer (`install-user`)

## Context

Today, skills in `claude-toolkit/skills/` are not visible to Claude Code unless they
are copied into a project's `.claude/skills/` (via `scripts/install.py`) or hand-installed
into `~/.claude/skills/`. The Claude Code harness only auto-discovers skills from those
two locations.

This is fine for **project-scoped skills** (e.g. `deploy-to-vercel`, `react-testing-patterns`) —
each project should pin its own version, and drift from the library is a feature, not a bug.
That's what `scripts/install.py` + `docs/guides/installing-components.md` are built around
("never symlink library→project").

It is **wrong for meta-skills** like `claude-toolkit-diff`, `-pull`, `-push`, `-suggestion`.
Those are about managing the toolkit itself. They need to:

- Be available in every Claude Code session on this machine (user-global, not project-scoped).
- Track the repo live — when the user edits `skills/claude-toolkit-diff/SKILL.md` and
  commits, the installed version should update with a plain `git pull`, not a re-run of
  an install script.

The fix is a second, separate installer (`scripts/install-user.{py,sh,ps1}`) that symlinks
selected skills from the local clone into `~/.claude/skills/`. It complements — does not
replace — the existing `install.py`.

**Outcome after executing this plan:**

- User runs `python scripts/install-user.py foundational` once on each of their machines.
- `~/.claude/skills/claude-toolkit-{diff,pull,push,suggestion}` exist as symlinks pointing
  into the clone.
- `git pull` inside the clone updates all four skills immediately, no re-install needed.
- Other users cloning this repo can run the same command and get the same result.
- The existing `install.py` (project-scoped copy flow) is untouched and still correct
  for its use case.

## Files to add

### 1. `scripts/install-user.py` (new)

Python 3, stdlib-only. Mirrors `install.py`'s argument style so the two feel like siblings.

**Usage:**

```
python install-user.py                          # interactive, lists groups
python install-user.py foundational             # install the foundational group (default target)
python install-user.py claude-toolkit-diff ...  # install named skills
python install-user.py all                      # install every skill in skills/
python install-user.py foundational --copy      # force copy instead of symlink
python install-user.py foundational --force-all # no prompts on conflicts
python install-user.py foundational --dry-run   # report what would happen
```

**Behavior:**

1. Resolve toolkit root the same way `install.py` does — `$CLAUDE_TOOLKIT` env var, else
   `Path(__file__).resolve().parent.parent`. Reuse `find_toolkit()` logic (copy-paste
   rather than import, to keep the script standalone).
2. Resolve destination: `Path.home() / ".claude" / "skills"`. Create if missing.
3. Parse `skills/SKILL_GROUPS.md` using the same `parse_groups()` from `install.py`
   (copy-paste; see `scripts/install.py:63-78`). Targets can be group names or skill names;
   special target `all` means every folder under `skills/`.
4. For each resolved skill name:
   - Source: `skills/<name>/` (absolute path — required on Windows for symlinks).
   - Destination: `~/.claude/skills/<name>/`.
   - If destination exists:
     - If it's a symlink already pointing at the same source → skip silently ("in sync").
     - If it's a symlink to a different target → prompt: relink / skip. `--force-all`: relink.
     - If it's a real directory → prompt: replace with link / skip. `--force-all`: replace.
       Replace means `shutil.rmtree()` then create symlink. Warn before rmtree.
   - If destination doesn't exist → create symlink (or copy under `--copy`).
5. Symlink creation:
   - Use `os.symlink(src, dst, target_is_directory=True)`.
   - On Windows, this raises `OSError` (WinError 1314, `ERROR_PRIVILEGE_NOT_HELD`) if
     Developer Mode is off and the process isn't elevated. Catch this specifically:
     print a clear message explaining Developer Mode (Settings → System → For developers),
     and suggest re-running with `--copy`. Exit non-zero. Do not fall back automatically —
     the user should make a conscious choice between live-update symlinks and frozen copies.
6. `--copy` fallback: uses the same `copy_skill()` approach as `install.py` (byte-level
   `rglob` copy; see `scripts/install.py:179-191`). Same drift caveat as the project
   installer.
7. Summary output: added / relinked / replaced / skipped / failed, same style as
   `install.py` (see `scripts/install.py:359-371`).
8. Next-steps footer: reminds user that live updates now flow through `git pull` inside
   the toolkit clone.

**Key differences from `install.py` (document in the script's docstring so the two
don't get confused):**

| Aspect          | `install.py`                | `install-user.py`                   |
|-----------------|-----------------------------|-------------------------------------|
| Destination     | `<project>/.claude/skills/` | `~/.claude/skills/`                 |
| Default method  | Byte copy                   | Symlink (copy opt-in via `--copy`)  |
| Update model    | Re-run installer            | `git pull` inside the toolkit clone |
| Match logic     | Exact / rename / fuzzy      | Exact only (user-global = simple)   |
| Intended for    | Project-scoped skills       | Meta-skills + personal globals      |

### 2. `scripts/install-user.sh` (new)

Thin bash wrapper, same pattern as `scripts/install.sh:1-7`:

```bash
#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec python "$DIR/install-user.py" "$@"
```

### 3. `scripts/install-user.ps1` (new)

PowerShell wrapper for Windows users who don't have a bash:

```powershell
#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
& python "$Dir\install-user.py" @args
```

## Files to edit

### 4. `scripts/README.md`

Add a new section **"install-user.py / install-user.sh / install-user.ps1"** above the
"Future helpers" section. Explicitly contrast with `install.py`:

- `install.py` → project-scoped copies (per-project pinning, drift is intentional).
- `install-user.py` → user-global symlinks (live-updated via `git pull`).

Include the usage block from section 1 above and a short note about Developer Mode on
Windows.

### 5. `docs/guides/installing-components.md`

Currently states "never symlink library→project" — that's correct for project-scoped
skills and should stay. Add a short new subsection **"User-global meta-skills (symlinks
are fine here)"** that:

- Explains the distinction: project-scoped skills must be pinned (copy); user-global
  meta-skills should track live (symlink).
- Points to `scripts/install-user.py` as the way to set up the user-global flow.
- Re-emphasizes the absolute-path warning for `~/.claude/settings.json` still applies to
  settings, not to `~/.claude/skills/` symlinks.

## Not doing

- **Not touching `install.py`.** It works, and its project-scoped copy semantics are the
  right thing for non-meta skills.
- **Not auto-installing on machine boot.** Symlinks are created once; updates flow through
  `git pull`. No scheduler, no hook, no watcher.
- **Not wiring hooks or rules.** Those still need manual `settings.json` merging per the
  existing install guide. Only skills are covered here.
- **Not publishing as a Claude Code plugin.** Discussed with the user; agreed that's
  overkill for now. Revisit if this toolkit is ever published for broader use.
- **Not installing all 33 skills globally by default.** Too noisy — every global skill
  is considered for auto-suggestion in every session. Default target is `foundational`
  (the four meta-skills). User can pass `all` if they really want everything.

## Verification

1. **Dry run on current machine:**
   ```
   python scripts/install-user.py foundational --dry-run
   ```
   Expect: four planned symlinks listed, no filesystem changes.

2. **Actual install:**
   ```
   python scripts/install-user.py foundational
   ```
   Expect: four symlinks created at `~/.claude/skills/claude-toolkit-{diff,pull,push,suggestion}`.
   If Developer Mode is off on Windows, expect a clear error message pointing to the setting
   and to `--copy`. (User currently has it off per earlier registry check.)

3. **Visibility check:** Start a new Claude Code session in any directory. Type
   `/claude-toolkit-diff` — it should now appear in auto-suggest.

4. **Live-update check:** Edit `skills/claude-toolkit-diff/SKILL.md` in the clone (e.g.,
   tweak the description). In a new Claude Code session, confirm the updated description
   is what the harness sees (via Skill tool listing or by reading `~/.claude/skills/claude-toolkit-diff/SKILL.md`
   — should show the edit, proving the symlink is live).

5. **Idempotency check:** Re-run the installer. Expect "already in sync" for all four
   skills; no prompts, no changes.

6. **Copy-mode check:** On a separate test dir or after removing the symlinks, run with
   `--copy`. Expect real directory copies, and editing the source should NOT update the
   installed copy (confirming the fallback behaves as documented).

7. **Cross-machine check (optional, later):** On a second machine or VM, clone the repo,
   run `python scripts/install-user.py foundational`, confirm the four skills become
   available.

## Files touched (summary)

- **New:** `scripts/install-user.py`, `scripts/install-user.sh`, `scripts/install-user.ps1`
- **Edited:** `scripts/README.md`, `docs/guides/installing-components.md`
- **Untouched:** `scripts/install.py`, `scripts/install.sh`, all skills, all hooks, all
  rules, `skills/SKILL_GROUPS.md`, `skills/RENAMES.md`.

## Post-execution follow-ups (requested by user)

After implementation, run:
- `/docs-update-all` — refresh any docs that reference installer flow.
- `/git-draft-commit` — draft commit for the new installer + doc edits.
- `/git-push` — push to origin.
