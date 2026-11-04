# Verification notes

## Test-first evidence

The initial `test_install.py -k skill_lock` run produced three expected failures because
`--adopt-skill-lock` was not supported; the existing no-adoption preservation test passed.
After implementation, those tests passed. Native review added a FIFO regression that
first failed with a two-second timeout, then passed after regular-file validation.

Final targeted checks: 33 installer tests, 36 Skill contract tests and 20 interactive
installer tests passed. Package Skill validation (10 Skills), setup quick validation,
shell syntax and `git diff --check` passed. Native `trellis-check` reported no unresolved
findings after fixing special-file rejection and strengthening project mapping pointers.

The shared final quality gate writes machine-readable results to `verification.json`;
that evidence is authoritative for the final worktree fingerprint.

## Independent setup exercise

An independent agent executed setup in temporary repositories:

- `/tmp/matt-setup-forward-a.d0qj8x`: Trellis, both rule files, an existing managed block,
  custom user rules and a legacy `.scratch/` tracker pointer. Setup configured Trellis,
  preserved old content/backups, and did not create another task or spec. Repetition was
  byte-idempotent for the tested version.
- `/tmp/matt-setup-forward-b.2HAWqh`: a non-Trellis CLAUDE-only project with an established
  local tracker. Setup created a discoverable Codex AGENTS entry and reused the existing
  tracker/domain documentation without introducing Trellis.

The parent inspected generated artifacts. After native review strengthened the generated
configuration read requirement and project mapping precedence, the independent agent
reapplied the final Skill to fixture A. Only its AGENTS entry changed (with a new backup);
all other existing files were unchanged. A further run preserved all 15 paths and hashes,
confirming final-version idempotency. No real target project was modified.

## Installed result

Installed all 10 manifest Skills into `/Users/hogen/.agents/skills` with copy, replacement
and explicit Skill lock adoption. All installed directories match repository sources.
The four conflicting names plus setup were removed from the third-party update lock;
34 unrelated lock entries and all other lock metadata remain identical to the backup.

All 102 files belonging to non-package shared Skills retained their aggregate SHA-256.
Codex global AGENTS, config.toml and hooks.json retained their original hashes.
The old `grill-me` Skill is outside the manifest and was preserved, as requested scope
does not include unrelated legacy cleanup.

Backups are under `/Users/hogen/.agents/.ai-workflow-backups/`, including
`.skill-lock.json.20261020T020823Z.bak` and the corresponding timestamped Skill directories.
No Git commit/push or global MCP/hook change was made. A future explicit upstream full
reinstall can still overwrite these names; use this package to update them instead.

## Graph evidence limitation

GitNexus query returned no installer execution flow; impact reported that the Bash
installer target was not indexed. No graph-based impact success is claimed. Direct
source review and temporary-directory installer tests supplied coverage instead.
