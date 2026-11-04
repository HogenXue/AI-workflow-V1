# Lock adoption known-findings closure review

Task: `.trellis/tasks/11-04-merge-hardening-design-review`
Date: 2026-11-04 (Asia/Shanghai)
Mode: targeted read-only review inside the main session's quality gate.
Source snapshot: `closure-source-fingerprints.json`.

## Spec

All previously reported lock-adoption findings are closed in the inspected source:

1. **Duplicate JSON keys:** the shared `unique_object` object-pairs hook rejects duplicates before adoption mutates either lock or payload. Unrelated registration/preferences remain in the parsed mapping.
2. **Explicit custom symlink target:** lexical path comparison preserves its caller-adjacent lock rather than reclassifying it by physical destination.
3. **Relative `.` within a custom symlink cwd:** wrappers now pass an explicit logical cwd (Bash `pwd -L`; PowerShell `CurrentFileSystemLocation.Path`). The shared helper checks absolute spelling plus `samefile(physical_cwd)` before using it. Invalid explicit hints fail closed; unverified/stale environment PWD is not used to redirect the lock. Configured standard-path alias fallback runs only when no verified caller spelling exists. This closes the exact previously reproduced combination without blindly trusting PWD.

Source inspection also confirms that adoption remains explicitly selected, strict catalog/identity checks precede mutation, previews/no matching locks do not write, lock backup precedes payload replacement, and lock publication follows all successful copies. Both shell rollback paths use the exact recorded backup and restore payloads as well as lock state.

## Standards

The earlier PowerShell/Windows gap is closed: both peers expose the adoption component flag, share the Python resolver/editor, and independently prompt Codex/Cursor users with default no only when Skills are selected. The helper uses path-based `os.chmod`, compatible with the declared Windows Python 3.10-3.12 baseline. Installer specifications now describe the verified logical-cwd rule and peer behavior.

No unresolved issue remains from this bounded review of the known findings. This statement does not expand the review to unrelated modules or claim universal platform/runtime compatibility.

## Evidence boundary

Read the new logical/stale-PWD test definitions and inspected both wrapper calls; did not run them again. The main session reports 12 lock/rollback cases and 38 TTY/interactive cases passed and owns the in-progress full final regression. Those are main-session results, not a second execution by this reviewer.

No repository files, HOME paths, Git index or host settings were changed. Only this private review and source fingerprint record were written under `/private/tmp`.
