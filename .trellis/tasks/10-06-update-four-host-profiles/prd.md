# Update four host profiles while preserving MCP URLs

## Goal

Run the existing one-click installer for Codex, Cursor, MiniMax Code and WorkBuddy. Preserve all existing MCP URLs and entries; record backups and verify installed configuration without project writes.

## Requirements

- Select profiles 1, 2, 4 and 5; perform the recommended full configuration install.
- Update the 18 manifest Skills and paired defaults with installer backups.
- Install native global instructions and Codex user hooks through the installer.
- Keep all existing URL and non-URL MCP entries. Do not supply `--mem0-url`.
- Skip Cursor project-scoped hooks/rules because no project root was requested.
- Preserve unselected profiles, native model/permission settings and repository
  dirty changes. Keep usable dependency CLIs at their installed versions.

## Acceptance Criteria

- [x] The actual interactive installer finishes successfully for all four profiles.
- [x] All 18 selected Skill trees and paired config files match the package source.
- [x] Applicable host global documents match the canonical template.
- [x] All pre-existing MCP URLs and server entries match the pre-install snapshot.
- [ ] Independently reproduce protection of native settings, unselected roots and
  the original dirty diff. The run reported success, but its original before-state
  fingerprints are lost; this criterion is not currently independently reproducible.
- [x] Apply native Trellis verification to installed files and record real checks.
  No unrelated full test suite, application upgrade, project init, API call,
  commit, push or automatic archive is performed.

## Notes

- Authorized operation, not an installer-code change; PRD-only planning is sufficient.
- Private snapshots stay outside the repository with restricted access.
- Installed-file verification does not claim application reload or external MCP
  connectivity; those remain separate evidence boundaries.

## Authorized review follow-up — 2026-10-10

- Recover actual execution output from this session's retained tool transcript.
  Persist sanitized logs, provenance, backup inventories and file fingerprints in
  this Task; keep private configuration copies in a durable, restricted directory.
- Separate original execution evidence, backup-derived pre-install evidence and
  a fresh read-only observation. Never label today's state as the lost October 6
  immediate post-install snapshot. Explicitly record unrecoverable evidence.
- Synchronize the shared installer spec and quality checklist with the already
  approved private-IP HTTP behavior, including exact CIDRs and rejected boundaries.
- Do not reinstall, modify MCP addresses/native settings, edit installer runtime
  code, commit/push, archive, or change unrelated dirty work.

### Follow-up acceptance

- [x] Sanitized execution records and their provenance are durable and traceable.
- [x] Existing backups are inventoried with fingerprints; private recovered
  configuration copies have restricted access and are not repository artifacts.
- [x] Historical limitations and fresh check results are clearly distinguished.
- [x] Spec/checklist matches the existing validator and its rejection boundaries.
