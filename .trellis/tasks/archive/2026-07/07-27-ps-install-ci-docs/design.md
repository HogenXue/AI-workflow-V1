# Design: ps-install-ci-docs

Parallel pytest modules calling `pwsh -File`. CI matrix + `windows-latest`. Docs/spec dual-implementation notes. Symlink tests: prefer Developer Mode / `SeCreateSymbolicLinkPrivilege` on runner; if impossible, document explicit skip with reason (last resort).
