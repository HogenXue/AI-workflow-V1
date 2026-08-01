# Scripts / Installer Guidelines

> Contracts for `scripts/install*.sh` / `scripts/install*.ps1`, host profile mapping, and project-scoped install safety.

---

## Overview

This layer covers the AI-workflow installer surface: interactive `install.sh` / `install.ps1`,
Codex/Cursor profile pairing, MCP merge, and explicit project-root rules. Load these specs before
changing installer scripts, merge helpers, or packaged templates under `trellis/codex/` /
`trellis/cursor/`.

**Dual implementation**: bash (`install*.sh`) is the macOS/Linux entry; PowerShell 7+ (`pwsh`,
`install*.ps1` + `install.cmd`) is the Windows-native peer. Behavioral contracts are shared; when a
contract changes, update **both** implementations in the same change set (or record an explicit
exemption). CI runs bash install tests on ubuntu/macos and PS install tests on `windows-latest`.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Installer Contracts](./installer-contracts.md) | CLI signatures, project-root resolution, profile pairing, MCP merge, Windows/PS notes | Active |

---

## Pre-Development Checklist

Before changing installer or host-merge code:

- [ ] Read [Installer Contracts](./installer-contracts.md) — especially project-root and profile tables
- [ ] Confirm whether the change touches **global** vs **project-scoped** writes
- [ ] Confirm Codex vs Cursor target paths (do not directory-copy between hosts)
- [ ] Confirm interactive (`TTY`, no args) vs non-interactive (`--project-root` / `--skip-project`) paths
- [ ] If the change alters a behavioral contract, plan updates for **both** bash and PowerShell ports
- [ ] Plan tests: bash `tests/test_install*.py` and/or PS `tests/test_install_*_ps.py` for new flags or skip/conflict behavior

---

## Quality Check

- [ ] Project-scoped paths never use silent `git rev-parse --show-toplevel` (or Windows equivalent)
- [ ] Selected profile only writes its own host tree; never deletes the other host
- [ ] Cursor rules land in `.cursor/rules/*.mdc`; installer never rewrites repo-root `AGENTS.md`
- [ ] MCP format matches host (Codex TOML vs Cursor JSON); remote HTTP MCP URLs are rejected
- [ ] Non-TTY `install.sh` / `install.ps1` with no args still exits `2` with usage
- [ ] Contract-affecting edits land in both bash and PS (or an explicit exemption is documented)

---

**Language**: All documentation should be written in **English**.
