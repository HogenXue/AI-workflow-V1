# Integrate AIHero practices into native Trellis

## Goal

Improve requirements discovery, task slicing, review, and session continuity while keeping Trellis as the sole workflow owner.

## Requirements

- R1: Preserve Trellis task state, PRD/design/implementation artifacts, native checks, and Git authorization boundaries.
- R2: Keep `grill-me` explicit and stateless. Reuse agreed conclusions without a second interview; unresolved ordinary requirements use native Trellis planning.
- R3: Inspect facts before questioning; settle prerequisite decisions first; ask only unresolved user choices. Mark branches requiring research or a bounded prototype instead of interviewing indefinitely.
- R4: Split large work into independently verifiable outcomes with explicit blockers; parent/child links are not dependencies.
- R5: Native `trellis-check` reviews Spec and Standards separately, including uncommitted and new task-owned files.
- R6: Capture domain language and durable decisions selectively in existing Trellis spec locations; resume from canonical artifacts and evidence.
- R7: Change the project-global template (`agents/AGENTS.global.md`), without editing live `.codex/AGENTS.md`, running installers, installing upstream skills, or adding a tracker.

## Acceptance Criteria

- [x] Global/project routing and native workflow agree on explicit Grill and ordinary planning.
- [x] Native planning covers dependency-aware questions, outcome slices, and selective domain/decision capture.
- [x] Native checking distinguishes Spec and Standards and covers the actual task scope.
- [x] Continuation references canonical artifacts and verification scope without duplicating specs or granting Git authorization.
- [x] Skill structure, task context, and relevant routing checks pass; unrelated failures are identified separately.

## Out of Scope

Runtime scripts, hooks, manifest changes, graph rebuilds, new task statuses, automatic subagents, global installation, Git commits/pushes, and unrelated working-tree edits.

## Authorization

The user requested implementation, chose native Trellis integration, and specified project-global-template edits instead of live Codex rules.
