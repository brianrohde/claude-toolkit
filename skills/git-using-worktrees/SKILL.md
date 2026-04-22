---
name: git-using-worktrees
description: Use when starting a new Claude Code session that needs isolation — creates a git worktree under .cc/worktrees/ with the project branch naming convention, safety checks, and branch mismatch detection. Pairs with /git-draft-commit for cleanup and audit.
---

# Using Git Worktrees

## Overview

Git worktrees give each Claude Code session a **physically separate folder** with its own staging area, preventing the cross-session staging collisions that caused a 300-file accidental commit in this project.

**Core principle:** One session → one worktree → one branch. Never two sessions in the same folder simultaneously.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

---

## This Project's Conventions

| Convention | Value |
|---|---|
| Worktree root | `.cc/worktrees/<slug>/` inside repo root |
| Branch naming | `cc/<YYYYMMDD-HHMM>/<slug>` |
| Gitignored | `.cc/` is already covered by `.gitignore` — no action needed |
| Reference guide | `docs/reference/git-worktrees-and-parallel-sessions.md` |
| Branch strategy | `docs/reference/git-branch-strategy.md` |

**Examples:**
```
.cc/worktrees/nielsen-fix/    →  branch: cc/20260420-1430/nielsen-fix
.cc/worktrees/chapter-2/      →  branch: cc/20260420-1600/chapter-2
.cc/worktrees/data-pipeline/  →  branch: cc/20260421-0900/data-pipeline
```

---

## Step 0 — Verify .cc/ is gitignored

```bash
git check-ignore -q .cc
```

If NOT ignored, add it before continuing:
1. Add `.cc/` to `.gitignore`
2. Commit: `git add .gitignore && git commit -m "chore: gitignore .cc worktree directory"`
3. Proceed

This is the most critical safety check — worktree contents must never be tracked.

---

## Step 1 — Derive branch name from session topic

From the user's task, extract 2–4 keywords and build the branch name:

```
Topic: "fix Nielsen auth token"
Slug:  nielsen-auth-fix
Date:  2026-04-20, 14:30
Branch: cc/20260420-1430/nielsen-auth-fix
Path:   .cc/worktrees/nielsen-auth-fix/
```

Slug rules:
- Lowercase, hyphens only
- 2–4 words max
- Mirrors topic prefix where possible (thesis, data, config, chore, feat, fix)

---

## Step 2 — Check for existing worktrees

```bash
git worktree list
```

If a worktree already covers this topic/branch, ask the user whether to reuse it or create a new one. Do not silently create a duplicate.

---

## Step 3 — Create the worktree

```bash
git worktree add .cc/worktrees/<slug> -b cc/<YYYYMMDD-HHMM>/<slug>
```

**PowerShell note:** Run this directly — no heredoc, no subshell wrapping needed.

Then confirm:
```bash
git worktree list
git branch --show-current
```

Output should show the new worktree and its branch.

---

## Step 4 — Open the worktree

The user points their terminal or VS Code at the worktree path:

```powershell
cd .cc\worktrees\<slug>
# or: code .cc\worktrees\<slug>
```

From this point, all Claude Code actions in that terminal are isolated to this folder and branch. The main `CMT_Codebase/` folder is unaffected.

---

## Step 5 — Report ready

```
Worktree ready at .cc/worktrees/<slug>/
Branch: cc/<YYYYMMDD-HHMM>/<slug>
Base: <SHA of HEAD at creation>

You're isolated from main and any other active sessions.
Work here, commit here, and open a draft PR when done.
```

---

## Ending a Session (cleanup)

Run from the **main repo folder** (not inside the worktree):

```bash
git worktree remove .cc/worktrees/<slug>
```

The folder is deleted. The branch and all commits survive in git history. Merge or open a PR before removing if you haven't already.

To list and prune stale worktrees:
```bash
git worktree list
git worktree prune
```

---

## Branch Mismatch Detection

Before committing, `/git-draft-commit` re-derives the session topic and checks the current branch using two-level matching:

| Level | Condition | Result |
|---|---|---|
| **Strict** | prefix matches AND ≥1 keyword in slug | Proceed silently |
| **Loose** | ≥1 keyword anywhere in branch name | Proceed, note loose match |
| **None** | Neither condition met | Flag mismatch, ask user to resolve |

If on `main` instead of a worktree branch, `/git-draft-commit` will warn and offer to create a worktree before proceeding.

---

## Quick Reference

| Situation | Action |
|---|---|
| Starting new session | Create worktree (Steps 0–5) |
| `.cc/` not gitignored | Add to `.gitignore` + commit first |
| Worktree already exists for topic | Ask user: reuse or new? |
| On `main` mid-session | See `/git-draft-commit` Step 0 — offer to create worktree |
| Session complete | `git worktree remove .cc/worktrees/<slug>` from repo root |
| Stale worktrees accumulating | `git worktree prune` |

---

## Common Mistakes

**Skipping the gitignore check**
- Problem: Worktree folder tracked by git, pollutes status
- Fix: Always run `git check-ignore -q .cc` before creating

**Creating worktree inside an existing worktree**
- Problem: Nested worktrees confuse git and Claude
- Fix: Always run `git worktree list` first; create from repo root

**Using bash heredoc syntax in commit commands (PowerShell)**
- Problem: `$(cat <<'EOF')` throws parser errors in PowerShell
- Fix: Use plain double-quoted string: `git commit -m "subject\n\n- bullet"`

**Two sessions in the same folder**
- Problem: Shared staging area → cross-session commit pollution
- Fix: Each session gets its own worktree path

---

## Integration

**Pairs with:**
- `/git-draft-commit` — commit from within the worktree; trailers include worktree path
- `docs/reference/git-worktrees-and-parallel-sessions.md` — plain-language guide for Brian and Enrico
- `docs/reference/git-branch-strategy.md` — full branch naming rules
- `.claude/rules/trigger-branch-strategy.md` — auto-fires on session start if on `main`

**Called when:**
- Starting any session where isolation matters (new feature, chapter edit, data work)
- `/git-draft-commit` detects `main` and offers worktree setup as Option [1]
- The branch guard hook fires and user chooses to create a new branch
