---
name: git-worktree-merge
description: Review and merge a worktree branch back to main. Handles diff review, overlap detection, GitHub PR guidance, and post-merge cleanup. Delegate this skill when the user says "merge", "merge back to main", "complete worktree", or "push and merge".
compatibility:
  tools: [Bash, Read, Grep]
  requires: git repository with active worktree or feature branch
---

# Worktree Merge

Complete the merge-back workflow: review changes, check for conflicts/overlaps, integrate via GitHub PR, and cleanup.

---

## When to use this skill

Invoke when:
- User says "merge this back", "merge to main", "complete the branch", "ready to merge", "merge back", or "merge"
- End of a worktree session before cleanup
- Before `git worktree remove` is run

**Prerequisite**: Work must be committed on a feature branch or worktree.
**Upstream skills**: `/git-worktrees` (setup), `/git-draft-commit` (message), `/git-commit` (staging)

---

## Algorithm

### Step 0 — Branch and worktree verification

```bash
git branch --show-current
git worktree list
git status --short
```

**Case A — In a worktree** (path contains `.cc/worktrees/`):
- Confirm branch name matches worktree
- Branch is isolated by design → safe to merge locally or via PR

**Case B — On a plain feature branch** (not main, not in worktree):
- Staging area is shared → GitHub PR workflow is safer
- Offer PR promotion as primary path

**Case C — On main**:
- Stop. You should not be merging FROM main.
- Delegate to `/git-worktrees` if branch is not yet created

---

### Step 1 — Diff summary

```bash
git diff --stat main..<current-branch>
git diff --name-only main..<current-branch>
```

Display to user:
- Number of files changed
- Number of insertions/deletions
- List of files (grouped by area: thesis/, data/, docs/, config/, .claude/)

Flag if spans multiple unrelated areas.

---

### Step 2 — Overlap detection

```bash
# Get list of open PRs in draft state
gh pr list --state open --search "state:draft" --json number,title,headRefName,baseRefName

# For each other branch:
git diff --name-only main..<other-branch>

# Compare file lists:
# If intersection exists → overlap detected
```

**If overlap found**:
```
⚠️  Overlap detected with 1 other open PR:
  - <branch-name>: <title>

Overlapping files:
  - <file-a>
  - <file-b>

Recommendation: Follow the RECONCILE WORKFLOW
  1. Keep both PRs as DRAFT
  2. Create a reconcile worktree:
     git worktree add .cc/worktrees/reconcile cc/YYYYMMDD-HHMM-initials/reconcile-<topic>
  3. Merge both branches in reconcile, resolve conflicts
  4. Open PR titled "Reconcile: <branch-a> + <branch-b>"
  5. Only merge the reconcile PR to main (not the individual branches)

See: docs/reference/git-worktrees-and-parallel-sessions.md#reconcile-workflow
```

**If no overlap**: Proceed to Step 3.

---

### Step 3 — Merge strategy selection

Present options:

```
Ready to merge <branch-name> into main.

Which workflow?
  [1] Open GitHub PR (recommended for all branches)
       - Push branch, create draft PR, promote when ready, merge via GitHub
       - Provides backup, audit trail, visible review point
  
  [2] Local merge commit (only for isolated worktrees)
       - Merge locally: git merge <branch> -m "..."
       - Run health gate validation
       - Push to main
       - Clean up worktree
  
  [3] Cancel

Which would you like?
```

---

### Step 4A — GitHub PR workflow (recommended)

**If user chooses [1]:**

```bash
# Push branch if not already pushed
git push -u origin <current-branch>

# Create/update draft PR
gh pr view --json number  # Check if PR exists
# If exists: gh pr edit <number> --body "updated status"
# If not: gh pr create --draft --title "[cc <session-id>] <title>" --body "..."
```

Output:
```
✅ Branch pushed to origin/<branch-name>

PR: https://github.com/<owner>/<repo>/pull/<number>
Status: DRAFT (can be safely kept open)

Next steps:
  [ ] Review the PR diff in GitHub UI
  [ ] When ready to merge, run: gh pr ready
  [ ] Then merge via GitHub UI (use "Create a merge commit" option)
  [ ] After merge, run: git worktree remove .cc/worktrees/<name>
```

---

### Step 4B — Local merge workflow (worktree only)

**If user chooses [2] and in isolated worktree:**

```bash
# Dry-run to check for conflicts
git merge --no-commit --no-ff main

# If dry-run has conflicts:
# → Stop and display conflict list
# → Ask user to resolve manually
# → Provide: git status, conflict markers, how to resolve

# If no conflicts:
# → Proceed to actual merge
git merge --no-ff -m "<merge commit message>" main
```

**Merge commit message format**:
```
Merge branch '<branch-name>' into main

Session-ID: cc-<YYYYMMDD-HHMM-initials>
Merged-by: <operator>
Worktree: <path>
Base-Commit: <SHA>
```

---

### Step 5 — Health gate validation (local merge only)

**If local merge was executed:**

```bash
python .claude/skills/workspace-enforce/scripts/enforce_runner.py --root .
```

**Interpret result:**
- Exit code `0` = PASS → Merge is valid
- Exit code `1` = FAIL → Violations present
  - List violations
  - Ask: Proceed anyway (mark as waived) or rollback merge?
  - Provide: `git reset --hard HEAD~1` to undo

---

### Step 6 — Push and confirm

**If local merge passed validation:**

```bash
git push -u origin main

# Confirm
git log -1 --oneline
git branch -vv  # show tracking relationship
```

Output:
```
✅ Merged and pushed to origin/main

Commit: <SHA> <subject>
Branch: main is now <N> commits ahead of origin/main
```

---

### Step 7 — Post-merge cleanup

Offer cleanup options:

```
Merge complete! Cleanup options:

  [1] Remove this worktree now
       → git worktree remove .cc/worktrees/<name>
  
  [2] Keep worktree for further work
       → (branch stays alive for continued feature work)
  
  [3] Show cleanup commands (copy-paste yourself)
```

**If [1]**: Run cleanup and confirm:
```bash
git worktree remove .cc/worktrees/<name>
git worktree list  # verify removed
```

Output:
```
✅ Worktree removed: .cc/worktrees/<name>

Branch '<branch-name>' remains in git history and on GitHub.
To fully delete the remote branch:
  gh repo delete-branch <branch-name>
  (only after PR is merged to main)
```

---

### Step 8 — Session summary (end of merge)

After merge completes, display:

```
Session Merge Summary
═════════════════════

Branch: <branch-name>
Merge method: [GitHub PR | Local merge]
Status: ✅ Completed

Files changed: <N>
Commits: <N>
Worktree removed: [Yes | No]

Next action:
  - If GitHub PR: Monitor PR for approval, then merge via GitHub UI
  - If local merge: Branch is live on main; can safely delete remote branch
  - If kept worktree: Continue with /git-draft-commit and /git-commit
```

---

## Example outputs

### Example 1: Worktree merge (no overlap, GitHub PR path)

```
✅ Diff Summary
  Files changed: 3
  Lines: +47, -12
  
  .claude/skills/git-worktree-merge/SKILL.md (new)
  thesis/thesis-writing/sections-drafts/phase-2-design.md (modified)
  docs/dev/repository_map.md (modified)

❌ No overlap detected with other open branches.

Ready to merge feat/phase2-merge-skill into main.

✅ Branch pushed to origin/feat/phase2-merge-skill

PR created: https://github.com/user/repo/pull/42

Next steps:
  1. Review PR diff in GitHub
  2. Run: gh pr ready (when ready to merge)
  3. Click "Merge" in GitHub UI (use "Create a merge commit")
  4. Run: git worktree remove .cc/worktrees/phase2-merge-skill
```

### Example 2: Overlap detected, reconcile workflow suggested

```
⚠️  Overlap detected with 1 other open PR:
  - config/tooling-setup: "Update settings.json schema"

Overlapping files:
  - .claude/settings.json

Recommendation: Follow RECONCILE WORKFLOW
  1. Keep both PRs as DRAFT
  2. git worktree add .cc/worktrees/reconcile cc/20260420-1530-br/reconcile-merge-tooling
  3. cd .cc/worktrees/reconcile
  4. git merge origin/feat/phase2-merge-skill
  5. git merge origin/config/tooling-setup
  6. [Resolve conflicts manually in .claude/settings.json]
  7. git add .claude/settings.json
  8. git commit -m "Reconcile: merge-skill + tooling-setup"
  9. git push -u origin cc/20260420-1530-br/reconcile-merge-tooling
  10. gh pr create --draft --title "Reconcile: merge-skill + tooling-setup"

Then merge ONLY the reconcile PR to main.

See: docs/reference/git-worktrees-and-parallel-sessions.md#reconcile-workflow
```

---

## Reference docs

- Worktree setup: `/git-worktrees`
- Commit message generation: `/git-draft-commit`
- Single-commit staging: `/git-commit`
- Branch strategy: `.claude/rules/trigger-branch-strategy.md`
- Full worktree guide: `docs/reference/git-worktrees-and-parallel-sessions.md`
- GitHub branch strategy: `docs/reference/git-branch-strategy.md`
- Health gate validation: `.claude/skills/workspace-enforce/SKILL.md`
