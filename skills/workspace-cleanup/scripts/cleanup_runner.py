"""
Cleanup runner: reads audit findings, dispatches fixes by tier, prompts for approval.
"""
import argparse
import json
import sys
from pathlib import Path

import fixers_safe
import fixers_medium


def main():
    parser = argparse.ArgumentParser(description='Workspace cleanup runner')
    parser.add_argument('--findings', type=Path, help='Findings JSON file (default: run audit)')
    parser.add_argument('--tier', choices=['safe', 'medium', 'all'], default='all',
                        help='Which tier to apply (default: all)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without applying')
    parser.add_argument('--log', type=Path, help='Log file for changes')
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository root')

    args = parser.parse_args()
    root = args.root.resolve()

    # Load findings
    if args.findings:
        findings = json.loads(args.findings.read_text(encoding='utf-8'))
    else:
        # Run audit to generate findings
        import subprocess
        result = subprocess.run(
            [sys.executable, '.claude/skills/workspace-audit/scripts/audit_runner.py',
             '--root', str(root), '--json'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f'Audit failed: {result.stderr}')
            sys.exit(1)
        findings = json.loads(result.stdout)

    # Filter findings by tier
    tier_findings = {
        'safe': [f for f in findings if f.get('fix_tier') == 1],
        'medium': [f for f in findings if f.get('fix_tier') == 2],
    }

    results = []

    if args.tier in ['safe', 'all'] and tier_findings['safe']:
        print(f'\nTier 1 (Safe Auto-Fix) - {len(tier_findings["safe"])} findings:')
        print('─' * 60)
        for f in tier_findings['safe']:
            print(f"  [{f['rule_id']}] {f['message']}")

        if not args.dry_run:
            response = input('\nApply all Tier 1 fixes? [y/N] ').strip().lower()
            if response != 'y':
                print('Skipped Tier 1 fixes.')
            else:
                results.append(fixers_safe.apply_tier1_fixes(root, tier_findings['safe'], args.dry_run))
                print('✅ Tier 1 fixes applied.')
        else:
            print('\n[DRY-RUN] Tier 1 fixes would be applied.')

    if args.tier in ['medium', 'all'] and tier_findings['medium']:
        print(f'\nTier 2 (Medium-Impact) - {len(tier_findings["medium"])} findings:')
        print('─' * 60)

        suggestions = fixers_medium.apply_tier2_suggestions(root, tier_findings['medium'])

        for sugg in suggestions:
            if sugg.get('error'):
                print(f"  Error: {sugg['error']}")
                continue

            if 'suggestions' in sugg:
                for s in sugg['suggestions']:
                    print(f"  [{sugg['rule_id']}] {s['message']}")
                    print(f"    Action: {s['action']}")
                    print(f"    Impact: {s['impact']}")

            if 'actions' in sugg:
                for a in sugg['actions']:
                    print(f"  [{sugg['rule_id']}] {a.get('message', a.get('action'))}")

        print('\nTier 2 fixes require manual review. See fix-registry.md for details.')

    # Log results if requested
    if args.log:
        with open(args.log, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    print('\nCleanup complete.')


if __name__ == '__main__':
    main()
