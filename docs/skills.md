# Skills

## ticket

The orchestrator and the entry point: `/ticket`. It takes a GitHub issue number, an epic number, pasted ticket text, or nothing. Any argument also overrides the matching setting in `agentic.toml`. With `dry-run`, it runs the whole workflow with every remote effect blocked, as `testing.md` says.

1. **Intake.** With pasted text, that text is the ticket. Otherwise it runs `pull-issue` with the issue or epic given.
2. **Worktree.** As soon as it has the ticket, it makes sure it is working in a linked git worktree, never in the main checkout. If it is not in one, it enters a new one, named from the ticket's number and title, or from its first line for pasted text. The worktree branches from the repository's default branch. For an issue, it then comments on the issue with the branch name.
3. **Run the agents** in the order below. It creates the run folder `<paths.runs>/<ticket>/` first. After each agent it reads the verdict at the top of that agent's report and goes to the next agent in the table, giving it the paths of the reports its doc says it reads. It does nothing else: it plans, codes and reviews nothing itself.
4. **Stop** when a verdict says to, and report to the user: the stage reached, each verdict returned, and what is needed.
5. **Keep the reports.** In a real run on an issue, it comments on the issue with each report in a collapsible block. In a dry run it copies the run folder into the main checkout, to `<paths.runs>/agentic-engineering-workflow/dry-runs/<ticket>/`, and then removes the worktree, discarding its commit.

| Agent | Verdict | Next |
|---|---|---|
| task-scoper | `FITS` | task-planner |
| | `SPLIT` | End: the sub-issues wait for the user to add `ai-ready` |
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

## pull-issue

Picks one eligible GitHub issue and claims it. It has its own doc: `skills/pull-issue.md`.

## tdd

The red, green, refactor loop that tdd-maestro and code-fu share. It has its own doc: `skills/tdd.md`.

## pr-handoff

The format of the pull request description. It has its own doc: `skills/pr-handoff.md`.
