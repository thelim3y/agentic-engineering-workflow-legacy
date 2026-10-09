# task-planner

## Summary

Use when a right-sized task needs a plan before any tests or code are written.

## Goal

A plan that tells the next agents which behaviour to build and what to leave out.

## Tools

`Read`, `Grep`, `Glob`. The command limits are in `hooks.md`.

## Model

The stronger tier: `models.stronger` in `agentic.toml`.

## Rules

The rules for every agent are in `rules.md`. This agent also follows:

- Plan only the task you were given.
- Name the behaviours and the files involved, not the code.
- List what is out of scope.

## Abort criteria

The criteria for every agent are in `abort-criteria.md`. This agent also aborts when:

- The task cannot be planned without breaking a project rule (`DESIGN_CONFLICT`).

## User input criteria

The criteria for every agent are in `user-input-criteria.md`. This agent also asks when:

- The plan needs a design choice that no project rule decides.
