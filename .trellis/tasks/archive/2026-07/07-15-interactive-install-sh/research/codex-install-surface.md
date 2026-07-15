# Research: Codex install surface (this repo)

## Current installer

- `scripts/install.sh` → `skills` | `agents` | `config`
- agents `--apply`: copy `trellis/AGENTS.global.md` → `$CODEX_HOME/AGENTS.md`; ensure `[features].hooks = true`
- config component → `~/.agents/config` only (skill defaults), not Codex `config.toml`
- No packaged `hooks.json` / MCP templates under `trellis/` today
- `trellis/config-check.sh` checks `$CODEX_HOME/{AGENTS.md,config.toml,hooks.json}` and lists MCP server names

## Documented MCP defaults

- recallium: HTTP `http://www.59005046.xyz:8102/mcp` (`skills/memory/references/memory-backends.md`)
- gitnexus: local stdio `gitnexus mcp` (user machine uses `/opt/homebrew/bin/gitnexus`)
- mem0: referenced by memory skill tool names; **no canonical URL in repo**; not present in current `~/.codex/config.toml`

## Hooks placement

- Trellis meta: Codex uses `.codex/hooks.json` + `.codex/config.toml`
- Cursor/Claude hooks in this repo are project-local
- Decision: global config.toml for hooks flag + MCP; project `.codex/` for hook registration/scripts
