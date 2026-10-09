# Hooks

One plugin-level `PreToolUse` hook enforces the limits the `tools` allowlist cannot. It matches `Edit`, `Write` and `Bash`, reads the tool input and `agent_type`, and denies a call that breaks a rule below with a reason naming the agent and the rule. A call from the main session has no `agent_type`, and the hook lets it through.

The hook is at plugin level because hooks in a subagent's frontmatter are ignored for plugin subagents.

## File rules

| Agent | Denied |
|---|---|
| tdd-maestro | `Edit` or `Write` on any file that does not match `paths.tests` |
| code-fu | `Edit` or `Write` on any file that matches `paths.tests` |

If `paths.tests` is not set, the hook denies both agents' edits and says to set it.

## Command rules

| Agent | `Bash` is limited to |
|---|---|
| task-scoper | `gh issue` commands, and `gh api` on the sub-issues endpoint |
| tdd-maestro | Build and test commands; no `git push` and no `gh` |
| code-fu | Build and test commands; no `git push` and no `gh` |
| test-runner | Build and test commands; no `git` and no `gh` |
| pr-evaluator | `git status`, `git diff` and `git log` |
| committer | `git status`, `git diff`, `git add` and `git commit` |
| pr-create | `git status`, `git log`, `git push` and `gh pr create` |
| pr-reviewer | `git diff`, `git log` and read-only `gh pr` commands |
| merge-evaluator | Read-only `gh pr` commands |
| merger-mage | `gh pr view`, `gh pr merge`, `gh issue close`, and `gh api` reads of the sub-issues endpoint |

## The ticket skill

The `ticket` skill, with `pull-issue`, runs in the main session. There the hook sees no `agent_type` and does not know which skill is active, so it cannot enforce a skill's limits. These are the skill's `allowed-tools` pre-approvals instead, which let it run without prompts and leave every other command to the normal permission prompt:

| Command | Used for |
|---|---|
| `mkdir` | Creating the run folder |
| `git rev-parse` | Checking whether it is in a linked worktree |
| `git status` | Checking the working tree is clean |
| `gh issue list` and `gh issue view` | Finding and reading the issue |
| `gh api` reads of the sub-issues endpoint | Finding the open sub-issues of a parent issue |
| `gh issue edit` | Assigning the issue to the user |
| `gh issue comment` | Naming the branch on the issue |
