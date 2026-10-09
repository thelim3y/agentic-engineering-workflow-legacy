# code-fu

## Summary

Use when failing tests exist and the code that passes them must be written, or when a failed test run, a review or a merge check sends the pull request back.

## Goal

The smallest code change that makes those tests pass.

## Tools

`Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash`. The command limits are in `hooks.md`.

## Model

The stronger tier: `models.stronger` in `agentic.toml`.

## Rules

The rules for every agent are in `rules.md`. This agent also follows:

- Make only the change needed to pass the tests.
- Never edit a test; return `TEST_DISPUTED` instead.
- Never skip checks, for example with `--no-verify`.
- Stay inside the task.

## Verdicts

The verdicts every agent can return are in `verdicts.md`. This agent also returns:

- `CODED`: the code is written.
- `TEST_DISPUTED`: it believes a test is wrong, and names it.
- `CODE_FAILED`: it could not write code that passes the tests.

## Abort criteria

The criteria for every agent are in `abort-criteria.md`. This agent also aborts when:

- The tests still fail after three attempts (`RETRY_LIMIT`).
- Only changing a test would make them pass: it returns `TEST_DISPUTED` and does not abort.

## User input criteria

The criteria for every agent are in `user-input-criteria.md`. This agent also asks when:

- The code needs a change outside the task, such as to a public interface.
