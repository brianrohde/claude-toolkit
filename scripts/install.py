#!/usr/bin/env python3
"""
install.py -- copy skills from claude-toolkit into a project, with diff + fuzzy match.

Usage:
    python install.py <project-path> [target ...] [--force-all]

Where each target is either:
    - a group name from .claude/skills/SKILL_GROUPS.md (e.g., "foundational", "webdev")
    - a single skill folder name (e.g., "git-commit")

Examples:
    python install.py ~/myproject foundational
    python install.py ~/myproject foundational webdev
    python install.py ~/myproject git-commit standup-log
    python install.py ~/myproject foundational --force-all  # skip per-skill prompts
    python install.py ~/myproject                            # interactive group-pick

Behavior:
    - Copies skill folders byte-by-byte into <project>/.claude/skills/<name>/.
    - For each toolkit skill, looks for a match in the destination by:
        1. Exact name (.claude/skills/<name>/).
        2. Known rename (consults .claude/skills/RENAMES.md).
        3. Description-field substring similarity (fuzzy).
    - If a match is found:
        - exact: shows diff, asks overwrite / skip / cancel-batch.
        - rename: tells the user old name -> toolkit name, offers replace-and-rename
          (delete old folder, install new) / install-alongside / skip.
        - fuzzy: tells the user the candidate match name + similarity score,
          offers same options.
    - If no match: installs cleanly.
    - --force-all: auto-accept overwrites + auto-rename (no prompts). Use with care.
    - Reports added / replaced / renamed / skipped / failed.

Toolkit location:
    - $CLAUDE_TOOLKIT env var, OR
    - the directory containing this script's parent (assumes scripts/ lives in the
      toolkit root).
"""
import os
import re
import shutil
import sys
from pathlib import Path


# ---------- toolkit + group + rename parsers ----------

def find_toolkit() -> Path:
    env = os.environ.get("CLAUDE_TOOLKIT")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / ".claude" / "skills").is_dir():
            return p
    here = Path(__file__).resolve().parent.parent
    if (here / ".claude" / "skills").is_dir():
        return here
    raise SystemExit(
        "ERROR: cannot find toolkit. Set $CLAUDE_TOOLKIT or run from inside the toolkit."
    )


def parse_groups(groups_md: Path) -> dict:
    if not groups_md.exists():
        return {}
    text = groups_md.read_text(encoding="utf-8")
    groups, current = {}, None
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


def parse_renames(renames_md: Path) -> dict:
    """Return {old_name: new_name} from RENAMES.md code blocks."""
    if not renames_md.exists():
        return {}
    text = renames_md.read_text(encoding="utf-8")
    renames = {}
    in_block = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            m = re.match(r"^([A-Za-z0-9_-]+)\s*->\s*([A-Za-z0-9_-]+)\s*$", line.strip())
            if m:
                renames[m.group(1)] = m.group(2)
    return renames


# ---------- description extractor + fuzzy match ----------

def get_description(skill_md: Path) -> str:
    if not skill_md.is_file():
        return ""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^description:\s*(.+?)$", text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip().strip("\"").strip("'")
    return ""


def normalize(s: str) -> set:
    """Tokenize for cheap Jaccard-ish similarity."""
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def find_dest_match(toolkit_name: str, toolkit_skill_dir: Path,
                    dest_skills_dir: Path, renames: dict) -> tuple:
    """
    Locate a corresponding skill in the destination.
    Returns (match_kind, dest_path) where match_kind is one of:
      "exact" | "rename" | "fuzzy" | None
    """
    # 1. Exact
    exact = dest_skills_dir / toolkit_name
    if exact.is_dir():
        return ("exact", exact)
    # 2. Rename: any old -> toolkit_name where old exists in dest
    old_candidates = [old for old, new in renames.items() if new == toolkit_name]
    for old in old_candidates:
        cand = dest_skills_dir / old
        if cand.is_dir():
            return ("rename", cand)
    # 3. Fuzzy: description Jaccard >= 0.55 on top of skill-name Jaccard >= 0.4
    if not dest_skills_dir.is_dir():
        return (None, None)
    toolkit_desc = normalize(get_description(toolkit_skill_dir / "SKILL.md"))
    toolkit_name_tokens = normalize(toolkit_name)
    best, best_score = None, 0.0
    for cand in dest_skills_dir.iterdir():
        if not cand.is_dir() or cand.name == toolkit_name:
            continue
        cand_desc = normalize(get_description(cand / "SKILL.md"))
        cand_name = normalize(cand.name)
        name_sim = jaccard(toolkit_name_tokens, cand_name)
        desc_sim = jaccard(toolkit_desc, cand_desc) if cand_desc else 0.0
        # Weight: name 0.4, desc 0.6
        score = 0.4 * name_sim + 0.6 * desc_sim
        if score > best_score and score >= 0.5:
            best, best_score = cand, score
    if best:
        return ("fuzzy", best)
    return (None, None)


# ---------- diff + copy ----------

def files_differ(a: Path, b: Path) -> bool:
    """Quick byte-level tree comparison."""
    if not a.is_dir() or not b.is_dir():
        return True
    a_files = {p.relative_to(a) for p in a.rglob("*") if p.is_file()}
    b_files = {p.relative_to(b) for p in b.rglob("*") if p.is_file()}
    if a_files != b_files:
        return True
    for rel in a_files:
        if (a / rel).read_bytes() != (b / rel).read_bytes():
            return True
    return False


def copy_skill(src: Path, dst: Path):
    """Byte-level copy. Removes dst first if it exists."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(item.read_bytes())


# ---------- prompt + main ----------

def prompt(question: str, options: list, force: bool, default: str) -> str:
    if force:
        return default
    while True:
        print(question)
        for i, (key, label) in enumerate(options, 1):
            print(f"  {i}. [{key}] {label}")
        choice = input("> ").strip().lower()
        if not choice:
            return default
        for key, _ in options:
            if choice == key or choice == key[0]:
                return key
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except ValueError:
            pass


def main():
    args = [a for a in sys.argv[1:] if a != "--force-all"]
    force = "--force-all" in sys.argv
    if len(args) < 1:
        print(__doc__)
        sys.exit(1)
    project = Path(args[0]).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"ERROR: project path not found: {project}")
    targets = args[1:]

    toolkit = find_toolkit()
    skills_dir = toolkit / ".claude" / "skills"
    groups = parse_groups(skills_dir / "SKILL_GROUPS.md")
    renames = parse_renames(skills_dir / "RENAMES.md")

    if not targets:
        print("Available groups:")
        for name, skills in groups.items():
            print(f"  {name} ({len(skills)} skills)")
        choice = input("\nGroup(s) to install (space-separated, or 'all'): ").strip()
        if not choice:
            raise SystemExit("No selection -- aborting.")
        targets = list(groups.keys()) if choice == "all" else choice.split()

    # Resolve targets to skill names
    to_install, unknown = [], []
    for t in targets:
        if t in groups:
            to_install.extend(groups[t])
        elif (skills_dir / t).is_dir():
            to_install.append(t)
        else:
            unknown.append(t)
    seen = set()
    to_install = [s for s in to_install if not (s in seen or seen.add(s))]
    if unknown:
        print(f"WARNING: unknown targets (not a group or skill): {unknown}")
    if not to_install:
        raise SystemExit("Nothing to install.")

    dest_skills = project / ".claude" / "skills"
    dest_skills.mkdir(parents=True, exist_ok=True)

    print(f"\nToolkit: {toolkit}")
    print(f"Project: {project}")
    print(f"Skills to install: {len(to_install)}")
    print()

    added, replaced, renamed_replaced, kept_alongside, skipped, failed = [], [], [], [], [], []

    for name in to_install:
        src = skills_dir / name
        if not src.is_dir():
            failed.append((name, "source not in toolkit"))
            continue

        kind, dest_match = find_dest_match(name, src, dest_skills, renames)
        target = dest_skills / name

        if kind is None:
            # Clean install
            try:
                copy_skill(src, target)
                added.append(name)
                print(f"  + {name}  (added)")
            except Exception as e:
                failed.append((name, str(e)))
            continue

        if kind == "exact":
            if not files_differ(src, dest_match):
                skipped.append(name)
                print(f"  = {name}  (already in sync)")
                continue
            print(f"\n[EXACT MATCH, differs] {name}")
            print(f"  toolkit: {src}")
            print(f"  dest:    {dest_match}")
            choice = prompt(
                "Action?",
                [("overwrite", "overwrite destination with toolkit version"),
                 ("skip", "leave destination as-is")],
                force, default="overwrite",
            )
            if choice == "overwrite":
                copy_skill(src, target)
                replaced.append(name)
                print(f"  ~ {name}  (replaced)")
            else:
                skipped.append(name)
                print(f"  > {name}  (skipped)")
            continue

        if kind == "rename":
            print(f"\n[RENAME MATCH] toolkit '{name}' <-> dest '{dest_match.name}' (per RENAMES.md)")
            choice = prompt(
                "Action?",
                [("replace", f"delete '{dest_match.name}', install '{name}' (recommended)"),
                 ("alongside", f"keep '{dest_match.name}', also install '{name}'"),
                 ("skip", "do nothing")],
                force, default="replace",
            )
            if choice == "replace":
                shutil.rmtree(dest_match)
                copy_skill(src, target)
                renamed_replaced.append((dest_match.name, name))
                print(f"  R {dest_match.name} -> {name}  (renamed-replaced)")
            elif choice == "alongside":
                copy_skill(src, target)
                kept_alongside.append(name)
                print(f"  + {name}  (added alongside {dest_match.name})")
            else:
                skipped.append(name)
                print(f"  > {name}  (skipped)")
            continue

        if kind == "fuzzy":
            print(f"\n[FUZZY MATCH] toolkit '{name}' looks similar to dest '{dest_match.name}'")
            print(f"  Consider: is '{dest_match.name}' an undocumented older name for '{name}'?")
            print(f"  If yes, you can add '{dest_match.name} -> {name}' to skills/RENAMES.md.")
            choice = prompt(
                "Action?",
                [("alongside", f"install '{name}' alongside (treat as different skill)"),
                 ("replace", f"delete '{dest_match.name}', install '{name}' (treat as same)"),
                 ("skip", "do nothing")],
                force, default="alongside",
            )
            if choice == "replace":
                shutil.rmtree(dest_match)
                copy_skill(src, target)
                renamed_replaced.append((dest_match.name, name))
                print(f"  R {dest_match.name} -> {name}  (fuzzy-renamed-replaced)")
            elif choice == "alongside":
                copy_skill(src, target)
                kept_alongside.append(name)
                print(f"  + {name}  (added alongside fuzzy '{dest_match.name}')")
            else:
                skipped.append(name)
                print(f"  > {name}  (skipped)")
            continue

    print()
    print("=== Install summary ===")
    print(f"Added (clean):           {len(added)}")
    print(f"Replaced (exact match):  {len(replaced)}")
    print(f"Renamed-replaced:        {len(renamed_replaced)}")
    if renamed_replaced:
        for old, new in renamed_replaced:
            print(f"  {old} -> {new}")
    print(f"Kept alongside:          {len(kept_alongside)}")
    print(f"Skipped:                 {len(skipped)}")
    if failed:
        print(f"Failed:                  {len(failed)}")
        for n, err in failed:
            print(f"  ! {n} -- {err}")
    print()
    print("Next steps in destination:")
    print(f"  cd {project}")
    print("  git status")
    print("  git add .claude/skills/")
    print("  git commit -m 'chore: sync skills from claude-toolkit'")


if __name__ == "__main__":
    main()
