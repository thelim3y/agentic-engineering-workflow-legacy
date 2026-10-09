# Summaries

When to call each agent. Each summary becomes the agent's `description`, which is how Claude decides when to use it.

| Agent | Summary |
|---|---|
| task-scoper | Use when a new ticket arrives, before any planning, to decide whether it is too large and to split it into sub-issues if so. |
| task-planner | Use when a right-sized task needs a plan before any tests or code are written. |
| tdd-maestro | Use when a planned task needs its failing tests written, or when code-fu disputes a test. |
| code-fu | Use when failing tests exist and the code that passes them must be written, or when a failed test run, a review or a merge check sends the pull request back. |
| test-runner | Use after code is written or changed, to run the full suite and report the result. |
| pr-create | Use when the suite passes, to push the branch and open the pull request. |
| pr-reviewer | Use when a pull request is open, to review it against the task. |
| merge-evaluator | Use when a pull request is approved, to decide whether it can be merged. |
| merger-mage | Use when a pull request is mergeable and merging is enabled, to merge it. |
