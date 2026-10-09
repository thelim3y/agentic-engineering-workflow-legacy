# Testing

Three layers, from cheapest to most faithful.

1. **Script tests.** `tests/test_enforce.py` checks every file, command and dry-run rule of the hook, and `tests/test_setup_scratch.py` checks the scratch setup script. They run in seconds and need no GitHub.
2. **Dry run.** `/ticket dry-run` runs every stage on a real ticket, with local changes real but disposable and remote changes blocked.
3. **A real run** on a scratch repository, made with `scripts/setup_scratch.py`,, with a small test issue, from `ai-ready` issue to merged pull request.

## Dry run

- Every run, dry or not, happens in a linked git worktree. In a dry run the worktree is disposable: the branch, the tests, the code and the commit are real there, and they are removed afterwards.
- Anything that reaches outside the machine is blocked by the hook: `git push`, creating a pull request, merging, and creating, editing, commenting on, closing or attaching issues.
- pr-create, merger-mage and any agent whose action is blocked report what it would have done, in its report, and return its usual verdict.
- Reports are written to the run folder as normal, so routing, verdicts and reports are all exercised.
