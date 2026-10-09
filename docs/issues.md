# Issues

Rules for the issues the workflow works on.

- Every task issue has a parent epic. The first lines of its body say `Parent epic: #E`. A sub-issue's parent epic is its parent issue's.
- An epic is an issue labelled `epic`. Epics are parents, never tasks.
- A parent issue is an issue that was split. It is labelled `parent-issue` and has the pieces as native GitHub sub-issues. Its text is not the task, because its sub-issues fulfil it. Like an epic, it is never picked.
- Only an issue labelled `ai-ready` is picked up.
- Only the user sets `ai-ready`. No agent adds it, and sub-issues the task-scoper creates wait for it.
- The skill that pulls an issue can be given an epic. With no epic, it takes the first result of the search.

## Eligible issues

An issue is eligible when all of these hold:

- It is open, labelled `ai-ready`, and not labelled `epic`.
- Every issue listed under its `## Dependencies` heading is closed.
- No open pull request names it.
- It is not assigned to someone else.
- It is the first open child in its epic's stated order. The epic body ends with its children as `#a, #b, #c, in that order`.

If none is eligible, the skill lists what blocks each candidate and stops.

## Claiming

When an issue is picked, it is assigned to the user. Once the branch exists, a comment on the issue names it. An assigned issue, or one named by an open pull request, counts as claimed, so parallel runs never take the same issue.

## Splitting

A large task is split so that each piece is a more focused step for the LLM, and so that each pull request and code review is small enough for a human to review when one is required (`merge.human_review`).

When the task-scoper splits an issue, it creates each piece as a sub-issue attached to the original, and labels the original `parent-issue`. Each sub-issue is its own run, with its own branch, one commit and one pull request, so no pull request is large. The sub-issues get no `ai-ready` label. The original's text is not changed. The native sub-issue list is the source of truth for order.

When the last sub-issue of a parent issue is closed, merger-mage closes the parent. If merging is turned off, the user closes it.
