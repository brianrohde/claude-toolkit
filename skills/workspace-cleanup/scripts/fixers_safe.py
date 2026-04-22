"""
Tier 1 (safe-auto-fix) fixers: batch-approvable fixes with no risk.
"""
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any


def remove_skill_readme(root: Path, findings: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """Remove README.md files from skill folders."""
    result = {'rule_id': 'R-SKILL-README', 'actions': [], 'error': None}

    for finding in findings:
        if finding['rule_id'] != 'R-SKILL-README':
            continue

        readme_path = root / finding['file']
        if not readme_path.exists():
            continue

        try:
            if not dry_run:
                readme_path.unlink()
            result['actions'].append({
                'file': finding['file'],
                'action': 'deleted',
                'dry_run': dry_run
            })
        except Exception as e:
            result['error'] = str(e)
            break

    return result


def add_gitignore_entries(root: Path, findings: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """Add .claude/ entries to .gitignore if not present."""
    result = {'rule_id': 'R-LOCAL-SCOPE', 'actions': [], 'error': None}

    gitignore_path = root / '.gitignore'
    entries_to_add = ['.claude/settings.local.json', '.claude/logs/']

    try:
        # Read existing .gitignore
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding='utf-8')
        else:
            content = ''

        # Check which entries are missing
        missing = [e for e in entries_to_add if e not in content]

        if missing:
            new_content = content
            if new_content and not new_content.endswith('\n'):
                new_content += '\n'

            for entry in missing:
                new_content += entry + '\n'

            if not dry_run:
                _safe_write(gitignore_path, new_content)

            result['actions'].append({
                'file': '.gitignore',
                'action': 'updated',
                'added': missing,
                'dry_run': dry_run
            })
        else:
            result['actions'].append({
                'file': '.gitignore',
                'action': 'already_present',
                'dry_run': dry_run
            })
    except Exception as e:
        result['error'] = str(e)

    return result


def fix_skill_name_casing(root: Path, findings: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """Rename skill folders to match kebab-case frontmatter names."""
    result = {'rule_id': 'R-SKILL-NAME', 'actions': [], 'error': None}

    skills_dir = root / '.claude' / 'skills'
    if not skills_dir.exists():
        return result

    for finding in findings:
        if finding['rule_id'] != 'R-SKILL-NAME':
            continue

        # Extract skill name from file path
        # File is something like '.claude/skills/MySkill/SKILL.md'
        skill_path = root / finding['file']
        skill_folder = skill_path.parent

        # Get the expected name from the frontmatter (parsed by finding generator)
        # For now, infer from message or try to rename based on pattern
        # This is a simplified version; full version would parse frontmatter
        try:
            skill_md = skill_folder / 'SKILL.md'
            if skill_md.exists():
                content = skill_md.read_text(encoding='utf-8')
                # Extract name from frontmatter
                import re
                match = re.search(r'name:\s*([^\n]+)', content)
                if match:
                    expected_name = match.group(1).strip().strip('"\'')
                    current_name = skill_folder.name

                    if current_name != expected_name:
                        new_folder = skill_folder.parent / expected_name

                        if not dry_run:
                            skill_folder.rename(new_folder)

                        result['actions'].append({
                            'file': str(skill_folder.relative_to(root)),
                            'action': 'renamed',
                            'from': current_name,
                            'to': expected_name,
                            'dry_run': dry_run
                        })
        except Exception as e:
            result['error'] = str(e)
            break

    return result


def _safe_write(path: Path, content: str) -> None:
    """Write file safely via temp file + move."""
    with tempfile.NamedTemporaryFile('w', suffix='.tmp', delete=False,
                                     encoding='utf-8', newline='\n') as f:
        f.write(content)
        tmp = Path(f.name)
    shutil.move(str(tmp), str(path))


def apply_tier1_fixes(root: Path, findings: List[Dict[str, Any]], dry_run: bool = False) -> List[Dict[str, Any]]:
    """Apply all Tier 1 fixes."""
    results = []
    results.append(remove_skill_readme(root, findings, dry_run))
    results.append(add_gitignore_entries(root, findings, dry_run))
    results.append(fix_skill_name_casing(root, findings, dry_run))
    return results
