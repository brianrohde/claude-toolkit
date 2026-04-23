# Module Investigation Checklist

Use this checklist when investigating each module in a repository.

## Repository Identification

- [ ] Repository name: `___________`
- [ ] Repository URL/Path: `___________`
- [ ] Purpose (1-2 sentences): `___________`
- [ ] Language(s): `___________`
- [ ] License: `___________`

## Directory Structure

- [ ] Mapped top-level directories (src/, lib/, plugin/, etc.)
- [ ] Identified main entry points
- [ ] Found configuration files (.json, .yaml, .toml, .env)
- [ ] Identified test directory structure
- [ ] Found documentation (CLAUDE.md, README.md, architecture diagrams)

## Module: `[Module Name]`

### Basic Info

- [ ] **Purpose:** What problem does this module solve?
  ```
  Answer: ___________
  ```

- [ ] **Location in repo:** 
  ```
  Primary path: ___________
  Related files: ___________
  ```

- [ ] **Dependencies:** What does this module require?
  ```
  External packages: ___________
  Runtimes (Node/Python/Rust/etc): ___________
  System packages: ___________
  Ports/daemons: ___________
  Databases: ___________
  ```

### Integration Analysis

- [ ] **Independence:** Can this be used alone or does it require the full system?
  ```
  Answer: ___________
  ```

- [ ] **Setup cost estimate:**
  ```
  Copy/install time: ___ minutes
  Configuration: ___ minutes
  Testing: ___ minutes
  Total: ___ minutes
  ```

- [ ] **Maintenance burden:**
  ```
  Actively maintained? ___________
  Rapidly evolving? ___________
  API stability? ___________
  ```

- [ ] **Learning curve:**
  ```
  Complexity: Low / Medium / High
  Documentation quality: ___________
  Examples available? ___________
  ```

### Current Project Alignment

- [ ] **Problem it solves:** Does your project have this problem?
  ```
  Current pain point: ___________
  How this solves it: ___________
  ```

- [ ] **Integration friction:** How much existing code must change?
  ```
  Files affected: ___________
  Breaking changes needed? ___________
  Refactor effort: ___________
  ```

- [ ] **Cross-project value:** Could other projects benefit?
  ```
  Projects that could use this: ___________
  Pattern transferability: ___________
  ```

### Key Code Examples

- [ ] **Sample implementation:** Read main handler/entry point
  ```
  File: ___________
  Key functions: ___________
  Architecture pattern: ___________
  ```

- [ ] **Configuration example:** How is it configured?
  ```
  Config file: ___________
  Environment variables: ___________
  Runtime flags: ___________
  ```

- [ ] **Error handling:** How does it fail gracefully?
  ```
  Error patterns observed: ___________
  Logging strategy: ___________
  Recovery mechanism: ___________
  ```

### Integration Plan (If Applicable)

- [ ] **Copy/adapt:** Which files to copy?
  ```
  Source files: ___________
  Modifications needed: ___________
  ```

- [ ] **Testing strategy:** How to verify it works?
  ```
  Unit tests: ___________
  Integration tests: ___________
  Test data: ___________
  ```

- [ ] **Blockers/risks:**
  ```
  Known issues: ___________
  Incompatibilities: ___________
  Mitigation: ___________
  ```

## Relevance Assessment

**Relevance Score:** ⭐⭐⭐⭐⭐ (1-5 stars)

- ⭐⭐⭐⭐⭐ = Must integrate immediately
- ⭐⭐⭐⭐ = High priority, integrate soon
- ⭐⭐⭐ = Medium priority, integrate if time allows
- ⭐⭐ = Low priority, nice-to-have
- ⭐ = Reference only, don't integrate

**Justification:**
```
___________
```

## Notes

```
Additional observations, questions, or follow-up research:

___________
```

---

**Completed:** [Date] | **Reviewer:** [Name]
