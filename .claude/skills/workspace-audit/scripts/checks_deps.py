"""
Dependency hygiene checks: lockfiles, sensitive paths in permissions.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any


def run(root: Path) -> List[Dict[str, Any]]:
    """Run all dependency hygiene checks."""
    findings = []
    findings.extend(_check_deps_lock(root))
    findings.extend(_check_sensitive_paths(root))
    findings.extend(_check_deps_audit(root))
    findings.extend(_check_deps_unused(root))
    return findings


def _check_deps_lock(root: Path) -> List[Dict[str, Any]]:
    """Check if required lockfiles are committed."""
    findings = []

    # Detect which ecosystems are in use
    has_python = _check_python_project(root)
    has_nodejs = _check_nodejs_project(root)
    has_ruby = _check_ruby_project(root)
    has_go = _check_go_project(root)

    # Check Python
    if has_python:
        lock_files = ['requirements.lock', 'poetry.lock', 'environment.lock.yml']
        has_lock = any((root / f).exists() for f in lock_files)
        if not has_lock:
            findings.append({
                'rule_id': 'R-DEPS-LOCK',
                'severity': 'HIGH',
                'fix_tier': 3,
                'category': 'Deps',
                'file': None,
                'line': None,
                'message': 'Python ecosystem detected but no lockfile committed',
                'detail': '''Found setup.py or requirements.txt but no lockfile.
Lockfiles ensure reproducible installs and prevent supply chain surprises.

To fix:
1. If using pip: pip freeze > requirements.lock && git add requirements.lock
2. If using poetry: poetry lock && git add poetry.lock
3. If using conda: conda env export > environment.lock.yml && git add environment.lock.yml

Re-run audit after committing.''',
                'is_violation': True
            })

    # Check Node.js
    if has_nodejs:
        lock_files = ['package-lock.json', 'yarn.lock']
        has_lock = any((root / f).exists() for f in lock_files)
        if not has_lock:
            findings.append({
                'rule_id': 'R-DEPS-LOCK',
                'severity': 'HIGH',
                'fix_tier': 3,
                'category': 'Deps',
                'file': None,
                'line': None,
                'message': 'Node.js ecosystem detected but no lockfile committed',
                'detail': '''Found package.json but no lockfile.

To fix:
1. If using npm: npm ci && git add package-lock.json
2. If using yarn: yarn install && git add yarn.lock

Re-run audit after committing.''',
                'is_violation': True
            })

    # Check Ruby
    if has_ruby:
        if not (root / 'Gemfile.lock').exists():
            findings.append({
                'rule_id': 'R-DEPS-LOCK',
                'severity': 'HIGH',
                'fix_tier': 3,
                'category': 'Deps',
                'file': None,
                'line': None,
                'message': 'Ruby ecosystem detected but Gemfile.lock not committed',
                'detail': '''Found Gemfile but no Gemfile.lock.

To fix:
1. bundle install && git add Gemfile.lock

Re-run audit after committing.''',
                'is_violation': True
            })

    # Check Go
    if has_go:
        if not (root / 'go.sum').exists():
            findings.append({
                'rule_id': 'R-DEPS-LOCK',
                'severity': 'HIGH',
                'fix_tier': 3,
                'category': 'Deps',
                'file': None,
                'line': None,
                'message': 'Go ecosystem detected but go.sum not committed',
                'detail': '''Found go.mod but no go.sum.

To fix:
1. go mod tidy && git add go.sum

Re-run audit after committing.''',
                'is_violation': True
            })

    return findings


def _check_sensitive_paths(root: Path) -> List[Dict[str, Any]]:
    """Check if settings.json permissions.deny covers sensitive patterns."""
    findings = []
    settings_json = root / '.claude' / 'settings.json'

    if not settings_json.exists():
        return findings

    try:
        content = settings_json.read_text(encoding='utf-8')
        data = json.loads(content)

        if 'permissions' not in data or 'deny' not in data['permissions']:
            findings.append({
                'rule_id': 'R-SENSITIVE-PATHS',
                'severity': 'HIGH',
                'fix_tier': 2,
                'category': 'Deps',
                'file': '.claude/settings.json',
                'line': None,
                'message': 'permissions.deny block missing or empty',
                'detail': '''settings.json must have a permissions.deny block covering sensitive file patterns.

Add or update:
"permissions": {
  "deny": [
    ".env*",
    "*.pem",
    "*.key",
    "credentials*",
    "secret*"
  ]
}

This protects against accidental commits of secrets and API keys.''',
                'is_violation': True
            })
            return findings

        deny_list = data['permissions']['deny']
        required_patterns = ['.env*', '*.pem', '*.key', 'credentials*', 'secret*']
        # Accept bare patterns or tool-prefixed variants (e.g. "Read(.env*)", "Edit(*.key)")
        def _pattern_covered(p, deny_list):
            if p in deny_list:
                return True
            return any(entry.endswith(f'({p})') for entry in deny_list)
        missing = [p for p in required_patterns if not _pattern_covered(p, deny_list)]

        if missing:
            findings.append({
                'rule_id': 'R-SENSITIVE-PATHS',
                'severity': 'HIGH',
                'fix_tier': 2,
                'category': 'Deps',
                'file': '.claude/settings.json',
                'line': None,
                'message': f'permissions.deny missing sensitive patterns: {", ".join(missing)}',
                'detail': f'''Current deny list: {deny_list}
Missing patterns: {missing}

Add the missing patterns to permissions.deny in settings.json.''',
                'is_violation': True
            })
    except Exception:
        pass

    return findings


def _check_deps_audit(root: Path) -> List[Dict[str, Any]]:
    """Informational: suggest pip-audit or npm audit."""
    findings = []

    has_python = _check_python_project(root)
    if has_python:
        findings.append({
            'rule_id': 'R-DEPS-AUDIT',
            'severity': 'LOW',
            'fix_tier': 3,
            'category': 'Deps',
            'file': None,
            'line': None,
            'message': 'Recommend running pip audit for Python vulnerability check',
            'detail': '''Tip: Run `pip audit` periodically to check for known vulnerabilities.

To see vulnerable packages:
  pip audit

To fix:
  pip install --upgrade <package>

This is informational; run as needed in your development workflow.''',
            'is_violation': False
        })

    has_nodejs = _check_nodejs_project(root)
    if has_nodejs:
        findings.append({
            'rule_id': 'R-DEPS-AUDIT',
            'severity': 'LOW',
            'fix_tier': 3,
            'category': 'Deps',
            'file': None,
            'line': None,
            'message': 'Recommend running npm audit for Node.js vulnerability check',
            'detail': '''Tip: Run `npm audit` periodically to check for known vulnerabilities.

To see vulnerable packages:
  npm audit

To fix:
  npm audit fix

This is informational; run as needed in your development workflow.''',
            'is_violation': False
        })

    return findings


def _check_deps_unused(root: Path) -> List[Dict[str, Any]]:
    """Informational: unused imports detected."""
    findings = []
    # Placeholder: full implementation would scan Python/JS for unused imports
    # For now, return empty (would require AST parsing)
    return findings


def _check_python_project(root: Path) -> bool:
    """Check if project has Python ecosystem."""
    return (
        (root / 'setup.py').exists() or
        (root / 'requirements.txt').exists() or
        (root / 'pyproject.toml').exists() or
        (root / 'poetry.lock').exists()
    )


def _check_nodejs_project(root: Path) -> bool:
    """Check if project has Node.js ecosystem."""
    return (root / 'package.json').exists()


def _check_ruby_project(root: Path) -> bool:
    """Check if project has Ruby ecosystem."""
    return (root / 'Gemfile').exists()


def _check_go_project(root: Path) -> bool:
    """Check if project has Go ecosystem."""
    return (root / 'go.mod').exists()
