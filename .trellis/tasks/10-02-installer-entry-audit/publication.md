# Installer publication — 2026-10-03

The user explicitly authorized commit and push to the existing `main` branch / `origin`.
Publication contains the installer, automatic dependency preparation, source/rollback/compatibility
repairs, related specs/docs/tests, and this task's review evidence. Independent AIHero/workflow,
model-routing, and memory-rule changes remain uncommitted.

The three templates are relocated from their committed root versions into `agents/` using staged
blobs; current user-edited bodies remain intact and unstaged. This avoids publishing another task's
rule changes through the installer migration. Generated full-suite logs and publication helper
files are excluded. The exported index snapshot is the validation target, rather than the dirty
shared working tree.

## Additional publication blocker and fix

Snapshot validation reproduced the previously intermittent backup concurrency failure: two
successful calls produced one backup. `New-Item -ItemType Directory` performs an existence check
and idempotent directory creation; two contenders can both report reservation success.

A deterministic barrier regression with two different sources reproduced the overwrite before
the fix. PowerShell now reserves a name with `FileMode.CreateNew`, stages into a unique payload,
and cleans the lock/unpublished payload in `finally`. Existing timestamp/sequence names and error
diagnostics remain. Bash already uses atomic `mkdir` and needs no change. The library suite passes
under current PowerShell and portable 7.0.13. This is a necessary backup-safety fix before push.

Final snapshot results are recorded below. No real tool installation or native
Unix full suite is implied. Recallium/Mem0 remain unavailable; save the stable backup reservation
decision with `scripts/install-lib.ps1` and `tests/test_install_lib_ps.py` when available.

## Exported staged-snapshot validation

- Current PowerShell task scope: **129 tests passed**, 50.249 seconds.
- Portable PowerShell 7.0.13 installer/wizard scope: **70 tests passed**, 53.762 seconds.
- Skill validator: all 7 Skills passed; configuration consumers passed.
- Staged whitespace/scope checks passed; GitNexus staged check reports low risk, with the
  previously documented graph coverage limitation for PowerShell retained.

Commit title: `feat(installer): bootstrap tools and harden install recovery`.
The three template relocations are exact committed-body moves. All extra global/project template
rule edits, root AGENTS edits, AIHero/workflow tasks, and model-routing tasks remain in the worktree.
