# Hooks

Claude Code hook scripts. Hooks fire on lifecycle events (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, etc.) and are registered in `.claude/settings.json`.

## Layout per hook

```
hooks/<hook_name>/
├── <hook_name>.py            The script
├── README.md                 Purpose, when to use, config, dependencies
└── settings.snippet.json     Paste-ready registration block for .claude/settings.json
```

## Installation

1. Copy the folder into the target project's `.claude/hooks/`.
2. Open the project's `.claude/settings.json`.
3. Paste the contents of `settings.snippet.json` into the appropriate `hooks` event array.
4. Commit both the script and the settings change to the project's repo.

## Critical rule: relative paths only

Never hard-code absolute paths in the registration command. Always use a path relative to the project root:

```json
"command": "python \".claude/hooks/branch_guard.py\""
```

Hard-coded absolute paths in **global** settings caused real breakage (see PTA project session 2026-04-22) — the global hook fired in projects that didn't have the script.

## Global vs. per-project registration

- **Per-project (default)**: Register in `<project>/.claude/settings.json`. Only fires for that project. Recommended for most hooks.
- **Global**: Register in `~/.claude/settings.json`. Fires for *every* session in *any* directory. Use only for genuinely universal behaviors, and prefer scripts that no-op when irrelevant (e.g., check for a marker file before enforcing).
