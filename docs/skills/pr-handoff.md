# pr-handoff

The format of the pull request description. pr-create writes it, and pr-reviewer and merge-evaluator read it.

## Contents

1. **Summary.** What the change does and why, in a few sentences from the plan. For a GitHub issue, it ends with `Closes #N`.
2. **Test-first evidence.**
   - The red command and the failure it was expected to show, from tdd-maestro's report.
   - The matching green result, from test-runner's report.
   - When no test could fail first, the alternate evidence and why, as `tdd.md` says.
3. **Verification.** The full suite run by test-runner and its result, and any other check that ran.

A green suite without an observed test-first failure does not satisfy this.

## Rules

pr-create takes every result from the agents' reports and runs no test itself. A result it cannot find in a report is left out and named as missing, never invented.
