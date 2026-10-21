#!/usr/bin/env python3
"""PreToolUse guard for Bash calls.

Enforces the hard rules from AGENTS.md:
  * nobody (main session or subagent) commits, pushes or starts long-running
    dev servers / infrastructure: that is always done by the human;
  * subagents never run tests, linters, builds or installs: a wave of parallel
    agents doing that would freeze the machine. The main session runs targeted
    checks once, sequentially (see the verify-changes skill).

Exit code 2 blocks the call and shows stderr to Claude.
"""

import json
import re
import sys

ALWAYS_BLOCKED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^git\b(?:\s+(?:-[cC]\s+\S+|--\S+))*\s+(?:commit|push)\b"),
     "git commit / git push are done by the human. Finish with a proposed commit message "
     "(commit-message skill)."),
    (re.compile(r"^(?:pnpm|npm|yarn|bun)\b.*\s(?:run\s+)?(?:dev|serve|start|preview)\b"),
     "Dev servers are started by the human. Ask them to run it, then inspect the UI."),
    (re.compile(r"^(?:vite)(?:\s+(?:dev|serve|preview)\b|\s*$|\s+--)"),
     "Dev servers are started by the human."),
    (re.compile(r"^(?:uvicorn|gunicorn|hypercorn)\b|^fastapi\s+(?:dev|run)\b"),
     "API servers are started by the human (`mise run dev:api`)."),
    (re.compile(r"^taskiq\s+worker\b|^cargo\s+watch\b|^(?:\./)?scripts/down\.sh\b"),
     "Long-running processes are started by the human."),
    (re.compile(r"^mise\s+(?:run\s+)?(?:up|down|dev:\S*|infra:\S*)(?:\s|$)"),
     "Dev servers and local infrastructure are managed by the human."),
    (re.compile(r"^docker(?:\s+compose|-compose)\b.*\s(?:up|start|restart|down|rm)\b"),
     "Local infrastructure is managed by the human (`mise run infra:up`)."),
]

HEAVY_FOR_SUBAGENTS = re.compile(
    r"^(?:"
    r"pytest|mypy|ruff|coverage|alembic"
    r"|eslint|vue-tsc|tsc|vitest|playwright|openapi-typescript"
    r"|cargo\s+(?:build|test|clippy|check|run|bench|doc|install|fmt)"
    r"|(?:pnpm|npm|yarn|bun)\b.*\b(?:install|add|build|test|lint|typecheck|generate|exec|dlx|x)\b"
    r"|uv\s+(?:sync|lock|add|remove|pip|tool|build)"
    r"|mise\s+(?:run\s+)?(?:lint|test|build|fix|setup|install|api:|db:)"
    r"|mise\s+install|docker\s+(?:build|buildx|run|compose)|lefthook\s+run|make\b"
    r")"
)

# Prefixes that only wrap the real command.
WRAPPERS = re.compile(
    r"^(?:"
    r"(?:\w+=\S*\s+)+"
    r"|(?:time|exec|nohup|sudo|command|env)\s+"
    r"|(?:ba|z)?sh\s+(?:-\w+\s+)*"
    r"|npx\s+(?:-y\s+|--yes\s+)?"
    r"|uv\s+run\s+(?:--\S+(?:\s+(?!-)\S+)?\s+)*"
    r"|uvx\s+"
    r"|(?:pnpm|npm)\s+exec\s+"
    r"|mise\s+(?:exec|x)\s+(?:\S+\s+)*?--\s+"
    r"|python3?\s+-m\s+"
    r")"
)

SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|&\n()]|\$\(|`")

# Heredoc bodies are data (file contents, messages), not commands.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$", re.DOTALL | re.MULTILINE)


def _segments(command: str) -> list[str]:
    result = []
    for raw in SEGMENT_SPLIT.split(HEREDOC.sub("", command)):
        segment = raw.strip()
        while True:
            stripped = WRAPPERS.sub("", segment, count=1).strip().strip("\"'")
            if stripped == segment:
                break
            segment = stripped.strip()
        if segment.startswith("cd "):
            continue
        if segment:
            result.append(segment)
    return result


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    is_subagent = bool(payload.get("agent_id"))

    for segment in _segments(command):
        for pattern, reason in ALWAYS_BLOCKED:
            if pattern.search(segment):
                print(f"Blocked by project policy: {reason}", file=sys.stderr)
                return 2
        if is_subagent and HEAVY_FOR_SUBAGENTS.search(segment):
            print(
                "Blocked by project policy: subagents never run tests, linters, builds or "
                "installs. Report what should be verified; the main session runs checks once.",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
