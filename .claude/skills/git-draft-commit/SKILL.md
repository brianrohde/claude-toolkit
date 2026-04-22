---
name: git-draft-commit
description: Generate a ready-to-paste git commit message from the current session. Trigger whenever the user mentions committing changes, preparing a git message, or wants to submit work. Includes worktree awareness, commit discipline check, optional trailers, draft PR reminder, and session summary. Works in any git repo — collaborative features activate automatically when a multi-person context is detected.
compatibility:
  tools: [Bash, Read, Grep]
  requires: git repository
---

# Draft Commit Message

Generate a ready-to-paste git commit message with full session context, worktree safety checks, and optional audit metadata.

---

## When to use this skill

Invoke when:
- The user says "commit", "git commit", "prepare commit", "draft commit", "what should my commit message be?"
- The session has accumulated changes and the user wants to bundle them
- The user asks "should I commit this?" or "make a commit"
- End of a session — always suggest committing before closing

The skill never auto-executes. The user copies the message and submits it.

---

## Algorithm

Run these steps in order. Each step informs the next.

### Step 0 — Worktree and branch check

Run first, before anything else:
```bash
git branch --show-current
git worktree list
```

**Case A — in a worktree (path contains `.cc/worktrees/`):**
Confirm which branch this worktree is on. Proceed freely — worktrees are fully isolated. Note the worktree path for the trailers block.

**Case B — on a feature branch (not `main`, not in a worktree):**
Proceed. Note that this is a plain branch without worktree isolation — safe as long as no other session is working in the same repo folder simultaneously.

**Case C — on `main`:**
Warn the user before proceeding:

```
⚠️  You are on `main`.

For safety, each Claude Code session should work on its own branch and worktree.
Suggested setup:

  git worktree add .cc/worktrees/<name> cc/<YYYYMMDD-HHMM-initials>/<slug>
  cd .cc/worktrees/<name>

Options:
  [1] Create a worktree now and commit there
  [2] Stay on main and commit anyway (only if merging completed work)
  [3] Cancel
```

Do not proceed without user confirmation.

---

### Step 1 — Commit discipline check

Before drafting the message, review the git diff and session context:

```bash
git diff --stat HEAD
git log --oneline -5
```

Check: **is this a logical checkpoint?**

A good checkpoint is:
- The diff has one clear purpose
- Changes are reviewable as a unit
- No half-finished edits mixed with unrelated changes

If the diff looks like micro-edits (many small unrelated changes, no clear theme), flag it:

```
⚠️  Commit discipline note:
This diff spans multiple unrelated areas.
Consider staging only the files related to one purpose:

  git add <specific-files>
  git commit -m "..."

Then commit the rest separately.

Continue with full diff anyway? [y/n]
```

---

### Step 2 — Reconstruct session context

Review the conversation to understand:
- What was changed and why
- What problem was being solved
- What decisions were made

This is the primary input for the commit message — more important than `git status` alone.

---

### Step 3 — Git state

```bash
git status --short
git log -1 --format="%H %ai %s"
```

Identify:
- Which files are modified, staged, or untracked
- The last commit SHA and timestamp (cutoff for uncommitted work)
- Any files in `git status` that have no session record (flag these)

---

### Step 4 — Standup notes (if present)

If `project_updates/standup_draft.md` exists, extract entries timestamped after the last commit. Merge into the changes list. If no standup file exists, skip silently.

---

### Step 5 — Draft the commit message

Format:

```
<type>: <imperative subject, ≤60 chars>

- <what changed and why — one line per logical unit>
- <...>
```

**Types:** `feat` · `fix` · `refactor` · `chore` · `docs` · `thesis` · `data`

**Rules:**
- Subject line is imperative ("add", "fix", "update" — not "added" or "adding")
- Bullets explain the *why*, not just the what
- If the message cannot explain why all changes belong together, note that the diff should be split

---

### Step 6 — Trailers block (recommended for collaborative repos)

Append structured trailers after the commit body. For the CBS Master Thesis repo (multi-person collaboration), always include these.

For single-person repos, include only if the user has opted in.

**Detect collaboration context:**
- If `git log --format="%ae" | sort -u | wc -l` shows more than one author email → collaborative repo → include trailers automatically
- If the branch follows the `cc/<date-id>/<slug>` naming scheme → include trailers

**Trailer block:**

```
Session-ID: cc-<YYYYMMDD-HHMM-initials>
Agent: claude-code
Operator: <git config user.name>
Worktree: <worktree path, or "none — plain branch">
Base-Commit: <SHA from git log -1>
```

Get the values:
```bash
git config user.name
git log -1 --format="%H"
```

**Note on Co-authored-by:**
If Enrico or another real human co-authored changes in this session, add:
```
Co-authored-by: Enrico <enrico@email.com>
```
Do not add `Co-authored-by: Claude` — Claude attribution goes in the `Agent:` trailer only.

---

### Step 7 — Draft PR reminder

After presenting the commit message, remind the user:

```
📋 Draft PR reminder:
After committing, push and open a draft PR to back up this work remotely:

  git push -u origin <branch-name>
  gh pr create --draft \
    --title "[cc <session-id>] <task title>" \
    --body "Objective: <what this session did>
  Files touched: <list>
  Status: In progress / Ready for review"

A draft PR cannot be merged accidentally. It acts as remote backup and audit record.
Promote to ready when done: gh pr ready
```

---

### Step 8 — Session summary (end of session)

If the user signals they're wrapping up ("that's it for today", "closing this session", "all done"), produce a session summary:

```
📝 Session summary

Session-ID: cc-<YYYYMMDD-HHMM-initials>
Branch: <branch-name>
Worktree: <path or none>
PR: <link if pushed, or "not yet opened">

Completed:
- <bullet>

Remaining / next steps:
- <bullet>

Files touched: <list>
Overlap risk: <any files that other open branches may also touch>
Recommended next action: <merge PR / continue next session / open reconcile branch>
```

---

## Full output format

Present in a single fenced code block, followed by:
1. Trailers block (if applicable)
2. Any flagged ambiguities (files with no session record, micro-commit warning)
3. Draft PR reminder
4. Session summary (if end-of-session)

### Example output (collaborative repo, in a worktree)

```
docs: add worktree workflow guide and upgrade parallel session strategy

- Add git-worktrees-and-parallel-sessions.md with plain-language guide
  covering worktree concepts, session startup, conflict detection,
  reconcile workflow, and collaborator setup for Enrico
- Rewrite git-branch-strategy.md with worktree-first model and new
  cc/<date-id>/<slug> naming convention
- Rewrite draft-commit SKILL.md with worktree check at Step 0,
  commit discipline warning, trailers, draft PR reminder
- Add .cc/worktrees/ to .gitignore

Session-ID: cc-20260420-br
Agent: claude-code
Operator: brianrohde
Worktree: none — plain branch
Base-Commit: 22bcbfc
```

---

## Submission — you control the commit

```bash
git add <specific-files>   # or git add -A if on an isolated branch/worktree
git commit -m "$(cat <<'EOF'
<type>: your message here

- bullet
- bullet

Session-ID: cc-...
Agent: claude-code
Operator: ...
Base-Commit: ...
EOF
)"
```

This skill never runs `git commit` itself.

---

## Repo-independent design

This skill works in any git repository. Collaborative features activate based on detected context:

| Signal | Behaviour activated |
|---|---|
| Multiple authors in `git log` | Trailers always included |
| Branch matches `cc/<id>/<slug>` | Trailers always included |
| In a `.cc/worktrees/` path | Worktree isolation confirmed |
| On `main` | Warn and offer worktree setup |
| Single-author repo, plain branch | Trailers optional, no worktree prompt |

For the CBS Master Thesis repo: trailers are always on, worktree workflow is the default, draft PRs are always recommended.

---

## Reference docs

- Full worktree guide: `docs/reference/git-worktrees-and-parallel-sessions.md`
- Branch strategy: `docs/reference/git-branch-strategy.md`
- Trigger rule: `.claude/rules/trigger-git-commit-workflow.md`
