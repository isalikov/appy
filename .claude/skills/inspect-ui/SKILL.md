---
name: inspect-ui
description: Look at a running frontend of this repo through the project Playwright MCP server (or Chrome tools if the human has them connected) — URLs, ports, viewports, what evidence to collect, and the rule that the human starts the servers. Use before and after any UI change, and when debugging frontend behaviour.
---

# Inspect UI

The project ships a Playwright MCP server (`.mcp.json`, server `playwright`). It runs in an isolated profile at 1440×900 and writes its files to `.playwright-mcp/`, which is gitignored.

## Servers (started by the human only)

The usual answer is `mise run up`: one command for the whole stack. Single apps can be started on their own:

Every app runs on `http://localhost:<APP>_PORT`. Ports and URLs are defined in `.env`, which you must not read. `.env.example` has the defaults, and the human can print the real values with `mise run urls`.

| Target | Command | URL |
|---|---|---|
| Web SPA | `mise run dev:web` | `PUBLIC_WEB_URL` (default http://localhost:5173) |
| Landing (SSG) | `mise run dev:landing` | `PUBLIC_LANDING_URL` (default http://localhost:5174) |
| Landing, production build | `pnpm --filter @appy/landing build && pnpm --filter @appy/landing preview` | same as the landing, on `LANDING_PORT` |
| API (Swagger UI) | `mise run dev:api` | `PUBLIC_API_URL` + `/docs` (default http://localhost:8000/docs) |

If the defaults do not respond, ask the human for the values from `mise run urls`. Frontends call the API directly at `PUBLIC_API_URL`, so a page that needs data requires the whole stack. Ask the human for `mise run up`, which starts infra, the API, the worker and every frontend. Cross-app flows, such as landing → login → app, follow the `PUBLIC_*_URL` values.

If a URL does not respond, tell the human the exact command and wait. Never start it yourself; the guard hook blocks that anyway.

## Evidence to collect

1. `browser_navigate` to the URL, then `browser_snapshot` for the accessibility tree.
2. `browser_resize` to 1440, 1024, 768 and 375 wide, with `browser_take_screenshot` at each size. Use descriptive file names.
3. `browser_console_messages` and `browser_network_requests` to find errors and failed calls.
4. Interaction states: hover, focus with the keyboard (Tab order), active, disabled, loading, empty and error.
5. Dark mode: `browser_emulate_media` with `colorScheme: "dark"`.

For anything non-trivial, delegate this to the `ui-inspector` agent so screenshots stay out of the main context. For before/after comparisons, use the same viewport sizes and file names with `-before` and `-after` suffixes.

## Chrome

If the human has the Claude-in-Chrome extension connected, it can inspect authenticated or real-profile sessions. Load its tools in a single ToolSearch call. Never trigger `alert`, `confirm` or `prompt` dialogs.
