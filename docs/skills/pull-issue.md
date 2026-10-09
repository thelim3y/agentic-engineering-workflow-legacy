# pull-issue

Picks one eligible GitHub issue and claims it. The `ticket` skill runs it when the ticket is a GitHub issue and not pasted text.

## Arguments

Both are optional.

- **An issue number:** use that issue. If it is not eligible, say why and stop; never substitute another.
- **An epic number:** take the first eligible child of that epic.

With neither, it takes the first eligible issue the search returns.

## Settings

`labels.ai_ready`, `labels.epic` and `labels.parent_issue` in `agentic.toml`.

## Steps

1. List the open issues labelled `labels.ai_ready` and not labelled `labels.epic` or `labels.parent_issue`.
2. Keep the eligible ones, by the rules in `issues.md`.
3. Choose one by the arguments above.
4. Assign it to the user. The `ticket` skill comments with the branch name once the branch exists.
5. Return the issue in full. The epic body is read only to find the order of its children.

A parent issue is never picked. Its open sub-issues are, first in GitHub's sub-issue order.

If no issue is eligible, list what blocks each candidate and stop.

## Tools

`Bash`, for `gh`.
