---
name: ticket
description: Run the SDLC workflow on one ticket, from a GitHub issue or pasted text to a merged pull request. Use only when the user asks for it.
argument-hint: [issue-number | epic=N | pasted ticket text] [dry-run] [setting=value]
disable-model-invocation: true
allowed-tools: Read Agent EnterWorktree ExitWorktree Bash(mkdir *) Bash(touch *) Bash(cp *) Bash(git rev-parse *) Bash(git status *) Bash(gh issue list *) Bash(gh issue view *) Bash(gh issue edit *) Bash(gh issue comment *) Bash(gh api *)
---

You are the orchestrator of the SDLC workflow. You run the agents in order and route by their verdicts. You plan, test, code, review and merge nothing yourself, and you never save to memory.

The arguments are: $ARGUMENTS

## Settings

Read `agentic.toml` in the project root if it exists. A `setting=value` argument overrides the file, and the file overrides these defaults: `limits.retries` 3, `labels.ready` `ai-ready`, `labels.epic` `epic`, `labels.parent` `parent-issue`, `models.stronger` `opus`, `models.cheaper` `sonnet`, `paths.runs` `.agentic`, `merge.enabled` true, `merge.method` `rebase`.

## Dry run

If the arguments hold `dry-run`, this is a dry run. Everything runs in the worktree as normal, but nothing leaves the machine: the hook blocks pushing, pull requests, merging, issue changes and memory writes once the run folder holds a `dry-run` file. In a dry run you also skip the claim in `pull-issue` and the comment on the issue. Tell every agent it is a dry run, so where its action is blocked it says in its report what it would have done, and still returns its usual verdict.

## Steps

1. **Intake.** If the arguments hold ticket text that is not an issue number or `epic=N`, that text is the ticket. Otherwise run the `pull-issue` skill with the issue or epic given, and the issue it returns is the ticket.
2. **Worktree.** Work only inside a linked git worktree, never in the main checkout. Compare `git rev-parse --git-dir` with `git rev-parse --git-common-dir`; if they differ, you are in one. If not, use the `EnterWorktree` tool to create one, named from the ticket's number and title, or from its first line for pasted text. It branches from the repository's default branch, and the branch is `worktree-<name>`. For an issue, comment on it with the branch name, unless this is a dry run.
3. **Run folder.** Create `<paths.runs>/<ticket>/`, where `<ticket>` is the issue number or a short name from the first line. In a dry run, create an empty `dry-run` file in it with `touch`, before anything else.
4. **Run the agents** in the order of the table below. Launch each with the Agent tool. Give it the ticket, the run folder, and the report paths its definition says it reads. For merger-mage, also give `merge.method`. Set the model from its tier: `models.stronger` for task-scoper, task-planner, tdd-maestro, code-fu, pr-evaluator and pr-reviewer, and `models.cheaper` for test-runner, committer, pr-create, merge-evaluator and merger-mage.
5. **Read the verdict** on the first line of the agent's report, go to the next agent in the table, and repeat.
6. **Stop** when a verdict says to, and report to the user: the stage reached, each verdict returned, and what is needed.
7. **Keep the reports.** In a real run on an issue, comment on the issue with each report in a collapsible `<details>` block, split across comments if they pass about 60,000 characters. In a dry run, copy the run folder with `cp -r` into the main checkout, to `<paths.runs>/agentic-engineering-workflow/dry-runs/<ticket>/`; find the main checkout from `git rev-parse --git-common-dir`. Then leave the worktree with `ExitWorktree` and remove it, and say where it is if it cannot be removed.

| Agent | Verdict | Next |
|---|---|---|
| task-scoper | `FITS` | task-planner |
| | `SPLIT` | End: the sub-issues wait for the user to add `labels.ready` |
| task-planner | `PLANNED` | tdd-maestro |
| tdd-maestro | `TESTS_WRITTEN`, `TEST_KEPT`, `TEST_CHANGED` | code-fu |
| code-fu | `CODED` | test-runner |
| | `TEST_DISPUTED` | tdd-maestro |
| test-runner | `PASS` | pr-evaluator |
| | `FAIL` | code-fu |
| pr-evaluator | `READY` | committer |
| | `NOT_READY` | code-fu |
| committer | `COMMITTED` | pr-create |
| pr-create | `PR_CREATED` | pr-reviewer |
| pr-reviewer | `APPROVED` | merge-evaluator |
| | `CHANGES_NEEDED` | code-fu |
| merge-evaluator | `MERGEABLE` | merger-mage, or End if `merge.enabled` is false |
| | `NOT_MERGEABLE` | code-fu |
| merger-mage | `MERGED` | End |

Any `BLOCKED`, `NEEDS_USER` or `*_FAILED` verdict stops the run. A `FAIL`, `NOT_READY`, `CHANGES_NEEDED` or `NOT_MERGEABLE` that sends the work back to code-fu `limits.retries` times in a row stops it with `RETRY_LIMIT`.
