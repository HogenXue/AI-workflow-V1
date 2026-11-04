# Design

## Merge boundary

Preserve current main behavior as the supported base; bring in incoming functional
intent rather than replacing newer modules with older branch snapshots. Review the
actual merge-base diff and originating task records. Keep new package helpers at
existing scripts/lib seams; avoid a second catalog, lifecycle or installer engine.
Map any obsolete root template to agents/AGENTS.global.md. Resolve manifest/setup
choices by ensuring one bounded owner and preserving all existing capabilities.

## Installation contracts

Third-party lock registration is a distinct opt-in action from Skill replacement.
Resolve lock location consistently across peers/profiles; preserve unrelated entries,
back up before writes, and roll back affected payload/metadata on failure. Retain
custom roots, no-write preview and final discovery audit. Share JSON/data helpers
between Bash and PowerShell rather than duplicating ownership semantics.

## Execution and evidence

Capture original patches, files and hashes in private durable storage. Stash only
those exact pre-existing dirty paths; leave current task planning records present.
Merge without committing, resolve conflicts, inspect actual combined code, reproduce
bugs before repairs, and run proportional tests. Use complete isolated fixtures if
shared changes affect all profiles. Final check is one native Trellis gate. Commit
then restore/verify saved local work, retaining the stash until restoration passes.

GitNexus lists only EGM/NASQ; no index exists for this repository. Source call paths,
Git diffs and fixture regressions supply impact evidence; no graph rebuild is run.
The main session owns code writes/final checks (inline mode). Parallel read-only
specialists may examine design seams; they do not start another implementation/check.

## Reviewed decisions

- The incoming branch predates five-host and 19-capability changes. Keep all current
  capabilities and add setup as a twentieth explicit-only, optional compatibility
  tool for actual third-party consumers; already adapted Skills need no bridge.
- Keep main's existing user/project-rule Memory authorization, including host-memory
  boundaries; a decision or handoff does not independently enlarge that authority.
- Keep the canonical agents/ templates and direct validator/unittest CI jobs. Add
  requirements-dev.txt to both cache keys and verbose test output. Do not revive
  removed workflow_check.py or root instruction templates.
- Move lock path semantics into the existing Python adoption helper used by both
  peers. Caller-visible aliases/dot paths keep their adjacent registration; only
  standard paths share the global/XDG lock. Validate logical cwd against physical
  cwd before trusting it. Reject duplicate JSON keys before updates.
- Apply the same opt-in, preview, backup and rollback behavior to PowerShell. Keep
  the original Codex/Cursor wizard adoption scope; other profiles remain native.
- Incoming branch history remains in research/incoming-* as evidence, while native
  main Session numbering is retained. Existing uncommitted history stays protected.

Selected impact boundary: shared Skill installation and five host consumers; high
risk is accidental ownership/metadata or payload loss. No graph exists here; source
callers and temporary-host rollback/preview tests supply the actual evidence.
