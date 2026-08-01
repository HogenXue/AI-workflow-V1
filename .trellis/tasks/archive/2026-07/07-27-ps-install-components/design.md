# Design: ps-install-components

Port `install-skills.sh`, `install-config.sh`, `install-graphify.sh`, `install-agents.sh` to `.ps1`. Dot-source `install-lib.ps1`. Keep CLI flags and stdout markers identical. Default `$HOME/.agents/...`. `--link` uses symbolic links; failure rolls back.
