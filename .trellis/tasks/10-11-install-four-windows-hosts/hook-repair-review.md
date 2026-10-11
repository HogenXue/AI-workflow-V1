# Windows Codex hook repair: review and publication

Date: 2026-10-11. Native task: `install-four-windows-hosts`.

## Problem and scope

The user reported three failed hooks in EGM after the four-host installation. The managed user
hook invoked WSL Bash with a Windows path; EGM invoked a Bash script through Python, and its
Graphify command retained a macOS executable path. File installation checks did not catch
these runtime failures.

Publish only these six package files:

- `.trellis/spec/scripts/installer-contracts.md`
- `scripts/install-codex-merge.ps1`
- `scripts/install-codex-merge.sh`
- `trellis/codex/hooks.json`
- `trellis/codex/hooks/session-start.py`
- `tests/test_install_codex_hook_ps.py`

Publish this task's PRD, task metadata, context manifests and this focused review as supporting
records. Earlier operational installation receipts, full local verification logs and machine-specific
runtime receipts remain local. Raw configuration/backups are outside the publication scope.
In EGM publish only `.codex/hooks.json`, to Gitee `EGM3.0`.

## Spec review

No blocking findings. Both package installer peers distribute the native Python helper and
register a quoted absolute `commandWindows` path, preserving the Unix command. The helper
locates Trellis from a nested session directory and propagates genuine context failures.
Live hooks were backed up before repair; a deep comparison confirms only planned registration
keys changed. EGM's tracked Windows command resolves `CODEX_HOME` or the native user home
instead of embedding a Windows account-specific path.

## Standards review

No blocking findings. The test filename matches Windows CI's existing `test_install_*_ps.py`
discovery pattern. No additional dependency, graph rebuild, lifecycle, business-code change or
global AGENTS edit is introduced. Independent hooks and existing dirty work are preserved.
EGM's Windows context command requires this package's user helper to be installed; that dependency
is satisfied on this machine. Both user and project SessionStart registrations remain, as before.

GitNexus change scans returned LOW with no indexed symbols/processes affected. Its graph does
not index the relevant PowerShell code, so exact Git diffs and runtime tests establish scope;
zero indexed symbols is not proof of complete coverage.

## Valid verification evidence

- Native Windows hook regression: 4/4 passed, including actual installed command execution,
  spaces in the home path, nested cwd, no-Trellis skip and context error propagation.
- PowerShell merge regressions: 13/13 passed.
- Existing hooks keep/replace regressions: 2/2 passed, including their subcases.
- Isolated LF Unix snapshot: Bash syntax and 12 selected installer tests passed; 3 portable
  runtime tests passed, with the Windows-only test explicitly skipped.
- Final live replay of all three EGM handlers: exit 0 and empty stderr; both SessionStart
  handlers emitted actual Trellis context. The installed Graphify `hook-check` is a compatibility
  no-op, so this proves command availability rather than graph analysis.
- Native task reference validation and scoped Git whitespace checks passed.

Successful coverage remains valid because the implementation and its runtime dependencies have
not changed since these checks. Only review/publication metadata changed. Direct WSL tests on
the Windows checkout encountered existing CRLF parse failures; the isolated LF checks do not
change repository line endings or claim native macOS acceptance.

## Publication safety

The user explicitly authorized review, commit and push on 2026-10-11, limited to these repairs.
AI-workflow uses the exact file allowlist above plus the five supporting task files. EGM's remote
tip is ahead of its working checkout, and its real index contains unrelated staged deletions.
Create EGM's one-file commit with an isolated index based on the latest Gitee tip; verify its
tree delta and keep the original checkout HEAD, real index and unrelated working files intact.
Use a normal push, never force; recheck remote SHA after each push. Do not push EGM to GitHub.

The prepared EGM commit is `4b66a6b6ca125a805a0002dbc6f76ed6a036a53e`, based on
Gitee tip `68289c1f366b7f9d541a9e1c1aaf82d273178d9e`, with exactly `.codex/hooks.json`
changed. It is retained locally as `codex/windows-hook-fix-20261011`. The real EGM index hash,
working hook bytes and checkout HEAD `277a0266853310c68d7d5707a9aa3ad784f98dbd` are unchanged
by this isolated commit operation.

Application reload, changed-hook trust and desktop statistics remain unobserved. No archive,
trust bypass, application restart or external MCP connectivity check is part of publication.
