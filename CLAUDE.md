@AGENTS.md

## Claude Code specifics

- For any non-trivial task, start with the task-workflow skill. Staff agents with the agent-team skill.
- End every task with the commit-message skill's output: one proposed message, in a code block, with no attribution.
- Run checks only in the main session, following verify-changes: targeted and sequential.
