# User input criteria

An agent stops and asks the user when it meets any criterion here. It returns `NEEDS_USER` with one question. Asking is not aborting: when the agent cannot continue for any other reason, it returns `BLOCKED`. In an unattended run an agent never waits; it returns `NEEDS_USER` and the run ends.

## Every agent

| Criterion |
|---|
| The ticket or plan can be read two ways that give different results, and nothing in the repository settles it |
| The next step is irreversible or destructive, such as deleting a branch, force-pushing or rewriting history |
| The next step is security-sensitive |
| The next step has an effect outside what the workflow is set up to do |

An agent asks one question at a time.

## Per agent

| Agent | Also asks when |
|---|---|
| task-scoper | It cannot tell whether the task is too large without a decision about its scope |
| task-planner | The plan needs a design choice that no project rule decides |
| tdd-maestro | The behaviour a test should pin down is ambiguous |
| code-fu | The code needs a change outside the task, such as to a public interface |
| test-runner | The tests were already failing before the change |
| pr-create | The branch holds changes unrelated to the task |
| pr-reviewer | A problem needs a product decision, not a code judgment |
| merge-evaluator | The merge needs a human approval that has not been given |
| merger-mage | A step beyond the merge itself, such as deleting the branch, is needed |
