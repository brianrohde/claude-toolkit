# checkpoint

**Tier**: beta (newly authored 2026-04-22)

## Purpose

End-of-session aggregator. One trigger runs the full wrap-up sequence:

1. `/docs-update-all` -- refresh docs.
2. `/plan-update-all` -- log plan outcomes.
3. `/git-draft-commit` -- draft commit message.
4. `/git-push` -- stage, commit, push.

For users tired of typing the four triggers in sequence at every session end.

## Trigger

`/checkpoint`

Optional flags: `--skip-docs`, `--skip-plan`, `--dry-run`.

## Installation

```
cp -r checkpoint/ <project>/.claude/skills/
```

Or via the toolkit installer:
```
python ~/claude-toolkit/scripts/install.py <project> checkpoint
```

(`checkpoint` is part of the `foundational` group, so any group install also installs it.)

## Dependencies

Requires the four child skills to be available in the project (or globally for `/git-push`):
- `docs-update-all`, `plan-update-all`, `git-draft-commit` -- toolkit foundational.
- `git-push` -- typically a global skill.

If a child skill is missing, the chain halts at that step and the error message points at `/claude-toolkit-pull <name>` to install.

## Provenance

Authored on 2026-04-22 in pta-cbp-parser as a session-wrap-up aggregator. Promoted to toolkit on the same day.
