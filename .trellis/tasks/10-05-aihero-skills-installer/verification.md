# Verification and continuation

Date: 2026-10-05. Implementation verified for the selected package contract; broader Windows/Git Bash baseline limitations are recorded below. Native task remains `in_progress` pending authorized Git/finish steps.

## Delivered scope

- Eleven new independent AIHero adaptations: documented Grill, grilling, domain modeling, spec synthesis, task slicing, wayfinding, research, prototypes, implementation, review, and handoff. Manifest now has 18 skills including the seven existing entries.
- Source pinned to `mattpocock/skills` commit `24fe0ef7737efae15c87225755e9f6f5965e4888`; original path/hash evidence in `research/upstream/` and `skills/aihero-provenance.json`. Every new skill carries portable metadata, source attribution, and MIT license.
- Global routing consolidated in project-owned `agents/AGENTS.global.md`; project/EGM/native guidance and install docs aligned. Trellis owns artifacts/state/final gates; new capability names do not grant implementation/Git permission.
- Bash/PowerShell legacy lists preserve the restored names. Both one-click plans expose the package and global template source. Windows CI explicitly runs the new installation regression module.
- No real user-level configuration installation, graph rebuild, commit, push, external tracker, or project initialization. Existing Windows hook fixes and other dirty work were preserved.

## Native Spec review

No unresolved findings in this task's requirements:

1. All selected skills are independently installable and useful; supporting interviewing/domain/research/prototype/handoff capabilities are present.
2. `grill-me` remains explicit/stateless. Documented discovery is task-bound and not repeated through native brainstorm. Synthesis, task slicing, wayfinding, implementation and review all use native artifacts and gates.
3. Upgrade/prune handling uses ordinary replacement/backups for restored names. Real copy tests verify files/resources and licensing in installed folders.
4. One-click host profiles continue to use the same manifest and host-specific destinations. Plans/global source mapping are coherent; helpers do not overwrite other repositories' native workflow files.
5. Verification captures failures and limits honestly rather than declaring the broader mixed-platform suite green.

## Native Standards review

Reviewed task-owned skill/template/installer/test/docs hunks against installer contracts, current user scope, skill-creator guidance, and project workflow. No unresolved task-caused standards violation. Contract changes are paired in both shell peers; script signatures, host MCP/hook boundaries and backup/rollback mechanics are unchanged. New tests exercise observable copied content, dry-run mutation boundaries, and prune upgrades. Existing assertions prohibiting the now-requested skills were updated without weakening unrelated checks.

No native MCP/command helper is exposed; the project native `trellis-check` instruction file was read and its Spec/Standards/check steps executed directly in inline mode. An independent skill-creator forward validation exercised skill behavior in an isolated fixture, not as a second quality gate.

## Executed checks

- Before implementation: new real installation regression module ran 6 tests, with 10 failure records caused by missing requested skills and restored names treated as legacy. This establishes RED.
- After implementation: same 6 tests passed in 12.746 seconds. Bash and PowerShell both verified fresh copy of all 18 folders/resources/licenses, preview preservation, and upgrade backups with only actual legacy names pruned.
- `python scripts/validate-all-skills.py`: all 18 skill structures and configuration consumers passed.
- `test_grill_with_docs_trellis_route.py`: 5 tests passed.
- `test_validate_all_skills.py`: 35 tests passed, including the later CI wiring change.
- Skill-creator quick validation: all 11 new skill frontmatters passed with explicit UTF-8 mode.
- Native `task.py validate`: implementation/check context references passed.
- Bash syntax checks for both changed shell entrypoints passed. Scoped `git diff --check` passed (only line-ending normalization notices).

## Broader installation batch and baseline comparison

Command: Python unittest discovery for `test_aihero_install.py`, `test_install.py`, `test_install_components_ps.py`, `test_install_wizard.py`, and `test_install_entry_ps.py`, with Git Bash on PATH and UTF-8. Full output: `install-checks.log`.

Result: 72 test methods in 111.145 seconds, with 11 failure records in 10 pre-existing Bash test methods. All 32 PowerShell/source-contract methods and the 3 new Bash contract methods passed. No skips were reported in this batch.

Failed categories: mixed Windows/POSIX path expectations and source-overlap handling, POSIX chmod/PATH-shim assumptions on Windows, and MiniMax/WorkBuddy wizard path-format assertions. Do not describe this batch as all passing.

To distinguish regressions, extracted unmodified HEAD `de4820b` with `git archive` into an isolated temporary root and ran exactly those 10 methods. Result: the same 11 failure records in 9.933 seconds. Full output: `baseline-checks.log`; reproducible test list/root/HEAD recorded in `research/baseline-run.json`. The first baseline harness lacked its import path, then was corrected before the recorded comparison; no production code was changed for that harness setup.

These known failures were not repaired or skipped by this task. Bash on actual Linux/macOS and full real dependency/MCP profile installs were not exercised here; CI retains those environments. Full-profile routing was exercised with isolated harmless component fixtures; production skill copy/upgrade behavior was exercised through real component entrypoints.

## Independent forward validation

Fixture: `C:/Users/hogen/AppData/Local/Temp/aihero-forward-ac1cx6om`.

- `code-review` correctly reported sum behavior and health behavior violations separately from missing type annotations. Actual targeted behavior probes failed as expected. Read-only review did not edit the application.
- `to-spec` incorporated confirmed numeric-input and TypeError acceptance into the existing PRD, retained health/API/no-network facts, and did not rediscover, implement, or publish. Only PRD changed; hashes of the other six fixture files remained unchanged.
- Instructions worked without a platform-specific Skill tool or native helper. This sample validation does not guarantee future model behavior for every capability.

## Impact, memory, and next action

Follow-up compatibility audit: see `compatibility-audit.md`. Corrected batch-child planning to preserve parent session context with supported `--no-start`; real native task and isolated install probes passed, as did all 18 structures and 40 relevant route/structure tests. Existing broad install evidence was not invalidated because executable installer logic is unchanged.

GitNexus historical index is stale; `_manifest_skills` and `validate_skill` impacts returned LOW, supplemented by current manifest/host source tracing and real isolated install evidence. No fresh graph or full PowerShell graph coverage is claimed. No commit was requested, so no pre-commit graph scan was needed.

Recallium feature memory #1248 was stored successfully with related files, stable packaging decisions and actual verification limits. That memory is not the canonical PRD/task. On continuation, reuse still-valid evidence and inspect only this task's hunks; unrelated dirty files must not enter a blanket commit. Real global installation and Git/archival remain separate authorized actions.
