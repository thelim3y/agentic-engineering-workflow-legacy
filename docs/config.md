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
# Left out, the tier runs on the session model.
# cheaper = ""
# stronger = ""

[merge]
# Whether the merger-mage runs at all.
enabled = true
```
