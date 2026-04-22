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
└── scripts/    Helpers (promotion diff, install, etc.)
```

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
| [branch_guard](hooks/branch_guard/) | hook | beta | UserPromptSubmit hook: suggests a feature branch when on `main`, confirms branch otherwise. Per-project install with relative path. |

## Cross-machine sync

This repo is the source of truth. Push to GitHub for backup and to sync across machines. Do **not** put it in OneDrive — OneDrive's encoding/CRLF/EEXIST quirks have caused enough pain in dependent projects (see `pta-cbp-parser/docs/tooling-issues.md`).
