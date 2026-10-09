---
name: tdd
description: The red, green, refactor loop shared by tdd-maestro and code-fu. Use when writing tests or code for a change.
---

Every change follows a red, green, refactor loop. tdd-maestro does the red steps and code-fu does the green and refactor steps.

1. **Red, by tdd-maestro.** Add the smallest focused test of the public behaviour. Run it before any production code changes, and confirm that it fails for the intended reason. A compile failure caused only by a genuinely absent new API is a valid first red.
2. **Green, by code-fu.** Make only the production change needed to pass that test. Rerun the same command and confirm that it passes.
3. **Repeat.** tdd-maestro adds the next test for negative, boundary, cancellation and lifetime behaviour, and code-fu passes it. Each test starts with an observed failure.
4. **Refactor, by code-fu.** Only while the suite stays green.

## When no test can fail first

For a pure refactor or a performance change, tdd-maestro picks specific executable evidence instead, runs it, and records why no test could fail first. It is for the odd change, and it does not excuse a test that could be written.

## Disputed tests

code-fu never edits a test. When it thinks one is wrong, it returns `TEST_DISPUTED`, and tdd-maestro rules on it.

## Tests

Tests exercise public behaviour, never private implementation.
