# Abort criteria

An agent aborts when it meets any criterion here. It returns `BLOCKED` with the reason named, and the `ticket` skill decides what happens next. Aborting is not asking: when the agent needs an answer from the user, it returns `NEEDS_USER`.

## Every agent

| Criterion | Reason |
|---|---|
| A tool or command the agent needs fails, and retrying does not fix it | `TOOLING_FAILURE` |
| An input or a thing the task depends on is missing or not ready | `DEPENDENCY_BLOCKED` |
| The agent needs something outside the repository, such as access or a service | `EXTERNAL_BLOCKED` |
| The task contradicts the plan, the tests or the project rules | `DESIGN_CONFLICT` |
| `limits.attempts_per_step` attempts at the same step have failed | `RETRY_LIMIT` |

Each agent's own criteria are in its doc in `agents/`.
