"""
Source quality checks: file length, function complexity (review triggers, never HIGH severity).
"""
from pathlib import Path
from typing import List, Dict, Any
import re


def run(root: Path) -> List[Dict[str, Any]]:
    """Run source quality checks."""
    findings = []
    findings.extend(_check_file_length(root))
    findings.extend(_check_function_complexity(root))
    return findings


def _check_file_length(root: Path) -> List[Dict[str, Any]]:
    """Check for files exceeding line count thresholds (review triggers)."""
    findings = []

    for py_file in root.rglob('*.py'):
        # Skip hidden dirs and common exclusions
        if any(part.startswith('.') for part in py_file.parts):
            continue
        if any(x in str(py_file) for x in ['__pycache__', '.venv', 'venv', 'node_modules']):
            continue

        try:
            lines = py_file.read_text(encoding='utf-8').split('\n')
            line_count = len(lines)

            if line_count >= 500:
                severity = 'MEDIUM'
            elif line_count >= 300:
                severity = 'LOW'
            else:
                continue

            findings.append({
                'rule_id': 'R-FILE-LEN',
                'severity': severity,
                'fix_tier': 3,
                'category': 'Source',
                'file': str(py_file.relative_to(root)),
                'line': None,
                'message': f'File exceeds {300 if severity == "LOW" else 500} LOC ({line_count} lines)',
                'detail': f'''File size: {line_count} lines.

Threshold for {severity} trigger: {500 if severity == "MEDIUM" else 300} LOC.

Recommendation: Review for cohesion; consider splitting into smaller modules or extracting utilities.

This is a review trigger; fix is optional unless multiple triggers accumulate.''',
                'is_violation': False
            })
        except Exception:
            pass

    return findings


def _check_function_complexity(root: Path) -> List[Dict[str, Any]]:
    """Check for complex functions (McCabe > 10 or > 60 LOC)."""
    findings = []

    for py_file in root.rglob('*.py'):
        # Skip hidden dirs and common exclusions
        if any(part.startswith('.') for part in py_file.parts):
            continue
        if any(x in str(py_file) for x in ['__pycache__', '.venv', 'venv', 'node_modules']):
            continue

        try:
            content = py_file.read_text(encoding='utf-8')

            # Simple heuristic: find def statements and count lines until next def or EOF
            func_pattern = r'^\s*def\s+(\w+)\('
            matches = list(re.finditer(func_pattern, content, re.MULTILINE))

            for i, match in enumerate(matches):
                func_name = match.group(1)
                func_start = match.start()

                # Find next function or EOF
                if i + 1 < len(matches):
                    func_end = matches[i + 1].start()
                else:
                    func_end = len(content)

                func_body = content[func_start:func_end]
                func_lines = func_body.count('\n')

                # Estimate McCabe complexity (very rough: count if/for/while/except/and/or)
                control_flow = len(re.findall(r'\b(if|elif|for|while|except|and|or)\b', func_body))

                if func_lines > 60 or control_flow > 10:
                    severity = 'MEDIUM' if func_lines > 60 or control_flow > 10 else 'LOW'

                    line_num = content[:func_start].count('\n') + 1

                    findings.append({
                        'rule_id': 'R-FUNC-CPLX',
                        'severity': severity,
                        'fix_tier': 3,
                        'category': 'Source',
                        'file': str(py_file.relative_to(root)),
                        'line': line_num,
                        'message': f'Function "{func_name}" is complex ({func_lines} LOC, ~{control_flow} control flow nodes)',
                        'detail': f'''Function: {func_name}
Lines: {func_lines}
Complexity estimate: {control_flow} control flow nodes

Threshold for MEDIUM: >60 LOC or McCabe >10.

Recommendation: Consider breaking into smaller, focused functions.

This is a review trigger; fix is optional.''',
                        'is_violation': False
                    })
        except Exception:
            pass

    return findings
