#!/usr/bin/env python3
"""
Utilities for the /git-worktree-merge skill.

Provides reusable functions for diff summary, overlap detection, merge validation,
and health gate execution.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


def run_cmd(cmd: str, capture: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            cwd=str(Path.cwd())
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def get_current_branch() -> str:
    """Get the currently checked-out branch."""
    rc, stdout, _ = run_cmd("git branch --show-current")
    if rc == 0:
        return stdout.strip()
    return ""


def get_diff_summary(source: str = "main", target: str = None) -> Dict:
    """
    Get diff summary between source and target branches.

    Returns:
        {
            "files_changed": int,
            "insertions": int,
            "deletions": int,
            "files": [{"path": str, "status": str}],
            "areas": {"thesis": [...], "data": [...], "docs": [...], "config": [...], ".claude": [...], "other": [...]}
        }
    """
    if target is None:
        target = get_current_branch()

    # Get stat
    rc, stdout, _ = run_cmd(f"git diff --stat {source}..{target}")
    files_changed = 0
    insertions = 0
    deletions = 0

    if rc == 0 and stdout:
        lines = stdout.strip().split('\n')
        # Last line is the summary
        if lines:
            summary_line = lines[-1]
            # Parse "N files changed, M insertions(+), K deletions(-)"
            parts = summary_line.split()
            for i, part in enumerate(parts):
                if "changed" in part and i > 0:
                    files_changed = int(parts[i - 1])
                if "insertion" in part and i > 0:
                    insertions = int(parts[i - 1])
                if "deletion" in part and i > 0:
                    deletions = int(parts[i - 1])

    # Get file list with status
    rc, stdout, _ = run_cmd(f"git diff --name-only --diff-filter=ACMRTUXB {source}..{target}")
    files = []
    areas = {
        "thesis": [],
        "data": [],
        "docs": [],
        "config": [],
        ".claude": [],
        "other": []
    }

    if rc == 0 and stdout:
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            files.append({"path": line, "status": "modified"})

            # Categorize by area
            if line.startswith("thesis/"):
                areas["thesis"].append(line)
            elif line.startswith("data/"):
                areas["data"].append(line)
            elif line.startswith("docs/"):
                areas["docs"].append(line)
            elif line.startswith("config/") or line.startswith(".claude/"):
                areas["config"].append(line)
            elif line.startswith(".claude/"):
                areas[".claude"].append(line)
            else:
                areas["other"].append(line)

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "files": files,
        "areas": areas
    }


def detect_overlaps(current_branch: str) -> Dict:
    """
    Detect overlaps with other open draft PRs.

    Returns:
        {
            "overlaps_found": bool,
            "overlapping_branches": [
                {
                    "branch": str,
                    "pr_number": int,
                    "pr_title": str,
                    "files": [str]
                }
            ],
            "all_overlapping_files": [str]
        }
    """
    # Query open draft PRs
    rc, stdout, _ = run_cmd(
        'gh pr list --state open --search "state:draft" --json number,title,headRefName,baseRefName'
    )

    if rc != 0 or not stdout:
        return {
            "overlaps_found": False,
            "overlapping_branches": [],
            "all_overlapping_files": []
        }

    try:
        prs = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "overlaps_found": False,
            "overlapping_branches": [],
            "all_overlapping_files": []
        }

    # Get files changed in current branch
    rc, stdout, _ = run_cmd(f"git diff --name-only main..{current_branch}")
    if rc != 0:
        current_files = set()
    else:
        current_files = set(stdout.strip().split('\n')) if stdout.strip() else set()

    overlapping_branches = []
    all_overlapping_files = set()

    # Check each other PR
    for pr in prs:
        other_branch = pr.get("headRefName", "")
        if other_branch == current_branch:
            continue

        rc, stdout, _ = run_cmd(f"git diff --name-only main..{other_branch}")
        if rc != 0:
            other_files = set()
        else:
            other_files = set(stdout.strip().split('\n')) if stdout.strip() else set()

        # Find intersection
        overlap = current_files & other_files
        if overlap:
            overlapping_branches.append({
                "branch": other_branch,
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title", ""),
                "files": sorted(list(overlap))
            })
            all_overlapping_files.update(overlap)

    return {
        "overlaps_found": len(overlapping_branches) > 0,
        "overlapping_branches": overlapping_branches,
        "all_overlapping_files": sorted(list(all_overlapping_files))
    }


def validate_merge_dryrun(source: str = "main", target: str = None) -> Dict:
    """
    Dry-run a merge to check for conflicts.

    Returns:
        {
            "has_conflicts": bool,
            "conflict_files": [str],
            "can_merge": bool
        }
    """
    if target is None:
        target = get_current_branch()

    # Create a temporary merge (no-commit, no-ff)
    rc, stdout, stderr = run_cmd(f"git merge --no-commit --no-ff {source}")

    # Check for conflicts
    has_conflicts = rc != 0 or "CONFLICT" in stdout or "CONFLICT" in stderr

    # Get list of conflicted files
    rc_status, stdout_status, _ = run_cmd("git status --short")
    conflict_files = []
    if rc_status == 0:
        for line in stdout_status.strip().split('\n'):
            if line.startswith("UU "):  # both modified
                conflict_files.append(line[3:])
            elif line.startswith("AA ") or line.startswith("DD "):
                conflict_files.append(line[3:])

    # Abort the merge
    run_cmd("git merge --abort")

    return {
        "has_conflicts": has_conflicts,
        "conflict_files": conflict_files,
        "can_merge": not has_conflicts
    }


def run_health_gate() -> Dict:
    """
    Run the workspace-enforce health gate and parse violations.

    Returns:
        {
            "passed": bool,
            "exit_code": int,
            "violations": [
                {
                    "severity": "HIGH" | "WARN" | "INFO",
                    "rule": str,
                    "message": str
                }
            ]
        }
    """
    script_path = "./.claude/skills/workspace-enforce/scripts/enforce_runner.py"

    if not Path(script_path).exists():
        return {
            "passed": True,
            "exit_code": 0,
            "violations": []
        }

    rc, stdout, stderr = run_cmd(f"python {script_path} --root .")

    # Parse violations from output
    violations = []
    combined_output = stdout + stderr

    # Simple heuristic: look for severity markers
    for line in combined_output.split('\n'):
        if "HIGH:" in line or "WARN:" in line or "INFO:" in line:
            violations.append({
                "severity": "HIGH" if "HIGH:" in line else ("WARN" if "WARN:" in line else "INFO"),
                "rule": line.split(":")[-1].strip() if ":" in line else line,
                "message": line
            })

    return {
        "passed": rc == 0,
        "exit_code": rc,
        "violations": violations
    }


if __name__ == "__main__":
    # Simple test: print summary of current branch vs main
    branch = get_current_branch()
    print(f"Current branch: {branch}")

    if branch != "main":
        summary = get_diff_summary("main", branch)
        print(f"\nDiff Summary:")
        print(f"  Files changed: {summary['files_changed']}")
        print(f"  +{summary['insertions']}, -{summary['deletions']}")

        overlaps = detect_overlaps(branch)
        print(f"\nOverlap Detection:")
        print(f"  Found: {overlaps['overlaps_found']}")
        if overlaps['overlapping_branches']:
            for ob in overlaps['overlapping_branches']:
                print(f"    - {ob['branch']}: {len(ob['files'])} files")
