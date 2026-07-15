# Research: Cursor↔Codex config mapping (article + local)

Source: [从 Cursor 迁到 Codex：别急着抄配置，先把脑回路迁过去](https://www.fanyamin.com/cong-cursor-qian-dao-codexbie-ji-zhao-chao-pei-zhi-xian-ba-nao-hui-lu-qian-guo-qu.html) (Walter Fan, 2026-04-23) + local machine paths.

## Core principle

Do **not** 1:1 copy folders. Map **responsibilities**:

| Cursor | Codex-like | Installer implication |
| --- | --- | --- |
| `.cursor/rules/*.mdc` | `AGENTS.md` chain (user → repo → nested) | Do **not** dump Cursor rules into Codex `rules` (sandbox allowlist) |
| `.cursor/commands/*.md` | Skills or AGENTS workflows | Our packaged item is already **skills**, not slash commands |
| User Rules | `~/.codex/AGENTS.md` | Cursor side needs an explicit target (open) |
| MCP servers | MCP servers | Lowest-friction share: `config.toml` ↔ `~/.cursor/mcp.json` |
| Hooks | `hooks.json` + `features.hooks` / `codex_hooks` | Codex needs feature flag; project and user hooks may both run |

## Safety / runtime notes (Codex)

- Default sandbox often `workspace-write` + `on-request`; `.git` / `.agents` / `.codex` can be read-only to the **agent** — user-run `install.sh` is outside that loop (OK).
- Hooks need feature enabled; Windows hooks may be disabled.
- Multiple `hooks.json` layers all run (no override); keep scripts short/idempotent.
- Keep `.cursor/` when adding Codex support (rollback / dual-tool teams).

## Local paths observed

- Codex MCP: `~/.codex/config.toml` (`gitnexus`, `recallium`; no `mem0`; no `hooks` key)
- Cursor MCP: `~/.cursor/mcp.json` (`recallium`, `gitnexus`)
- Cursor skills home: `~/.cursor/skills` (many skills present)
- This repo already has project `.cursor/hooks.json` + hooks scripts (Trellis)

## Installer design takeaway

- Shared: skills package + MCP server list (same three: recallium/mem0/gitnexus) with host-specific file format.
- Codex-only: `config.toml` hooks flag, optional project `.codex/hooks`.
- Cursor-only: `~/.cursor/mcp.json` merge, project `.cursor/hooks` ensure/update, skills → `~/.cursor/skills`, plus **AGENTS/rules target still TBD**.
- Never delete the other host’s directory as part of install.
- Never treat Cursor Rules as Codex Rules files.
