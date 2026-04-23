#!/usr/bin/env python3
"""
sync_status.py -- compare one or more destination repos to the claude-toolkit.

Usage:
    python sync_status.py <repo-path> [<repo-path> ...]
    python sync_status.py --type skills <repo-path>
    python sync_status.py                     # defaults to CWD

For each repo, compares .claude/skills, .claude/hooks, .claude/rules against the
toolkit and reports IN_SYNC / TOOLKIT_NEWER / PROJECT_NEWER / DIVERGED plus
toolkit-only and project-only components. Byte-level equality is computed after
normalizing CRLF -> LF so line-ending drift is not flagged.

Toolkit location:
    - $CLAUDE_TOOLKIT env var, else
    - the directory containing this script's parent.
"""
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


SUBTREES = ("skills", "hooks", "rules")


def find_toolkit() -> Path:
    env = os.environ.get("CLAUDE_TOOLKIT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / ".claude").is_dir():
            return p
    here = Path(__file__).resolve().parent.parent
    if (here / ".claude").is_dir():
        return here
    raise SystemExit("ERROR: cannot find toolkit. Set $CLAUDE_TOOLKIT.")


def norm_hash(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    except Exception as e:
        return f"ERR:{e}"


def tree_hash(root: Path) -> dict:
    if not root.exists():
        return {}
    return {
        f.relative_to(root).as_posix(): norm_hash(f)
        for f in sorted(root.rglob("*"))
        if f.is_file()
    }


def git_last_commit(repo: Path, relpath: str) -> int:
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%at", "--", relpath],
            capture_output=True, text=True, timeout=10,
        )
        t = r.stdout.strip()
        return int(t) if t else 0
    except Exception:
        return 0


def compare_subtree(toolkit: Path, dest: Path, sub: str) -> dict:
    tk_root = toolkit / ".claude" / sub
    pr_root = dest / ".claude" / sub
    tk_items = {p.name for p in tk_root.iterdir() if p.is_dir()} if tk_root.exists() else set()
    pr_items = {p.name for p in pr_root.iterdir() if p.is_dir()} if pr_root.exists() else set()
    overlap = sorted(tk_items & pr_items)

    buckets = {"in_sync": [], "toolkit_newer": [], "project_newer": [], "diverged": []}
    for name in overlap:
        if tree_hash(tk_root / name) == tree_hash(pr_root / name):
            buckets["in_sync"].append(name)
            continue
        ta = git_last_commit(toolkit, f".claude/{sub}/{name}")
        tb = git_last_commit(dest, f".claude/{sub}/{name}")
        if ta and tb:
            (buckets["toolkit_newer"] if ta > tb else buckets["project_newer"]).append(name)
        elif ta or tb:
            (buckets["toolkit_newer"] if ta else buckets["project_newer"]).append(name)
        else:
            buckets["diverged"].append(name)

    buckets["toolkit_only"] = sorted(tk_items - pr_items)
    buckets["project_only"] = sorted(pr_items - tk_items)
    return buckets


def print_report(toolkit: Path, dest: Path, subtrees):
    print(f"\n========== {dest.name} vs toolkit ==========")
    print(f"toolkit: {toolkit}")
    print(f"repo:    {dest}")
    for sub in subtrees:
        b = compare_subtree(toolkit, dest, sub)
        print(f"\n--- {sub} ---")
        print(f"IN_SYNC        ({len(b['in_sync'])}): {', '.join(b['in_sync']) or '-'}")
        print(f"TOOLKIT_NEWER  ({len(b['toolkit_newer'])}): {', '.join(b['toolkit_newer']) or '-'}")
        print(f"PROJECT_NEWER  ({len(b['project_newer'])}): {', '.join(b['project_newer']) or '-'}")
        print(f"DIVERGED       ({len(b['diverged'])}): {', '.join(b['diverged']) or '-'}")
        print(f"Toolkit-only   ({len(b['toolkit_only'])}): {', '.join(b['toolkit_only']) or '-'}")
        print(f"Project-only   ({len(b['project_only'])}): {', '.join(b['project_only']) or '-'}")


def main():
    ap = argparse.ArgumentParser(description="Compare repos to claude-toolkit.")
    ap.add_argument("repos", nargs="*", help="One or more repo paths (default: CWD).")
    ap.add_argument("--type", choices=SUBTREES, help="Scope to one subtree.")
    args = ap.parse_args()

    toolkit = find_toolkit()
    subtrees = (args.type,) if args.type else SUBTREES
    repos = [Path(r).expanduser().resolve() for r in args.repos] or [Path.cwd()]

    for repo in repos:
        if not repo.is_dir():
            print(f"SKIP (not a directory): {repo}", file=sys.stderr)
            continue
        if not (repo / ".claude").is_dir():
            print(f"SKIP (no .claude dir): {repo}", file=sys.stderr)
            continue
        print_report(toolkit, repo, subtrees)


if __name__ == "__main__":
    main()
