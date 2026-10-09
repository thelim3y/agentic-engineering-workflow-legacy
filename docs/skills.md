# Skills

## ticket

The orchestrator and the entry point: `/ticket`. It takes a GitHub issue number, an epic number, pasted ticket text, or nothing. Any argument also overrides the matching setting in `agentic.toml`.

1. **Intake.** With pasted text, that text is the ticket. Otherwise it runs `pull-issue` with the issue or epic given.
2. **Run the agents** in the order below. After each agent it reads the verdict and goes to the next agent in the table. It does nothing else: it plans, codes and reviews nothing itself.
3. **Stop** when a verdict says to, and report to the user: the stage reached, each verdict returned, and what is needed.

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

Used by `ticket` when the ticket is a GitHub issue and not pasted text. It picks one issue by the rules in `issues.md` and claims it. Both arguments are optional:

- **An issue number:** use that issue. If it is not eligible, say why and stop; never substitute another.
- **An epic number:** take the first eligible child of that epic.
- **Nothing:** take the first eligible issue the search returns.

It returns the issue in full. The epic body is read only to find the order of its children.

## tdd

Used by the TDD agent and the Implementer. Every change follows a red, green, refactor loop:

1. Add the smallest focused test of the public behaviour.
2. Run it before changing production behaviour and confirm that it fails for the intended reason.
3. Make only the production change needed to pass it.
4. Rerun the same command and confirm that it passes.
5. Repeat for negative, boundary, cancellation and lifetime behaviour.
6. Refactor only while the suite stays green.

A compile failure caused only by a genuinely absent new API is a valid first red. If no test can fail first, as with a pure refactor or a performance change, pick specific executable evidence instead and record why.

Tests exercise public behaviour, never private implementation. The TDD agent writes and owns the tests. The Implementer does not change them and asks the TDD agent when it thinks one is wrong.

## pr-handoff

The Implementer writes it, and the Reviewer and the Merger read it. The pull request description lists:

- the red command and the expected failure;
- the matching green result;
- the broader verification;
- when no test could fail first, the alternate evidence and why.

A green suite without an observed test-first failure does not satisfy this.
