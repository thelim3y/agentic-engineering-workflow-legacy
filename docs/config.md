# Configuration

Each project keeps its settings in `agentic.toml` in the project root. A value comes from, in order of priority:

1. An argument passed when a skill runs.
2. `agentic.toml`.
3. The built-in default.

```toml
[limits]
# Attempts at the same step before an agent aborts with RETRY_LIMIT.
retries = 3

[labels]
# The label that marks an issue as ready for the workflow.
ready = "ai-ready"
# The label that marks an issue as an epic.
epic = "epic"

[models]
# The model each tier runs on. The tier of each agent is in agents.md.
# A model alias (haiku, sonnet, opus, fable) or a full model ID.
cheaper = "haiku"
stronger = "sonnet"

[paths]
# The folder that holds each run's reports. It is not committed.
runs = ".agentic"
# Globs of the project's test files. tdd-maestro may edit only these, and
# code-fu may edit none of them. No default: the hook denies both until it is set.
tests = ["tests/**"]

[merge]
# Whether the merger-mage runs at all.
enabled = true
```
