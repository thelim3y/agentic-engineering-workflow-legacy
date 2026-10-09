# Configuration

Each project keeps its settings in `agentic.toml` in the project root. A value comes from, in order of priority:

1. An argument passed when a skill runs.
2. `agentic.toml`.
3. The built-in default.

```toml
[limits]
# How many times an agent may attempt the same step before it aborts with
# RETRY_LIMIT.
attempts_per_step = 3
# How many times in a row a run may send the work back to code-fu, after a
# failed test run, a review or a merge check, before it stops with RETRY_LIMIT.
rework_loops = 3
# The most files, tests included, that one task may create or change. A task
# that needs more is too large and is split. Smaller tasks are more focused
# steps for the LLM, and give pull requests and code reviews small enough
# for a human to review properly.
max_files_per_task = 5

[labels]
# The label that marks an issue as ready for the workflow.
ai_ready = "ai-ready"
# The label that marks an issue as an epic.
epic = "epic"
# The label that marks a split issue as a parent issue.
parent_issue = "parent-issue"

[models]
# The model each tier runs on. The tier of each agent is in agents.md.
# A model alias: haiku, sonnet, opus or fable. A full model ID is not
# accepted when the ticket skill launches an agent.
cheaper_tier = "sonnet"
stronger_tier = "opus"

# Optional. With this section, the hook runs the agents' commands as the AI's
# own GitHub account, so branches, commits, issue claims and pull requests
# show that account and not you. Leave it out to run as yourself.
# scripts/ai_account.py init writes it.
[github]
# The AI's GitHub account name, and the repository it works in.
ai_account = "ai-bot"
repo = "owner/name"
# The name of the environment variable that holds the account's token. The
# token itself never goes in this file.
token_env_var = "AGENTIC_GH_TOKEN"
# The path to the account's own SSH key, used for git over SSH.
ssh_key_path = "~/.ssh/ai_key"
# The name and email on the account's commits.
commit_author_name = "AI Bot"
commit_author_email = "ai@example.com"

[paths]
# The folder that holds each run's reports. It is not committed.
run_folder = ".agentic"
# Globs of the project's test files. tdd-maestro may edit only these, and
# code-fu may edit none of them. There is no default: the hook denies both
# until you set it, for example test_files = ["tests/**"].
# test_files = []

[merge]
# Whether merger-mage merges the pull request. When false, a human merges.
merge_automatically = true
# Whether a human must review and approve the pull request before it is
# merged and its task closed. When true, merge-evaluator returns NEEDS_USER
# until a human has approved.
require_human_review = true
# How merger-mage merges: "rebase", "merge" or "squash". If the repository
# does not allow it, merger-mage falls back to a merge commit.
merge_method = "rebase"
```
