# Windows hooks repair publication review

Date: 2026-10-05. Reviewed against current HEAD `4632c8f` and the existing installer-entry task.

## Approved plan and scope

The user authorized retaining effective fixes, reviewing the plan, and submitting them. Preserve
the smallest repair: delimit `${codexHome}` and `${proj}` before the literal question mark in two
PowerShell existing-target prompts. Include the focused regression module, native contract note,
task acceptance update, original repair evidence, and this review. Prior commit/push authorization
continues; no new branch, force push, amend, deletion, archive or real user installation is needed.

Exclude unrelated model-routing plans, historical archived task folders and the old broad suite
log. GitNexus skill files have no content difference from HEAD and need no content commit.

## Native Spec review

No remaining finding. The corrected prompt now resolves the intended variable under StrictMode,
retaining the same user-visible path/question and default No. Keep and replace branches remain
unchanged, as do MCP URL decisions, explicit project-root handling and timestamped backups.

The regression tests execute copied real merge scripts and helpers inside disposable roots.
They cover Codex/Cursor x No/Yes, original-hook retention on No, installed hooks/rules on Yes,
existing URL choices, and preservation of the project's root AGENTS. The TTY seam is stubbed
only in the disposable helper; prompt/merge/backup behavior is real.

## Native Standards review

No remaining finding in the repair scope. Literal variable boundaries are explicit and supported
by the existing PowerShell runtime range. No function/API signatures, task schema, dependency,
host mappings or rollback logic changed. Bash does not parse these PowerShell strings; a matching
Bash change would be unnecessary. The paired Codex/Cursor defect is fixed consistently.

This is a local low-risk string-interpolation repair. Current source references and native test
evidence establish scope; no graph refresh or unrelated runtime refactor is warranted. Native
`trellis-check` steps were performed directly in inline mode, not through an unavailable helper.

## Verification run for publication

- New existing-hooks module plus existing PowerShell merge module: 15 test methods passed in
  10.011 seconds, no skips. The two regression methods contain four keep/replace subcases.
- Baseline negative control: copied the unmodified HEAD versions of both scripts into the same
  disposable fixtures; two test methods produced four expected StrictMode failure records,
  zero unexpected errors and zero skips. Neither production working-tree script was reverted.
- Native task context validation passed.
- Staged whitespace check passed after normalizing captured log line endings. The native diff
  contains nine repair/evidence paths. GitNexus staged detection reported no indexed changes,
  so it is not evidence that the PowerShell edit has zero impact; current source review and the
  real targeted tests establish this local scope.
- Review confirms CI's existing `test_install_*_ps.py` pattern includes the new module.
- Prior actual isolated Windows interactive and portable PowerShell 7.0.13 evidence remains in
  `windows-hooks-fix-2026-10-05.md`; those checks were not rerun or claimed as new evidence here.

Full outputs: `windows-hooks-publication-checks.log` and `windows-hooks-before-fix-checks.log`.
No full-repository test pass is claimed. No real user's configuration/hooks were test targets.

## Commit boundary

Stage only the repair, regression and necessary task/spec documentation. Verify staged diff and
remote state, then create a separate `fix(installer)` commit and push normally. Preserve every
unrelated worktree change; task archival remains separate from this publication checkpoint.
