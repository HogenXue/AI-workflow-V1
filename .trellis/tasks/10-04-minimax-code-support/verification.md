# Verification — 2026-10-04

The initial host-support checks below precede the endpoint-default follow-up.
The final section records the current checks for the affected MCP behavior.

## Result and scope

MiniMax Code and WorkBuddy repository support is implemented: independent wizard
profiles, native global Skills/defaults/instructions, native JSON MCP components,
home overrides and existing-file precedence. Bash and PowerShell implementations
are present. No commit, push, real user-profile installation, application download,
authentication, model API call or project/platform initialization was performed.

## TDD and implementation evidence

Before production changes, new merge tests failed with
`ERROR: unknown installer component: minimax-merge` / `workbuddy-merge`, and new
wizard cases failed with `ERROR: invalid agent choice` for selections 4/5.
These feature-missing assertion failures supplied RED evidence. Missing-fragment
fixture errors were not counted as RED evidence.

After implementation, native-path, transport, backup/preservation, dry-run,
invalid-input and wizard routing/failure tests passed. Additional tests execute
the real full-profile component sequence in temporary HOME directories: seven
Skills, paired defaults, correct global documents and MCP are installed while
native model/permission config and other profile/project roots remain unchanged.

Two adjacent macOS failures were also reproduced against the unchanged HEAD
installer: Bash 3.2 rejects an empty array expansion under `set -u`, and the PATH
fixture assumed a `python` command already existed. The touched entry now handles
empty component arguments explicitly; the fixture tests the available interpreter.
The old three-host parser assertion and PowerShell document-mapping assertion were
updated for the approved five-host contract and shared document-profile helper.

## Actual commands and results

| Command / check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests -p test_install_new_hosts.py -v` | 20 discovered: 10 passed, 10 skipped (`pwsh` absent); 2.227 s |
| `python3 -m unittest discover -s tests -p test_install_wizard.py -v` | 23 discovered: 13 passed, 10 skipped; 0.464 s |
| Python unittest loader discovering `test_install_interactive.py`, `test_install_entry_ps.py`, `test_install_merge_ps.py` in one suite | 60 discovered: 38 passed, 22 skipped; 3.014 s; 0 failures/errors |
| `bash -n` for `install.sh`, `install-json-mcp.sh`, `install-minimax-merge.sh`, `install-workbuddy-merge.sh` | passed |
| `ast.parse` of changed Python implementation/tests and JSON parsing of both native fragments | passed |
| `python3 .trellis/scripts/task.py validate .trellis/tasks/10-04-minimax-code-support` | passed |
| `git diff --check` | passed |
| `git apply --reverse --check <pre-edit snapshot>/unstaged.patch` plus scoped source/byte comparisons | passed: pre-existing LAN code/tests/README policy/task files, AGENTS deletion and index retained |

Total: **61 passed, 42 skipped** across the selected modules. Passing new-host and
wizard evidence was reused after documentation/formatting-only edits. The adjacent
suite was retried after updating its obsolete contract assertions. No full
repository suite or package-level quality preset was selected.

## Native Trellis check

The repository's `.cursor/skills/trellis-check/SKILL.md` was read and applied
manually in the configured Codex inline mode; no dedicated tool was exposed.

- PRD compliance: approved profile routing, native directories/formats, overrides,
  backup/preview behavior, failure propagation and preservation map to the tests.
- Standards: both ports and native templates were reviewed; document-profile reuse
  preserves Claude's paths/prompts/component; no cross-host directory copy or
  project-root inference was introduced. Malformed MCP objects fail before writes.
- Scope: pre-existing changes were separated from this task by an external snapshot
  and preservation checks. Relevant installer specs and README were updated.
- PowerShell source wiring checks cover document mapping, components and explicit
  wrapper exit propagation. They do not substitute for native runtime evidence.

## Uncovered / not run

- Native PowerShell parsing and runtime: **not_run**, because no usable `pwsh`
  was available. No new PowerShell installation was attempted. CI is configured
  to execute the PowerShell cases on Windows.
- MiniMax Code and WorkBuddy application discovery/loading/connection acceptance:
  **not_run**. Configuration shapes were grounded in official documentation and
  MiniMax source at `564e9166d81f87b0b767b005e4779d4697b512be`; isolated installation
  evidence is not a real application-session acceptance result.
- Real dependency installation, credentials, external MCP connectivity and
  account/model behavior: **not_run**.

The task remains recorded without commit/push or automatic archival.

## Follow-up: Mem0 and Recallium defaults — 2026-10-04

The user explicitly set both default URLs to `https://www.59005046.xyz:8102/mcp`.
All five host templates now carry that value; Recallium already matched.
Mem0 no longer requires an override to be installed. Explicit `--mem0-url` values
still override only Mem0, and Enter at existing-URL prompts preserves that entry.
No installed user configuration was edited.

RED: before the changes, cross-host tests proved missing default Mem0 entries,
placeholder template URLs and replacement prompts requiring an additional URL.
GREEN: defaults, explicit overrides and keep/replace behavior now pass across
Codex TOML and all four JSON profiles. Obsolete Codex/Claude interactive tests
were adapted to use the explicit override or assert the new default behavior.

Actual affected final checks:

- A unittest loader combined `test_mcp_defaults.py`, `test_install_interactive.py`,
  `test_install_new_hosts.py`, `test_install_merge_ps.py`: **72 discovered,
  50 passed, 22 skipped, zero failures/errors**, 12.088 seconds. Skips require
  unavailable `pwsh`; runtime availability remains unchanged.
- Python AST and the four native JSON fragments parsed successfully.
- `task.py validate .trellis/tasks/10-04-minimax-code-support` passed.
- `git diff --check` passed.
- Native `trellis-check` applied manually: default/override/keep contracts reviewed
  against the PRD and updated installer spec. Both shell ports use this shared
  Python merger; no port-specific runtime code changed. Prior unrelated wizard
  and entry evidence remains applicable.

No full repository suite, external MCP connection, real-profile write, commit or
push was performed. Prior standalone application/PowerShell limitations still apply.
