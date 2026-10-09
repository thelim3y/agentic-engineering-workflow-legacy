# Skills

## ticket

The orchestrator and the entry point: `/ticket <GitHub issue or pasted text>`. It runs the Planner, the TDD agent, the Implementer, the Reviewer and, if enabled, the Merger in order. A pull request that is not approved goes back to the Implementer.

## tdd

Used by the TDD agent and the Implementer. Every change follows a red, green, refactor loop:

1. Add the smallest focused test of the public behaviour.
2. Run it before changing production behaviour and confirm that it fails for the intended reason.
3. Make only the production change needed to pass it.
4. Rerun the same command and confirm that it passes.
5. Repeat for negative, boundary, cancellation and lifetime behaviour.
6. Refactor only while the suite stays green.

A compile failure caused only by a genuinely absent new API is a valid first red. If no test can fail first, as with a pure refactor or a performance change, pick specific executable evidence instead and record why.

Tests exercise public behaviour, never private implementation. The TDD agent writes and owns the tests. The Implementer does not change them and asks the TDD agent when it thinks one is wrong.

## pr-handoff

The Implementer writes it, and the Reviewer and the Merger read it. The pull request description lists:

- the red command and the expected failure;
- the matching green result;
- the broader verification;
- when no test could fail first, the alternate evidence and why.

A green suite without an observed test-first failure does not satisfy this.
