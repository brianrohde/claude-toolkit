---
name: checkpoint-save
description: This skill should be used when the user says "checkpoint-save", "/checkpoint-save", "round up the session", "wrap up and commit", or wants to run the full end-of-session sweep in one command. Aggregates four skills in sequence: /docs-update-all (refresh docs), /plan-update-all (log plan outcomes), /git-draft-commit (draft a commit message), /git-push (stage + commit + push). One command instead of four.
version: 0.1.0
---

# checkpoint-save

## Purpose

End-of-session aggregator. One command runs the full wrap-up sequence so you don't have to remember and type four separate triggers.

The default sequence:
1. `/docs-update-all` -- update any documentation that drifted during the session.
2. `/plan-update-all` -- write outcome files for any plan(s) executed in the session.
3. `/git-draft-commit` -- draft a ready-to-paste commit message from the session context.
4. `/git-push` -- stage everything, commit with the drafted message, and push to the current branch.

## Trigger

`/checkpoint-save` (no arguments)

Optional flags in the user prompt:
- `--skip-docs` -- skip step 1 (docs already current).
- `--skip-plan` -- skip step 2 (no plan was executed).
- `--dry-run` -- run steps 1-3, but stop before pushing (still commits locally? no -- stops before commit too; just shows the drafted message).

## Algorithm

### Step 1: docs-update-all
Invoke `/docs-update-all`. Surface its summary line. If it skips everything (no doc-relevant changes), continue silently.

### Step 2: plan-update-all
Invoke `/plan-update-all`. If there is no in-progress plan in `.claude/plans/plan_files/` without a matching outcome file, this is a no-op -- continue.

### Step 3: git-draft-commit
Invoke `/git-draft-commit`. Capture the drafted commit message. Show it to the user.

### Step 4: git-push
Invoke `/git-push` with the drafted message. This handles:
- staging affected files (per `/git-push`'s own logic),
- committing with the drafted message,
- pushing to `origin/<current-branch>`.

If `--dry-run` was passed, stop here and report the drafted message + what would be pushed.

### Step 5: Report
End with a tight one-line summary:
```
checkpoint-save: docs <updated|skipped>, plan <logged|skipped>, commit <hash> pushed to <branch>
```

If any step fails:
- Halt the chain. Do not proceed to the next step.
- Report which step failed and surface its error.
- Do NOT attempt rollback (the user can resolve manually).

## Composition notes

This skill is purely an aggregator. It does not duplicate the logic of the four child skills -- it only orchestrates them. If a child skill changes its trigger or signature, update the corresponding step here.

The child skills resolve at runtime via Claude Code's normal skill discovery. Required:
- `docs-update-all` (toolkit foundational group, project-installed)
- `plan-update-all` (toolkit foundational group, project-installed)
- `git-draft-commit` (toolkit foundational group, project-installed)
- `git-push` (currently a global skill; not in toolkit but available in any session)

If any child skill is missing in the current project, the chain will fail at that step. The error message should suggest installing the missing piece via `/claude-toolkit-pull <name>`.

## Output

Per-step pass-through of each child skill's output, plus the final one-line summary.

## Failure modes

- **Missing child skill**: surface "skill X not found"; suggest `/claude-toolkit-pull X` for toolkit-managed skills, or "ensure /git-push is installed globally" for the push step.
- **Uncommitted state from prior session**: `/git-push` will surface; the user should resolve before re-running checkpoint-save.
- **Push fails (no auth, branch protection, etc.)**: surface the error; the local commit stands; user can push manually.
- **Drafted commit message looks wrong**: rerun `/git-draft-commit` standalone to refine, then `/git-push` separately. Don't blindly re-run /checkpoint-save -- it would draft a fresh message from a now-stale context.
