#!/usr/bin/env python3
"""
Enhanced Skill Audit Handler with prefix handling and categorization
"""

import json
import os
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import sys

class SkillAuditor:
    """Enhanced auditor with G-S/G-C prefix handling and skill categorization"""

    # Category mapping by skill name patterns
    CATEGORY_PATTERNS = {
        'Documentation': [
            'standup', 'commit', 'plan', 'docs', 'log', 'notes', 'memo', 'draft', 'prepare',
            'finalize', 'review'
        ],
        'Data Analysis': [
            'polars', 'pandas', 'numpy', 'scipy', 'statistical', 'analysis', 'exploratory',
            'matplotlib', 'seaborn', 'shap', 'scikit', 'statsmodels', 'pymc'
        ],
        'Research/Academic': [
            'academic', 'paper', 'literature', 'citation', 'apa', 'thesis', 'hypothesis',
            'research', 'scholar', 'grants', 'notebooklm'
        ],
        'Visualization': [
            'visualization', 'matplotlib', 'seaborn', 'plot', 'chart', 'graph', 'networkx'
        ],
        'Development': [
            'git', 'push', 'repo', 'integration', 'test', 'codebase', 'hook', 'deploy',
            'vercel', 'command', 'development'
        ],
        'Skills Management': [
            'skill', 'audit', 'find', 'creator', 'development'
        ],
        'Scientific': [
            'scientific', 'critical', 'thinking', 'writing', 'evaluation'
        ],
        'Data Processing': [
            'pipeline', 'aeon', 'processing', 'extraction', 'field', 'inspector'
        ],
        'UI/Web': [
            'react', 'typescript', 'web', 'design', 'webapp', 'testing', 'view', 'transition',
            'composition'
        ],
        'Utilities': [
            'parallel', 'orchestration', 'deep', 'research'
        ]
    }

    def __init__(self):
        self.global_skills: Dict[str, dict] = {}
        self.project_skills: Dict[str, Dict[str, dict]] = {}
        self.global_paths = [
            Path.home() / '.claude' / 'skills',
            Path.home() / '.agents' / 'skills'
        ]
        self.similarity_threshold = 0.75

    def normalize_name(self, name: str) -> str:
        """Remove G-S-, G-C-, S-, C- prefixes from skill name"""
        return re.sub(r'^(?:G-)?[SC]-', '', name, flags=re.IGNORECASE)

    def extract_scope_and_type(self, name: str) -> Tuple[str, str]:
        """Extract scope (GLOBAL/PROJECT) and type (SKILL/COMMAND) from name"""
        scope = "GLOBAL" if name.upper().startswith("G-") else "PROJECT"
        skill_type = "COMMAND" if "-C-" in name.upper() else "SKILL"
        return scope, skill_type

    def categorize_skill(self, name: str) -> str:
        """Categorize skill based on name patterns"""
        normalized = self.normalize_name(name).lower()

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in normalized:
                    return category

        return "Uncategorized"

    def discover_skills(self, skill_dir: Path) -> Dict[str, dict]:
        """Discover all skills in a directory and extract metadata"""
        skills = {}
        if not skill_dir.exists():
            return skills

        for skill_path in skill_dir.iterdir():
            if not skill_path.is_dir():
                continue

            skill_md = skill_path / 'SKILL.md'
            if not skill_md.exists():
                continue

            metadata = self._extract_metadata(skill_md, skill_path)
            if metadata:
                skills[metadata['name']] = metadata

        return skills

    def _extract_metadata(self, skill_md: Path, skill_path: Path) -> Optional[dict]:
        """Extract metadata from SKILL.md frontmatter and file"""
        try:
            content = skill_md.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None

        # Parse YAML frontmatter
        frontmatter = {}
        if content.startswith('---'):
            match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if match:
                fm_text = match.group(1)
                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')

        name = frontmatter.get('name', skill_path.name)
        description = frontmatter.get('description', '')

        triggers = self._extract_triggers(content)
        dependencies = self._check_dependencies(skill_path)

        stat = skill_md.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        scope, skill_type = self.extract_scope_and_type(name)
        category = self.categorize_skill(name)

        return {
            'name': name,
            'normalized_name': self.normalize_name(name),
            'description': description.strip(),
            'path': str(skill_path),
            'triggers': triggers,
            'dependencies': dependencies,
            'modified': modified,
            'scope': scope,
            'type': skill_type,
            'category': category
        }

    def _extract_triggers(self, content: str) -> List[str]:
        """Extract trigger keywords/patterns from skill description"""
        triggers = []
        trigger_patterns = [
            r'when .*?(?:asks|says|requests|wants|calls)',
            r'trigger[s]?:?\s*(.+?)(?:\n|$)',
            r'use this.*?when',
        ]

        for pattern in trigger_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            triggers.extend(matches)

        return list(set(triggers))[:5]

    def _check_dependencies(self, skill_path: Path) -> Dict[str, List[str]]:
        """Check for external dependencies (settings.json, env vars, etc.)"""
        deps = {'hooks': [], 'env_vars': [], 'external_tools': []}

        settings_path = skill_path.parent.parent / 'settings.json'
        if settings_path.exists():
            try:
                settings = json.loads(settings_path.read_text())
                if 'hooks' in settings:
                    for hook_type, hook_list in settings['hooks'].items():
                        if isinstance(hook_list, list):
                            for hook in hook_list:
                                if skill_path.name in str(hook):
                                    deps['hooks'].append(hook_type)
            except Exception:
                pass

        skill_md = skill_path / 'SKILL.md'
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding='utf-8', errors='ignore')
                env_refs = re.findall(r'\$([A-Z_][A-Z0-9_]*)', content)
                deps['env_vars'] = list(set(env_refs))
            except Exception:
                pass

        return {k: v for k, v in deps.items() if v}

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two description texts"""
        if not text1 or not text2:
            return 0.0

        text1 = ' '.join(text1.lower().split())[:200]
        text2 = ' '.join(text2.lower().split())[:200]

        return SequenceMatcher(None, text1, text2).ratio()

    def find_duplicates(self, all_skills: Dict[str, dict]) -> List[Tuple[str, str, float]]:
        """Find potential duplicate skills by normalized name or description similarity"""
        duplicates = []
        skill_names = list(all_skills.keys())

        for i, name1 in enumerate(skill_names):
            for name2 in skill_names[i+1:]:
                if name1 == name2:
                    continue

                # Check for prefix variations (G-S-X vs X)
                norm1 = all_skills[name1]['normalized_name']
                norm2 = all_skills[name2]['normalized_name']

                if norm1 == norm2:
                    similarity = 1.0
                    duplicates.append((name1, name2, similarity))
                    continue

                # Check by description similarity
                desc1 = all_skills[name1].get('description', '')
                desc2 = all_skills[name2].get('description', '')

                similarity = self.calculate_similarity(desc1, desc2)

                if similarity >= self.similarity_threshold:
                    duplicates.append((name1, name2, similarity))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)

    def audit_global(self) -> None:
        """Audit global skill directories"""
        for path in self.global_paths:
            self.global_skills.update(self.discover_skills(path))

    def audit_projects(self, project_paths: List[str]) -> None:
        """Audit skills in specified project directories"""
        for proj_path_str in project_paths:
            proj_path = Path(proj_path_str).expanduser()
            if not proj_path.exists():
                print(f"Warning: Project path not found: {proj_path_str}")
                continue

            proj_name = proj_path.name
            self.project_skills[proj_name] = {}

            for skill_dir_name in ['skills', '.agents/skills']:
                skill_dir = proj_path / '.claude' / skill_dir_name
                if skill_dir_name.startswith('.'):
                    skill_dir = proj_path / skill_dir_name

                self.project_skills[proj_name].update(self.discover_skills(skill_dir))

    def generate_gaps_table(self) -> str:
        """Generate gaps table with category and normalized names"""
        output = []
        output.append("\n## Skill Gaps by Location\n")

        # Group skills by normalized name to detect prefix conflicts
        skill_groups = {}
        all_skill_names = set(self.global_skills.keys())
        for proj_skills in self.project_skills.values():
            all_skill_names.update(proj_skills.keys())

        # Build groups
        for skill_name in all_skill_names:
            if skill_name in self.global_skills:
                skill_data = self.global_skills[skill_name]
            else:
                for proj_skills in self.project_skills.values():
                    if skill_name in proj_skills:
                        skill_data = proj_skills[skill_name]
                        break

            norm_name = skill_data['normalized_name']
            if norm_name not in skill_groups:
                skill_groups[norm_name] = []
            skill_groups[norm_name].append(skill_name)

        if not all_skill_names:
            return "No skills found.\n"

        headers = ['Skill Name', 'Category', 'Scope/Type', 'Locations', 'Gap Status']
        output.append("| " + " | ".join(headers) + " |")
        output.append("|" + "|".join(["---"] * len(headers)) + "|")

        for norm_name in sorted(skill_groups.keys()):
            group = skill_groups[norm_name]

            # Get first skill's metadata for category/type
            representative_skill = group[0]
            if representative_skill in self.global_skills:
                skill_data = self.global_skills[representative_skill]
                category = skill_data['category']
                scope_type = f"{skill_data['scope']}/{skill_data['type']}"
            else:
                for proj_skills in self.project_skills.values():
                    if representative_skill in proj_skills:
                        skill_data = proj_skills[representative_skill]
                        category = skill_data['category']
                        scope_type = f"{skill_data['scope']}/{skill_data['type']}"
                        break

            # Determine locations
            locations = []
            for skill_name in group:
                if skill_name in self.global_skills:
                    locations.append("GLOBAL")
                for proj_name in self.project_skills.keys():
                    if skill_name in self.project_skills[proj_name]:
                        locations.append(proj_name.upper())

            # Determine gap status
            has_global = any(s in self.global_skills for s in group)
            proj_count = len(set(p for s in group for p in self.project_skills.keys()
                                if s in self.project_skills[p]))

            if has_global and proj_count == 0:
                gap_status = "UNUSED_GLOBAL"
            elif not has_global and proj_count >= 2:
                gap_status = "PROMOTE_TO_GLOBAL"
            elif has_global and proj_count < len(self.project_skills):
                gap_status = "SCOPE_CONFLICT"
            elif not has_global and proj_count == 1:
                gap_status = "PROJECT_ONLY"
            else:
                gap_status = "OK"

            # Display group
            display_name = norm_name
            if len(group) > 1:
                display_name += f" ({len(group)} variants)"

            loc_str = ", ".join(sorted(set(locations)))
            if len(loc_str) > 40:
                loc_str = loc_str[:37] + "..."

            output.append(f"| {display_name} | {category} | {scope_type} | {loc_str} | {gap_status} |")

        return "\n".join(output) + "\n"

    def generate_summary(self) -> str:
        """Generate execution summary"""
        output = []
        output.append("\n## Summary\n")

        total_global = len(self.global_skills)
        total_projects = sum(len(skills) for skills in self.project_skills.values())

        # Count unique normalized names
        all_normalized = set()
        for skill in self.global_skills.values():
            all_normalized.add(skill['normalized_name'])
        for proj_skills in self.project_skills.values():
            for skill in proj_skills.values():
                all_normalized.add(skill['normalized_name'])

        output.append(f"- Global skills: {total_global}")
        output.append(f"- Project skills: {total_projects}")
        output.append(f"- Unique skills (normalized): {len(all_normalized)}")
        output.append(f"- Projects analyzed: {len(self.project_skills)}")
        output.append("")

        return "\n".join(output) + "\n"

    def generate_summary_report(self) -> str:
        """Generate concise summary for terminal display"""
        report = []
        report.append("# Skill Audit Summary\n")
        report.append(f"Generated: {datetime.now().isoformat()}\n")

        report.append(self.generate_summary())
        report.append(self.generate_gaps_table())

        all_skills = {**self.global_skills}
        for proj_skills in self.project_skills.values():
            all_skills.update(proj_skills)
        duplicates = self.find_duplicates(all_skills)

        if duplicates:
            report.append(f"\n## Conflicts/Duplicates Detected: {len(duplicates)}\n")
            report.append("Run full report for details on scope conflicts and consolidation.\n")

        return "\n".join(report)

    def generate_full_report(self) -> str:
        """Generate complete audit report"""
        report = []
        report.append("# Skill Audit Report\n")
        report.append(f"Generated: {datetime.now().isoformat()}\n")

        report.append(self.generate_summary())
        report.append(self.generate_gaps_table())

        # Scope conflicts
        all_skills = {**self.global_skills}
        for proj_skills in self.project_skills.values():
            all_skills.update(proj_skills)
        duplicates = self.find_duplicates(all_skills)

        output = []
        output.append("\n## Scope Conflicts & Duplicates\n")

        if not duplicates:
            output.append("No conflicts detected.\n")
        else:
            for skill1, skill2, similarity in duplicates:
                pct = int(similarity * 100)
                output.append(f"- {skill1} <-> {skill2} ({pct}% match)")
                output.append("")

        report.append("\n".join(output) + "\n")

        return "\n".join(report)

    def save_report(self, report: str, output_dir: Optional[str] = None) -> str:
        """Save full report to .claude/logs/skill-audits/"""
        if output_dir is None:
            output_dir = Path.home() / '.claude' / 'logs' / 'skill-audits'
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = output_dir / f'audit_{timestamp}.md'

        report_path.write_text(report, encoding='utf-8')
        return str(report_path)


def main():
    """Main entry point"""
    auditor = SkillAuditor()

    auditor.audit_global()

    project_paths = sys.argv[1:] if len(sys.argv) > 1 else ['.']
    auditor.audit_projects(project_paths)

    # Generate summary for display
    summary = auditor.generate_summary_report()
    print(summary)

    # Generate and save full report
    full_report = auditor.generate_full_report()
    report_path = auditor.save_report(full_report)
    print(f"\nFull report saved to: {report_path}")


if __name__ == '__main__':
    main()
