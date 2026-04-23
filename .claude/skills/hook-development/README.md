# hook-development

**Tier**: beta

## Purpose

Reference guide for authoring Claude Code hooks: event types (PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification), the prompt-based hooks API, `${CLAUDE_PLUGIN_ROOT}` usage, validation patterns, and dangerous-command blocking.

## When to use

- Creating a new hook for a project.
- Debugging why an existing hook isn't firing or isn't receiving the expected payload.
- Deciding which hook event matches a desired automation.

## Related skills

- `command-development` -- for slash commands (skills), not hooks.
- `skill-creator` -- for authoring skills.

## Provenance

Promoted from `pta-cbp-parser/.claude/skills/hook-development/` on 2026-04-23.
