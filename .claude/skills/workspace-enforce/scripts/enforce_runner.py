"""
Enforce runner: CI gate that checks audit findings against gate rules and waivers.
"""
import argparse
import json
import sys
from pathlib import Path

# Import audit checks at runtime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'workspace-audit' / 'scripts'))
import checks_claude
import checks_deps
import checks_source

import waiver_loader


DEFAULT_GATE_RULES = [
    'R-CLAUDE-SIZE',
    'R-SKILL-NAME',
    'R-SKILL-README',
    'R-SKILL-SIZE',
    'R-LOCAL-SCOPE',
    'R-DEPS-LOCK',
    'R-SENSITIVE-PATHS',
]


def main():
    parser = argparse.ArgumentParser(description='Workspace health enforcement gate')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository root')
    parser.add_argument('--waivers', type=Path, help='Waivers file (default: .claude/audit-waivers.json)')
    parser.add_argument('--gate-rules', type=str, help='Comma-separated list of rules to gate (default: Claude + Deps)')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--include-source', action='store_true', help='Include source quality rules in gate')
    parser.add_argument('--exit-on-fail', action='store_true', help='Exit non-zero on violations')

    args = parser.parse_args()
    root = args.root.resolve()

    # Load waivers
    waivers_path = args.waivers or (root / '.claude' / 'audit-waivers.json')
    waivers = waiver_loader.load_waivers(waivers_path.parent)

    # Determine gate rules
    if args.gate_rules:
        gate_rules = [r.strip() for r in args.gate_rules.split(',')]
    else:
        gate_rules = DEFAULT_GATE_RULES
        if args.include_source:
            gate_rules.extend(['R-FILE-LEN', 'R-FUNC-CPLX'])

    # Run audit
    findings = []
    findings.extend(checks_claude.run(root))
    findings.extend(checks_deps.run(root))
    if args.include_source:
        findings.extend(checks_source.run(root))

    # Categorize findings
    violations = [f for f in findings if f['is_violation']]
    unwaived_violations = []
    waived_violations = []

    for v in violations:
        rule_id = v['rule_id']
        is_waived, reason = waiver_loader.is_waived(rule_id, waivers)

        if rule_id in gate_rules:
            if is_waived:
                v['waived'] = True
                v['waiver_reason'] = reason
                waived_violations.append(v)
            else:
                v['waived'] = False
                unwaived_violations.append(v)

    # Output
    if args.format == 'json':
        output = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'repository': str(root),
            'gate_rules': gate_rules,
            'waivers_file': str(waivers_path),
            'exit_code': 1 if unwaived_violations else 0,
            'status': 'FAIL' if unwaived_violations else 'PASS',
            'violations': {
                'unwaived': unwaived_violations,
                'waived': waived_violations,
            },
            'summary': {
                'total_unwaived': len(unwaived_violations),
                'total_waived': len(waived_violations),
                'gate_blocks_merge': len(unwaived_violations) > 0,
            }
        }
        print(json.dumps(output, indent=2, default=str))
        sys.exit(output['exit_code'] if args.exit_on_fail else 0)
    else:
        _output_text(root, gate_rules, waivers_path, unwaived_violations, waived_violations)
        sys.exit(1 if (unwaived_violations and args.exit_on_fail) else 0)


def _output_text(root: Path, gate_rules: list, waivers_path: Path, unwaived: list, waived: list) -> None:
    """Output human-readable gate report."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    lines = []
    lines.append('=' * 80)
    lines.append('WORKSPACE HEALTH ENFORCEMENT GATE')
    lines.append(f'Repository: {root}')
    lines.append(f'Gate Rules: {", ".join(gate_rules)}')
    lines.append(f'Waivers File: {waivers_path}')
    lines.append('=' * 80)
    lines.append('')

    if unwaived:
        lines.append(f'GATE VIOLATIONS ({len(unwaived)} unwaived):')
        lines.append('─' * 80)
        lines.append('')
        for v in unwaived:
            lines.append(f"[{v['rule_id']}] {v['message']}")
            if v['file']:
                lines.append(f"  File: {v['file']}")
            lines.append(f"  Severity: {v['severity']}")
            lines.append(f"  Waived: NO — violation blocks gate")
            lines.append('')

    if waived:
        lines.append(f'GATE VIOLATIONS WAIVED ({len(waived)}):')
        lines.append('─' * 80)
        lines.append('')
        for v in waived:
            lines.append(f"[{v['rule_id']}] {v['message']}")
            if v['file']:
                lines.append(f"  File: {v['file']}")
            lines.append(f"  Waived: YES ({v.get('waiver_reason', 'N/A')})")
            lines.append('')

    lines.append('RESULT: ' + ('FAIL ❌' if unwaived else 'PASS ✅'))
    lines.append('─' * 80)

    if unwaived:
        lines.append(f'Unwaived violations: {len(unwaived)}')
        lines.append('Gate will block merge until all unwaived violations are resolved.')
    else:
        lines.append('All violations resolved or waived. Gate allows merge.')

    lines.append('')
    lines.append('=' * 80)

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
