# Abort criteria

An agent aborts when it meets any criterion here. It returns `BLOCKED` with the reason named, and the `ticket` skill decides what happens next. Aborting is not asking: when the agent needs an answer from the user, it returns `NEEDS_USER`.

## Every agent

| Criterion | Reason |
|---|---|
| A tool or command the agent needs fails, and retrying does not fix it | `TOOLING_FAILURE` |
| An input or a thing the task depends on is missing or not ready | `DEPENDENCY_BLOCKED` |
| The agent needs something outside the repository, such as access or a service | `EXTERNAL_BLOCKED` |
| The task contradicts the plan, the tests or the project rules | `DESIGN_CONFLICT` |
| Three attempts at the same step have failed | `RETRY_LIMIT` |

## Per agent

| Agent | Also aborts when |
|---|---|
| task-scoper | The ticket text is missing or empty (`DEPENDENCY_BLOCKED`). The split pieces are still too large after three attempts (`RETRY_LIMIT`). |
| task-planner | The task cannot be planned without breaking a project rule (`DESIGN_CONFLICT`). |
| tdd-maestro | It cannot write a test that fails for the intended reason after three attempts (`RETRY_LIMIT`). |
| code-fu | The tests still fail after three attempts (`RETRY_LIMIT`). Only changing a test would make them pass: it returns `TEST_DISPUTED` and does not abort. |
| test-runner | The suite cannot run, for example because the build is broken (`TOOLING_FAILURE`). |
| pr-create | Pushing or creating the pull request fails (`TOOLING_FAILURE`). The branch has no commits (`DEPENDENCY_BLOCKED`). |
| pr-reviewer | The diff cannot be read (`TOOLING_FAILURE`). |
| merge-evaluator | The CI status cannot be read (`EXTERNAL_BLOCKED`). |
| merger-mage | The merge is refused, for example by branch protection (`EXTERNAL_BLOCKED`). |
