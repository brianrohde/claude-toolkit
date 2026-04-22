# claude-toolkit

Personal library of reusable Claude Code components: hooks, skills, rules, agents, and helper scripts. Curated, versioned, and project-agnostic.

## Philosophy

- **Library is a source, not a sync target.** Components flow library → project via copy. Projects own their copy and may diverge.
- **Promotion is explicit.** When a project-local improvement proves reusable, it's manually promoted back to the library. No auto-sync.
- **Reuse earns inclusion.** Components migrate in *as they're reused*, not pre-emptively.

## Layout

```
claude-toolkit/
├── hooks/      Claude Code hook scripts (PreToolUse, UserPromptSubmit, etc.)
├── skills/     Reusable skills (SKILL.md + handler scripts)
├── rules/      Project-agnostic rule docs (workflow patterns, conventions)
├── agents/     Custom agent definitions
├── plans/      Plan/outcome scaffolding for project use (plan_files/, outcome_files/)
├── docs/       Toolkit documentation (guides/installing-components.md, etc.)
└── scripts/    Helpers (promotion diff, install, etc.)
```

For step-by-step install instructions, see [docs/guides/installing-components.md](docs/guides/installing-components.md).

Each component lives in its own subfolder containing:
- The component file(s)
- `README.md` — what it does, when to use, configuration, dependencies
- `settings.snippet.json` (for hooks) — paste-ready registration block

## Maturity tiers

Tag each component in its README:

| Tier | Meaning |
|---|---|
| **stable** | Battle-tested across 2+ projects |
| **beta** | Works, but only used in 1 project so far |
| **experimental** | Sketch/prototype, may break |

Don't reach for `experimental` components in a new project without reviewing them.

## Workflows

### Installing a component into a new project

1. Copy the component folder into the project's `.claude/` (e.g. `cp -r ~/claude-toolkit/hooks/branch_guard <project>/.claude/hooks/`).
2. If it's a hook, paste the `settings.snippet.json` block into the project's `.claude/settings.json`.
3. Commit it to the project's repo. The project now owns this copy.

### Promoting a project-local improvement back to the library

1. Run `scripts/promote.sh <project-path> <component-name>` to diff the project's copy against the library's copy.
2. Decide what changes are general vs. project-specific.
3. Apply the general changes to the library copy, commit, and push.

### Starting a new component

1. Build it inside whichever project needs it first.
2. Once it works, copy it into the library, write a README, tag it `beta`.
3. After it's reused successfully in a second project, bump to `stable`.

## Component index

| Component | Type | Tier | Description |
|---|---|---|---|
| [branch_guard](hooks/branch_guard/) | hook | beta | UserPromptSubmit hook: suggests a feature branch when on `main`, confirms branch otherwise. |
| [check_file_edit](hooks/check_file_edit/) | hook | beta | PreToolUse hook: blocks Edit/Write on OneDrive .py files (EEXIST/byte-corruption guard) and any .env file. |
| [claude-toolkit-diff](skills/claude-toolkit-diff/) | skill | beta | Compare overlapping components between project and toolkit; report which side is newer/diverged. Read-only. |
| [claude-toolkit-new-skill](skills/claude-toolkit-new-skill/) | skill | beta | First-time promotion of a project skill to the toolkit; scrubs project-specific refs, commits, pushes. |
| [claude-toolkit-suggestion](skills/claude-toolkit-suggestion/) | skill | beta | Recommend toolkit components that fit the current project's tech stack. Read-only. |
| [claude-toolkit-update](skills/claude-toolkit-update/) | skill | beta | Pull canonical version of a toolkit component into a project; opposite of claude-toolkit-new-skill. |
| [deploy-to-vercel](skills/deploy-to-vercel/) | skill | beta | Deploy applications and websites to Vercel via CLI. |
| [docs-update-all](skills/docs-update-all/) | skill | beta | Update all documentation in a session sweep. |
| [errors-log](skills/errors-log/) | skill | beta | Scan session for tool failures and append to `.claude/logs/tooling-issues.jsonl`. |
| [git-commit](skills/git-commit/) | skill | beta | Execute a git commit from an approved draft message. |
| [git-draft-commit](skills/git-draft-commit/) | skill | beta | Generate a ready-to-paste git commit message from the current session. |
| [git-using-worktrees](skills/git-using-worktrees/) | skill | beta | Create a git worktree under `.cc/worktrees/` for isolated parallel sessions. |
| [git-worktree-merge](skills/git-worktree-merge/) | skill | beta | Review and merge a worktree branch back to main. |
| [plan-update-all](skills/plan-update-all/) | skill | beta | Log and finalize completed plans (relocate, rename, write outcome file). |
| [react-testing-patterns](skills/react-testing-patterns/) | skill | beta | React testing patterns and best practices. |
| [root-directory-hygiene](skills/root-directory-hygiene/) | skill | beta | Keep the repo root tidy; enforce documentation folder placement. |
| [skill-update-workflow](skills/skill-update-workflow/) | skill | beta | Promote project-local skill changes back to the toolkit (diff + cross-ref validator). |
| [standup-finalize](skills/standup-finalize/) | skill | beta | Clean and finalize the standup draft for supervisor delivery. |
| [standup-init](skills/standup-init/) | skill | beta | Initialize a new standup draft for the next supervisor meeting. |
| [standup-log](skills/standup-log/) | skill | beta | Append a timestamped entry to the active standup draft. |
| [standup-prep](skills/standup-prep/) | skill | beta | Prepare an outgoing standup from the draft. |
| [test-codebase-integrity](skills/test-codebase-integrity/) | skill | beta | Run codebase integrity checks (imports, smoke tests, lint). |
| [typescript-advanced-types](skills/typescript-advanced-types/) | skill | beta | TypeScript advanced type system reference. |
| [vercel-cli-with-tokens](skills/vercel-cli-with-tokens/) | skill | beta | Vercel CLI with token-based authentication. |
| [vercel-composition-patterns](skills/vercel-composition-patterns/) | skill | beta | React composition patterns that scale. |
| [vercel-react-best-practices](skills/vercel-react-best-practices/) | skill | beta | React/Next.js performance optimization guidelines from Vercel Engineering. |
| [vercel-react-native-skills](skills/vercel-react-native-skills/) | skill | beta | React Native and Expo best practices. |
| [vercel-react-view-transitions](skills/vercel-react-view-transitions/) | skill | beta | React View Transitions API guide. |
| [web-design-guidelines](skills/web-design-guidelines/) | skill | beta | Review UI code for Web Interface Guidelines compliance. |
| [webapp-testing](skills/webapp-testing/) | skill | beta | Test local web apps with Playwright. |
| [workspace-audit](skills/workspace-audit/) | skill | beta | Read-only repository health auditor (Claude hygiene, dependencies, source quality). |
| [workspace-cleanup](skills/workspace-cleanup/) | skill | beta | Repository fixer that applies tiered fixes to audit findings. |
| [workspace-enforce](skills/workspace-enforce/) | skill | beta | CI gate for workspace health; blocks merge on unwaived violations. |
| [context-token-optimization](rules/context-token-optimization/) | rule | beta | Model tier selection, tool optimization, memory persistence guidance. |
| [one-off-execution](rules/one-off-execution/) | rule | beta | Trigger phrases execute once unless an interval is specified. |
| [repository-map-reference](rules/repository-map-reference/) | rule | beta | Auto-loads `docs/repository-map.md` for codebase questions. |
| [tooling-issues-workflow](rules/tooling-issues-workflow/) | rule | beta | JSONL-as-source-of-truth workflow for `.claude/logs/tooling-issues.jsonl`. |
| [trigger-branch-strategy](rules/trigger-branch-strategy/) | rule | beta | Branch-strategy trigger phrases and policy reference. |
| [trigger-docs-workflow](rules/trigger-docs-workflow/) | rule | beta | `/docs-update-all` trigger and update priority order. |
| [trigger-git-commit-workflow](rules/trigger-git-commit-workflow/) | rule | beta | `/draft_commit` trigger algorithm and commit message format. |
| [trigger-plan-workflow](rules/trigger-plan-workflow/) | rule | beta | Plan file mirroring + outcome documentation workflow. |

## Cross-machine sync

This repo is the source of truth. Push to GitHub for backup and to sync across machines. Do **not** put it in OneDrive — OneDrive's encoding/CRLF/EEXIST quirks have caused enough pain in dependent projects (see `pta-cbp-parser/docs/tooling-issues.md`).
