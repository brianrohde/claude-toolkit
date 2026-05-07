---
name: git-using-worktrees
description: Use when starting a new Claude Code session that needs isolation — creates a git worktree under worktrees/ with the project branch naming convention, safety checks, and branch mismatch detection. Pairs with /git-draft-commit for cleanup and audit.
---

# Using Git Worktrees

## Overview

Git worktrees give each Claude Code session a **physically separate folder** with its own staging area, preventing the cross-session staging collisions that can cause accidental multi-file commits.

**Core principle:** One session → one worktree → one branch. Never two sessions in the same folder simultaneously.

**Announce at start:** "I'm using the git-using-worktrees skill to set up an isolated workspace."

---

## Two patterns

There are two valid ways to get session isolation. Choose deliberately.

### Pattern A — Sub-agent auto-worktree (DEFAULT, recommended)

Use the `Agent` tool with `isolation: "worktree"`. The harness auto-creates a worktree, runs the sub-agent there, and returns results to the main session. The main session never leaves its folder.

- **Proven** on 2026-04-22 in this repo (Plans A+B, commits `f7785ca` and `18c1c6e`).
- **Best for** scoped tasks, parallel work, and anything the main agent can fully specify up front.
- The main session stays on its own branch/folder; the sub-agent commits inside its worktree and reports back.

### Pattern B — Manual worktree + new Claude Code window

Use THIS skill to create a worktree and branch. Then the USER opens a **new terminal or VS Code window** at the worktree path and starts a **new Claude Code session** there.

- **Best for** interactive, multi-turn isolated work the user wants to steer themselves.
- Requires the user to physically switch windows — nothing the current session does will migrate it into the worktree.

### Critical fact

A running Claude Code session **cannot** `cd` into a worktree and keep working from it. The process stays pinned to its launch directory. Pattern B therefore **requires** opening a new Claude Code window. If you want isolation without switching windows, use Pattern A instead.

---

## Before execution — ask the user

Before creating any worktree, prompt the user:

> This task looks [parallelizable with X / sequential]. How would you like to run it?
> - **[A] Auto-isolate via sub-agent** (I handle worktree + cleanup; recommended default for scoped work)
> - **[B] Manual worktree** (I create `worktrees/<slug>/` + branch; you open a new Claude Code window there)
> - **[C] Run here on main** (no isolation; fine for tiny reversible edits)

If the user picks **B**: after creating the worktree, tell them the exact path and remind them:
> You must open a new Claude Code window at `worktrees/<slug>/` — this session cannot switch into it.

This prompt is also enforced by `.claude/rules/trigger-parallel-execution-prompt.md` at task kickoff; in-skill it's a second safeguard.

---

## This Project's Conventions

| Convention | Value |
|---|---|
| Worktree root | `worktrees/<slug>/` at repo root |
| Branch naming | `cc/<YYYYMMDD-HHMM>/<slug>` |
| Gitignored | `worktrees/*` is in `.gitignore` |
| Default pattern | Pattern A (sub-agent `isolation: "worktree"`) — use Pattern B only when user wants interactive control |

**Examples:**
```
worktrees/submitter-boundary-phase2/  →  branch: cc/20260423-1430/submitter-boundary-phase2
worktrees/hts-context-aware/          →  branch: cc/20260423-1600/hts-context-aware
worktrees/regex-fix-batch/            →  branch: cc/20260424-0900/regex-fix-batch
```

---

## Step 0 — Verify worktrees/ is gitignored

```bash
git check-ignore -q worktrees/test
```

If NOT ignored, add it before continuing:
1. Add `worktrees/*` to `.gitignore`
2. Commit: `git add .gitignore && git commit -m "chore: gitignore worktrees directory"`
3. Proceed

In THIS repo (`pta-cbp-parser`), `worktrees/*` is already gitignored — just verify.

This is the most critical safety check — worktree contents must never be tracked.

---

## Step 1 — Derive branch name from session topic

From the user's task, extract 2–4 keywords and build the branch name:

```
Topic: "fix submitter address boundary detection"
Slug:  submitter-boundary-phase2
Date:  2026-04-23, 14:30
Branch: cc/20260423-1430/submitter-boundary-phase2
Path:   worktrees/submitter-boundary-phase2/
```

Slug rules:
- Lowercase, hyphens only
- 2–4 words max
- Mirrors topic prefix where possible (feat, fix, chore, regex, phase)

---

## Step 2 — Check for existing worktrees

```bash
git worktree list
```

If a worktree already covers this topic/branch, ask the user whether to reuse it or create a new one. Do not silently create a duplicate.

---

## Step 3 — Create the worktree

```bash
git worktree add worktrees/<slug> -b cc/<YYYYMMDD-HHMM>/<slug>
```

**PowerShell note:** Run this directly — no heredoc, no subshell wrapping needed.

Then confirm:
```bash
git worktree list
```

Output should show the new worktree and its branch.

---

## Step 4 — Open the worktree (USER action, in a NEW Claude Code window)

**This step is done by the USER, not by the current Claude Code session.** The current session's job ends at "report ready" (Step 5). The current session CANNOT follow itself into the worktree.

The user opens a new terminal or VS Code window pointed at the worktree path and starts a fresh Claude Code session there:

```powershell
cd worktrees\<slug>
# or: code worktrees\<slug>
# then launch Claude Code in that window
```

From that new session, all Claude Code actions are isolated to this folder and branch. The main repo folder is unaffected.

---

## Step 5 — Report ready

```
Worktree ready at worktrees/<slug>/
Branch: cc/<YYYYMMDD-HHMM>/<slug>
Base: <SHA of HEAD at creation>

Open a NEW Claude Code window at worktrees/<slug>/ to work there.
This session cannot switch into the worktree — it stays pinned here.
```

---

## Ending a Session (cleanup)

Run from the **main repo folder** (not inside the worktree):

```bash
git worktree remove worktrees/<slug>
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
| Starting new session | Ask A/B/C; if B, run Steps 0–5 |
| `worktrees/` not gitignored | Add `worktrees/*` to `.gitignore` + commit first |
| Worktree already exists for topic | Ask user: reuse or new? |
| On `main` mid-session | See `/git-draft-commit` Step 0 — offer to create worktree |
| Session complete | `git worktree remove worktrees/<slug>` from repo root |
| Stale worktrees accumulating | `git worktree prune` |

---

## Common Mistakes

**Skipping the gitignore check**
- Problem: Worktree folder tracked by git, pollutes status
- Fix: Always run `git check-ignore -q worktrees/test` before creating

**Assuming the current session follows into the worktree**
- Problem: It doesn't. Claude Code stays pinned to its launch directory. A `cd` in Bash changes nothing about which folder the session is operating in across turns.
- Fix: You must open a NEW Claude Code window at the worktree path. Or use Pattern A (sub-agent `isolation: "worktree"`) if you don't want to switch windows.

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

**Called when:**
- Starting any session where isolation matters (new feature, regex batch, data work)
- `/git-draft-commit` detects `main` and offers worktree setup as Option [1]
- The branch guard hook fires and user chooses to create a new branch
