# Implementation

- [x] Inspect source, installations, native specs, and concurrent changes.
- [x] Preserve source and user-directory backups.
- [x] Activate the approved task and apply instruction corrections.
- [x] Normalize diagnostic paths and align old routing assertions with native task checks.
- [x] Validate source skills and user references.
- [x] Apply the clarified seven-skill scope; update both installers, configuration consumers, docs, and tests.
- [x] Verify backup hashes, move named removed directories into backup, then install seven skills and paired config.
- [x] Verify installed hashes, absence of duplicates/legacy files, and preservation of system/plugins.
- [x] Record task-scoped Trellis review and complete without Git commits.

## Validation

- `python -B scripts/validate-all-skills.py`
- Existing validator, Grill routing, effective-config, and PowerShell component installer tests.
- `python -B .trellis/scripts/task.py validate .trellis/tasks/10-02-skills-cleanup`
- Scoped diff whitespace, backup/content hashes, reference resolution, and local Graphify query/path/explain smoke checks. The offline AnySearch doc check preceded the subsequent explicit removal of that skill.

Apply native `trellis-check` in the main session. Report existing failures independently. No native helper/subagent is exposed or required.
