# Repair Claude memory MCP connectors

## Goal

Remove Headroom from the local Claude Code connectors, configure the existing
self-hosted Mem0 service, and repair Recallium connectivity.

## Scope and constraints

- Authorized by the user's explicit request on 2026-11-05.
- Update the relevant user-scoped MCP entries in `~/.claude.json` and a verified
  MCP runtime compatibility setting in `~/.claude/settings.json`. If network
  evidence requires it, add narrowly scoped Clash Verge routing exceptions for
  the two MCP endpoints. Preserve unrelated settings, servers, active Claude
  sessions, and background jobs.
- Reuse the existing Recallium and Mem0 services. Do not install another backend,
  weaken TLS verification, or modify other hosts or the package's installers.
- Back up the configuration before mutation. No Git operations or task archival.
- This is a lightweight host-configuration repair; use live MCP handshake and
  discovery checks as the regression evidence, rather than production-code tests.

## Acceptance criteria

- [x] Headroom is absent from Claude's user-scoped MCP configuration.
- [x] Mem0 loads as an HTTP MCP server at the existing service's correct endpoint.
- [x] Recallium connects successfully and exposes its tools to Claude.
- [x] Repeated native connection checks succeed after any required network fix.
- [x] Original and final connectivity results, root cause, backup location, and
  any session-refresh limits are recorded in this task.
- [x] Unrelated Claude configuration and existing repository changes are preserved.
