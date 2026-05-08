# Repository Guidelines

## Project Structure & Module Organization
- `skills/` is the canonical source of skills, each representing a capability domain of Lingxi API Gateway.
- Each skill contains `SKILL.md` and optional `scripts/` or `references/`.
- `tests/` mirrors skill names and stores smoke-test specs (`tests/**/SKILL.md`).
- `scripts/` contains shared utilities like the async polling adapter.
- `examples/` contains prompt patterns and usage scenarios.
- `output/` is for generated artifacts only; do not commit files from this directory.

## Build, Test, and Development Commands
- Validate all Python scripts: `make validate`
- Run smoke tests: `make test`
- Clean generated files: `make clean`

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints where practical.
- Skill folders use kebab-case, prefixed by `lingxi-` (example: `lingxi-chat`).
- Keep frontmatter in every `SKILL.md` with at least `name` and `description`.
- Language policy: keep `skills/**/SKILL.md` content in English only.

## Testing Guidelines
- Add/update tests under `tests/<skill>-test/SKILL.md`.
- Keep tests minimal and reproducible: one read-only or low-risk API path, clear pass/fail criteria.
- Include exact prerequisites (env vars, base URL, SDK install command).

## Commit & Pull Request Guidelines
- Follow Conventional Commit style: `feat: ...`, `chore: ...`, `docs: ...`.
- Keep commits scoped to one concern (skill content, docs, or tests).
