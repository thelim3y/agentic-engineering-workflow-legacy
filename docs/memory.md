# Memory

The workflow uses [engram](https://github.com/Gentleman-Programming/engram) (MIT) to carry lessons from one run to the next. Reports within a run are files, not memory.

## Who reads and writes

Every agent reads memory. Only test-runner and pr-reviewer write to it, because they record what they observed from outside the code. code-fu is read-only.
