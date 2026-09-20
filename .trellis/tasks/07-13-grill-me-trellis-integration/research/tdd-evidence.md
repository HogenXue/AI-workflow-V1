# TDD and installation evidence

## Hooks merge

- RED: `test_codex_merge_preserves_existing_hooks_and_idempotently_adds_session_start` failed because the installer returned `CONFLICT` when a valid existing `hooks.json` was present.
- GREEN: after event-level merge implementation, the focused hooks tests passed. The installer preserves existing PermissionRequest/PreToolUse/PostToolUse/Stop handlers and maintains exactly one managed SessionStart entry across repeated installs.

## Package verification

- `scripts/validate-all-skills.py`: all 9 packaged Skills passed.
- Focused Python suite: 99 tests passed, 1 PowerShell-dependent test skipped.
- Shell syntax checks passed for the affected installers.
- Installation readback confirmed 9 synchronized Skills, a complete shared config runtime, synchronized global AGENTS, `gpt-5.6-sol` with high reasoning, GitNexus/Recallium/Mem0 MCP entries, and five hook event groups including SessionStart.

This evidence covers configuration and packaging behavior. It does not claim application behavior in an already-running Codex session; the app must start a new session or restart to discover the new Skills and model defaults.

## Codex 0.154 configuration cleanup

Removed three ignored settings reported by Codex: `disable_response_storage`, `mcp_servers.gitnexus.type`, and `mcp_servers.headroom.type`. Current Codex infers MCP transport from `command` or `url`. The installer MCP fragments were updated so future merges do not reintroduce `type`.

`codex features list` loaded the configuration without warnings. `codex doctor --summary` confirmed configuration, authentication, six MCP entries, connectivity, and installation health; its nonzero result came from unrelated `TERM=dumb` and thread-inventory diagnostics, not configuration parsing.
