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

_Empty for now._

| Rule | Purpose |
|---|---|
| _(none yet)_ | |
