# Plan

- [x] Fetch main/remote branch, record ancestry, preserve existing working state.
- [x] Confirm merge target and authorize the local merge under this Task.
- [x] Stash exact old dirty paths and prepare the real uncommitted merge.
- [x] Review conflict resolutions, incoming ownership design and native routing.
- [x] Reproduce verified behavior gaps; repair shared helpers/peers and document contracts.
- [x] Run selected regressions, package validation and native Spec/Standards check.
- [x] Complete local merge, restore and verify prior work, record continuation/memory.

Selected gates: targeted lock/adoption/profile tests, meaningful regression failures,
package validation, Bash syntax, Task context validation and diff checks. Because
merging old/new shared installers affects five profiles, run the stable combined
unittest suite in an isolated HOME after integration. PowerShell runtime tests use
an available isolated native runtime; actual Windows/app/MCP acceptance stays not_run
when unavailable. Do not install packages into the real HOME or change its config.
