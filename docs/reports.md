# Reports

Each agent writes one report file in the run folder, `.agentic/<ticket>/`, which is not committed. The `ticket` skill gives the next agent the paths of the reports it needs and nothing else.

Every report starts with the agent's verdict. For `BLOCKED` it names the reason, and for `NEEDS_USER` it holds the question. The rest is facts the agent observed, each with the command or file that shows it.

## What each report holds

| Agent | Report | Holds |
|---|---|---|
| task-scoper | `scope.md` | Why the task fits or was split; for a split, the number and title of each sub-issue |
| task-planner | `plan.md` | The behaviours to build, the files involved, and what is out of scope |
| tdd-maestro | `tests.md` | The tests written, the red command, the failure it was expected to show and the failure observed; for a disputed test, the ruling; when no test could fail first, the alternate evidence and why |
| code-fu | `code.md` | The files changed and the check it ran; for a disputed test, the test and why |
| test-runner | `run.md` | The commands run and their results, the failing tests with their output, and any rerun |
| pr-create | `pr.md` | The pull request number and link, and the branch |
| pr-reviewer | `review.md` | Each finding with its file and line |
| merge-evaluator | `merge.md` | Each merge condition checked, and its state |
| merger-mage | `merged.md` | The merge and the commit it made |

## Who reads what

| Agent | Reads |
|---|---|
| task-scoper | The ticket |
| task-planner | The ticket, `scope.md` |
| tdd-maestro | `plan.md`, and `code.md` when it rules on a disputed test |
| code-fu | `plan.md`, `tests.md`, and the latest `run.md`, `review.md` or `merge.md` that sent the work back |
| test-runner | `tests.md` |
| pr-create | `plan.md`, `tests.md`, `run.md` |
| pr-reviewer | The ticket, the diff and the tests; never `code.md`, so it reviews without knowing how the code was written |
| merge-evaluator | `pr.md`, `review.md` |
| merger-mage | `merge.md` |

Every agent also reads memory, as `memory.md` says.
