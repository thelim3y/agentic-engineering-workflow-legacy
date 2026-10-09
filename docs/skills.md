# Skills

## ticket

The orchestrator and the entry point: `/ticket`. It takes a GitHub issue number, an epic number, pasted ticket text, or nothing. Any argument also overrides the matching setting in `agentic.toml`.

1. **Intake.** With pasted text, that text is the ticket. Otherwise it runs `pull-issue` with the issue or epic given.
2. **Branch.** As soon as it has the ticket, it creates a branch from the repository's default branch, named from the ticket's number and title, or from its first line for pasted text. For an issue, it then comments on the issue with the branch name.
3. **Run the agents** in the order below. After each agent it reads the verdict and goes to the next agent in the table. It does nothing else: it plans, codes and reviews nothing itself.
4. **Stop** when a verdict says to, and report to the user: the stage reached, each verdict returned, and what is needed.

| Agent | Verdict | Next |
|---|---|---|
| task-scoper | `FITS` | task-planner |
| | `SPLIT` | End: the sub-issues wait for the user to add `ai-ready` |
| task-planner | `PLANNED` | tdd-maestro |
| tdd-maestro | `TESTS_WRITTEN`, `TEST_KEPT`, `TEST_CHANGED` | code-fu |
| code-fu | `CODED` | test-runner |
| | `TEST_DISPUTED` | tdd-maestro |
| test-runner | `PASS` | pr-create |
| | `FAIL` | code-fu |
| pr-create | `PR_CREATED` | pr-reviewer |
| pr-reviewer | `APPROVED` | merge-evaluator |
| | `CHANGES_NEEDED` | code-fu |
| merge-evaluator | `MERGEABLE` | merger-mage, or End if `merge.enabled` is false |
| | `NOT_MERGEABLE` | code-fu |
| merger-mage | `MERGED` | End |

Any `BLOCKED`, `NEEDS_USER` or `*_FAILED` verdict stops the run. A `FAIL`, `CHANGES_NEEDED` or `NOT_MERGEABLE` that sends the work back to code-fu `limits.retries` times in a row stops it with `RETRY_LIMIT`.

## pull-issue

Picks one eligible GitHub issue and claims it. It has its own doc: `skills/pull-issue.md`.

## tdd

The red, green, refactor loop that tdd-maestro and code-fu share. It has its own doc: `skills/tdd.md`.

## pr-handoff

The Implementer writes it, and the Reviewer and the Merger read it. The pull request description lists:

- the red command and the expected failure;
- the matching green result;
- the broader verification;
- when no test could fail first, the alternate evidence and why.

A green suite without an observed test-first failure does not satisfy this.
