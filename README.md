# agentic-engineering-workflow

Project-agnostic SDLC agents and skills that carry a ticket, from a GitHub issue or pasted text, to a merged pull request: planning, with large tasks split into sub-issues; test-driven implementation; review; and an optional final check and merge.

## What it does

A ticket comes in as a GitHub issue or as pasted text. Nine agents, each with one task, take it through:

1. **Intake.** The `pull-issue` skill picks an issue, or the ticket is pasted.
2. **Scoping.** `task-scoper` decides whether the task is too large and splits it into sub-issues if so.
3. **Planning.** `task-planner` plans one right-sized task.
4. **Tests first.** `tdd-maestro` writes the failing tests.
5. **Coding.** `code-fu` writes the code that passes them.
6. **Testing.** `test-runner` runs the tests and reports.
7. **Pull request.** `pr-create` makes the pull request.
8. **Review.** `pr-reviewer` reviews it.
9. **Merge check.** `merge-evaluator` decides whether it can be merged.
10. **Merge.** `merger-mage` merges it. This stage is optional.

Any agent can also stop with `BLOCKED` or `NEEDS_USER`.

## Flow

```mermaid
flowchart TD
    ticket["Ticket<br/>pull-issue skill or pasted text"] --> scope["task-scoper"]
    scope -- FITS --> plan["task-planner"]
    scope -- SPLIT --> subs["Each sub-issue"] --> plan
    plan --> tests["tdd-maestro<br/>tests first"]
    tests --> code["code-fu"]
    code -. TEST_DISPUTED .-> tests
    code --> run["test-runner"]
    run -- FAIL --> code
    run -- PASS --> pr["pr-create"]
    pr --> review["pr-reviewer"]
    review -- CHANGES_NEEDED --> code
    review -- APPROVED --> eval["merge-evaluator"]
    eval -- NOT_MERGEABLE --> code
    eval -- MERGEABLE --> merge["merger-mage<br/>optional"]
    merge --> done(["Merged"])
```

## Documents

- `docs/agents.md`: the agents, each with its own doc in `docs/agents/`.
- `docs/rules.md`, `docs/abort-criteria.md`, `docs/user-input-criteria.md`: what holds for every agent.
- `docs/verdicts.md`: the verdicts agents return.
- `docs/hooks.md`: the hook that enforces file and command limits.
- `docs/skills.md`: the skills.
- `docs/issues.md`: the rules for the issues the workflow works on.
- `docs/config.md`: `agentic.toml` and its settings.
