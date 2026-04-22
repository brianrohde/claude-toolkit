# Installing components from claude-toolkit into a project

The toolkit is the source of truth. Projects own per-project copies. This is the install workflow.

## General principle

Components flow **library -> project** via copy. Never symlink, never auto-sync. The project commits its copy and may diverge.

## Hooks

```
cp claude-toolkit/.claude/hooks/<hook-name>/<hook-name>.py <project>/.claude/hooks/<hook-name>.py
```

Then merge `<hook-name>/settings.snippet.json` into `<project>/.claude/settings.json` (the snippet uses a **relative path** -- never replace it with an absolute path).

Commit both the script and the settings.json change.

## Skills

```
cp -r claude-toolkit/.claude/skills/<skill-name>/ <project>/.claude/skills/
```

Confirm the YAML `name:` field inside `SKILL.md` matches the folder name. (All toolkit skills should already be correct.)

Commit the folder.

## Rules

```
cp claude-toolkit/.claude/rules/<rule-name>/<rule-name>.md <project>/.claude/rules/<rule-name>.md
```

Some rules auto-load (referenced from `CLAUDE.md`); others are referenced by trigger phrase. Check the rule's README for activation pattern.

## After installing

1. Restart your Claude Code session in the project (so new hooks/skills register).
2. Smoke-test the component (run the trigger, fire the hook, check the rule loads).

## When to promote project changes back to toolkit

When you edit a project copy and the change feels reusable, run `/skill-update-workflow <skill-name>` from the project. It diffs, validates, and walks you through promoting general changes back to `claude-toolkit/`.

## Critical rule

**Never hard-code an absolute path to a project file in `~/.claude/settings.json`.** That bug class is what created this toolkit -- a global hook with an absolute path to a project file broke every Claude Code session in every project once the file moved. Always per-project, always relative.
