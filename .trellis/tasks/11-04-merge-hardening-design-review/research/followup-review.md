# Lock-adoption follow-up review

Task: `.trellis/tasks/11-04-merge-hardening-design-review`
Scope: current `adopt_skill_lock.py`, `install-lib.{sh,ps1}`, `install-skills.{sh,ps1}`, and Codex/Cursor wizard adoption wiring. Read-only; no repository/HOME/index mutations or repeated test suite. Main session owns the running fixture suite and final gate.

## Original findings

- **Duplicate-key loss — resolved by source review.** `json.loads(..., object_pairs_hook=unique_object)` now rejects duplicate keys recursively before payload/lock backups or writes. Normal component invocation does not read/modify external lock metadata unless the explicit adoption flag is present.
- **Missing PowerShell peer / Windows Python 3.10–3.12 fchmod — resolved by source review.** PS accepts the flag, calls the same resolver/JSON helper, previews entries, backs up the exact lock, publishes only after successful Skill copies, and restores the recorded lock backup through `Invoke-SkillsRollback`. Both Codex and Cursor wizards offer an independent default-no prompt only when Skills are selected. `os.chmod(temporary_path, mode)` replaces the incompatible fchmod call.
- **Custom alias chooses global lock — explicit-path case resolved; relative logical-cwd case remains below.** Standard-root comparison no longer follows an explicitly supplied custom symlink.

## Spec: remaining P2

`resolve_skill_lock_path()` uses `os.path.abspath(target.expanduser())`. For a relative target this obtains the physical process working directory, losing the shell's caller-visible symlink path. If the caller first executes `cd -L custom/skills` where this directory links to `~/.agents/skills`, then invokes `skills --target . --adopt-skill-lock`, the resolver chooses the global `.agents/.skill-lock.json`, not the caller-adjacent `custom/.skill-lock.json` promised by the existing custom-dot/custom-symlink contract.

A single new read-only resolver probe in an isolated temporary directory confirmed exit 0 and selection of the global lock. No test suite was rerun and no lock file was changed.

Recommendation: supply a verified logical cwd from the wrappers for relative targets, or use `PWD` only after verifying that it refers to the same actual directory as `os.getcwd()`. Do not blindly trust an arbitrary inherited PWD. Bash `pwd -L` and PowerShell's selected location can provide caller spelling; retain the current lexical standard-root match for absolute targets. Add one targeted relative-dot-through-custom-alias regression, alongside a stale/mismatched PWD case.

## Standards and transaction review

No additional standards violation was identified in this bounded source review:

- authoritative catalog/identity preflight remains before adoption validation and before writes;
- replacement consent and external registry adoption remain distinct;
- malformed/symlink locks fail before mutation;
- missing locks/no matching names do not create backups or rewrite bytes;
- matching lock backups are created before payload mutation;
- lock publication occurs after all copies; failure reaches both payload and lock rollback;
- normal opt-out preserves lock metadata; skip-Skills avoids the ownership prompt;
- source/target independence, current native profiles, final discovery audit and existing MCP/hooks behavior remain present.

The current documented wizard scope is Codex/Cursor. Other native profiles remain intact; this review does not silently expand adoption promises to additional third-party lock layouts.

The source review does not supersede the main session's currently running automated results, and it does not establish Windows-native runtime acceptance or concurrent external-writer safety.
