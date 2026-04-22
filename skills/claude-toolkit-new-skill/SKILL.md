---
name: claude-toolkit-new-skill
description: This skill should be used when the user asks to "promote a project skill to toolkit", "/claude-toolkit-new-skill", "add this skill to the library", or names a project skill (e.g., "/claude-toolkit-new-skill my-new-skill"). Copies a project-local skill (or hook/rule) into the claude-toolkit library as a NEW component, scrubs project-specific references, writes a generic README, commits, and pushes. Use for first-time promotion. For updating an EXISTING toolkit component, use /skill-update-workflow instead.
version: 0.1.0
---

# claude-toolkit-new-skill

## Purpose

Promote a project-local component to the toolkit as a brand-new entry. This is the **project -> library** direction for first-time additions.

Sister skills:
- `/skill-update-workflow` -- promote changes to a component that ALREADY exists in the toolkit (diff + lift).
- `/claude-toolkit-update` -- pull a toolkit component into a project (the reverse direction).
- `/claude-toolkit-suggestion` -- discover existing toolkit components before reinventing.

## Trigger

`/claude-toolkit-new-skill [optional component-name]`

Examples:
- `/claude-toolkit-new-skill` -> ask the user which project component to promote.
- `/claude-toolkit-new-skill my-cool-skill` -> promote that skill specifically.
- `/claude-toolkit-new-skill some-hook` -> works for hooks too (auto-detects component type by location).

## Algorithm

### Step 0: Reuse check
Before promoting, run a quick search of the toolkit's existing skills/hooks/rules for similar functionality. If a match is found:
- Halt and recommend `/skill-update-workflow` instead (this is an update, not a new entry).
- If genuinely different, proceed -- but document the distinction in the new component's README.

### Step 1: Locate the toolkit
Standard resolution (env var -> default paths -> ask).

### Step 2: Resolve the source component
- If user passed a name, find it in `<project>/.claude/{skills,hooks,rules}/<name>/`.
- If no name, list all project components NOT already in the toolkit and ask which to promote.
- Auto-detect type from location (skills / hooks / rules).

### Step 3: Generality audit (critical)
Scan the source for project-specific references that must be scrubbed before the toolkit copy. Flag:

- **Project name / domain**: e.g., "thesis", "research", "pta-cbp", "CMT_Codebase", "master thesis", "ruling letter", "tariff", "preferential trade".
- **Project-specific paths**: hard-coded absolute paths to project files; project-specific subdirs (`docs/repository-map.md` references that assume the project's structure).
- **Project-specific vocabulary**: domain terms (e.g., "MSc thesis", "supervisor meeting", "CBS", "regex iteration").
- **Hard-coded user paths**: `C:/Users/brian/...`, `/home/<user>/...`, OneDrive paths.
- **Project-specific tool names**: script names that exist only in the source project.
- **Stale slash-refs**: refs to skills not in the toolkit's canonical name list.

For each flagged item:
- Show the user the line and ask: rewrite generically / drop / keep (rare -- requires justification).

### Step 4: Generate generic version
Apply the rewrites:
- Replace project-specific terms with generic equivalents (e.g., "PTA project" -> "the project", "supervisor" -> "stakeholder", "thesis" -> "document").
- Replace hard-coded paths with placeholders (`<project>/...`, `~/...`).
- Update YAML `description:` field to be project-agnostic.
- Update slash-refs to canonical toolkit names.

### Step 5: Copy to toolkit
Use the byte-level temp-script pattern:
1. Write a temp `.py` script.
2. Copy source tree to `<toolkit>/<type>/<name>/`.
3. After copy, apply the rewrites from Step 4 to the destination files (not the source -- never modify the project copy here).

### Step 6: Write a generic README
Create `<toolkit>/<type>/<name>/README.md` with:
- Title.
- Tier: `beta` (new entry, only proven in 1 project).
- Purpose (2-4 lines, generic).
- Installation instructions (copy command pointing into `<project>/.claude/`).
- Provenance (where it came from, date, what was scrubbed).

### Step 7: Update toolkit indexes
Add a row to:
- Root `claude-toolkit/README.md` component index.
- `<toolkit>/<type>/README.md` listing for that type.

### Step 8: Commit and push
In the toolkit directory:
- `git add <type>/<name>/ README.md <type>/README.md`
- Commit message: `feat(<type>): add <name> -- promoted from <project>`.
- `git push origin main`.

### Step 9: Suggest follow-up
Tell the user:
- The skill is now in the toolkit at tier `beta`.
- To bump to `stable`, install it in a second project successfully first.
- Other projects can install it via `/claude-toolkit-update <name>`.

## Output

Report:
- Source component path
- Destination toolkit path
- Generality rewrites applied (with line counts)
- Files written
- Toolkit commit hash + push status
- Tier assigned (beta)
- Suggested next steps

## Failure modes

- **Component name collides with existing toolkit entry**: halt; recommend `/skill-update-workflow` instead.
- **Project-specific references the user wants to keep**: warn that the toolkit copy will not be project-agnostic; require explicit user override.
- **Toolkit not found / not a git repo**: ask user; do not initialize one without permission.
- **Push fails (no auth, no remote)**: leave the commit local; tell the user to push manually.
