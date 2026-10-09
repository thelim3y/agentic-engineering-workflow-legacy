# Issues

Rules for the issues the workflow works on.

- Every task issue has a parent epic. The first lines of its body say `Parent epic: #E`.
- An epic is an issue labelled `epic`. Epics are parents, never tasks.
- Only an issue labelled `ai-ready` is picked up.
- The skill that pulls an issue can be given an epic. With no epic, it takes the first result of the search.
