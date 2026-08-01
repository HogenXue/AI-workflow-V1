# Design: ps-install-lib

## Approach

Port `install-lib.sh` function-for-function into `install-lib.ps1` as advanced functions / script-scoped functions. Components will:

```powershell
. "$PSScriptRoot/install-lib.ps1"
```

## Mapping

| bash | PowerShell |
|------|------------|
| `install_lib_prompt_yn` | `Install-LibPromptYn` |
| `install_lib_resolve_project_root` | `Install-LibResolveProjectRoot` → sets `$script:InstallProjectRoot` or env-style output var matching callers |
| `install_lib_backup_file` | `Install-LibBackupFile` → `$script:InstallBackupPath` |
| `install_lib_restore_backup` / `rollback_target` | same names in PS verb form |
| path helpers | use .NET for absolute/full path; preserve overlap semantics on Windows drives |

## Notes

- Lock via `New-Item -ItemType Directory` on `*.lock` (mkdir atomicity on NTFS).
- Prefer `Copy-Item -Recurse` + move for publish; preserve symlink backup behavior where .NET allows (`Copy-Item` / robocopy caveats documented in implement if needed).
- Export variable names documented for callers (`InstallProjectRoot`, `InstallBackupPath`).
