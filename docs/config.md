# Configuration

Each project keeps its settings in `agentic.toml` in the project root. A value comes from, in order of priority:

1. An argument passed when a skill runs.
2. `agentic.toml`.
3. The built-in default.

```toml
[limits]
# Attempts at the same step before an agent aborts with RETRY_LIMIT.
retries = 3
# The most files, tests included, that one task may create or change. A task
# that needs more is too large and is split. Smaller tasks are more focused
# steps for the LLM, and give pull requests and code reviews small enough
# for a human to review properly.
max_files = 5

[labels]
# The label that marks an issue as ready for the workflow.
ready = "ai-ready"
# The label that marks an issue as an epic.
epic = "epic"
# The label that marks a split issue as a parent issue.
parent = "parent-issue"

[models]
# The model each tier runs on. The tier of each agent is in agents.md.
# A model alias: haiku, sonnet, opus or fable. A full model ID is not
# accepted when the ticket skill launches an agent.
cheaper = "sonnet"
stronger = "opus"

[github]
# Optional. When any of these is set, the hook runs the agents' commands as
# this account, so branches, commits, issue claims and pull requests show the
# AI account and not you. Leave the section out to run as yourself.
# The account name and repository, written by scripts/ai_account.py init and
# used by its check.
account = "ai-bot"
repo = "owner/name"
# The name of the environment variable that holds the account's token. The
# token itself never goes in this file.
token_env = "AGENTIC_GH_TOKEN"
# The account's own SSH key, used for git over SSH.
ssh_key = "~/.ssh/ai_key"
# The commit identity of the account.
author_name = "AI Bot"
author_email = "ai@example.com"

[paths]
# The folder that holds each run's reports. It is not committed.
runs = ".agentic"
# Globs of the project's test files. tdd-maestro may edit only these, and
# code-fu may edit none of them. No default: the hook denies both until it is set.
tests = ["tests/**"]

[merge]
# Whether the merger-mage runs at all.
enabled = true
# Whether a human must review and approve the pull request before it is
# merged and its task closed. When true, merge-evaluator returns NEEDS_USER
# until a human has approved.
human_review = true
# How merger-mage merges: "rebase", "merge" or "squash". If the repository
# does not allow it, merger-mage falls back to a merge commit.
method = "rebase"
```
