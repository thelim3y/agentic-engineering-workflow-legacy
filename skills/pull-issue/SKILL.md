---
name: pull-issue
description: Pick one eligible GitHub issue and claim it. Use when the ticket is a GitHub issue and not pasted text.
argument-hint: [issue-number | epic=N]
allowed-tools: Bash(gh issue list *) Bash(gh issue view *) Bash(gh issue edit *) Bash(gh pr list *) Bash(gh api *)
---

Pick one issue to work on and claim it. The arguments are: $ARGUMENTS

Settings come from `agentic.toml` (`labels.ready`, `labels.epic`, `labels.parent`), with the defaults `ai-ready`, `epic` and `parent-issue`.

## Steps

1. List the open issues labelled `labels.ready` and not labelled `labels.epic` or `labels.parent`, with `gh issue list`.
2. Keep the eligible ones. An issue is eligible when:
   - every issue listed under its `## Dependencies` heading is closed;
   - no open pull request names it;
   - it is not assigned to someone else;
   - it is the first open child in its epic's stated order. The epic is named on its `Parent epic: #E` line, and the epic body ends with its children as `#a, #b, #c, in that order`. A sub-issue takes its parent issue's epic.
3. Choose one:
   - With an issue number, use that issue. If it is not eligible, say why and stop; never substitute another.
   - With `epic=N`, take the first eligible child of that epic.
   - With neither, take the first eligible issue the search returns.
4. A parent issue is never picked. Its open sub-issues are, first in GitHub's sub-issue order. List them with `gh api repos/{owner}/{repo}/issues/{number}/sub_issues`.
5. Claim it by assigning it to the user with `gh issue edit --add-assignee @me`. In a dry run, skip this step.
6. Return the issue in full. Read the epic body only to find the order of its children.

If no issue is eligible, list what blocks each candidate and stop.
