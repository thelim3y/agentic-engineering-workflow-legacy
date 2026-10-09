# pull-issue

Picks one eligible GitHub issue and claims it. The `ticket` skill runs it when the ticket is a GitHub issue and not pasted text.

## Arguments

Both are optional.

- **An issue number:** use that issue. If it is not eligible, say why and stop; never substitute another.
- **An epic number:** take the first eligible child of that epic.

With neither, it takes the first eligible issue the search returns.

## Settings

`labels.ready` and `labels.epic` in `agentic.toml`.

## Steps

1. List the open issues labelled `labels.ready` and not labelled `labels.epic`.
2. Keep the eligible ones, by the rules in `issues.md`.
3. Choose one by the arguments above.
4. Claim it, as `issues.md` says.
5. Return the issue in full. The epic body is read only to find the order of its children.

If no issue is eligible, list what blocks each candidate and stop.

## Tools

`Bash`, for `gh`.
