# Design: ps-install-entry

`install.ps1` mirrors `install.sh` control flow (interactive_main, profiles, dispatch). `install.cmd` locates `pwsh.exe` (PATH then common install dirs) and runs `-NoProfile -File "%~dp0install.ps1" %*`.
