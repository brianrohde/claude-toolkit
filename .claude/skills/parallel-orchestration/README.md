# parallel-orchestration

**Tier**: beta

## Purpose

Pattern for running 2-5 subagents in parallel and synthesizing results. Saves ~50% wall time vs sequential. Use when tasks are independent (code review + refactor + test, or skill creation across multiple domains); avoid when agents depend on each other's output.

## When to use

- Multi-agent tasks that are independent.
- Time-sensitive workflows where wall-clock matters.

## When NOT to use

- Single-agent tasks (just invoke the skill directly).
- Sequential pipelines where B consumes A's output.

## Related skills

- `claude-api` -- underlying SDK patterns for parallel tool use.

## Provenance

Promoted from `pta-cbp-parser/.claude/skills/parallel-orchestration/` on 2026-04-23.
