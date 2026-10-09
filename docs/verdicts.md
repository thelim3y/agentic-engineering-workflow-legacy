# Verdicts

Every agent ends with exactly one verdict and a short reason. The `ticket` skill branches on the verdict and nothing else.

## Verdicts every agent can return

| Verdict | Meaning |
|---|---|
| `BLOCKED` | An abort criterion was met. It carries a blocked reason. |
| `NEEDS_USER` | A user input criterion was met. It carries the question. |

A `*_FAILED` verdict means the agent tried its task and could not complete it. `BLOCKED` means a stop condition ended the work, and it carries a typed reason.

## Blocked reasons

| Reason | Meaning |
|---|---|
| `TOOLING_FAILURE` | A tool or command the agent needs failed |
| `DEPENDENCY_BLOCKED` | Something the task depends on is not ready |
| `EXTERNAL_BLOCKED` | The agent needs something outside the repository |
| `DESIGN_CONFLICT` | The task contradicts the plan, the tests or the project rules |
| `RETRY_LIMIT` | The retry limit was reached without success |

## Verdicts per agent

| Agent | Verdicts |
|---|---|
| task-scoper | `FITS`: the task is right-sized. `SPLIT`: the task was split into the sub-issues it lists. `SCOPE_FAILED`: it could not judge or split the task. |
| task-planner | `PLANNED`: the plan is written. `PLAN_FAILED`: it could not produce a plan. |
| tdd-maestro | `TESTS_WRITTEN`: the tests fail for the intended reason. `TEST_KEPT`: a disputed test stays. `TEST_CHANGED`: a disputed test was changed. `TESTS_NOT_WRITTEN`: it could not write tests that fail for the intended reason. |
| code-fu | `CODED`: the code is written. `TEST_DISPUTED`: it believes a test is wrong, and names it. `CODE_FAILED`: it could not write code that passes the tests. |
| test-runner | `PASS`: the suite passes. `FAIL`: it lists the failing tests. |
| pr-create | `PR_CREATED`: it names the pull request. `PR_FAILED`: the pull request was not created. |
| pr-reviewer | `APPROVED`: the pull request is good. `CHANGES_NEEDED`: it lists the changes. |
| merge-evaluator | `MERGEABLE`: all merge conditions hold. `NOT_MERGEABLE`: it lists the conditions that fail. |
| merger-mage | `MERGED`: the pull request is merged. `MERGE_FAILED`: the merge did not happen. |
