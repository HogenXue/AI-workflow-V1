# Two-axis review and implementation evidence

## Scope

User-confirmed baseline: `3bc7af23029a772d3da9672411b30e3d500e98b0`.
Pinned review HEAD: `b32419bb68c4298a62e54b874286537a359a71f1`.
Diff command: `git diff 3bc7af2...HEAD`.
Commits: `29cb55c`, `fe1e3fd`, `b32419b`.

The original spec is the archived `10-20-matt-skills-trellis-compat` Trellis PRD.
This task adds the explicitly requested one-click integration and audit of
`AGENTS.global.md`, `AGENTS.project.md`, and `AGENTS-egm.md`. The audit must not
misclassify unchanged templates or newly requested coverage as original-diff regressions.

## Standards

Independent Standards reviewer: no documented-standard violations or actionable Fowler
smells in the pinned diff. The existing explicit opt-in, backup, preflight validation,
exact-name removal and rollback behavior satisfy the installer contracts. The three
templates have no confirmed mutually exclusive rules within their intended contexts.

Standards findings: **0**; no worst severity. This is a static-review conclusion, not
a claim that tests ran during that initial review.

## Spec

Independent Spec reviewer: no confirmed regression or scope creep against the original
archived PRD. Two P2 findings concern the newly requested coverage and pre-existing rules:

1. **New coverage, P2 — recommended full installers did not offer ownership adoption.**
   The component accepted `--adopt-skill-lock`, but neither Codex nor Cursor full profile
   forwarded it. Fixed with a separate default-no prompt after Skills replacement consent;
   declining or skipping Skills does not detach registration.
2. **Pre-existing template, P2 — the global capability summary applied Trellis-only
   routes unconditionally.** The non-Trellis workflow fallback conflicted with unconditional
   Grill with Docs and Trellis artifact destinations. Fixed by qualifying the interview,
   design, TDD and task-capability routes and preserving other projects' existing workflow.

`AGENTS.project.md` and `AGENTS-egm.md` are project-specific Trellis supplements. No
confirmed additional defect was found; neither file was rewritten.

Spec findings: **2**, worst **P2**, both fixed. Original-PRD regressions: **0**.

## Additional compatibility checks

- Locally inspected cached third-party `skills` CLI 1.7.4: global registration uses
  `$XDG_STATE_HOME/skills/.skill-lock.json`, otherwise `~/.agents/.skill-lock.json`.
  Standard Codex/Cursor targets therefore cannot assume an adjacent per-host lock.
  A shared resolver now selects the actual global metadata path. This extends the older
  adjacent-lock design for known global targets; it is not counted as an original-PRD
  regression. Adoption does not synchronize or delete other host Skill copies.
- Native `trellis-check` caught a custom symlink-target regression during implementation:
  resolving the directory physically also selected the wrong adjacent lock. The fix uses
  canonical paths only for standard-host matching and preserves the caller's custom parent.
- GitNexus query returned no installer execution flow; impact lookup for
  `scripts/install.sh` returned Target not found. No successful graph impact analysis is
  claimed. Source tracing and isolated behavior tests supplied the fallback evidence.

## TDD and native review evidence

- Global-lock tests: RED showed Codex/Cursor/XDG/preview selecting the wrong lock;
  GREEN passed all three added test methods (including standard-host subcases).
- Four real-PTY profile tests: initial RED had three failures because the adoption prompt
  was absent; skip already passed. GREEN passed all four, covering Codex acceptance,
  default decline, Cursor shared-lock adoption and Skills skip.
- Full interactive module: **24 tests passed**. Component module before the symlink
  regression test: **36 tests passed**. Skill-validator module: **36 tests passed**.
- Symlink regression: RED changed the physical-directory sentinel instead of the caller's
  lock; GREEN passed the new test, then all **13 lock-related tests passed**.
- Global routing module after the final template edits: **5 tests passed**.
- `bash -n` on all three changed Shell files and `git diff --check` passed.
- Native `trellis-check` completed with **no unresolved implementation findings** after
  the symlink fix and final template-boundary review.

All behavior tests use temporary HOME/project roots and local Graphify fixtures; no
real host configuration, external project, network install, commit or push was performed.

## Final gates

The final repository-wide check is `config/workflow_check.py quality --task` with the
task directory. Its machine-readable result is stored in `verification.json`; that
file, not this advance note, is authoritative for the final quality result. The current
suite inventory is 129 test methods. Completion must reuse the resulting content
fingerprint without modifying tracked task records afterward.
