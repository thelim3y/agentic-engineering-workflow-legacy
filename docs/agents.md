# Agents

Every agent has these sections:

- **Name**
- **Summary:** when to call the agent.
- **Goal:** the outcome the agent works toward.
- **Tools:** what the agent may use.
- **Rules:** what it must and must not do.
- **Abort criteria:** when it stops and gives up.
- **User input criteria:** when it stops and asks the user.

Four agents and an optional fifth, run in order by an orchestrator skill.

## Planner

Reads the ticket, a GitHub issue or pasted text, and writes the plan. If the task is too large, it splits it into sub-issues and plans each. It writes no code.

## TDD agent

Writes the failing tests that define the task, before any code, and adds further tests as the work shows the need. It owns the tests: the Implementer cannot change them and asks the TDD agent when it thinks one is wrong.

## Implementer

Writes the code that passes the tests, runs them, and opens the pull request. It is the only agent that edits non-test code.

## Reviewer

Reads the pull request and either approves it or lists the changes needed. It is read-only. A pull request that is not approved goes back to the Implementer.

## Merger

Optional. Runs the final checks and merges. It is the only agent that merges.

## Orchestrator

A skill, not an agent. It runs the stages in order and sends a rejected pull request back to the Implementer.
