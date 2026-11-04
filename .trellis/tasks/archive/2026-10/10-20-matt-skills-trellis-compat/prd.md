# Adapt Matt skills to Trellis and resolve shared skill ownership

## Goal

Keep Trellis as the sole workflow, package a compatible setup entrypoint, restore four adapted skills, and prevent third-party lock updates from replacing package-managed copies.

## Requirements

- Package a compatible `setup-matt-pocock-skills` entrypoint for reuse in other projects.
- In Trellis repositories, keep tasks, requirements, execution, quality gates, domain terms,
  and durable decisions in their existing Trellis locations. Setup adds configuration
  pointers, not a second workflow or task lifecycle.
- Codex must discover project instructions even when `CLAUDE.md` also exists. Preserve
  existing instructions, managed blocks, user customizations, and authorization boundaries.
- Non-Trellis repositories retain their current workflow; setup does not initialize Trellis.
- Restore the package's four adapted shared Skills (`grill-with-docs`, `tdd`,
  `diagnosing-bugs`, `codebase-design`) and install the adapted setup in Codex.
- Provide explicit, backed-up adoption of package-owned names from an adjacent third-party
  Skill lock. Preserve unrelated entries and metadata; preview is read-only; failures
  restore prior Skills and lock contents.
- Do not modify other projects, global MCP/hooks, or Git history as part of this request.

## Acceptance Criteria

- [x] The setup Skill and its templates pass package validation and preserve Trellis ownership.
- [x] The installer distributes setup and offers explicit, transactional Skill lock adoption.
- [x] Regression tests cover adoption, unrelated metadata, preview, invalid lock, and rollback.
- [x] Shared Codex copies of setup and the four adapted Skills match this repository, with
  their third-party update registrations detached and backups retained.
- [x] Native Trellis review covers the final implementation with no unresolved findings.

## Scope confirmation

The user explicitly requested adaptation, preservation of Trellis, and resolution of the
four installed Skill conflicts. Existing non-conflicting Matt Skills remain installed.
