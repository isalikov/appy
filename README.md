# Appy

A boilerplate for production-grade full-stack applications:

- **API** on FastAPI, using Postgres with pgvector, MongoDB, and Redis for sessions, cache and taskiq queues
- **SPA** on Vue 3, Vite and UnoCSS
- **SSG landing** built with vite-ssg
- **CLI** in Rust with clap and ratatui

The repo is a monorepo wired together with mise, lefthook and GitHub Actions. It ships with a Claude Code setup: agents, skills, guard hooks and Playwright MCP.

## Quick start

```sh
mise trust && mise install   # toolchain pinned in mise.toml
mise run setup               # deps, git hooks, .env from .env.example

mise run up                  # docker infra + migrations + api, worker, web, landing (logs in this terminal)
                             # Ctrl+C stops the apps
mise run down                # stop docker and free every port; DB data is kept

mise run urls                # where everything lives (ports/URLs come from .env)
mise run dev:cli             # prints "Hello from Appy"; `mise run dev:cli -- tui` for the TUI
```

Local data lives in the named docker volumes `appy_postgres-data`, `appy_mongo-data` and `appy_redis-data`. It survives `up`/`down` cycles. Only `mise run infra:reset` deletes it. Single apps can still be run on their own with `mise run dev:api`, `dev:worker`, `dev:web` and `dev:landing`.

`mise tasks` lists every task. `AGENTS.md` describes the layout, conventions and delivery pipeline in detail.

## Configuration

Local configuration lives in `.env`, which is gitignored and created from `.env.example`. mise loads it into every task, Vite and Playwright read it from the repo root, and `compose.yaml` reads it for the infrastructure. In deployed environments the same variables are injected by the platform.

There are no local domains. Each app listens on `localhost:<APP>_PORT` (`LANDING_PORT`, `WEB_PORT`, `API_PORT`) and is linked through `PUBLIC_<APP>_URL`. Every cross-app link and redirect uses these URLs, as do CORS and OAuth callbacks. `mise run urls` prints them.

The frontend images read `PUBLIC_*_URL` at **runtime**: Caddy renders `/env.js` from the container env. So the same image works for any environment:

```sh
docker run -p 8080:8080 \
  -e PUBLIC_LANDING_URL=https://example.com \
  -e PUBLIC_WEB_URL=https://app.example.com \
  -e PUBLIC_API_URL=https://api.example.com \
  ghcr.io/<owner>/appy-landing:latest
```

## Images and releases

| Trigger | Result |
|---|---|
| push to `master` | `ghcr.io/<owner>/appy-{api,web,landing}:latest` |
| tag `x.y.z` | `ghcr.io/<owner>/appy-{api,web,landing}:x.y.z`, plus a GitHub Release with `appy` CLI binaries |
| pull request | images are built but not pushed |

The API image also runs migrations (`alembic upgrade head`) and the task worker (`taskiq worker …`); see `apps/api/Dockerfile`.

## Working with Claude Code

- Agent Teams and the Playwright MCP server are enabled at the project level. On first launch, approve the project MCP server and trust the folder, since project hooks need trust.
- Agents never commit, push, start servers or run heavy checks. `.claude/hooks/guard-bash.py` enforces this.
- At the end of a task Claude proposes one commit message. You commit it yourself.
