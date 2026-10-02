# Final-review repairs — 2026-10-03

## Result

All three findings in `final-review-2026-10-03.md` are repaired and verified within the
authorized installer scope. The original review and probe output remain historical evidence.

## Changes

- P1: `Install-LibNormalizePath` follows existing path components' symlink/junction targets,
  including relative targets and parent links. It preserves missing suffixes, bounds link depth,
  normalizes supported DOS/UNC extended prefixes, and refuses unresolved/device/cyclic paths.
  Overlap/backup checks fail closed. Config/Skills installers refuse source aliases before backup
  or removal. Unrelated directory aliases still allow normal installation.
- P2: Both Graphify ports record whether the target existed and use the shared rollback helper
  for CLI failure and success-without-`SKILL.md`. Fresh partial targets are removed, retry succeeds
  without `--replace`, and original Skills are restored on replacement failure. PowerShell's
  shared restore/rollback existence checks include dangling links, matching Bash behavior.
- P2: The entrypoint launches `pwsh` under `PSHOME`, avoiding `Environment.ProcessPath` while
  retaining child-process isolation, argument forwarding, and nonzero exit propagation.

## TDD evidence

Before production fixes, the new 10-test review module produced 10 failing assertions/subtests
covering aliased source mutation, nested backup creation, missing suffixes/cycles, and fresh
Graphify failure. Existing-target recovery passed as a negative control. A further device-path
refusal test was observed red before its guard was added; positive alias-copy controls pass.

Portable PowerShell 7.0.13 reproduced the original dispatcher error:
`The property 'ProcessPath' cannot be found on this object.` After repair, its complete selected
installation suite passes. The portable runtime was unpacked under temporary storage; default
machine PowerShell, user PATH, and user profiles were not changed.

## Final validation

| Check | Result |
| --- | --- |
| Current PowerShell task-scoped suite | 128 tests passed in 49.792 seconds |
| Portable PowerShell 7.0.13 installation/wizard suite | 69 tests passed in 54.124 seconds |
| New dedicated review regression module | 13 tests passed |
| All installer PowerShell syntax | Passed |
| All installer Bash syntax | Passed |
| Skill validator | All 7 current manifest Skills passed |
| Configuration consumer validation | Passed |
| Trellis implement/check context validation | Passed |
| `git diff --check` | Passed |
| Original review probes rerun | Source marker preserved; fresh Graphify targets cleared; no retry conflict |

The modern suite discovers `test_install_*_ps.py`, `test_install_dependencies.py`,
`test_install_wizard.py`, `test_validate_all_skills.py`, `test_effective_config.py`,
and `test_grill_with_docs_trellis_route.py`. The minimum-runtime suite discovers
`test_install_*_ps.py` and `test_install_wizard.py` with the portable runtime first on the process PATH.

Portable runtime source: https://github.com/PowerShell/PowerShell/releases/tag/v7.0.13
Artifact: `PowerShell-7.0.13-win-x64.zip`.
Official and downloaded SHA256 both equal:
`A93894F2DD8B508F78DFF6A774A678D4E45BA45ECB7F9409D24E4E3D7768D3A4`.

## Native Trellis check

Applied the existing native `trellis-check` skill manually in Codex inline mode; no callable
native helper is exposed.

- **Spec**: All new PRD repair criteria are backed by executable regressions, preserved-marker
  assertions, retry/restoration checks, and a real PowerShell 7.0 runtime run. No remaining finding
  from this review is open within the verified scope.
- **Standards**: The path resolver reuses pre-existing PowerShell LinkType/Target metadata rather
  than introducing a .NET 6 requirement. Both Graphify ports share the existing rollback contract.
  Scope is narrow; unrelated dirty files, project rules, host configurations and template bodies
  are preserved. Installer/spec consistency and task context checks pass.

## Boundaries

- Native macOS/Linux full suites remain unrun; Bash regressions ran in Git Bash on Windows.
- No real GitNexus/Graphify/Trellis download/install, user-profile installation, commit, or push
  was performed. The only real download was the portable PowerShell test runtime.
- Source impact review covered every caller of the shared path and rollback helpers: Skills,
  config, agents, Graphify, and all host MCP merges. GitNexus is stale and does not index this
  PowerShell symbol, so no complete graph impact result is claimed. The approved source/regression
  fallback was used; full-worktree detect-changes also includes unrelated work.
- Recallium/Mem0 tools remain unavailable. Memory was not retrieved or saved. Contracts are
  recorded in `.trellis/spec/scripts/installer-contracts.md`; save the stable fixes with related
  files when the memory backend becomes available.
