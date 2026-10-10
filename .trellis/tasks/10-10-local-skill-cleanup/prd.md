# Audit and prune obsolete or duplicate local Skills

## Goal

Review user-level Skill roots, remove verified redundant/obsolete entries with recoverable backups, relocate archival copies out of discovery, and preserve current host capabilities and MCP settings.

## Requirements

- Audit user-level Skills in `.agents`, legacy `.codex`, Cursor, Claude, MiniMax
  and WorkBuddy; distinguish per-host installations from duplicate Codex entries.
- Back up and remove confirmed same-source aliases, obsolete/unadapted workflow
  entries and redundant generic routing, retaining specialized capabilities.
- Consolidate Graphify into the shared user root while retaining the existing
  narrower, personally adapted variant and its resources without rewriting it.
- Move historical backup containers out of Skill roots, including the July
  obsolete Grill Me interviewer. Preserve their data in recoverable storage.
- Current Grill Me copies match the source manifest and are explicit/stateless;
  retain them unless the user's optional clarification explicitly retires all copies.
- Preserve system/plugin-managed Skills, CC Switch sources, Superpowers source
  package, other host's independent Skills, MCP/config/hooks and repository work.

## Acceptance Criteria

- [x] Decisions and pre/post fingerprints are recorded for every changed path.
- [x] Duplicate aliases are gone and retained canonical definitions still exist.
- [x] Old `open-spec`, `write-a-prd`, duplicate debugging/general-policy entries
  and the redundant Superpowers discovery link are absent from active roots.
- [x] One Graphify variant remains in `.agents/skills`, matching the chosen
  original customized tree; its removed counterparts are recoverable.
- [x] Archive containers/obsolete July Grill Me no longer reside in Skill roots;
  current Grill Me and independent host installations are preserved.
- [x] Backups match original fingerprints and rollback paths are documented.
- [x] Protected configuration/root fingerprints, references and native Task
  checks pass; no application acceptance, commit/push or archive is claimed.

## Notes

- The user explicitly authorized deletion of redundant/obsolete local Skills.
- A name being outside this repository's manifest is insufficient by itself:
  keep useful native/non-Trellis OpenSpec, release and domain/tool capabilities.
- No repository Skill source, manifest, invocation policy or plugin cache change.
