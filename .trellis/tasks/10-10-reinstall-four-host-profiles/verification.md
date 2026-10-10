# Local installation verification — 2026-10-10

## Actual operation

Source revision: `276a8d4c802f2b403c2f7b9245fe39b5a2822b98`.
The user authorized installing the current package on this Mac. The existing
`bash scripts/install.sh` ran in a real PTY, with `umask 077`; stdout/stderr were
persisted as they were produced. The installer exited **0** and printed `Done.`.

Decisions: profiles `1 2 4 5`, recommended full install, Cursor project steps
skipped, managed Skill/default replacement accepted with backups, existing
non-URL MCP entries kept, every URL replacement declined. No `--mem0-url`,
legacy pruning or cross-root pruning option was used.

Graphify replacement was explicitly declined to preserve the constrained
canonical tree selected by the preceding cleanup. Existing GitNexus, Trellis and
Graphify CLIs were detected as usable and retained at their installed versions.

## Verified result

| Profile | Skill root | Verified manifest Skills | MCP file |
| --- | --- | ---: | --- |
| Codex | `~/.agents/skills` | 18 | `~/.codex/config.toml` |
| Cursor | `~/.cursor/skills` | 18 | `~/.cursor/mcp.json` |
| MiniMax Code | `~/.minimax/skills` | 18 | `~/.minimax/mcp/mcp.json` |
| WorkBuddy | `~/.codebuddy/skills` | 18 | `~/.codebuddy/mcp.json` |

- All **72 Skill trees** match the source by relative structure, symlink targets,
  individual file SHA-256 and byte lengths.
- All **four default-config trees** match the actual installer payload; root
  `__pycache__`, `.pyc` and `.pyo` entries are excluded as the script specifies.
- Three global guides match `agents/AGENTS.global.md` byte-for-byte. The Codex
  managed SessionStart script matches its template; the hook is registered.
  All **four unrelated hook entries** from the verified original backup remain.
- All **21 existing MCP server definitions and 11 URLs** match the pre-install
  state. All **four MCP files are byte-identical**, and non-MCP keys are unchanged.
- All **56 protected paths** match before-state fingerprints. This includes the
  chosen Graphify tree, old-entry absence, independent Skills, legacy Codex root,
  native settings and unselected Claude configuration/Skills.
- All **542 tracked repository paths** and the unrelated pre-existing dirty paths
  were byte/type-identical immediately after installation. The existing
  `AGENTS.md` deletion and old LAN task remain. Later Task/Journal recording is
  the authorized documentation delta, not an installer source change.
- All **85 new timestamped backups** match original fingerprints, and every
  existing replacement target has a matching backup. No temporary directory is
  required for the evidence chain.
- Private snapshot/raw-log permissions are verified: directory **0700**, files
  **0600**. The private root is outside the repository and Skill discovery.

## Native check and durable evidence

The native `.cursor/skills/trellis-check/SKILL.md` was applied manually in Codex
inline mode to this operational Task. The applicable scripts spec was checked
against the actual selected paths, keep policy, backups, preserved cleanup and
installed payload. No installer runtime code changed; full repository tests,
lint or type-check are not appropriate evidence for this local installation.

Actual verification commands:

- `python3 <private-evidence-root>/audit.py before`
- `python3 <private-evidence-root>/run_installer.py` (PTY wrapper for the installer)
- `python3 <private-evidence-root>/audit.py after` — **passed**
- Targeted backup-coverage, unrelated-hook and private-permission assertions —
  **passed**
- `python3 .trellis/scripts/task.py validate .trellis/tasks/10-10-reinstall-four-host-profiles`
  and `git diff --check` — **passed**.

See [evidence/README.md](evidence/README.md) and `installed-verification.json`.
Private evidence root:
`/Users/hogenxue/.local/state/codextamplate/installation-audits/2026-10-10-6w4gwze7`.

This fresh installation is independent of the missing historical October 6
protected-state evidence; it does not relabel the old acceptance as reproduced.

## Not run / retained boundaries

- Application reload/discovery/loading: **not_run**.
- External MCP connectivity and API/credential checks: **not_run**.
- Cursor project rules/hooks, application binaries, project/graph initialization,
  model/permission/plugin changes, commit/push and Task archive: not performed.
- Current Grill Me copies remain current/stateless; removed obsolete variants
  and duplicate aliases were not restored by installation.

OpenAI Docs reference: https://learn.chatgpt.com/docs/build-skills (user discovery
root, symlink support, non-merging same-name entries and automatic Skill refresh).

Completion context saved to Recallium memory **#1302**.

## Publication — 2026-10-11

The user separately authorized commit/push after installation. Publication is
limited to this Task and Session 8 Journal/index changes. The receipt's
`git_publication: not_run` refers to the installation verification phase. Private
snapshots/raw log, the existing `AGENTS.md` deletion and the old LAN task are
outside the commit. No reinstall or application/MCP acceptance was run.
