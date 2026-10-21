# AGENTS.md

Instructions for AI agents working in this repository. Humans: see `README.md`.

Appy is a boilerplate for **production-grade** full-stack products. Anything built on it is a stable, long-lived application, not an MVP. Write code accordingly: typed, tested, observable, secure, with every error path handled.

## Hard rules

These are non-negotiable. `.claude/hooks/guard-bash.py` enforces the first three.

1. **Never `git commit` or `git push`.** The human does it. At the end of every task, inspect the working tree and propose **one** commit message covering all of the work (commit-message skill).
2. **Never start dev servers, workers or local infrastructure.** That covers `mise run dev:*`, `mise run infra:*`, `vite`, `uvicorn`, `docker compose up` and the like. Ask the human to run them.
3. **Subagents never run tests, linters, type checkers, builds or installs.** A wave of agents doing that freezes the machine. The main session runs targeted checks once, sequentially, at the end (verify-changes skill).
4. **Commit messages** use the form `feat: …`, `fix: …` or `chore: …` (conventional commits; an optional scope such as `feat(api): …` is fine) and **never contain AI attribution** such as `Co-Authored-By` or "Generated with". The commit-msg hook rejects both.
5. **Language:** every file, doc, code comment, skill and agent brief is in English. Talk to the human in the language the conversation started in.
6. **Process:** for complex tasks, follow the task-workflow skill. Gather artifacts with agents, look at the UI (Playwright MCP or Chrome), research, ask questions wizard-style (`AskUserQuestion`, recommended option first), then plan, implement with an agent team (agent-team skill), verify centrally and review.
7. **Models:** give every agent the cheapest model that does the job well (the table is in the agent-team skill). Agent Teams are enabled in `.claude/settings.json`.
8. **UI work** always uses the **ui-ux-pro-max** skill to its full extent, through the `ui-designer` agent or directly. Never ship a screen without loading, empty, error and success states, keyboard support and AA contrast.
9. **Secrets:** never read or write `.env`. Configuration is documented in `.env.example`, and every new variable goes there.
10. **Ports and URLs:** no local domains and no hard-coded ports or hosts. Every app listens on `localhost:<APP>_PORT` and is linked through `PUBLIC_<APP>_URL`, both from `.env` (see "Ports and URLs" below).

## Layout

```
apps/
  api/        FastAPI service (Python 3.14, uv)        -> image ghcr.io/<owner>/appy-api
  web/        Vue 3 SPA (Vite, UnoCSS, Pinia)           -> image ghcr.io/<owner>/appy-web
  landing/    Vue 3 SSG landing (vite-ssg, UnoCSS)      -> image ghcr.io/<owner>/appy-landing
  cli/        Rust CLI `appy` (clap, ratatui)           -> GitHub Release binaries
packages/
  config/     App registry, public URLs (appUrl/appLink), shared Vite config (@appy/config)
  ui/         Shared Vue components + UnoCSS preset/tokens (@appy/ui, @appy/ui/unocss)
  api-client/ Typed API client generated from OpenAPI (@appy/api-client)
infra/        Local infrastructure helpers (postgres init, caddy runtime env template)
.github/      CI, image publishing, CLI release workflows
.claude/      Agents, skills, hooks, settings (Agent Teams, Playwright MCP)
```

There can be any number of SPAs, APIs and CLIs. Add them with the add-app skill.

## Ports and URLs

- **No local domains.** Every app runs on `http://localhost:<APP>_PORT`, and every port is set in `.env` (`LANDING_PORT`, `WEB_PORT`, `API_PORT`, …). Never hard-code a port or a host in code, configs or docs. Read it from the env.
- **Every app has a public URL** in `.env`: `PUBLIC_<APP>_URL`, for example `PUBLIC_WEB_URL=http://localhost:${WEB_PORT}`. Use it for every cross-app link and redirect, for CORS (`API_CORS_ORIGINS`) and for cookies. For example, the landing "Log in" button goes to an auth SPA, which does OAuth and then redirects to `PUBLIC_WEB_URL`.
  - **Frontend:** `appUrl(app)` and `appLink(app, path, query)` from `@appy/config`.
  - **API:** `settings.public_<app>_url`.
- `PUBLIC_*` variables are visible to browsers, so never put secrets in them. In a local dev or preview build, Vite inlines them from the root `.env`. In containers they are runtime config: the bundle ships with Caddy placeholders, and Caddy renders `/env.js` and the pre-rendered HTML from the container env, so one image serves every environment.
- **App registry:** `packages/config/src/apps.ts`. Adding an app also means updating `.env.example` and `infra/caddy/env.js`.
- **Seeing the values:** `mise run urls` prints every public URL.

## Toolchain

`mise` pins every tool (`mise.toml`): node, pnpm, python, uv, rust and lefthook. It also loads the root `.env` into every task. To list the tasks, run `mise tasks`. The main ones:

| Task | What it does |
|---|---|
| `mise run setup` | Install deps and git hooks, and create `.env` from `.env.example` |
| `mise run up` | **Whole local stack** (human only): docker infra, then migrations, then api, worker, web and landing in one terminal with `[task]`-prefixed logs, plus a summary of every app and service with its port and status once they listen. Ctrl+C stops the apps. |
| `mise run down` | Stops the docker services and frees every app port. Data volumes are **kept**. |
| `mise run infra:up` / `infra:down` / `infra:reset` | Only the docker services. `infra:reset` is the **only** command that deletes local data. |
| `mise run dev:api` / `dev:worker` / `dev:web` / `dev:landing` / `dev:cli` | Single app (human only) |
| `mise run db:migrate` / `db:revision -- -m "..."` | Alembic migrations |
| `mise run api:openapi` | Export the OpenAPI schema and regenerate `@appy/api-client` |
| `mise run lint` / `test` / `fix` / `build` | Whole-repo checks (human or CI; agents use targeted commands) |

The workspaces are pnpm (`apps/*`, `packages/*`), uv (root `pyproject.toml`) and cargo (root `Cargo.toml`).

## Backend: `apps/api`

- **App:** an app factory (`appy_api.main:create_app`) with a lifespan that creates `Resources`: the SQLAlchemy async engine, an async PyMongo client and an async Redis client.
- **Settings:** read in `settings.py` from `API_*` variables using pydantic-settings. Connection strings have no defaults, so a missing one fails at startup.
- **Postgres:** SQLAlchemy 2 async over asyncpg. Models subclass `db.postgres.Base`, use deterministic constraint names, and are registered in `models/__init__.py`. Schema changes require an Alembic migration (`migrations/`). pgvector is enabled by migration `0001`; use `pgvector.sqlalchemy.Vector`.
- **MongoDB:** for unstructured collections, through `MongoDep`, with documents validated by pydantic models.
- **Redis:** sessions and cache (`RedisDep`; namespaced keys, always with a TTL), plus queues via taskiq (`tasks/broker.py`, `tasks/jobs.py`). The worker command is in the Dockerfile header.
- **Routes:** `api/routes/*.py`, with tagged routers and typed responses. Operation ids are `<tag>_<function>` so the generated client has clean names. `/health` pings every backing service and returns 503 when any of them is down.
- **Tests:** `tests/unit` overrides dependencies and needs no services. `tests/integration` is marked `integration` and needs `mise run infra:up` (CI provides service containers).
- **Quality:** ruff (format and an extensive rule set) and mypy strict with the pydantic plugin. The config lives in the root `pyproject.toml`.

## Frontend: `apps/web`, `apps/landing`, `packages/ui`

- **Stack:** Vue 3 `<script setup lang="ts">`, TypeScript strict (`tsconfig.base.json`), Vite and vue-router. The SPA also uses Pinia.
- **UnoCSS** (preset-wind4, icons, typography) uses the shared preset `@appy/ui/unocss`. Colours are semantic tokens (`bg`, `fg`, `muted`, `border`, `primary`) backed by CSS variables, with light and dark variants. Never use raw hex colours in components. Icons are `i-lucide-*`.
- **API access:** only through `@appy/api-client`, typed from OpenAPI, called directly at `appUrl('api')`. The API allows the frontend origins via CORS.
- **Shared Vite settings:** `appViteConfig(app, env)` from `@appy/config/vite` sets the root `.env`, the `PUBLIC_` prefix and `localhost:<APP>_PORT` for both dev and preview.
- **Landing:** pre-rendered by vite-ssg. Keep the code SSR-safe and set head tags with `useHead`.
- **Quality:** ESLint uses `@antfu/eslint-config` with UnoCSS rules (it also formats, so there is no Prettier). Type checking is vue-tsc, unit tests are Vitest next to the components, and e2e is Playwright (`apps/web/e2e`).

## CLI: `apps/cli`

Rust 2024. clap derive drives the commands and ratatui the TUI (`appy tui`). The workspace lints (clippy pedantic, no `unwrap`) are in the root `Cargo.toml`. `appy` with no arguments prints `Hello from Appy`.

## Delivery

- **Images:** built only by `.github/workflows/images.yml`, never locally for publishing. Pushes to `master` produce `:latest` (plus `:sha-…`), a tag `x.y.z` produces `:x.y.z` and `:x.y`, and pull requests build without pushing. Dockerfiles live in `apps/<app>/Dockerfile` and use the repo-root context.
- **CLI binaries:** a tag `x.y.z` triggers `.github/workflows/cli-release.yml`, which builds macOS (arm64, x64) and Linux musl (x64, arm64) tarballs and attaches them to a GitHub Release.
- **CI:** `.github/workflows/ci.yml` runs the Python checks with real services, the frontend lint, typecheck, test, build and e2e, and the Rust fmt, clippy and test.
- **Git hooks** (lefthook): `pre-commit` formats and lints staged files and refuses `.env*`. `commit-msg` enforces the message format. `pre-push` runs the full checks sequentially.

## Claude Code setup (`.claude/`)

- `settings.json`: enables Agent Teams, disables attribution, approves the Playwright MCP server, adds deny rules for commit, push and `.env`, and registers the guard hook.
- `agents/`:
  - `scout` (haiku)
  - `researcher`, `ui-inspector` and the `*-engineer` agents (sonnet)
  - `architect`, `ui-designer`, `reviewer` (opus)
- `skills/`:
  - `task-workflow`, `agent-team`, `verify-changes`, `commit-message`, `inspect-ui`, `add-app`
  - the design skills: `ui-ux-pro-max`, `design-system`, `ui-styling`, `design`, `brand`, `banner-design`, `slides`
- `hooks/guard-bash.py`: enforces hard rules 1–3.
- `.mcp.json` (repo root): the Playwright MCP server.
