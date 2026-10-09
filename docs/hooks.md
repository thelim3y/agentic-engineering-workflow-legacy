# Hooks

One plugin-level `PreToolUse` hook enforces the limits the `tools` allowlist cannot. It matches `Edit`, `Write` and `Bash`, reads the tool input and `agent_type`, and denies a call that breaks a rule below with a reason naming the agent and the rule. A call from the main session has no `agent_type`, and the hook lets it through.

The hook is at plugin level because hooks in a subagent's frontmatter are ignored for plugin subagents.

## File rules

Every agent may write in the run folder, `paths.run_folder` in `agentic.toml`, which is where reports go. Every agent except the two below is denied a write anywhere else.

| Agent | Denied |
|---|---|
| tdd-maestro | `Edit` or `Write` on any file that does not match `paths.test_files` |
| code-fu | `Edit` or `Write` on any file that matches `paths.test_files` |

If `paths.test_files` is not set, the hook denies both agents' edits and says to set it.

## Command rules

An agent on a list may also run plain reads: `ls`, `cat`, `head`, `tail`, `wc`, `pwd`, `grep`, `rg`, `find` without `-delete` or `-exec`, `stat`, `diff`, `sort`, `uniq`, `tree`, `file`, `git ls-files` and `git rev-parse`.

| Agent | `Bash` is limited to |
|---|---|
| task-scoper | `gh issue` commands, `gh repo view`, and `gh api` on the sub-issues endpoint |
| tdd-maestro | Build and test commands; no `git push` and no `gh` |
| code-fu | Build and test commands; no `git push` and no `gh` |
| test-runner | Build and test commands; no `git` and no `gh` |
| pr-evaluator | `git status`, `git diff` and `git log` |
| committer | `git status`, `git diff`, `git add` and `git commit` |
| pr-create | `git status`, `git log`, `git push` and `gh pr create` |
| pr-reviewer | `git diff`, `git log` and read-only `gh pr` commands |
| merge-evaluator | Read-only `gh pr` commands |
| merger-mage | `gh pr view`, `gh pr merge`, `gh issue close`, and `gh api` reads of the sub-issues endpoint |

## Running as the AI account

If `agentic.toml` has a `[github]` section, the hook also rewrites each agent's `Bash` command so that it runs as that account. It puts `export` of `GH_TOKEN` (taken from the variable `github.token_env_var` names), the git author and committer name and email, and `GIT_SSH_COMMAND` with the account's key in front of the command. The token is passed as a reference to the variable and is never written into the command or the log. If the variable is not set, the command is denied, so nothing runs as you by mistake. The rewrite does not decide permission, so the usual permission rules still apply to the rewritten command. The main session is not rewritten.

## Dry run

While a `dry-run` file exists in `<paths.run_folder>/<ticket>/` of the worktree, the same hook also denies, for every caller including the main session:

- `git push`;
- any `gh` command other than `gh issue view`, `list` and `status`, `gh pr view`, `diff`, `checks`, `list` and `status`, and `gh repo view`;
- `gh api` with a method other than GET, or with `-f`, `-F`, `--field`, `--raw-field` or `--input`;
- the engram `mem_save` tool.

Local edits, commits and tests are not blocked.

## The ticket skill

The `ticket` skill, with `pull-issue`, runs in the main session. There the hook sees no `agent_type` and does not know which skill is active, so it cannot enforce a skill's limits. These are the skill's `allowed-tools` pre-approvals instead, which let it run without prompts and leave every other command to the normal permission prompt:

| Command | Used for |
|---|---|
| `mkdir` | Creating the run folder |
| `cp` | Copying a dry run's reports out of the worktree |
| `gh issue comment` | Posting the reports to the issue in a real run |
| `git rev-parse` | Checking whether it is in a linked worktree |
| `git status` | Checking the working tree is clean |
| `gh issue list` and `gh issue view` | Finding and reading the issue |
| `gh api` reads of the sub-issues endpoint | Finding the open sub-issues of a parent issue |
| `gh issue edit` | Assigning the issue to the user |
| `gh issue comment` | Naming the branch on the issue |
