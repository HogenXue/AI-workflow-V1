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
- Exact-commit CI results will be added after the independent branch run finishes.

## Boundaries

- All install tests target temporary fixtures. No Skills or configuration are installed in real host profiles.
- The Mac executor briefly disconnected after cloning, then recovered. The first post-clone command did not execute; branch state was checked before creating the repair branch. No remote mutations occurred during the interruption.
