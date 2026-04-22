# Root Allowlist

Canonical policy for what belongs — and what does not — at the repository root.

## Required (must be present)

| File | Rationale |
|------|-----------|
| `README.md` | Universal project entry point; GitHub/GitLab surface this automatically |
| `.gitignore` | Version control hygiene; required in virtually all repos |
| Primary manifest (`pyproject.toml` / `package.json` / `Cargo.toml` / `go.mod`) | Packaging tools and dependency managers require root placement |

## Conditionally Allowed (permitted when actually used by the repo)

| File / Pattern | Condition |
|----------------|-----------|
| `CONTRIBUTING.md` | When the project accepts external contributions |
| `CHANGELOG.md` | When maintained as a canonical release record |
| `SECURITY.md` | When a security disclosure process exists |
| `CODE_OF_CONDUCT.md` | When the project has a formal CoC |
| `SUPPORT.md` | When the project has a formal support channel |
| `CODEOWNERS` | When GitHub/GitLab code ownership is enforced |
| `CITATION.cff` | When academic citation is needed |
| `LICENSE` / `LICENSE.md` | When a license file is required |
| `Makefile` | When build/dev targets are driven by make |
| `Dockerfile` / `compose.yaml` / `docker-compose.yml` | When the repo ships containerised workloads |
| `.editorconfig` | When cross-editor formatting consistency is enforced |
| `.pre-commit-config.yaml` | When pre-commit hooks are used |
| `.markdownlint*` / `.markdownlint-cli2.*` | When Markdown linting is configured |
| `mkdocs.yml` / `docusaurus.config.*` / `conf.py` | Docs-site config — required at root by those tools |
| `pnpm-workspace.yaml` / `turbo.json` / `nx.json` | Monorepo workspace config |
| `CLAUDE.md` | Claude Code project instructions (this project's exception) |
| `.claude/` | Claude Code project settings and skills (this project's exception) |
| `.github/` / `.gitlab/` | CI, PR templates, community health files |
| `pyproject.toml` / `setup.cfg` / `setup.py` | Python packaging |
| `requirements*.txt` / `requirements.lock` | Python dependency pinning |
| `poetry.lock` / `uv.lock` / `Pipfile.lock` | Python lockfiles |
| `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | JS/TS lockfiles |
| `tsconfig*.json` / `jsconfig.json` | TypeScript/JavaScript config |
| `eslint.config.*` / `.eslintrc*` / `.prettierrc*` | JS/TS linting and formatting |
| `pytest.ini` / `tox.ini` / `.coveragerc` | Python test config |
| `conftest.py` | Pytest root conftest |
| `CHEATSHEET.md` | Project-specific quick reference (this project's exception) |

## Discouraged (should move to `docs/`)

These files are often created in root for convenience but belong in a `docs/` subfolder.

| Pattern | Recommended destination |
|---------|------------------------|
| `ARCHITECTURE.md` | `docs/explanation/architecture.md` |
| `ROADMAP.md` | `docs/explanation/roadmap.md` |
| `DESIGN.md` | `docs/explanation/design.md` |
| `PLAN.md` / `PLAN_*.md` | `docs/planning/YYYY_MM_DD-plan-name.md` |
| `RUNBOOK.md` | `docs/guides/runbook.md` |
| `MIGRATION*.md` | `docs/planning/YYYY_MM_DD-migration-name.md` |
| `NOTES.md` / `TODO.md` | `docs/notes/YYYY_MM_DD-topic.md` |
| `REPORT.md` / `ANALYSIS.md` | `docs/notes/YYYY_MM_DD-topic.md` |
| `*_SUMMARY.md` / `*_GUIDE.md` | `docs/guides/` or `docs/reference/` |
| `*_HANDOVER.md` / `*HANDOVER*.md` | `docs/handover/YYYY_MM_DD-topic.md` |
| `*INTEGRATION*.md` | `docs/guides/` or `docs/explanation/` |
| `SKILL_ACTIVATION_SUMMARY.md` | `docs/reference/` |
| `ZOTERO_QUICK_REFERENCE.md` | `docs/reference/zotero-quick-reference.md` |

## Forbidden (must not be in root)

| Pattern | Reason |
|---------|--------|
| Temporary notes, scratch files | Root pollution; no canonical purpose |
| AI scratchpad outputs | Not a project entrypoint |
| `*-final.*` / `*-new.*` / `*-copy.*` / `*-v2.*` | Duplicate naming antipattern |
| Exported benchmark artifacts | Not canonical; belongs in `docs/notes/` or `resources/` |
| One-off investigation files | Should be in `docs/notes/` with a date prefix |
| Image dumps (`*.png`, `*.jpg`, `*.svg` with no manifest entry) | Should be in `docs/assets/images/` |
| Backup files (`*.bak`, `*.orig`, `~*`) | Should not be committed |
| Editor swap files (`.*.swp`, `*.tmp`) | Should be in `.gitignore` |

---

## Evaluation Notes

- When classifying, check whether the file is actually consumed by a tool before applying "forbidden". A `Makefile` that exists but contains nothing useful is `discouraged`, not `required`.
- Files in `.github/`, `.gitlab/`, `.vscode/`, `.idea/` are implicitly allowed; they are platform/editor convention directories.
- `CLAUDE.md` and `.claude/` are project-specific exceptions for this repo — they would be `discouraged` in a generic repo that doesn't use Claude Code.
