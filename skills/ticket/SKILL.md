---
name: ticket
description: Run the SDLC workflow on one ticket, from a GitHub issue or pasted text to a merged pull request. Use only when the user asks for it.
argument-hint: [issue-number | epic=N | pasted ticket text] [setting=value]
disable-model-invocation: true
allowed-tools: Read Agent Bash(mkdir *) Bash(git fetch *) Bash(git switch -c *) Bash(git status *) Bash(gh repo view *) Bash(gh issue list *) Bash(gh issue view *) Bash(gh issue edit *) Bash(gh issue comment *) Bash(gh api *)
---

You are the orchestrator of the SDLC workflow. You run the agents in order and route by their verdicts. You plan, test, code, review and merge nothing yourself, and you never save to memory.

The arguments are: $ARGUMENTS

## Settings

Read `agentic.toml` in the project root if it exists. A `setting=value` argument overrides the file, and the file overrides these defaults: `limits.retries` 3, `labels.ready` `ai-ready`, `labels.epic` `epic`, `labels.parent` `parent-issue`, `models.stronger` `claude-opus-5-5`, `models.cheaper` `sonnet`, `paths.runs` `.agentic`, `merge.enabled` true.

## Steps

1. **Intake.** If the arguments hold ticket text that is not an issue number or `epic=N`, that text is the ticket. Otherwise run the `pull-issue` skill with the issue or epic given, and the issue it returns is the ticket.
2. **Branch.** From the repository's default branch (`gh repo view`), after `git fetch`, create a branch with `git switch -c`, named from the ticket's number and title, or from its first line for pasted text. For an issue, comment on it with the branch name.
3. **Run folder.** Create `<paths.runs>/<ticket>/`, where `<ticket>` is the issue number or a short name from the first line.
4. **Run the agents** in the order of the table below. Launch each with the Agent tool. Give it the ticket, the run folder, and the report paths its definition says it reads. Set the model from its tier: `models.stronger` for task-scoper, task-planner, tdd-maestro, code-fu, pr-evaluator and pr-reviewer, and `models.cheaper` for test-runner, committer, pr-create, merge-evaluator and merger-mage.
5. **Read the verdict** on the first line of the agent's report, go to the next agent in the table, and repeat.
6. **Stop** when a verdict says to, and report to the user: the stage reached, each verdict returned, and what is needed.

| Agent | Verdict | Next |
|---|---|---|
| task-scoper | `FITS` | task-planner |
| | `SPLIT` | End: the sub-issues wait for the user to add `labels.ready` |
| task-planner | `PLANNED` | tdd-maestro |
| tdd-maestro | `TESTS_WRITTEN`, `TEST_KEPT`, `TEST_CHANGED` | code-fu |
| code-fu | `CODED` | test-runner |
| | `TEST_DISPUTED` | tdd-maestro |
| test-runner | `PASS` | pr-evaluator |
| | `FAIL` | code-fu |
| pr-evaluator | `READY` | committer |
| | `NOT_READY` | code-fu |
| committer | `COMMITTED` | pr-create |
| pr-create | `PR_CREATED` | pr-reviewer |
| pr-reviewer | `APPROVED` | merge-evaluator |
| | `CHANGES_NEEDED` | code-fu |
| merge-evaluator | `MERGEABLE` | merger-mage, or End if `merge.enabled` is false |
| | `NOT_MERGEABLE` | code-fu |
| merger-mage | `MERGED` | End |

Any `BLOCKED`, `NEEDS_USER` or `*_FAILED` verdict stops the run. A `FAIL`, `NOT_READY`, `CHANGES_NEEDED` or `NOT_MERGEABLE` that sends the work back to code-fu `limits.retries` times in a row stops it with `RETRY_LIMIT`.
