# Windows existing-hooks confirmation repair — 2026-10-05

## Verified cause and scope

The user's exact failure was in the Codex existing-hook prompt after MCP merge. PowerShell
parses `$codexHome?` as the variable `codexHome?`; strict mode raises an unset-variable error before
the confirmation is displayed. Cursor's `$proj?` prompt had the same defect. The only production
changes are explicit `${codexHome}` / `${proj}` boundaries in those two strings.

The earlier isolated fresh-profile runs correctly reached Done, but did not trigger existing-hook
confirmations. The 2026-10-04 diagnostic remains historical evidence; the reported symptom is now
reproduced, understood and repaired.

## TDD and checks

- RED: two new regression tests, four subcases (Codex/Cursor x No/Yes), reproduced the exact
  unset-variable errors. The Codex fixture uses the user's HTTP Recallium and HTTPS Mem0 URL
  shapes and explicitly answers No to both URL replacements.
- GREEN: both tests/four subcases passed after the two-line production change.
- Existing PowerShell merge module: 13 tests passed in 7.710 seconds.
- Portable PowerShell 7.0.13: both new tests passed in 3.207 seconds.
- Both changed scripts passed PowerShell parsing; no remaining unbraced `$name?` patterns occur
  in installer PowerShell scripts. `git diff --check` passed.

## Actual Windows interactive acceptance

Ran the real CMD launcher and full Codex wizard in an isolated HOME/USERPROFILE/CODEX_HOME with
pre-existing hooks and MCP URLs. Input sequence: agent 1, full mode 1, Proceed Yes, MCP overwrite
Yes, Recallium replacement No, Mem0 replacement No, existing-hook replacement Yes.

Observed the formerly failing question, backups of original hooks, installation of hooks.json and
session-start.sh, final `Done.`, and process exit 0. The fixture retained the HTTP Recallium and
HTTPS Mem0 URLs. Automated No cases additionally prove original hooks survive and return 0.

Real user-level config/hooks were never test targets. No actual tool download, commit, push or
task-state mutation was performed. Broader fresh-profile evidence is reused; no unrelated full
repository suite was rerun for this local prompt-boundary fix.

## Native Trellis check and memory

Applied native trellis-check guidance manually: Spec criteria cover successful keep/replace,
URL choice preservation and actual interactive completion; Standards cover minimal local scope,
literal variable boundaries, targeted tests and preserving unrelated work. No remaining finding
within this repair scope. Mem0 is configured/available; Recallium MCP remains unexposed.
