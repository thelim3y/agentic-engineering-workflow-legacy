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

Each agent's own criteria are in its doc in `agents/`.
