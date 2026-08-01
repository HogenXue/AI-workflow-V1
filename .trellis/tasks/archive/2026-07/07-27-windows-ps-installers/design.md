# Design: Windows PowerShell installers (parent)

## Architecture

Mirror bash layout under `scripts/`:

```text
scripts/
  install.cmd                 # launcher → pwsh -File install.ps1
  install.ps1                 # interactive + component dispatch
  install-lib.ps1             # shared helpers (dot-sourced)
  install-skills.ps1
  install-config.ps1
  install-graphify.ps1
  install-agents.ps1
  install-codex-merge.ps1
  install-cursor-merge.ps1
  lib/merge_host_mcp.py       # unchanged; invoked via resolved python
  install*.sh                 # retained Unix/Git-Bash entry
```

## Boundaries

| Layer | Owns | Does not own |
|-------|------|--------------|
| `install-lib.ps1` | prompt, project-root resolve, backup lock/publish, path normalize/overlap, restore/rollback | component business rules |
| Component `.ps1` | flags, dry-run/apply, replace/prune, install payload | MCP merge policy |
| Merge `.ps1` | host MCP + project hooks/rules; call Python merge helper | skill/config trees |
| `install.ps1` | menus, profile orchestration, dispatch | low-level backup |
| `install.cmd` | find `pwsh`, forward argv, missing-pwsh diagnostics | any install logic |
| Tests | parallel PS suites; bash suites unchanged | rewriting merge_host_mcp |

## Contracts (must match bash)

- Exit `2`: usage / unknown component / non-TTY empty args / MCP conflict with `ask`.
- Exit `1`: invalid `--project-root`, backup failure, conflict without `--replace`, symlink/link failure after rollback path.
- Exit `0`: success or user abort (`Aborted.`).
- Never silent `git rev-parse` as applied project root.
- Profile pairing: Codex ↔ `~/.agents` + `~/.codex`; Cursor ↔ `~/.cursor` + project `.cursor`; no cross-host copy; never rewrite repo-root `AGENTS.md`.
- Backup: `<name>.<UTC stamp>.bak` with lock-dir reservation; never overwrite existing `.bak`; nested backup dir rejected.
- Python: resolve `python` then `python3` (Windows-first); fail with clear `ERROR:` if missing when merge needs it.
- Runtime gate: refuse Windows PowerShell 5.1 / non-pwsh with message pointing to install PS7.

## Path / HOME semantics

- Use `$HOME` (PowerShell 7 = user profile) for `~/.agents` / `~/.cursor` / `~/.codex` equivalents via `Join-Path $HOME ...`.
- Normalize with .NET/`Resolve-Path` carefully for non-existent targets (parity with bash `install_lib_normalize_path`).
- Symlinks: `New-Item -ItemType SymbolicLink`; on failure rollback (D2).

## Compatibility / Drift

- bash remains macOS/Linux(/Git Bash) entry; PS is Windows-native peer.
- Spec update documents: both must be updated when installer contracts change; CI enforces each side on its OS matrix.
- No directory-copy between hosts (existing decision).

## Testing strategy

- New: `tests/test_install_ps.py`, `tests/test_install_interactive_ps.py` (names flexible) invoking `pwsh -NoProfile -File scripts/install.ps1 ...`.
- Lib-only tests may invoke `install-lib.ps1` helpers via a small harness or exported test mode — prefer matching bash’s approach of sourcing lib inside component tests / dedicated subprocess helpers.
- CI: add `windows-latest`; install/ensure `pwsh`; run PS install tests (and shared quality as appropriate). Keep ubuntu/macos bash install tests.

## Rollback / ops

- Component-scoped transaction only (same as bash): later component failure does not undo earlier successful components.
- Backup artifacts retained; restore uses exact `BACKUP:` path.

## Trade-offs

| Choice | Why | Cost |
|--------|-----|------|
| Full PS port vs thin bash wrapper | User chose B + 1:1 | Dual maintenance |
| Parallel tests vs dual-runner | Isolate OS differences | Some assertion duplication |
| pwsh-only | Simpler, modern | Requires PS7 install on machines with only 5.1 |
