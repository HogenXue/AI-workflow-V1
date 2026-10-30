# Adapt one-click Skill ownership and review AGENTS templates

## Goal

Connect ownership adoption to the Codex/Cursor wizard and review AGENTS.global.md, AGENTS.project.md and AGENTS-egm.md against baseline 3bc7af2 while preserving Trellis.

## Requirements

- Adapt the existing Codex/Cursor recommended installer to offer explicit, backed-up
  ownership of package Skill names, independently from replacement consent.
- Use the third-party global Skill lock for standard host targets, including XDG state
  configuration. Preserve custom-target adjacent-lock compatibility and unrelated entries.
- Review changes since user-confirmed baseline `3bc7af2` along separate Standards and Spec
  axes. Also audit AGENTS.global.md, AGENTS.project.md and AGENTS-egm.md; these are the
  three templates the user meant, not three installation hosts.
- Resolve verified routing conflicts while preserving Trellis and non-Trellis workflows,
  managed blocks, host-specific destinations and explicit project-root boundaries.
- Preserve ordinary CLI behavior, opt-out, backup and rollback guarantees. Do not add a
  Claude installation profile, alter EGM business architecture, or modify other projects.
- Leave Git changes uncommitted unless separately requested.
- Follow-up: align installed implementation, release, interview and domain Skills with
  Trellis ownership and explicit Git authorization; unify Memory write consent and
  Graphify platform dispatch, and sync the repaired packaged Skills locally with backups.

## Acceptance Criteria

- [x] Real TTY tests prove Codex/Cursor can opt into ownership adoption and decline it safely.
- [x] Standard targets use the shared global lock (including XDG); custom target tests and
  unrelated metadata/rollback contracts remain valid.
- [x] Both review axes and all three template audit outcomes are recorded separately.
- [x] The global template routes non-Trellis tasks to their existing workflow.
- [x] Targeted tests and native Trellis review pass with no unresolved implementation findings.
- [x] Review follow-up: Codex setup selects the active override entry and custom dot
  target spellings resolve the adjacent lock without changing symlink ownership.

## Scope confirmation

The user subsequently authorized repair of the six Skill compatibility findings and
local installation alignment. This does not authorize commits, releases or graph rebuilds.

The user explicitly requested installer adaptation and review, then confirmed baseline
`3bc7af2` and the three named AGENTS templates. No further product choice remains open.
