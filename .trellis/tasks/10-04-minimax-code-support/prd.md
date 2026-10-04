# MiniMax Code and WorkBuddy installer support

## Confirmed request

The user requested MiniMax support, selected MiniMax Code (`mcode`) as an additional
installer host, then explicitly added WorkBuddy to the same request.

## Requirements

- Add MiniMax Code and WorkBuddy as independently selectable full-install profiles
  and expose `minimax-merge` / `workbuddy-merge` components in Bash and PowerShell.
- Install the existing seven Skills and paired defaults into each host's user
  directory. Install canonical global instructions as `AGENTS.md` for MiniMax
  Code and `CODEBUDDY.md` for WorkBuddy without Codex feature changes.
- Merge GitNexus, Recallium and Mem0 using native JSON. Preserve unrelated
  keys, server entries and existing URLs unless replacement is chosen.
- Follow-up: the user set both Mem0 and Recallium default URLs to
  `https://www.59005046.xyz:8102/mcp` for all supported hosts. An explicit
  `--mem0-url` still overrides Mem0 only; existing URLs keep the prior choice policy.
- Match host overrides and MCP file precedence. Back up existing target files
  before writing; preview must not create files/directories or backups.
- Preserve existing hosts and all pre-existing dirty changes.

## Acceptance criteria

- Menu selections 4 and 5 select MiniMax Code and WorkBuddy, alone or with existing
  hosts. Invalid selections and component failures still stop safely.
- Pair `skills` with `config` under each host home; global instructions and MCP
  target user configuration only, with no project writes.
- MiniMax respects `MINIMAX_DATA_DIR`, then `MAVIS_DATA_DIR`, defaulting to
  `~/.minimax`; MCP respects existing `mcp.json`, then `mcp/mcp.json`.
- WorkBuddy respects `CODEBUDDY_CONFIG_DIR`, defaulting to `~/.codebuddy`; MCP
  follows `.mcp.json`, `mcp.json`, then legacy `~/.codebuddy.json` precedence.
- Fragments use native `type: stdio/http`; isolated tests cover preview, keep,
  overwrite, conflict, invalid-input and backup paths.
- All five host templates supply the confirmed default URLs. Installation without
  `--mem0-url` uses the default; explicit overrides and existing-URL keep choices
  still work for both TOML and JSON.
- Relevant new and adjacent installer tests pass. Explicitly report unavailable
  PowerShell runtime checks when `pwsh` is absent.

## Boundaries

Repository support only: no real user-profile install, application download,
authentication, model API call, Trellis platform initialization, graph generation,
commit or push. New hosts do not receive guessed hooks.
