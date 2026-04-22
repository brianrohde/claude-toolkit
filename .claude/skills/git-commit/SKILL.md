---
name: git-commit
description: Execute a git commit from an approved draft message. Handles staging, PowerShell-safe commit command, and post-commit checklist. Always verify worktree isolation before committing. Pairs with /git-draft-commit (message generation) and /git-using-worktrees (workspace setup).
compatibility:
  tools: [Bash, Read]
  requires: git repository
---

# Git Commit

Execute a git commit from an approved draft message. This skill handles the submission half of the commit workflow — staging files and running the commit command.

**Upstream:** Use `/git-draft-commit` first to generate and approve the message.
**Prerequisite:** Worktree must be verified or `/git-using-worktrees` must have been run.

---

## When to use this skill

Invoke when:
- The user says "commit this", "run the commit", "submit", "execute the commit"
- A `/git-draft-commit` message has been reviewed and approved
- The user wants to stage + commit in one step

This skill **does** run `git commit`. It will ask for confirmation before executing.

---

## Algorithm

### Step 0 — Verify worktree / branch

```bash
git branch --show-current
git worktree list
```

- **In a worktree** (`.cc/worktrees/` in path): safe, proceed.
- **On a feature branch**: safe, proceed. Note: shared staging area risk if another session is active.
- **On `main`**: stop. Run `/git-using-worktrees` first. Do not commit to main.

---

### Step 1 — Confirm the draft message

If the user provides a message directly, use it. If not, locate the most recent `/git-draft-commit` output in the conversation and display it for confirmation:

```
Commit message to submit:
─────────────────────────
<type>: <subject>

- <bullet>

Session-ID: ...
Agent: claude-code
Operator: ...
Worktree: ...
Base-Commit: ...
─────────────────────────
Confirm? [y to proceed / edit to revise]
```

Do not proceed without explicit confirmation.

---

### Step 2 — Choose files to stage

Ask the user (or infer from context):

```
Stage:
  [A] All changed files  →  git add -A
  [S] Specific files     →  git add <file1> <file2> ...
  [K] Keep current staging area as-is
```

If on an isolated worktree branch, `git add -A` is safe. If on a plain feature branch, prefer specific files.

Show what will be staged:
```bash
git status --short
```

---

### Step 3 — Stage the files

Run the chosen staging command. Confirm with:
```bash
git status --short
```

---

### Step 4 — Execute the commit (PowerShell-safe)

Use a plain double-quoted multi-line string — **never** bash heredoc syntax:

```powershell
git commit -m "<type>: <subject>

- <bullet 1>
- <bullet 2>

Session-ID: cc-...
Agent: claude-code
Operator: ...
Worktree: ...
Base-Commit: ..."
```

Confirm success:
```bash
git log -1 --oneline
```

---

### Step 5 — Post-commit checklist

After a successful commit, remind the user:

```
Commit recorded: <SHA> <subject>

Next steps:
  [ ] Push branch and open draft PR:
        git push -u origin <branch-name>
        gh pr create --draft --title "[cc <session-id>] <title>" --body "..."
  [ ] Or continue working and commit again at the next checkpoint
```

If this is end-of-session, suggest running `/git-draft-commit` Step 8 for the session summary.

---

## Quick reference (copy-paste)

### Stage all + commit (isolated worktree)
```powershell
git add -A
git commit -m "<type>: <subject>

- <bullet>

Session-ID: cc-<YYYYMMDD-HHMM-initials>
Agent: claude-code
Operator: brianrohde
Worktree: .cc/worktrees/<slug>
Base-Commit: <SHA>"
```

### Push + open draft PR
```powershell
git push -u origin <branch-name>
gh pr create --draft --title "[cc <session-id>] <title>" --body "Objective: <what this session did>
Files touched: <list>
Status: In progress"
```

---

## Reference docs

- Message generation: `/git-draft-commit`
- Worktree setup: `/git-using-worktrees`
- Full worktree guide: `docs/reference/git-worktrees-and-parallel-sessions.md`
- Branch strategy: `docs/reference/git-branch-strategy.md`
