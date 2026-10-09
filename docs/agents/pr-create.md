# pr-create

## Summary

Use when the suite passes, to push the branch and open the pull request.

## Goal

A pull request a reviewer can read without asking questions.

## Tools

`Read`, `Grep`, `Bash`, and from engram: `mem_search`. The command limits are in `hooks.md`.

## Model

The cheaper tier: `models.cheaper` in `agentic.toml`.

## Rules

The rules for every agent are in `rules.md`. This agent also follows:

- Write the description with the `pr-handoff` skill.
- Include no change unrelated to the task.

## Verdicts

The verdicts every agent can return are in `verdicts.md`. This agent also returns:

- `PR_CREATED`: it names the pull request.
- `PR_FAILED`: the pull request was not created.

## Abort criteria

The criteria for every agent are in `abort-criteria.md`. This agent also aborts when:

- Pushing or creating the pull request fails (`TOOLING_FAILURE`).
- The branch has no commits (`DEPENDENCY_BLOCKED`).

## User input criteria

The criteria for every agent are in `user-input-criteria.md`. This agent also asks when:

- The branch holds changes unrelated to the task.
