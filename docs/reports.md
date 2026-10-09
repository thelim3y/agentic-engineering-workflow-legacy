# Reports

Each agent writes one report file in the run folder, `.agentic/<ticket>/`, which is not committed. The `ticket` skill gives the next agent the paths of the reports it needs and nothing else.

Every report starts with the agent's verdict. For `BLOCKED` it names the reason, and for `NEEDS_USER` it holds the question. The rest is facts the agent observed, each with the command or file that shows it.

What each agent writes and reads is in its doc in `agents/`. Every agent also reads memory, as `memory.md` says.
