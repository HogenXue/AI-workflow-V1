# Verification

## Scope and review

- Base: main `4f3753f9dce612a45b4e09fa5d1f17bddc802c1e`.
- Branch: `codex/fix-main-ci-portability`; independent clone under the Codex task directory.
- The existing Projects/CodexTamplate main working tree has unrelated tracked deletions and task/journal changes. None are included or edited.
- Requirements: keep the exact empty-HOME assertions; real Python helpers execute in the CRLF regression shim; preserve failed exit status/stderr, lock metadata and backup contents.
- Standards: local changes remain in the installer layer. Native PowerShell parsing is unchanged. No workflow checks or assertions are disabled. Use the native trellis-check source/checklist because its direct tool is not exposed; `.agents/skills` is absent in this clone.

## Confirmed causes

1. Native Python CRLF output survives Bash command substitution as trailing CR. The unmodified installer fails the new real-helper CRLF preview/copy and lock-adoption tests with `source skill not found: .../skills/memory`.
2. PowerShell 7.5.4 startup alone, with `-NoProfile -Command 'exit 0'`, creates `.cache/powershell` and `.local/share/powershell` beneath an isolated HOME on macOS. This precedes installer code. Separate fixture-owned XDG roots let the existing empty-HOME assertions test the installer itself.

## Local results

- Before implementation, new CRLF tests: 2 expected failures. Failed catalog exit-code regression already passes on the baseline.
- After implementation, `test_aihero_install.py`: 9 passed, no skips (portable PowerShell 7.5.4 in /tmp).
- After implementation, `test_host_preservation.py`: 17 passed, no skips, including runtime-only startup and all Bash/PowerShell previews.
- Bash syntax and `git diff --check`: passed.
- Full suite on macOS/Python 3.12 with the temporary PowerShell runtime: 316 tests, OK in 162.287 seconds; 7 existing Windows-only skips (CMD launcher/fixtures, junction/device namespace).
- Package validation passed for all 20 Skills; AST parsing passed for 34 Python files and Bash syntax for 17 scripts.
- Native task context validation and final Git diff checks passed. Spec and Standards review found no remaining violations in the authorized changes.
- First push `7bcd6ef`, run https://github.com/HogenXue/AI-workflow-V1/actions/runs/41790118589: macOS passed (316 tests, 7 skips). Windows passed CRLF regressions and the initial installer suites, then exposed bare `bash` resolving to the WSL launcher and native runtime `AppData` under the preview HOME. Ubuntu exposed `test_parallel_backups_never_overwrite_each_other`: `mv` could not stat a reserved lock's payload. Neither failure is treated as a pass.
- Windows follow-up uses absolute PATH-resolved shell paths and separates native USERPROFILE/AppData from installer HOME; host installer sources explicitly prefer environment HOME. The parallel-backup test now exercises eight concurrent writers and captures both workers' full traces on failure to diagnose the Ubuntu-only disappearance; no backup assertion is relaxed.
- Confirmed Ubuntu assertion: `test_install.ComponentInstallTests.test_parallel_backups_never_overwrite_each_other`, exit 1 with `mv: cannot stat '.../parallel-backups/source.txt.20261104T070827Z.bak.lock/payload': No such file or directory`, then `ERROR: could not finalize backup`. Windows first-push totals before stopping: 9 AIHero tests passed; 70 installer tests passed (4 existing skips); 20 new-host tests passed; preservation then failed with WSL launcher output and `home/AppData`. Its runtime-only startup regression also reproduced the AppData creation without installer code.
- Local Windows-harness follow-up checks: preservation 17/17 passed, catalog 9/9 passed, eight-writer backup test passed on macOS. An extra inherited-XDG experiment left all inherited roots untouched while the two startup/preview cases passed.
- Local 60-run stress with the original two workers and tracing: passed, so it does not establish an Ubuntu fix. Docker is not running on this Mac; Linux reproduction continues in the authorized CI environment.
- Follow-up `edab52e`, run https://github.com/HogenXue/AI-workflow-V1/actions/runs/41791736517: Ubuntu and macOS passed, including the stronger eight-writer backup test. Windows preservation (17 tests) passed after shell/runtime isolation. It then exposed native argv paths versus Git Bash HOME string mismatch in catalog other-root pruning tests; the safety assertions remained enabled and correctly failed at the earlier usage boundary.
- Standard-root comparison now converts only path representation via `cygpath -u` when available. Original I/O arguments and logical caller/symlink identity remain intact; native PowerShell already uses its native path comparisons.
- Mac stress of the strengthened eight-writer test: 60 runs passed in 18.794 seconds. This is diagnostic evidence, not a claimed fix for the one observed Ubuntu backup failure.
- After the logical path-format fix, local catalog tests 9/9 and component installer tests 39/39 passed; shell syntax and diff checks passed. Independent cloud Linux/PowerShell 7.5.4 verification of `edab52e` was reported as 316 tests OK (7 Windows-only skips), with 100 original two-writer Bash, 40 PowerShell, and 100 strengthened eight-writer stress runs also passing. At this stage the disappearance remained unreproduced; the deterministic diagnosis below subsequently resolved it.

## Deterministic backup diagnosis and repair

- Third run https://github.com/HogenXue/AI-workflow-V1/actions/runs/41792564783 reproduced the Ubuntu failure with full eight-worker traces. PIDs 4046 and 4070 both treated `...-6.bak.lock` creation as successful and used the same `payload`; PID 4046's cleanup deleted the other worker's staged content. macOS passed. Windows passed catalog/preservation/MCP suites, then its wizard display assertion compared a Windows string with the correct Git Bash `/tmp/...` representation of the same temporary path.
- Upstream uutils coreutils 0.10.0 `mkdir` checks existence before creation, but its create-error handler returns success for an existing directory even without `-p`. This permits the observed double ownership under a race. Confirmed upstream: https://github.com/uutils/coreutils/issues/13970 and https://github.com/uutils/coreutils/commit/bf423f3 . A Linux CI diagnostic now records the runner's actual mkdir version; no utility implementation is silently substituted.
- A deterministic two-writer shim models that check/create interleaving and holds both copies before publication. The existing directory-lock helper fails this new regression locally with one lost payload. This establishes a causal regression rather than relying on repeated green stress runs.
- Bash now reserves via a scoped `noclobber` exclusive lock file and copies into a unique private `mktemp -d` directory. Cleanup cannot remove another worker's payload. Public backup naming, copy-before-mutate and rollback behavior stay unchanged; PowerShell already uses `FileMode.CreateNew` with a unique staging path.
- Source impact review covered all Bash backup call sites in agents/config/skills/Graphify and host merges. No graph tool is exposed; source analysis and full installer/rollback suites provide the verification boundary. The change introduces no Python dependency for shell-only backup callers.
- The wizard test still asserts the full intended fixture path, using the platform's cygpath representation only for Windows Bash output; no expected path fragment or safety assertion is dropped.
- Local full suite after the atomic reservation and wizard fixes: 317 tests OK in 159.945 seconds (7 existing Windows-only skips). The additional staging-allocation failure regression then brought component coverage to 41 passing tests; it verifies lock release, empty backup directory and unchanged source. All pre-existing test method names remain; two backup regressions, three CRLF regressions and one startup regression are added overall.
- Repair commit `f9b2c216996bcdcc4a70122febe517a37d9af821`, run https://github.com/HogenXue/AI-workflow-V1/actions/runs/41794717798: Ubuntu passed 318 tests (7 existing Windows-only skips). Its new diagnostic confirms `/usr/bin/mkdir`, `mkdir (uutils coreutils) 0.10.0`, matching the affected upstream implementation. Both the deterministic race and eight-writer tests passed on that same affected runner; the runner version and utility were not replaced.

## Final repair verification

All jobs for `f9b2c216996bcdcc4a70122febe517a37d9af821` completed successfully in run 41794717798:

| Platform | Actual suite | Result |
| --- | --- | --- |
| Ubuntu | Full package validation and 318 tests | 311 passed, 7 existing Windows-only skips |
| macOS | Full package validation and 318 tests | 311 passed, 7 existing Windows-only skips |
| Windows | Eight dedicated installer patterns, 177 tests total | 173 passed, 4 existing Unix-Bash-only skips |

The Windows patterns are AIHero installation, native PowerShell installer tests, new hosts,
host preservation, catalog, MCP native formats, wizard and dependency bootstrap. No failed
suite is skipped or filtered out. Both Python setup and dependency installation actually ran.
Independent cloud Linux/PowerShell verification of this same repair commit also passed all
318 tests (7 Windows-only skips) in 134.194 seconds.

The final evidence-only follow-up changes no source, tests or workflow. Its exact remote HEAD
is checked separately in CI and linked in the delivery response. The original main remains
`4f3753f`; no merge, deployment or real host Skills installation is performed. Original dirty
work remains untouched in Projects/CodexTamplate. Native task archive/journal is not invoked.

## Retrospective (native break-loop / retro)

- Python stdout is a protocol at the Bash boundary: native line endings affect names, modes and paths together. The implemented regression wraps real helpers, including their real failures, instead of mocking a successful installer.
- An empty preview HOME can be polluted before script entry. Runtime-only startup evidence established the cause; fixture-owned XDG/native profile roots preserve the original exact no-write assertions.
- Windows shell selection and path identity are distinct contracts. Absolute executable resolution avoids the WSL launcher; cygpath changes representation without dereferencing ownership aliases. Wizard assertions retain the full intended path in the selected shell's representation.
- Passing hundreds of stress attempts did not prove the backup failure repaired. Complete worker traces exposed two apparent owners; upstream source and the deterministic check/create barrier reproduced the defect. Atomic file reservation and private staging address the cause while preserving backup and rollback behavior.
- Prevention is implemented in the existing installer spec and regressions. CI keeps all three platforms and the current runner versions, logs the Linux utility implementation, and must be checked against the exact final remote HEAD. No new tracker or installation workflow is introduced.

## Boundaries

- All install tests target temporary fixtures. No Skills or configuration are installed in real host profiles.
- The Mac executor briefly disconnected after cloning, then recovered. The first post-clone command did not execute; branch state was checked before creating the repair branch. No remote mutations occurred during the interruption.
