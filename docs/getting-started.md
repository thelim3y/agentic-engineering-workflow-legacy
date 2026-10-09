# Getting started

How to set up the plugin on a project and try a dry run. A dry run does the work in a disposable worktree and changes nothing outside your machine.

## Requirements

- Claude Code with plugin support.
- `git`, and the GitHub CLI `gh` signed in (`gh auth status`).
- Python 3.11 or later, for the hook script.
- `jq` and `curl`, which the engram plugin's hooks need.

## 1. Check the plugin

From a clone of this repository:

```bash
claude plugin validate .
python3 -m unittest discover -s tests
```

Both must pass.

## 2. Install engram

engram carries lessons between runs.

```bash
brew install gentleman-programming/tap/engram
claude plugin marketplace add Gentleman-Programming/engram
claude plugin install engram
engram setup claude-code
```

Without Homebrew, see engram's `docs/INSTALLATION.md` for `go install` and binary downloads.

## 3. Prepare the project

To try the workflow on a throwaway project, let the script make one:

```bash
python3 scripts/setup_scratch.py ../agentic-scratch
```

It creates a tiny Python project with tests, an `agentic.toml`, a `.gitignore` for the run folder and a `CLAUDE.md` with the test command, and commits it. Nothing leaves your machine. To also create a private GitHub repository with the three labels, an epic and two ready issues (one small, one too large, so you can try a split), add `--github OWNER/NAME`.

To use your own project instead:

In the project you want to run the workflow on:

1. Create `agentic.toml` in the project root. Only `paths.tests` is required; everything else has a default (see `config.md`).

   ```toml
   [paths]
   tests = ["tests/**"]
   ```

2. Add the run folder to `.gitignore`:

   ```text
   .agentic/
   ```

3. For tickets that come from GitHub issues, create the labels:

   ```bash
   gh label create ai-ready
   gh label create epic
   gh label create parent-issue
   ```

   A ticket pasted as text needs none of this.

## 4. Start Claude Code with the plugin

```bash
claude --plugin-dir /path/to/agentic-engineering-workflow
```

Plugin skills and agents are namespaced under the plugin name, so the skill is `/agentic-engineering-workflow:ticket`.

## 5. Run a dry run

The simplest first dry run uses a ticket pasted as text, so it needs no issue:

```text
/agentic-engineering-workflow:ticket dry-run Add a function that returns the sum of two numbers
```

For a GitHub issue, give its number:

```text
/agentic-engineering-workflow:ticket dry-run 42
```

## 6. Check the result

- The reports are copied to `.agentic/agentic-engineering-workflow/dry-runs/<ticket>/` in your project, because the worktree is removed.
- The run folder holds one report per agent. Each starts with its verdict, and together they show the route the run took.
- Nothing changed on GitHub: no pull request, comment, assignment, sub-issue or merge.
- No tracked file in your main checkout changed. The work happened in a worktree, which a dry run removes at the end.
- No new entry was saved to engram.

If a command was blocked, the reason names the rule, and `hooks.md` explains each one.

## Next

Once a dry run completes, try a real run on a scratch repository, as `testing.md` describes.
