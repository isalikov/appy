---
name: add-app
description: Checklist for adding another app to the monorepo — an SPA (Vue/Vite/UnoCSS), an API (FastAPI), a CLI (Rust) or another SSG site — including workspace registration, env, Dockerfile, CI image matrix, release workflow and docs. Use when the human asks for a new app/service/CLI.
---

# Add an app

Ask the human for the app name in kebab-case (`<name>`) and its purpose first. Copy the closest existing app as the template, then rename everything. Package names follow `@appy/<name>` (JS), `appy-<name>` / `appy_<name>` (Python), and `appy-<name>` crate / binary name of choice (Rust).

## Every app: port and URL (no local domains)

1. Register the app in `packages/config/src/apps.ts`, for example `admin: 'ADMIN'`.
2. In `.env.example`, add `<NAME>_PORT=<next free port>` and `PUBLIC_<NAME>_URL=http://localhost:${<NAME>_PORT}`. Tell the human to add both to their `.env`.
3. Add the key to `BUILD_TIME` in `packages/config/src/index.ts` and its `ImportMetaEnv` entry in `packages/config/src/env.d.ts`.
4. Add the key to `infra/caddy/env.js` and to the `ENV PUBLIC_…` placeholder block in every frontend Dockerfile.
5. If browsers call the API from it, add `${PUBLIC_<NAME>_URL}` to `API_CORS_ORIGINS`. For an API, add `public_<name>_url` to the other APIs' settings if they redirect to it.
6. Add `PUBLIC_<NAME>_URL` to the CI python job's `env` block.

## SPA (template: `apps/web`)

1. Copy `apps/web` to `apps/<name>`. In `vite.config.ts`, update the `name` in `package.json`, the `<title>` and `appViteConfig('<name>', env)`. The port comes from `<NAME>_PORT`. Update `appPort('<name>')` in the Playwright config.
2. If it needs extra browser-visible variables, add `PUBLIC_*` entries to `.env.example`, `packages/config` and `infra/caddy/env.js`. Never put secrets in `PUBLIC_*`.
3. Add a `dev:<name>` task to `mise.toml`.
4. CI: add `<name>` to the `matrix.app` list in `.github/workflows/images.yml`. Add an e2e step to `ci.yml` if it has e2e tests.
5. Update the layout table in `AGENTS.md` and the port table in the inspect-ui skill.

## API (template: `apps/api`)

1. Copy `apps/api` to `apps/<name>`. Rename the package directory to `src/appy_<name>`, set `name = "appy-<name>"` and `module-name` in its `pyproject.toml`, and fix the imports and `uvicorn --factory` paths.
2. Pick a unique `env_prefix` (for example `<NAME>_`) in `settings.py`. Add its variables to `.env.example` and to the CI `env` block. Use a separate Postgres database or schema, a Mongo database and Redis DB numbers.
3. Root `pyproject.toml`: add the member to `[tool.uv.workspace].members`, and add its `src`, `tests` and `migrations/env.py` paths to mypy `files` and `mypy_path`.
4. Every API Dockerfile must `COPY` the `pyproject.toml` of **every** workspace member before `uv sync`. Update the existing Dockerfiles too.
5. Add `dev:<name>`, `db:<name>:migrate` and an openapi export task to `mise.toml`. If a frontend consumes it, add a client package (`packages/<name>-client`).
6. Add it to the `images.yml` matrix. Update `AGENTS.md`.
7. The human runs `uv lock`, or the main session does once.

## CLI (template: `apps/cli`)

1. Copy `apps/cli` to `apps/<name>`. Set the package `name` and the `[[bin]] name`, and add it to `[workspace].members` in the root `Cargo.toml`.
2. In `.github/workflows/cli-release.yml`, turn the single build into a matrix over binaries, or add a second `cargo build -p` and package step. Use the archive name `<bin>-<version>-<target>`.
3. Add a `dev:<name>` task. Update `AGENTS.md`.

## SSG site (template: `apps/landing`)

Same steps as an SPA, using the landing `Caddyfile`, which has no SPA fallback, and `vite-ssg build`.

## Always

- Delegate the edits to `infra-engineer`, plus `backend-engineer`, `frontend-engineer` or `rust-engineer` for the app code, using the agent-team skill. Then verify centrally with verify-changes.
- Lockfiles (`pnpm-lock.yaml`, `uv.lock`, `Cargo.lock`) must be updated in the same change, by the main session or the human.
