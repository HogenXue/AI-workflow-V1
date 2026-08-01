# Implement: ps-install-merge

1. Port both merge scripts; reuse lib helpers.
2. Smoke MCP dry paths + `--skip-project` on Windows.
3. Quality check.

Depends: `07-27-ps-install-lib`. Parallel-safe with components.

## Known gaps (non-blocking for finish)

- **Dangling-symlink backup (PRD R4 / contracts)**: bash covers this in `test_install_interactive.py` via `cp -pR` + `-L` detection. PowerShell `Install-LibBackupFile` uses `Copy-Item`, which does not reliably preserve dangling reparse points on Windows, and creating symlinks often needs Developer Mode / elevation (probe failed with privilege error on this host). MCP conflict rollback for ordinary files is covered by `test_install_merge_ps.py`. Full dangling-symlink parity remains deferred to `07-27-ps-install-ci-docs` / lib hardening when Windows symlink privileges are available — do not block merge finish or entry child start.
