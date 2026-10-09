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
| task-scoper | `gh issue` commands |
| tdd-maestro | Build and test commands; no `git push` and no `gh` |
| code-fu | Build and test commands; no `git push` and no `gh` |
| test-runner | Build and test commands; no `git` and no `gh` |
| pr-create | `git status`, `git log`, `git diff`, `git push` and `gh pr create` |
| pr-reviewer | `git diff`, `git log` and read-only `gh pr` commands |
| merge-evaluator | Read-only `gh pr` commands |
| merger-mage | `gh pr view` and `gh pr merge` |
