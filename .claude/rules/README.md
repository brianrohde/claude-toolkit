# Rules

Project-agnostic rule documents — workflow patterns, conventions, and guidance Claude should follow. These are markdown files referenced from a project's `CLAUDE.md` or auto-loaded via `.claude/rules/`.

## Layout per rule

```
rules/<rule_name>/
├── <rule_name>.md       The rule content
└── README.md            When to use, what it changes about Claude's behavior
```

For single-file rules, you can skip the subfolder and place `<rule_name>.md` directly in `rules/` — but add a one-line entry to the index in this README.

## Installation

1. Copy the rule file into the project's `.claude/rules/` folder.
2. Reference it from `CLAUDE.md` if it should be explicitly loaded, or rely on auto-loading if the project's setup supports it.

## Index

| Rule | Tier | Purpose |
|---|---|---|
| [context-token-optimization](context-token-optimization/) | beta | Model tier selection, tool optimization, memory persistence guidance. |
| [one-off-execution](one-off-execution/) | beta | Trigger phrases execute once unless an interval is specified. |
| [repository-map-reference](repository-map-reference/) | beta | Auto-loads `docs/repository-map.md` for codebase questions. |
| [tooling-issues-workflow](tooling-issues-workflow/) | beta | JSONL-as-source-of-truth workflow for `.claude/logs/tooling-issues.jsonl`. |
| [trigger-branch-strategy](trigger-branch-strategy/) | beta | Branch-strategy trigger phrases and policy reference. |
| [trigger-docs-workflow](trigger-docs-workflow/) | beta | `/docs-update-all` trigger and update priority order. |
| [trigger-git-commit-workflow](trigger-git-commit-workflow/) | beta | `/draft_commit` trigger algorithm and commit message format. |
| [trigger-plan-workflow](trigger-plan-workflow/) | beta | Plan file mirroring + outcome documentation workflow. |
