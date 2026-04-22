"""
Tier 2 (medium-impact) fixers: per-item preview + approval required.
"""
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any


def trim_claude_md(root: Path, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Suggest trimming CLAUDE.md; return suggestions for user review."""
    result = {'rule_id': 'R-CLAUDE-SIZE', 'suggestions': [], 'error': None}

    claude_md = root / 'CLAUDE.md'
    if not claude_md.exists():
        return result

    try:
        content = claude_md.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Identify multi-line tables and verbose sections
        import re

        # Suggestion 1: Replace long tables with references
        table_matches = list(re.finditer(r'\|\s*-+\s*\|.*?\n(?:\|.*?\n){5,}', content))
        if table_matches:
            result['suggestions'].append({
                'type': 'table_to_reference',
                'message': f'Found {len(table_matches)} table(s) that could be moved to external reference',
                'action': 'Review tables in CLAUDE.md; move detailed tables to docs/ or .claude/rules/',
                'impact': 'Can reduce file by 20-40 lines'
            })

        # Suggestion 2: Condense verbose sections
        long_sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        if len(long_sections) > 8:
            result['suggestions'].append({
                'type': 'condense_sections',
                'message': f'Found {len(long_sections)} H2 sections; consider consolidating or moving some',
                'action': 'Merge related sections or move detailed content to separate docs',
                'impact': f'Can reduce file by 10-30 lines'
            })

        # Suggestion 3: Replace detailed workflows with cross-references
        workflow_lines = [l for l in lines if 'workflow' in l.lower()]
        if len(workflow_lines) > 3:
            result['suggestions'].append({
                'type': 'workflow_reference',
                'message': 'Multiple workflow descriptions found; consider referencing .claude/rules/ instead',
                'action': 'Replace inline workflow descriptions with links to .claude/rules/',
                'impact': 'Can reduce file by 15-25 lines'
            })

    except Exception as e:
        result['error'] = str(e)

    return result


def trim_skill_md(root: Path, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Suggest trimming oversized SKILL.md files; return suggestions for user review."""
    result = {'rule_id': 'R-SKILL-SIZE', 'suggestions': [], 'error': None}

    skills_dir = root / '.claude' / 'skills'
    if not skills_dir.exists():
        return result

    try:
        for skill_md in skills_dir.rglob('SKILL.md'):
            content = skill_md.read_text(encoding='utf-8')
            lines = content.split('\n')
            line_count = len(lines)

            if line_count < 300:
                continue

            import re

            # Find code blocks, examples, appendix sections
            code_blocks = len(re.findall(r'```', content))
            example_matches = list(re.finditer(r'^###?\s+Example', content, re.MULTILINE))
            appendix_match = re.search(r'^##\s+Appendix', content, re.MULTILINE)

            if code_blocks > 5 or len(example_matches) > 3:
                result['suggestions'].append({
                    'type': 'extract_examples',
                    'file': str(skill_md.relative_to(root)),
                    'message': f'Found {code_blocks} code blocks and {len(example_matches)} examples',
                    'action': f'Move examples to assets/examples.md or references/',
                    'impact': f'Can reduce SKILL.md from {line_count} to ~150-200 LOC'
                })

            if appendix_match:
                result['suggestions'].append({
                    'type': 'extract_appendix',
                    'file': str(skill_md.relative_to(root)),
                    'message': 'Appendix section found',
                    'action': 'Move appendix to references/ subdirectory',
                    'impact': 'Can reduce SKILL.md by 30-50 lines'
                })

    except Exception as e:
        result['error'] = str(e)

    return result


def update_permissions_deny(root: Path, findings: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """Add missing sensitive patterns to permissions.deny in settings.json."""
    result = {'rule_id': 'R-SENSITIVE-PATHS', 'actions': [], 'error': None}

    settings_json = root / '.claude' / 'settings.json'
    if not settings_json.exists():
        result['error'] = 'settings.json not found'
        return result

    try:
        data = json.loads(settings_json.read_text(encoding='utf-8'))

        if 'permissions' not in data:
            data['permissions'] = {}
        if 'deny' not in data['permissions']:
            data['permissions']['deny'] = []

        deny_list = data['permissions']['deny']
        required = ['.env*', '*.pem', '*.key', 'credentials*', 'secret*']
        missing = [p for p in required if p not in deny_list]

        if missing:
            new_deny = deny_list + missing
            data['permissions']['deny'] = new_deny

            if not dry_run:
                _safe_write(settings_json, json.dumps(data, indent=2))

            result['actions'].append({
                'file': '.claude/settings.json',
                'action': 'updated',
                'added': missing,
                'new_deny_list': new_deny,
                'dry_run': dry_run
            })
        else:
            result['actions'].append({
                'file': '.claude/settings.json',
                'action': 'no_changes',
                'reason': 'all required patterns already present'
            })

    except Exception as e:
        result['error'] = str(e)

    return result


def _safe_write(path: Path, content: str) -> None:
    """Write file safely via temp file + move."""
    with tempfile.NamedTemporaryFile('w', suffix='.tmp', delete=False,
                                     encoding='utf-8', newline='\n') as f:
        f.write(content)
        tmp = Path(f.name)
    shutil.move(str(tmp), str(path))


def apply_tier2_suggestions(root: Path, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collect Tier 2 suggestions for user review."""
    suggestions = []
    suggestions.append(trim_claude_md(root, findings))
    suggestions.append(trim_skill_md(root, findings))
    suggestions.append(update_permissions_deny(root, findings, dry_run=True))  # Show as preview
    return suggestions
