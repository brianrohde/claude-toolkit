"""
Audit runner: orchestrates all checks and outputs findings.
"""
import argparse
import json
import sys
from pathlib import Path

import checks_claude
import checks_deps
import checks_source


def main():
    parser = argparse.ArgumentParser(description='Workspace health audit runner')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository root')
    parser.add_argument('--only-claude', action='store_true', help='Run only Claude hygiene checks')
    parser.add_argument('--only-deps', action='store_true', help='Run only dependency checks')
    parser.add_argument('--only-source', action='store_true', help='Run only source quality checks')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--output', type=Path, help='Output file (default: stdout)')

    args = parser.parse_args()
    root = args.root.resolve()

    # Determine which checks to run
    run_all = not (args.only_claude or args.only_deps or args.only_source)

    findings = []

    if run_all or args.only_claude:
        findings.extend(checks_claude.run(root))

    if run_all or args.only_deps:
        findings.extend(checks_deps.run(root))

    if run_all or args.only_source:
        findings.extend(checks_source.run(root))

    # Format output
    if args.json:
        output = json.dumps(findings, indent=2)
    else:
        output = _format_report(findings, root)

    # Write output
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(output)


def _format_report(findings: list, root: Path) -> str:
    """Format findings as human-readable report."""
    violations = [f for f in findings if f['is_violation']]
    high_violations = [f for f in violations if f['severity'] == 'HIGH']
    other_findings = [f for f in findings if not f['is_violation']]
    medium_findings = [f for f in other_findings if f['severity'] == 'MEDIUM']
    low_findings = [f for f in other_findings if f['severity'] == 'LOW']

    report = []
    report.append('=' * 80)
    report.append('WORKSPACE HEALTH AUDIT')
    report.append(f'Root: {root}')
    report.append('=' * 80)
    report.append('')

    if violations:
        report.append(f'VIOLATIONS ({len(high_violations)} HIGH, gate will fail):')
        report.append('─' * 80)
        report.append('')
        for finding in violations:
            report.append(_format_finding(finding))
            report.append('')

    if other_findings:
        report.append(f'FINDINGS ({len(medium_findings)} MEDIUM, {len(low_findings)} LOW, optional):')
        report.append('─' * 80)
        report.append('')
        for finding in other_findings:
            report.append(_format_finding(finding))
            report.append('')

    report.append('SUMMARY:')
    report.append('─' * 80)
    report.append(f'Total violations: {len(violations)} ({len(high_violations)} HIGH, {len([f for f in violations if f["severity"] == "MEDIUM"])} MEDIUM)')
    report.append(f'Total findings: {len(other_findings)} (0 HIGH, {len(medium_findings)} MEDIUM, {len(low_findings)} LOW)')
    report.append(f'Gate status: {"FAIL" if violations else "PASS"} {"❌" if violations else "✅"}')
    report.append('')

    if violations:
        report.append('To apply Tier 1 auto-fixes:')
        report.append('  python .claude/skills/workspace-cleanup/scripts/cleanup_runner.py --tier safe')
        report.append('')

    report.append('To see all findings in JSON:')
    report.append('  python .claude/skills/workspace-audit/scripts/audit_runner.py --json')
    report.append('')
    report.append('=' * 80)

    return '\n'.join(report)


def _format_finding(finding: dict) -> str:
    """Format a single finding."""
    lines = []
    msg = f"[{finding['rule_id']}] {finding['message']}"
    lines.append(msg)

    if finding['file']:
        lines.append(f"  File: {finding['file']}", )
        if finding['line']:
            lines[-1] += f":{finding['line']}"

    lines.append(f"  Severity: {finding['severity']} | Fix Tier: Tier {finding['fix_tier']}")

    if finding['detail']:
        lines.append(f"  {finding['detail']}")

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
