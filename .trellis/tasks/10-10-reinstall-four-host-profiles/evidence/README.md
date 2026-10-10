# Installation evidence — 2026-10-10

- `provenance.json`: actual installer command/exit, private evidence location and
  raw/sanitized transcript fingerprints.
- `installation.redacted.log`: actual PTY transcript. URL values are replaced by
  hashes; no raw configuration or credentials are repository evidence.
- `before-fingerprints.json`: durable pre-install per-file/tree hashes, MCP server
  and URL hashes, protected paths and existing dirty-work fingerprints.
- `installed-fingerprints.json`: source/installed Skill and config trees, guide/MCP
  checks and protected after-state, including individual file hashes.
- `backup-inventory.json`: all 85 new timestamped backups, their full fingerprints
  and original paths they match. Every replacement target is covered.

The private directory is restricted to its owner (0700); configuration snapshots
and the raw log are 0600. It is outside Skill discovery and is not temporary.
SHA-256 fingerprints prove the recorded comparisons; reading raw values for a
future private audit requires authorized access to that restricted directory.
This new October 10 installation does not reconstruct missing October 6 evidence.
Application loading and external MCP connectivity remain `not_run`.
