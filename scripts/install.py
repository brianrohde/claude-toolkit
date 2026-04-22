#!/usr/bin/env python3
"""
install.py -- copy skills (and optionally hooks/rules) from claude-toolkit into a project.

Usage:
    python install.py <project-path> [target ...]

Where each target is either:
    - a group name from skills/SKILL_GROUPS.md (e.g., "foundational", "webdev")
    - a single skill folder name (e.g., "git-commit")

Examples:
    python install.py ~/myproject foundational
    python install.py ~/myproject foundational webdev
    python install.py ~/myproject git-commit standup-log
    python install.py ~/myproject              # interactive: lists groups, asks

Behavior:
    - Copies skill folders byte-by-byte into <project>/.claude/skills/<name>/
    - Skips skills that already exist in the project (use /claude-toolkit-pull to update).
    - Reports added / skipped / failed.
    - Does NOT install hooks/rules (those need settings.json merging; install manually).
    - Does NOT touch git -- the user commits the new files.

Toolkit location:
    - $CLAUDE_TOOLKIT env var, OR
    - the directory containing this script's parent (assumes scripts/ lives in the toolkit root).
"""
import os
import re
import shutil
import sys
from pathlib import Path


def find_toolkit() -> Path:
    env = os.environ.get("CLAUDE_TOOLKIT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "skills").is_dir():
            return p
    here = Path(__file__).resolve().parent.parent
    if (here / "skills").is_dir():
        return here
    raise SystemExit(
        "ERROR: cannot find toolkit. Set $CLAUDE_TOOLKIT or run from inside the toolkit."
    )


def parse_groups(groups_md: Path) -> dict:
    """Parse SKILL_GROUPS.md into {group_name: [skill, ...]}."""
    if not groups_md.exists():
        return {}
    text = groups_md.read_text(encoding="utf-8")
    groups = {}
    current = None
    for line in text.splitlines():
        h = re.match(r"^##\s+([a-z][a-z0-9_-]*)\s*$", line)
        if h:
            current = h.group(1)
            groups[current] = []
            continue
        if current:
            m = re.match(r"^-\s+([A-Za-z0-9_-]+)\s*$", line)
            if m:
                groups[current].append(m.group(1))
    return groups


def copy_skill(src: Path, dst: Path) -> str:
    """Byte-level copy of a skill folder. Returns 'added' or 'skipped' or raises."""
    if dst.exists():
        return "skipped"
    dst.mkdir(parents=True)
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(item.read_bytes())
    return "added"


def interactive_pick(groups: dict) -> list:
    print("Available groups:")
    for name, skills in groups.items():
        print(f"  {name} ({len(skills)} skills)")
    print()
    choice = input("Group(s) to install (space-separated, or 'all'): ").strip()
    if not choice:
        raise SystemExit("No selection -- aborting.")
    if choice == "all":
        return list(groups.keys())
    return choice.split()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    project = Path(sys.argv[1]).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"ERROR: project path not found: {project}")
    targets = sys.argv[2:]

    toolkit = find_toolkit()
    skills_dir = toolkit / "skills"
    groups_md = skills_dir / "SKILL_GROUPS.md"
    groups = parse_groups(groups_md)

    if not targets:
        targets = interactive_pick(groups)

    # Resolve targets to actual skill names (groups expand)
    to_install = []
    unknown = []
    for t in targets:
        if t in groups:
            to_install.extend(groups[t])
        elif (skills_dir / t).is_dir():
            to_install.append(t)
        else:
            unknown.append(t)
    # Dedupe preserving order
    seen = set()
    to_install = [s for s in to_install if not (s in seen or seen.add(s))]

    if unknown:
        print(f"WARNING: unknown targets (not a group or skill): {unknown}")
    if not to_install:
        raise SystemExit("Nothing to install.")

    project_skills = project / ".claude" / "skills"
    project_skills.mkdir(parents=True, exist_ok=True)

    added, skipped, failed = [], [], []
    for name in to_install:
        src = skills_dir / name
        dst = project_skills / name
        if not src.is_dir():
            failed.append((name, "source not in toolkit"))
            continue
        try:
            result = copy_skill(src, dst)
            if result == "added":
                added.append(name)
            else:
                skipped.append(name)
        except Exception as e:
            failed.append((name, str(e)))

    print()
    print(f"=== Install summary ===")
    print(f"Toolkit: {toolkit}")
    print(f"Project: {project}")
    print(f"Added:   {len(added)}")
    for n in added:
        print(f"  + {n}")
    print(f"Skipped: {len(skipped)} (already installed -- use /claude-toolkit-pull to update)")
    for n in skipped:
        print(f"  = {n}")
    if failed:
        print(f"Failed:  {len(failed)}")
        for n, err in failed:
            print(f"  ! {n} -- {err}")

    print()
    print("Next steps:")
    print(f"  cd {project}")
    print("  git add .claude/skills/")
    print("  git commit -m 'chore: install claude-toolkit skills'")


if __name__ == "__main__":
    main()
