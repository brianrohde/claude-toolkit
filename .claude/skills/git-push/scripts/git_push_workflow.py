#!/usr/bin/env python3
"""
Git push workflow: stage, commit, and push in one step.
Designed to chain with /draft_commit skill.
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path


def run_command(cmd, description):
    """Run a git command and return output or exit on failure."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {description}:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr or e.stdout}")
        sys.exit(1)


def get_commit_message(provided_message):
    """Get commit message from argument or temp file."""
    if provided_message:
        return provided_message

    # Try to read from temp file
    temp_dir = tempfile.gettempdir()
    draft_file = Path(temp_dir) / "git-commit-draft.txt"

    if draft_file.exists():
        try:
            message = draft_file.read_text(encoding='utf-8').strip()
            if message:
                print(f"[INFO] Using commit message from {draft_file}")
                return message
        except Exception as e:
            print(f"[WARN] Could not read draft file: {e}")

    print("[FAIL] No commit message provided and no draft found.")
    print(f"   Looked for: {draft_file}")
    print("   Either:")
    print("   1. Run /draft_commit first, then /git-push")
    print("   2. Provide the message: /git-push <message>")
    sys.exit(1)


def get_current_branch():
    """Get the current git branch."""
    stdout, _ = run_command(
        "git rev-parse --abbrev-ref HEAD",
        "Get current branch"
    )
    return stdout.strip()


def get_staged_files():
    """Get list of files that will be staged."""
    stdout, _ = run_command(
        "git status --short",
        "Check git status"
    )
    if not stdout:
        return []
    return [line.strip() for line in stdout.split('\n') if line.strip()]


def stage_all_files():
    """Stage all changes (modified, new, deleted)."""
    run_command("git add -A", "Stage all files")
    stdout, _ = run_command(
        "git diff --cached --name-only",
        "Get staged files"
    )
    staged = [line.strip() for line in stdout.split('\n') if line.strip()]

    if not staged:
        print("[FAIL] No files to stage. Working directory is clean.")
        sys.exit(1)

    print(f"[OK] Staged {len(staged)} files:")
    for f in staged:
        print(f"   - {f}")

    return staged


def commit(message):
    """Create a commit with the given message."""
    # Escape the message for shell
    escaped_msg = message.replace('"', '\\"')
    run_command(
        f'git commit -m "{escaped_msg}"',
        "Create commit"
    )

    # Get commit info
    stdout, _ = run_command(
        "git log -1 --pretty=format:%H",
        "Get commit hash"
    )
    commit_hash = stdout[:7]

    stdout, _ = run_command(
        "git log -1 --pretty=format:%s",
        "Get commit subject"
    )
    subject = stdout

    print(f"[OK] Commit created: {commit_hash} {subject}")
    return commit_hash


def push(branch):
    """Push to origin/branch."""
    run_command(
        f"git push origin {branch}",
        f"Push to origin/{branch}"
    )
    print(f"[OK] Pushed to origin/{branch}")


def main():
    # Get commit message from argument or temp file
    commit_message = sys.argv[1] if len(sys.argv) > 1 else None
    message = get_commit_message(commit_message)

    # Get current branch
    branch = get_current_branch()
    print(f"[INFO] Current branch: {branch}")

    # Check for uncommitted changes
    files_to_stage = get_staged_files()
    if not files_to_stage:
        print("[OK] Working directory is clean, nothing to push.")
        sys.exit(0)

    print(f"[INFO] Found {len(files_to_stage)} changes to stage")

    # Stage all changes
    staged = stage_all_files()

    # Commit
    commit(message)

    # Push
    push(branch)

    print("\n[OK] Workflow complete!")
    print(f"   Files: {len(staged)}")
    print(f"   Branch: {branch}")
    print(f"   Destination: origin/{branch}")


if __name__ == "__main__":
    main()
