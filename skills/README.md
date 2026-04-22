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
- Existing global skills are prefixed `G-S-*` in `~/.claude/skills/`. Library copies should drop the prefix and use plain names — the prefix is a runtime location convention, not part of the skill itself.
