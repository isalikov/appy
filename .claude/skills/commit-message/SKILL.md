---
name: commit-message
description: Build ONE conventional commit message that covers all work in the working tree, for the human to commit. Use at the end of every task. Never runs git commit or git push.
---

# Commit message

The human always commits and pushes. Your job is to propose the message.

1. Inspect the whole working tree, not just what you remember changing:
   ```sh
   git status --short
   git diff --stat
   git diff
   git diff --cached
   ```
   Read the untracked files as well. Mention anything unrelated to the task, but do not drop it from the summary silently.
2. Pick **one** type for the whole change:
   - `feat`: new user-facing capability
   - `fix`: bug fix
   - `chore`: tooling, deps, config, infra, docs-only or refactor without behaviour change

   `refactor`, `docs`, `test`, `ci`, `perf`, `build` and `revert` are also accepted by `scripts/check-commit-msg.sh`, but prefer the three above.
3. Write the message:
   ```
   <type>(<optional scope>): <imperative summary, lower case, ≤72 chars, no period>

   - <what changed and why, one bullet per logical change>
   - <migrations, new env vars, breaking changes, manual steps>
   ```
   - The scope is the app or package (`api`, `web`, `landing`, `cli`, `ui`, `infra`) when the change is confined to one.
   - Mark breaking changes with `!` after the type and a `BREAKING CHANGE:` line in the body.
4. **Never** add `Co-Authored-By`, "Generated with Claude" or any other AI attribution. The commit-msg hook rejects it.
5. Output the message in a fenced code block, ready to paste into `git commit -F -` or an editor. Below it, list anything the human must do before committing, such as running a migration or regenerating the client.
