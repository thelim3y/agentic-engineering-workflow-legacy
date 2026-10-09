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

An agent that mostly reads text and finds things in it runs on a cheaper model. One that makes judgments runs on a stronger one.

| Agent | Its one task | Model |
|---|---|---|
| task-scoper | Decide whether the task is too large, and split it into sub-issues if so | stronger |
| task-planner | Plan one right-sized task | stronger |
| tdd-maestro | Write the failing tests, and own them | stronger |
| code-fu | Write the code that passes the tests | stronger |
| test-runner | Run the tests and report | cheaper |
| pr-create | Make the pull request | cheaper |
| pr-reviewer | Review the pull request | stronger |
| merge-evaluator | Decide whether the pull request can be merged | cheaper |
| merger-mage | Merge it (optional) | cheaper |
