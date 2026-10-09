# Memory

The workflow uses [engram](https://github.com/Gentleman-Programming/engram) (MIT) to carry lessons from one run to the next. Reports within a run are files, not memory.

## Who reads and writes

Every agent reads memory. Only test-runner and pr-reviewer write to it, because they record what they observed from outside the code. code-fu is read-only.

## What they write

- test-runner records repeated failures.
- pr-reviewer records repeated findings.

## When an item counts as repeated

The first time an agent sees an item, it saves it with a count of one. Each later sighting of the same item, saved under the same topic key, raises the count. An item is a lesson once its count reaches two, and agents reading memory ignore entries below two.
