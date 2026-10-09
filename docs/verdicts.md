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

Each agent's own verdicts are in its doc in `agents/`.
