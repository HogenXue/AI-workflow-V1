# Live installation verification — 2026-10-06

## Actual operation

The user authorized the repository one-click installer for Codex, Cursor, MiniMax
Code and WorkBuddy, explicitly keeping MCP addresses. The real command was
`bash scripts/install.sh`, with a PTY and `umask 077`, from the repository at
`029d9a4`. The installer exited **0** and printed `Done.`.

Wizard decisions: profiles `1 2 4 5`, recommended full install, Cursor project
scope skipped, managed Skills/defaults and Graphify replacement accepted with
backups, all existing non-URL MCP entries kept, all URL replacement prompts
answered No. No `--mem0-url` was supplied.

Existing usable GitNexus, Trellis and Graphify CLIs were detected and retained;
no dependency/application upgrade or project initialization was performed.

## Historical reported payload and preservation

| Profile | Skill root | Verified manifest Skills | MCP file |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills` | 18 | `~/.codex/config.toml` |
| Cursor | `~/.cursor/skills` | 18 | `~/.cursor/mcp.json` |
| MiniMax Code | `~/.minimax/skills` | 18 | Existing `~/.minimax/mcp/mcp.json` |
| WorkBuddy | `~/.codebuddy/skills` | 18 | Existing `~/.codebuddy/mcp.json` |

- The recovered original verification output reports that all 72 selected Skill trees matched their package sources by relative file/link
  structure and SHA-256. Four paired default-config trees match the installer
  payload, excluding root Python cache files as the installer specifies.
- Codex/MiniMax `AGENTS.md` and WorkBuddy `CODEBUDDY.md` match
  `agents/AGENTS.global.md` byte-for-byte. Codex user hook JSON parsed, its
  `SessionStart` hook exists, and `hooks/session-start.sh` matches the source.
  Codex's separate Graphify Skill was updated from the installed CLI.
- The recovered original verification output reports **21 existing MCP server entries and all 11 URLs unchanged**, with all four MCP
  files **byte-identical** to their then-available pre-install snapshots.
  Codex/MiniMax Mem0 keeps its existing port 8103; Cursor/WorkBuddy keeps 8102.
- The original checker reported no drift in protected settings, unselected roots
  and the original dirty diff. Its original before-state fingerprints are lost,
  so this historical comparison is not now independently reproducible.
- **86 timestamped backups** were created in the five existing host backup roots.
  All four MCP backups match the corresponding original file bytes.

The first default-config comparison included root Python caches; inspection of
`install-config.sh` established that these are deliberately excluded. The
comparison was corrected to the actual payload contract, without changing any
installed files.

## Evidence and native Trellis check

Durable repository evidence is in [evidence/README.md](evidence/README.md).
The original PTY transcript and executed verification result were recovered from
retained session output, not reenacted. Their provenance, sanitized transcript,
86 original-backup fingerprints and fresh read-only observations are committed-
ready task artifacts. Raw configuration copies remain outside the repository in
a restricted persistent directory identified by `evidence/provenance.json`.

The former temporary audit directory is no longer an evidence dependency. Its
original protected-state baseline and October 6 post-state fingerprint inventory
cannot be recovered; the original reported pass is not relabeled as independently
reproducible evidence. See the pending historical acceptance item in the PRD.

Actual checks were the Python SHA-256/tree/JSON/TOML comparer, MCP backup comparison,
Codex hook comparison, and `task.py validate` / `git diff --check`.
The native `.cursor/skills/trellis-check/SKILL.md` was read and applied manually in
Codex inline mode to this operational Task: approved write scope, native host
formats, backup behavior, source-payload equality and MCP preservation all passed.
No implementation diff or new runtime behavior requires another full test suite.

## Not run / boundaries

- Cursor project hooks/rules: skipped because no project root was requested.
- Application reload/discovery acceptance and business MCP connection checks:
  not run. The result proves installed configuration and preserved addresses.
- Application binaries, credentials, permissions/model settings, project init,
  graph generation, unrelated tests, commit/push and archive: not performed.
- Recallium `get_rules` succeeded; the scoped history search returned no matches.
  Completion-memory status is recorded in `task.json` after the save attempt.

## Review recovery — 2026-10-10

- Recovered 20 actual terminal-output chunks, including the original exit code 0,
  and the actual original verification JSON. No installation was repeated.
- All 86 backup paths from that transcript still exist and were fingerprinted.
- Original MCP merge-before files were recovered from those timestamped backups.
  Today's live files were read and copied separately, with explicit dates.
- **Fresh observation**: all 11 original URLs still match; 20 of 21 original
  server definitions and 3 of 4 MCP file bytes match. Codex `node_repl` differs.
  No current definition was changed. This is not an October 6 post-install result.
- 40 of 72 currently installed Skill trees match the pinned installation source
  `029d9a4`. Differences are recorded as later observations, not attributed to
  the October 6 installer and not automatically overwritten.
- The exact original protected-state fingerprints remain unavailable. The
  historical receipt is retained with this limitation instead of inventing hashes
  or rerunning a modifying installer to manufacture a before/after comparison.
