---
name: verify-changes
description: How the main session verifies finished work — targeted, sequential checks only for the areas touched (API, frontend apps, CLI), never in subagents, never full-repo by default. Use after implementation and before review/commit message.
---

# Verify changes

Only the **main session** runs checks, and only once per round of changes. Run the commands **one at a time** (no parallel Bash calls), and only for the areas in `git status --short`. Never start dev servers or infrastructure. If an integration test needs Postgres, Mongo or Redis, ask the human to run `mise run up` (or `mise run infra:up`) first.

## Python API (`apps/api/**`, root `pyproject.toml`)

```sh
uv run ruff format <changed .py files>
uv run ruff check --fix <changed .py files>
uv run mypy
uv run pytest apps/api/tests/unit -q          # integration: add `-m integration` once infra is up
```

If a route or model changed, regenerate the client and include it in the change:

```sh
mise run api:openapi
```

If a model changed, ask the human to create and apply the migration: `mise run db:revision -- -m "..."`, then `mise run db:migrate`. Or write the migration by hand.

## Frontend (`apps/web`, `apps/landing`, `packages/*`)

```sh
pnpm exec eslint --fix <changed files>
pnpm --filter <package> typecheck
pnpm --filter <package> test
```

Build only when you touched build config, routing or SSG: `pnpm --filter <package> build`. Leave e2e (`test:e2e`) to CI unless the change is e2e-specific.

## Rust CLI (`apps/cli/**`, `Cargo.toml`)

```sh
cargo fmt --all
cargo clippy -p <crate> --all-targets --locked -- -D warnings
cargo test -p <crate> --locked
```

## Infra (Dockerfiles, compose, workflows)

Do not build images or run compose. Re-read the changes against the conventions in `AGENTS.md`. Validate YAML by reading it carefully, and run `lefthook validate` when `lefthook.yml` changed. List the manual checks for the human.

## Reporting

Report what you ran and what each command printed. Report failures plainly, with their output, and fix or explain them. Never claim that something was verified when it wasn't.
