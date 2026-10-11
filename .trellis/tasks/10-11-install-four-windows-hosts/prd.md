# Install current package into four Windows hosts

## Goal

Update Codex, Cursor, Claude and WorkBuddy from current source using existing component installers, backups and MCP/native-setting preservation.

## Requirements

- Install the current package at source `875bd95` on this Windows machine for Codex, Cursor, Claude and WorkBuddy (profiles 1/2/3/5, not MiniMax).
- Use existing native component installers sequentially, with copy/replacement backups for managed manifest Skills, paired defaults and applicable global documents.
- Preserve every existing MCP definition/URL, unrelated native settings, independent Skills, existing Graphify and unselected hosts. No legacy/cross-root pruning.
- Cursor project hooks/rules are skipped because no explicit project root was requested.
- Check Codex hooks before replacement; never remove unrelated hook entries/files as part of this update. Preserve the existing global override file if present.
- Keep raw configuration snapshots and logs outside the repository in durable user-restricted storage. Persist sanitized receipts and hash-based verification in this Task.
- Verify 72 manifest Skill trees, four default payloads, three global documents, Codex managed hooks, preserved native/MCP values, independent entries and backups. No application restart, external MCP connectivity, Git publication or archive is implied.

## Acceptance Criteria

- [x] All selected component installs return 0, with real per-component evidence.
- [x] Installed managed payloads match current source; preservation and backup checks pass.
- [x] Operational native Trellis check, task reference validation and documentation scope checks pass with explicit limits.

## Authorization and scope

The user's explicit four-host installation request authorizes updating managed local payloads through the installers and their backups. This is a Windows operational task, not the historical Mac/MiniMax tasks. PRD-only planning is sufficient for the settled operation; no installer source/runtime change is planned. Any unexpected customization conflict must be handled without destroying unrelated data.

## Runtime repair follow-up (2026-10-11)

The user reported three failed Codex hooks and identified EGM as the affected project.
Reproductions show WSL Bash cannot open the installed Windows absolute path, EGM uses Python
to execute a Bash script, and its Graphify hook retains a macOS-only executable path.
The original file-only acceptance does not establish runtime success.

- Add an official `commandWindows` override using native Python for managed Codex context
  hooks, keeping Unix commands compatible. Package the required helper through both installers.
- Verify installed commands actually execute from a path containing spaces and a nested project
  directory without requiring Bash/WSL; preserve meaningful context failures.
- Back up and repair the current user hook and EGM's two failing hook registrations only.
  Do not change EGM business code, unrelated hooks/settings, or dirty Git work.
- Replay all three affected handlers locally with representative JSON input. Desktop hook
  reload/trust and the old statistics panel remain separate application-level checks.
- Initially no Git publication, application restart, graph rebuild or hook trust bypass was
  authorized. On 2026-10-11 the user authorized review, scoped commit and push of these repairs.
  The remaining exclusions still apply; see `hook-repair-review.md` for the exact publication scope.
