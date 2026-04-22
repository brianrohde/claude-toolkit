"""
Claude hygiene checks: CLAUDE.md size, skill names, README presence, SKILL.md size, duplicate instructions, local scope, content.
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Any


def run(root: Path) -> List[Dict[str, Any]]:
    """
    Run all Claude hygiene checks on a repository.

    Returns list of finding dicts: {rule_id, severity, fix_tier, category, file, line, message, detail, is_violation}
    """
    findings = []

    # R-CLAUDE-SIZE
    findings.extend(_check_claude_size(root))

    # R-SKILL-NAME
    findings.extend(_check_skill_names(root))

    # R-SKILL-README
    findings.extend(_check_skill_readme(root))

    # R-SKILL-SIZE
    findings.extend(_check_skill_size(root))

    # R-DUP-INSTR
    findings.extend(_check_duplicate_instructions(root))

    # R-LOCAL-SCOPE
    findings.extend(_check_local_scope(root))

    # R-CLAUDE-CONTENT
    findings.extend(_check_claude_content(root))

    return findings


def _check_claude_size(root: Path) -> List[Dict[str, Any]]:
    """Check if CLAUDE.md exceeds 200 lines."""
    findings = []
    claude_md = root / 'CLAUDE.md'

    if not claude_md.exists():
        return findings

    try:
        lines = claude_md.read_text(encoding='utf-8').split('\n')
        line_count = len(lines)

        if line_count > 200:
            severity = 'HIGH'
        elif line_count > 150:
            severity = 'MEDIUM'
        else:
            return findings

        findings.append({
            'rule_id': 'R-CLAUDE-SIZE',
            'severity': severity,
            'fix_tier': 2,
            'category': 'Claude',
            'file': 'CLAUDE.md',
            'line': None,
            'message': f'CLAUDE.md exceeds target size ({line_count} lines)',
            'detail': f'''CLAUDE.md loads at every session start. Current: {line_count} lines.
Target: 80–150 lines. Max acceptable: 200 lines.

Recommendation:
1. Move detailed workflows to .claude/rules/ or skill SKILL.md files
2. Trim table entries to one-line summaries
3. Replace multi-paragraph sections with links to external docs

See rule-catalog.md for details.''',
            'is_violation': severity == 'HIGH'
        })
    except Exception:
        pass

    return findings


def _check_skill_names(root: Path) -> List[Dict[str, Any]]:
    """Check skill folder names match frontmatter 'name' and are kebab-case."""
    findings = []
    skills_dir = root / '.claude' / 'skills'

    if not skills_dir.exists():
        return findings

    for skill_folder in skills_dir.iterdir():
        if not skill_folder.is_dir() or skill_folder.name.startswith('_'):
            continue

        skill_md = skill_folder / 'SKILL.md'
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text(encoding='utf-8')
            match = re.search(r'name:\s*([^\n]+)', content)
            if not match:
                continue

            frontmatter_name = match.group(1).strip().strip('"\'')
            folder_name = skill_folder.name

            # Check if folder name matches frontmatter name
            if folder_name != frontmatter_name:
                findings.append({
                    'rule_id': 'R-SKILL-NAME',
                    'severity': 'HIGH',
                    'fix_tier': 1,
                    'category': 'Claude',
                    'file': str(skill_md.relative_to(root)),
                    'line': 2,
                    'message': f'Skill folder name mismatch: folder="{folder_name}" vs name="{frontmatter_name}"',
                    'detail': f'''Folder names are the public API. Mismatches cause lookup failure and user confusion.

Folder: .claude/skills/{folder_name}/
Frontmatter name: {frontmatter_name}

Fix: Rename folder to .claude/skills/{frontmatter_name}/ (kebab-case, lowercase).''',
                    'is_violation': True
                })

            # Check if kebab-case
            if not _is_kebab_case(frontmatter_name):
                findings.append({
                    'rule_id': 'R-SKILL-NAME',
                    'severity': 'HIGH',
                    'fix_tier': 1,
                    'category': 'Claude',
                    'file': str(skill_md.relative_to(root)),
                    'line': 2,
                    'message': f'Skill name not kebab-case: "{frontmatter_name}" (expected lowercase with hyphens)',
                    'detail': f'''Skill names must be kebab-case (lowercase with hyphens).
Found: {frontmatter_name}
Rename to: {_to_kebab_case(frontmatter_name)}''',
                    'is_violation': True
                })
        except Exception:
            pass

    return findings


def _check_skill_readme(root: Path) -> List[Dict[str, Any]]:
    """Check if README.md exists in any skill folder."""
    findings = []
    skills_dir = root / '.claude' / 'skills'

    if not skills_dir.exists():
        return findings

    for skill_folder in skills_dir.rglob('README.md'):
        if '.claude/skills' in str(skill_folder):
            findings.append({
                'rule_id': 'R-SKILL-README',
                'severity': 'MEDIUM',
                'fix_tier': 1,
                'category': 'Claude',
                'file': str(skill_folder.relative_to(root)),
                'line': None,
                'message': f'README.md found in skill folder (should be deleted)',
                'detail': '''SKILL.md is the single source of truth for skill documentation.
A separate README causes duplication and divergence.

Action: Delete this file.''',
                'is_violation': False
            })

    return findings


def _check_skill_size(root: Path) -> List[Dict[str, Any]]:
    """Check if SKILL.md files exceed 500 lines."""
    findings = []
    skills_dir = root / '.claude' / 'skills'

    if not skills_dir.exists():
        return findings

    for skill_md in skills_dir.rglob('SKILL.md'):
        if not str(skill_md).count('.claude/skills'):
            continue

        try:
            lines = skill_md.read_text(encoding='utf-8').split('\n')
            line_count = len(lines)

            if line_count > 500:
                severity = 'HIGH'
            elif line_count > 300:
                severity = 'MEDIUM'
            else:
                continue

            findings.append({
                'rule_id': 'R-SKILL-SIZE',
                'severity': severity,
                'fix_tier': 2,
                'category': 'Claude',
                'file': str(skill_md.relative_to(root)),
                'line': None,
                'message': f'SKILL.md exceeds target size ({line_count} lines)',
                'detail': f'''SKILL.md loads when skill is activated. Current: {line_count} lines.
Target: 100–250 lines. Max acceptable: 500 lines.

Recommendation: Extract examples, guides, or reference material into assets/ or references/ subdirs.''',
                'is_violation': severity == 'HIGH'
            })
        except Exception:
            pass

    return findings


def _check_duplicate_instructions(root: Path) -> List[Dict[str, Any]]:
    """Check for duplicate H2/H3 headings across CLAUDE.md and .claude/rules/."""
    findings = []

    # Collect headings from CLAUDE.md
    claude_md = root / 'CLAUDE.md'
    claude_headings = {}
    if claude_md.exists():
        try:
            content = claude_md.read_text(encoding='utf-8')
            for match in re.finditer(r'^(#{2,3})\s+(.+)$', content, re.MULTILINE):
                level = len(match.group(1))
                heading = match.group(2).strip()
                claude_headings[heading] = ('CLAUDE.md', match.start())
        except Exception:
            pass

    # Collect headings from .claude/rules/
    rules_dir = root / '.claude' / 'rules'
    if rules_dir.exists():
        for rule_file in rules_dir.glob('*.md'):
            try:
                content = rule_file.read_text(encoding='utf-8')
                for match in re.finditer(r'^(#{2,3})\s+(.+)$', content, re.MULTILINE):
                    level = len(match.group(1))
                    heading = match.group(2).strip()
                    if heading in claude_headings:
                        findings.append({
                            'rule_id': 'R-DUP-INSTR',
                            'severity': 'HIGH',
                            'fix_tier': 2,
                            'category': 'Claude',
                            'file': str(rule_file.relative_to(root)),
                            'line': None,
                            'message': f'Duplicate heading "{heading}" found in CLAUDE.md and {rule_file.name}',
                            'detail': f'''Duplicate section names confuse users and obscure scope.

Heading: {heading}
Found in: CLAUDE.md and {rule_file.name}

Fix: Rename one or consolidate into a single location.''',
                            'is_violation': True
                        })
            except Exception:
                pass

    return findings


def _check_local_scope(root: Path) -> List[Dict[str, Any]]:
    """Check if settings.local.json is gitignored and warn about stale paths."""
    findings = []

    # Check if .claude/settings.local.json is gitignored
    gitignore = root / '.gitignore'
    settings_local = root / '.claude' / 'settings.local.json'

    is_gitignored = False
    if gitignore.exists():
        try:
            content = gitignore.read_text(encoding='utf-8')
            if '.claude/settings.local.json' in content or '.claude/logs' in content:
                is_gitignored = True
        except Exception:
            pass

    if not is_gitignored:
        findings.append({
            'rule_id': 'R-LOCAL-SCOPE',
            'severity': 'HIGH',
            'fix_tier': 1,
            'category': 'Claude',
            'file': '.gitignore',
            'line': None,
            'message': 'settings.local.json not gitignored (or .claude/logs/ not gitignored)',
            'detail': '''settings.local.json and .claude/logs/ should not be committed.

Action:
1. Add to .gitignore:
   .claude/settings.local.json
   .claude/logs/
2. Commit the .gitignore change.''',
            'is_violation': True
        })

    # Check for stale paths in settings.local.json
    if settings_local.exists():
        try:
            content = settings_local.read_text(encoding='utf-8')

            # Flag if it contains dead machine names or unreachable paths
            stale_patterns = [
                r'/mnt/\w+machine\.local',
                r'C:\\dead_drive',
                r'\\\\oldmachine',
                r'enricomanfron',  # Example stale machine name
            ]

            stale_entries = []
            for pattern in stale_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                stale_entries.extend(matches)

            if stale_entries:
                findings.append({
                    'rule_id': 'R-LOCAL-SCOPE',
                    'severity': 'HIGH',
                    'fix_tier': 1,
                    'category': 'Claude',
                    'file': str(settings_local.relative_to(root)),
                    'line': None,
                    'message': f'settings.local.json contains stale paths (dead machine names detected)',
                    'detail': f'''Found stale entries from previous machines:
{', '.join(set(stale_entries))}

This file should be gitignored and deleted. It's machine-local and should not be in the repo.

Action:
1. Delete .claude/settings.local.json
2. Ensure it's in .gitignore
3. Commit the .gitignore change.''',
                    'is_violation': True
                })
        except Exception:
            pass

    return findings


def _check_claude_content(root: Path) -> List[Dict[str, Any]]:
    """Check if CLAUDE.md contains step-by-step procedures (should be external)."""
    findings = []
    claude_md = root / 'CLAUDE.md'

    if not claude_md.exists():
        return findings

    try:
        content = claude_md.read_text(encoding='utf-8')

        # Look for numbered lists (1. 2. 3.) that span multiple lines
        if re.search(r'^\s*\d+\.\s+.+$\n\s*\d+\.\s+.+$', content, re.MULTILINE):
            findings.append({
                'rule_id': 'R-CLAUDE-CONTENT',
                'severity': 'MEDIUM',
                'fix_tier': 2,
                'category': 'Claude',
                'file': 'CLAUDE.md',
                'line': None,
                'message': 'Step-by-step procedures detected in CLAUDE.md (should be in external docs)',
                'detail': '''CLAUDE.md should be a navigation hub, not a procedures manual.
Detailed workflows belong in .claude/rules/ or skill SKILL.md files.

Recommendation: Move procedures to external docs and replace with cross-references.''',
                'is_violation': False
            })
    except Exception:
        pass

    return findings


def _is_kebab_case(s: str) -> bool:
    """Check if string is kebab-case (lowercase with hyphens, alphanumeric)."""
    return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', s))


def _to_kebab_case(s: str) -> str:
    """Convert string to kebab-case."""
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s)  # CamelCase -> camel-case
    s = re.sub(r'_', '-', s)  # underscore_case -> hyphen-case
    return s.lower()
