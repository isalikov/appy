---
name: task-workflow
description: The mandatory way to run any non-trivial task in this repo (a feature, bug, refactor, new app, UI work, research). Sequence is artifacts → UI inspection → research → wizard-style questions → plan → implementation by an agent team → central verification → review → proposed commit message. Use at the start of every task that touches more than one file or needs a decision.
---

# Task workflow

Every phase below is required for non-trivial work. For a one-line fix you may collapse phases 1–4, but never skip phase 7 or the commit message at the end.

## 1. Gather artifacts (parallel, cheap)

Launch read-only agents **in a single message** so they run concurrently. Choose their models with the agent-team skill.
- `scout`: the existing code, conventions and similar features.
- `researcher`: library docs (context7) and external knowledge, whenever versions or APIs matter.
- `ui-inspector`: the current state of every affected screen, whenever a UI is involved. It needs a running dev server: ask the human to run `mise run up` (or a single `mise run dev:<app>`) and wait. Never start it yourself.

## 2. Look at the interface

For UI work, look at the ui-inspector screenshots yourself before deciding anything. If the human has Chrome connected, the claude-in-chrome tools are an alternative to Playwright.

## 3. Research the solution

Synthesize the artifacts. For UI work, run the `ui-designer` agent, which applies the **ui-ux-pro-max** skill in full. Never design an interface without that skill.

## 4. Ask questions, wizard-style

Use `AskUserQuestion` for every decision that belongs to the human: product behaviour, trade-offs, naming, scope. Batch up to four questions per call, give 2–4 concrete options each, and put the recommended option first, marked "(Recommended)". Never ask what the code or a sensible default already answers. Ask again whenever a later phase surfaces a new decision.

## 5. Plan

For cross-cutting work, have `architect` (opus) turn the artifacts and answers into work packages, where no two packages touch the same file. Present the plan briefly and get the human's go-ahead before implementing large changes.

## 6. Implement with a team

Launch the engineer agents (`backend-engineer`, `frontend-engineer`, `rust-engineer`, `infra-engineer`), one per work package, in parallel when the packages are independent. Each brief contains:
- the goal
- the exact files
- the contracts
- the acceptance criteria
- a reminder that the agent must not run checks

Integrate their reports yourself. If a contract changed, regenerate the API client (`mise run api:openapi`) once, from the main session.

## 7. Verify centrally

Follow the verify-changes skill: the main session runs the targeted checks **once, sequentially**, only for the areas touched. Subagents never run checks. For UI changes, send `ui-inspector` again to compare before and after.

## 8. Review

For non-trivial diffs, run `reviewer` (opus). Fix the confirmed findings and re-verify only what changed.

## 9. Hand over

Never commit, push or start servers. Run the commit-message skill and end your reply with:
- a short summary of what changed and how it was verified, including anything not verified
- the commands the human should run, such as `mise run up` or `mise run down`, or migrations
- the proposed commit message in a code block

## Language

All files, docs, code comments, agent briefs and skills are in English. Talk to the human in the language the conversation started in.
