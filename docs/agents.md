# Agents

Every agent has its own doc in `agents/` with these sections:

- **Name**
- **Summary:** when to call the agent.
- **Goal:** the outcome the agent works toward.
- **Tools:** what the agent may use.
- **Model:** which model the agent runs on, chosen per agent to save tokens.
- **Rules:** what it must and must not do.
- **Abort criteria:** when it stops and gives up.
- **User input criteria:** when it stops and asks the user.

Each agent has one task. The `ticket` skill runs them in order.

An agent that mostly reads text and finds things in it runs on the cheaper model tier. One that makes judgments runs on the stronger tier. No agent spawns another, and none reaches the web.

| Agent | Its one task |
|---|---|
| [task-scoper](agents/task-scoper.md) | Decide whether the task is too large, and split it into sub-issues if so |
| [task-planner](agents/task-planner.md) | Plan one right-sized task |
| [tdd-maestro](agents/tdd-maestro.md) | Write the failing tests, and own them |
| [code-fu](agents/code-fu.md) | Write the code that passes the tests |
| [test-runner](agents/test-runner.md) | Run the tests and report |
| [pr-create](agents/pr-create.md) | Make the pull request |
| [pr-reviewer](agents/pr-reviewer.md) | Review the pull request |
| [merge-evaluator](agents/merge-evaluator.md) | Decide whether the pull request can be merged |
| [merger-mage](agents/merger-mage.md) | Merge it (optional) |
