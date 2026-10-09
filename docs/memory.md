# Memory

The workflow uses [engram](https://github.com/Gentleman-Programming/engram) (MIT) to carry lessons from one run to the next. Reports within a run are files, not memory.

## Who reads and writes

Every agent reads memory. Only test-runner and pr-reviewer write to it, because they record what they observed from outside the code. code-fu is read-only.

## What they write

- test-runner records repeated failures.
- pr-reviewer records repeated findings.

## When an item counts as repeated

The first time an agent sees an item, it saves it with a count of one. Each later sighting of the same item, saved under the same topic key, raises the count. A lesson is an item whose count has reached two. Agents reading memory ignore entries below two.

## Scope

A lesson belongs to one project. Nothing is shared across projects.

## Where it lives

On the user's machine, in engram's local database. Nothing is committed to the repository.

## How agents reach it

Through engram's Claude Code plugin, which brings its hooks, and engram's MCP server, which `scripts/install_engram.py` registers at local scope. The MCP server gives 19 tools, named `mcp__engram__<tool>`. The plugin alone gives no tools.

## The plugin's hooks

| Hook | What it does | Effect on our rules |
|---|---|---|
| `SessionStart` | Starts the engram server, opens a session, and injects the memory protocol and recent context into the main session | Subagents do not get it, so each reads memory with `mem_search` |
| `UserPromptSubmit` | In the main session, loads the engram tools and nudges it to save every 15 minutes | The `ticket` skill never saves to memory, whatever the nudge says |
| `SubagentStop` | Sends each subagent's final message to engram, which saves only the items under a `## Key Learnings:` heading and ignores all other text | No agent writes that heading; the `rules.md` rule below keeps the capture empty |
| `PreToolUse` | Binds the session on write calls | None |
| `SessionEnd` and compaction recovery | Marks the session ended and restores context after compaction | None |

Only test-runner and pr-reviewer have `mem_save` in their tools, so no other agent can save through the tool. Passive capture bypasses the tools list, which is why no agent writes the `## Key Learnings:` heading. The protocol engram injects tells agents to write it, and whether subagents see that protocol is not verified.
