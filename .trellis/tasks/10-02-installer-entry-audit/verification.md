# Installer delivery evidence — 2026-10-02

## Result

The authorized entry hardening, agents template migration, and missing-CLI bootstrap are
implemented. No commit, push, actual user-profile install, or real dependency download was run.

## Native Trellis check

The native helper is not exposed as a callable tool; its current `trellis-check` skill was
read and applied manually in the configured Codex inline mode.

- **Spec**: All PRD acceptance criteria map to the implementation and isolated regression
  evidence. Full installs prepare dependencies before host writes; invalid input and component
  failures stop the wizard. Existing usable CLI versions are kept. The canonical global template
  supplies both agents documents and Cursor rule bodies; project/EGM supplements remain deliberate
  references. Dependency paths append after existing PATH entries, preserving the user's Python.
- **Standards**: Bash/PowerShell ports share dependency logic and preserve their CLI/host mapping.
  Changes stay within the authorized installer/template/docs/test scope. Existing project rules,
  independent task changes, system Python, shell startup files, and runtime versions are preserved.
  No debug hooks, real package-install test, or automatic project initialization was introduced.

## Final checks

| Check | Result |
| --- | --- |
| Task-scoped unittest suite | 115 tests passed in 37.525 seconds |
| Skill validator | All 7 current manifest Skills passed |
| Configuration consumer validation | Passed |
| Bash syntax: entry, agents, Cursor, Graphify, deps | Passed |
| PowerShell syntax: corresponding 5 scripts | Passed |
| Trellis implement/check context validation | Passed, 2 entries each |
| `git diff --check` | Passed |

The unittest suite discovers `test_install_*_ps.py`, `test_install_dependencies.py`,
`test_install_wizard.py`, `test_validate_all_skills.py`, `test_effective_config.py`,
and `test_grill_with_docs_trellis_route.py`. Dependency subprocesses are simulated;
actual Bash/PowerShell entry previews and temporary-template installs are also exercised.

## TDD and diagnostic history

- RED: PowerShell continued after fixture exit 37 and printed `Done.`. Both mode menus accepted
  invalid input/EOF. Bash skipped dangling-root replacement prompts. Entry fixes turned these green.
- RED: Agents preview still referenced the obsolete root global template. Migration changed the
  source to `agents/AGENTS.global.md`; actual temporary agents/Claude/Cursor installs pass.
- RED: `deps` dispatch and preflight were absent. Bootstrap tests now cover ordering, failure
  propagation, missing tools/runtimes, engine flags, dry-run purity, npm PATH recovery, isolated
  Graphify installation, existing/broken commands, and false-success detection.
- RED: A private tool directory could shadow PowerShell's existing Python. Appending PATH rather
  than prepending fixes this; the dual-shell path-transfer regression passes.
- Windows symlink assertions now allow the equivalent `\\?\` target namespace prefix while still
  checking that the backup is a symlink pointing to the expected destination.
- An intermediate 115-test run failed the pre-existing parallel-backup finalization test once.
  Its implementation was unchanged. The final 115-test run, including that test, passed.
- An earlier all-platform diagnostic run on Windows ran 160 tests with 20 failures. It mixed
  Unix-oriented path/permission assumptions, intermediate assertions, and concurrent unrelated
  changes. This is retained in `full-suite.log`; it is not the final task-scoped gate.

## Boundaries and limitations

- Real npm/PyPI downloads and complete native macOS/Linux suites are unrun. Runtime package engine
  checks are enforced during actual npm installation; OS runtimes are prerequisites.
- Before deleting the three old root templates, their SHA-256 values matched the corresponding
  `agents/` copies. This task did not change their bodies. Later independent rule updates to the
  canonical global/project templates are preserved.
- Recallium/Mem0 tools remain unavailable. No rules/history retrieval or memory save is claimed.
  Stable contracts are recorded in `.trellis/spec/scripts/installer-contracts.md`; save them to
  Recallium with related files when the backend becomes available.
- GitNexus indexing succeeded, but impact traversal returned partial/error results. The user
  approved source-reference analysis and dual-platform regression as the replacement. A read-only
  full-worktree detect-changes run returned medium risk and includes unrelated concurrent work.
- Optional cleanup of `.codex-tmp/installer-audit` was rejected with `blocked by policy`; the
  generated directory is retained. This is separate from the completed template deletion.

## Use

The recommended full-install wizard prepares missing dependencies automatically. To run only
dependency preparation on Windows:

```powershell
scripts\install.cmd deps --dry-run
scripts\install.cmd deps --apply
```

Unix equivalents are `bash scripts/install.sh deps --dry-run` and `deps --apply`.
