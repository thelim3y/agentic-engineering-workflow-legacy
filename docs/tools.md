# Tools

The tools each agent may use, as the `tools` allowlist in its definition. No agent has `Agent`, so none spawns another, and none has `WebFetch` or `WebSearch`.

| Agent | Tools | Why |
|---|---|---|
| task-scoper | `Read`, `Grep`, `Glob`, `Bash` | Reads the ticket and the code, and creates sub-issues with `gh` |
| task-planner | `Read`, `Grep`, `Glob` | Reads only; the plan is its report |
| tdd-maestro | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` | Writes test files and runs them to see them fail |
| code-fu | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` | Writes the code, builds it and runs the tests |
| test-runner | `Read`, `Grep`, `Glob`, `Bash` | Runs the tests and edits nothing |
| pr-create | `Read`, `Grep`, `Bash` | Pushes the branch and creates the pull request |
| pr-reviewer | `Read`, `Grep`, `Glob`, `Bash` | Reads the diff with `gh` and edits nothing |
| merge-evaluator | `Read`, `Bash` | Reads the pull request's checks and approvals with `gh` |
| merger-mage | `Read`, `Bash` | Merges with `gh` |

## Limits the allowlist cannot enforce

A `tools` allowlist cannot restrict `Bash` to certain commands. Command limits, such as only `gh` for merge-evaluator, are `Bash` deny rules in `permissions.deny`, and they apply to every agent. Which files an agent may edit is a rule in its definition: tdd-maestro edits only tests and code-fu edits no tests.
