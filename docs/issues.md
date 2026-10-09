# Issues

Rules for the issues the workflow works on.

- Every task issue has a parent epic. The first lines of its body say `Parent epic: #E`.
- An epic is an issue labelled `epic`. Epics are parents, never tasks.
- Only an issue labelled `ai-ready` is picked up.
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

When an issue is picked, it is assigned to the user and gets a comment naming the branch. An assigned issue or one named by an open pull request counts as claimed, so parallel runs never take the same issue.
