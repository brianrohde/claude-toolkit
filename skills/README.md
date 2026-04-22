# Skills

Reusable Claude Code skills. A skill bundles a `SKILL.md` (instructions Claude reads) with an optional handler script.

## Layout per skill

```
skills/<skill_name>/
├── SKILL.md         Instructions Claude follows when the skill is invoked
├── handler.py       (optional) Executable logic
└── README.md        Purpose, trigger phrases, dependencies, install notes
```

## Installation

Skills can live globally (`~/.claude/skills/`) or per-project (`<project>/.claude/skills/`). To install:

1. Copy the folder to the chosen `skills/` directory.
2. Restart the Claude Code session so the skill is discovered.

## Notes

- See memory entry `claude_code_skill_architecture.md`: `.agents/skills/` are parallelizable; `.claude/skills/` are synchronous.
- Toolkit skills use plain names. The `G-S-*` prefix is reserved for the two genuinely global skills (`g-s-skill-creator`, `g-s-find-skills`) that remain in `~/.claude/skills/` for cross-project meta-tooling.

## Available skills

See the [root README's component index](../README.md#component-index) for the canonical list with descriptions.

Quick categories:
- **Workspace hygiene**: `workspace-audit`, `workspace-cleanup`, `workspace-enforce`, `root-directory-hygiene`
- **Git workflow**: `git-commit`, `git-draft-commit`, `git-using-worktrees`, `git-worktree-merge`
- **Standup**: `standup-init`, `standup-log`, `standup-prep`, `standup-finalize`
- **Plans + docs**: `plan-update-all`, `docs-update-all`, `errors-log`
- **Toolkit meta**: `claude-toolkit-pull`, `claude-toolkit-push`, `claude-toolkit-suggestion`, `claude-toolkit-diff`
- **Testing**: `test-codebase-integrity`, `webapp-testing`, `react-testing-patterns`
- **Web/dev**: `deploy-to-vercel`, `vercel-cli-with-tokens`, `vercel-composition-patterns`, `vercel-react-best-practices`, `vercel-react-native-skills`, `vercel-react-view-transitions`, `typescript-advanced-types`, `web-design-guidelines`
