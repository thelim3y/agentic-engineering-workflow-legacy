---
name: pr-handoff
description: The format of the pull request description. Use when writing a pull request.
---

Write the pull request description with these parts.

1. **Summary.** What the change does and why, in a few sentences from the plan. For a GitHub issue, end with `Closes #N`.
2. **Test-first evidence.**
   - The red command and the failure it was expected to show, from tdd-maestro's report.
   - The matching green result, from test-runner's report.
   - When no test could fail first, the alternate evidence and why.
3. **Verification.** The full suite run by test-runner and its result, and any other check that ran.

A green suite without an observed test-first failure does not satisfy this.

Take every result from the agents' reports. Run no test yourself. A result you cannot find in a report is left out and named as missing, never invented.
