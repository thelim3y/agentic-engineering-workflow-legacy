# Agents

Every agent has these sections:

- **Name**
- **Summary:** when to call the agent.
- **Goal:** the outcome the agent works toward.
- **Tools:** what the agent may use.
- **Model:** which model the agent runs on, chosen per agent to save tokens.
- **Rules:** what it must and must not do.
- **Abort criteria:** when it stops and gives up.
- **User input criteria:** when it stops and asks the user.

Each agent has one task. The `ticket` skill runs them in order.

| Agent | Its one task |
|---|---|
| task-scoper | Decide whether the task is too large, and split it into sub-issues if so |
| task-planner | Plan one right-sized task |
| tdd-maestro | Write the failing tests, and own them |
| code-fu | Write the code that passes the tests |
| test-runner | Run the tests and report |
| pr-create | Make the pull request |
| pr-reviewer | Review the pull request |
| merge-evaluator | Decide whether the pull request can be merged |
| merger-mage | Merge it (optional) |
