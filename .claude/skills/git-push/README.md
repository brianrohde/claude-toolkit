# git-push

**Tier**: beta

## Purpose

Completes the git workflow after `/git-draft-commit`: stages all changed files, commits with the drafted message, and pushes to the current branch. Complementary to `git-commit` (which only stages + commits); `git-push` is the one-shot "commit-and-push" variant.

## When to use

- Immediately after `/git-draft-commit` when you also want to push.
- When the commit + push cadence is one step, not two (e.g., solo work on a feature branch with trusted CI).

## When NOT to use

- If you want a review window between commit and push -- use `/git-commit` instead and push manually when ready.
- On `main` without explicit intent -- the trigger-branch-strategy rule still applies.

## Overlap with other skills

- `git-commit` -- stages + commits only; does not push.
- `git-draft-commit` -- drafts the message only.
- `git-push` = both of those + `git push`.

## Provenance

Promoted from `pta-cbp-parser/.claude/skills/git-push/` on 2026-04-23.
