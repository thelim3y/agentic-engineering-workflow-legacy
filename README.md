# agentic-engineering-workflow

Project-agnostic SDLC agents and skills that carry a ticket to a merged pull request.

## What it does

A ticket comes in as a GitHub issue or as pasted text. The workflow takes it through:

1. **Intake.** The ticket is read from the issue or from the pasted text.
2. **Planning.** The task is planned.
3. **Splitting.** A task that is too large is split into sub-issues, and each sub-issue is planned in turn.
4. **Tests first.** The tests that define the task are written before any code.
5. **Coding.** The code that passes those tests is written.
6. **Testing.** The full test suite is run.
7. **Pull request review.** A reviewer agent reads the pull request.
8. **Final check and merge.** An optional agent makes the last checks and merges.

It is built from agents and skills, and it does not assume any one project.

## Flow

```mermaid
flowchart TD
    ticket["Intake<br/>GitHub issue or pasted text"] --> plan["Planning"]
    plan --> large{"Too large?"}
    large -- yes --> split["Split into sub-issues"]
    split --> plan
    large -- no --> tests["Tests first"]
    tests --> code["Coding"]
    code --> test["Testing"]
    test --> pr["Open the pull request"]
    pr --> review["PR reviewer agent"]
    review --> ok{"Approved?"}
    ok -- no --> code
    ok -- yes --> merge["Final check and merge agent<br/>optional"]
    merge --> done(["Merged"])
```
