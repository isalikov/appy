---
name: agent-team
description: How to staff a team/swarm of agents for a task in this repo — which project agent to use for which job, which model each runs on and when to override it, how to brief agents, and the limits on parallelism. Use whenever you are about to launch more than one agent, or need to pick a model for an agent.
---

# Agent team

Agent Teams are enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `.claude/settings.json`). Use a team for anything that needs research across several areas, or implementation across more than one app.

## Roster and models

Pick the cheapest model that solves the job well. Never use opus for search or mechanical edits, and never use haiku for design or architecture.

| Agent | Model | Use for |
|---|---|---|
| `scout` | haiku | Locating code, configs, conventions. Pure lookup. |
| `researcher` | sonnet | External docs, library comparisons, version-specific behaviour. |
| `ui-inspector` | sonnet | Browser evidence: screenshots, a11y snapshot, console, network. |
| `ui-designer` | opus | Design specs with the ui-ux-pro-max skill. Visual quality matters. |
| `architect` | opus | Cross-cutting plans, data models, contracts, risk analysis. |
| `backend-engineer` | sonnet | FastAPI, SQLAlchemy/Alembic, Mongo, Redis, taskiq. |
| `frontend-engineer` | sonnet | Vue/Vite/UnoCSS pages, components, stores. |
| `rust-engineer` | sonnet | clap/ratatui CLI work. |
| `infra-engineer` | sonnet | Dockerfiles, compose, GitHub Actions, mise, lefthook. |
| `reviewer` | opus | Final diff review for correctness and security. |

Override a model with the Agent tool's `model` parameter only when the task clearly differs from the default:
- Use `haiku` for a mechanical, fully specified edit, such as renaming across files or adding an env var everywhere.
- Use `opus` for an engineer facing a tricky algorithm, concurrency, or a migration of live data.

## Briefing

Every brief is self-contained, because agents do not see the conversation. It contains:
- the goal and why it matters
- the exact files or areas in scope, and what is out of scope
- the contracts the agent must honour: types, endpoints, tokens
- the acceptance criteria
- the expected report format
- a reminder: "Do not run tests, linters, builds, installs or servers; list the checks for the main session instead."

## Parallelism limits

- Launch independent agents in one message so they run concurrently. Keep a wave to **5 agents or fewer**.
- Two agents never edit the same file in the same wave.
- Agents never run heavy processes. The `.claude/hooks/guard-bash.py` hook enforces this for any call that carries an `agent_id`. The main session runs the checks once at the end (verify-changes skill).
- Do not duplicate work: once something is delegated, wait for the result instead of searching for it yourself.
