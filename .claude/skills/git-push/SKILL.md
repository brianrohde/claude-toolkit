---
name: git-push
description: |
  Complete the git workflow: stage all affected files, commit with a drafted message, and push to the current branch.
  
  Use this skill immediately after `/draft_commit` to push your changes. It will:
  1. Stage all modified, new, and deleted files from the current session
  2. Commit using the message you provide (or from a recent draft)
  3. Push to your current branch on origin
  
  Triggers: After `/draft_commit`, or when you say "push these changes", "git push with commit", "complete the git workflow", "push to remote"
  
  Provide the commit message as an argument, or leave blank to read from a temp file if one exists from a recent `/draft_commit` run.
---

# git-push Skill

## Overview

This skill automates the final stages of your git workflow: staging all changes, committing with a prepared message, and pushing to your remote branch in one step.

## Usage

```
/git-push [commit message]
```

**Arguments:**
- `[commit message]` (optional): The commit message to use. If omitted, the skill will look for a recent draft in the temp directory.

## Workflow

This skill is designed to chain with `/draft_commit`:

1. Run `/draft_commit` to generate a commit message
2. Run `/git-push` (with or without the message) to complete the push
3. Verification output shows files staged, commit hash, and push result

## What It Does

### Step 1: Determine Commit Message
- If you provided a message as an argument, use that
- Otherwise, check for a recent `git-commit-draft.txt` file in the temp directory
- If neither exists, fail with a helpful error

### Step 2: Stage All Changes
- Run `git add -A` to stage all modified, new, and deleted files
- Display the list of staged files
- If staging fails, stop and report the error

### Step 3: Create Commit
- Commit with the prepared message
- If the commit fails (e.g., nothing to commit), report and stop
- Display the commit hash and summary

### Step 4: Push to Remote
- Detect the current branch with `git rev-parse --abbrev-ref HEAD`
- Push to `origin/<current-branch>`
- If push fails (e.g., no remote, authentication issues), stop and report the error
- Display the push result with branch and URL info

## Error Handling

The skill stops and reports errors at any stage:
- No commit message found
- Staging fails
- Commit fails
- Push fails

Each error includes the git command output so you can diagnose and fix the issue.

## Example Session

```
User: /draft_commit
Claude: [outputs commit message]

User: /git-push
Claude: 
  ✅ Staged 5 files (3 modified, 2 new)
  ✅ Commit: abc1234 feat: add git-push skill
  ✅ Pushed to origin/main
  
  Files pushed:
  - src/skill-push.py
  - .claude/skills/git-push/SKILL.md
  - ... (2 more)
```

## Notes

- The temp file location is platform-aware (Windows: `%TEMP%`, Unix: `/tmp`)
- Current branch is detected automatically — no need to specify it
- The skill respects your git configuration (user.name, user.email, etc.)
