# Testing

Three layers, from cheapest to most faithful.

1. **Hook tests.** `tests/test_enforce.py` checks every file and command rule of the hook with unit tests. They run in seconds and need no GitHub.
2. **Dry run.** `/ticket dry-run` runs every stage on a real ticket, with local changes real but disposable and remote changes blocked.
3. **A real run** on a scratch repository, with a small test issue, from `ai-ready` issue to merged pull request.

## Dry run

- The run happens in a disposable git worktree. The branch, the tests, the code and the commit are real there, and they are removed afterwards.
- Anything that reaches outside the machine is blocked by the hook: `git push`, creating a pull request, merging, and creating, editing, commenting on, closing or attaching issues.
- pr-create, merger-mage and any agent whose action is blocked report what it would have done, in its report, and return its usual verdict.
- Reports are written to the run folder as normal, so routing, verdicts and reports are all exercised.
