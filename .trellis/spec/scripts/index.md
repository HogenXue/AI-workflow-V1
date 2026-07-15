# Scripts / Installer Guidelines

> Contracts for `scripts/install*.sh`, host profile mapping, and project-scoped install safety.

---

## Overview

This layer covers the AI-workflow installer surface: interactive `install.sh`, Codex/Cursor
profile pairing, MCP merge, and explicit project-root rules. Load these specs before changing
installer scripts, merge helpers, or packaged templates under `trellis/codex/` / `trellis/cursor/`.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Installer Contracts](./installer-contracts.md) | CLI signatures, project-root resolution, profile pairing, MCP merge | Active |

---

## Pre-Development Checklist

Before changing installer or host-merge code:

- [ ] Read [Installer Contracts](./installer-contracts.md) — especially project-root and profile tables
- [ ] Confirm whether the change touches **global** vs **project-scoped** writes
- [ ] Confirm Codex vs Cursor target paths (do not directory-copy between hosts)
- [ ] Confirm interactive (`TTY`, no args) vs non-interactive (`--project-root` / `--skip-project`) paths
- [ ] Plan tests in `tests/test_install*.py` for any new flag or skip/conflict behavior

---

## Quality Check

- [ ] Project-scoped paths never use silent `git rev-parse --show-toplevel`
- [ ] Selected profile only writes its own host tree; never deletes the other host
- [ ] Cursor rules land in `.cursor/rules/*.mdc`; installer never rewrites repo-root `AGENTS.md`
- [ ] MCP format matches host (Codex TOML vs Cursor JSON)
- [ ] Non-TTY `install.sh` with no args still exits `2` with usage

---

**Language**: All documentation should be written in **English**.
