# One-click installer entry audit

## Requirements

Audit the Bash, PowerShell, and CMD installer entrypoints and their component calls.
Harden local wizard control flow while preserving component CLI flags, host target mapping,
explicit project-root selection, backups, and user-owned configuration.
Keep unrelated worktree changes intact. Do not perform a real user-profile install or commit.
The user additionally requested that the three templates under `agents/` become the sole
package sources and their identical old root copies be deleted. Preserve the actual filenames
`AGENTS.global.md`, `AGENTS.project.md`, and `AGENTS-egm.md`. Project and EGM templates remain
reference supplements; the global installer must not automatically inject them into projects.
The user also requested automatic installation of missing GitNexus, Graphify, and Trellis CLIs.
Full-profile installation must prepare these tools before writing host profiles. Existing usable
tools keep their installed versions. A dependency-only component provides preview and apply modes.
Node/npm and Python are prerequisites, with actionable failure messages rather than OS/runtime
installation or automatic privilege escalation. Installing a CLI does not initialize projects,
build graphs, or invoke host setup outside this installer's existing merge flow.

## Acceptance criteria

- [x] Failed components stop the wizard before later components/profiles and before `Done.`;
      the caller receives the component's nonzero exit code.
- [x] Invalid mode selection and EOF stop before any component runs. Empty mode retains
      the full-install default; valid full and single-component modes remain usable.
- [x] Existing dangling skills/config links receive the normal replacement prompt;
      declining replacement skips the component.
- [x] Bash and PowerShell share the corrected behavior; CMD forwards the exit code.
- [x] Regression tests run against real entry functions with isolated component fixtures.
- [x] Relevant existing installer checks pass, with platform limitations stated explicitly.
- [x] All active installer, test, config-consumer, and documentation references use `agents/`;
      all three duplicate root templates are removed, preserving their content in `agents/`.
- [x] Dependency preview causes no installation, network command, or filesystem mutation.
- [x] Apply installs only missing CLIs, verifies each command, and stops on failure before
      profile writes. Existing usable tools are kept; installer-local paths reach child components.
- [x] Graphify uses an isolated managed environment, and its component can locate that environment
      on later runs. npm installs use the official packages and enforce package engine constraints.
- [x] Automated dependency tests simulate package managers; no actual tool reinstall is performed.

## Final-review fixes authorized on 2026-10-03

The user requested fixes for all three final-review findings. Preserve PowerShell 7.0+ support
rather than raising the runtime requirement. Shared path and rollback behavior must remain safe
for every existing caller, and historical review evidence remains unchanged.

- [x] Resolve physical directory ancestors, including symbolic links and Windows junctions,
      before source/target and backup containment checks. Refuse unresolved cyclic paths safely.
- [x] Installing config through an alias of the package source fails before mutation; the source
      marker and directory contents survive, including targets with nonexistent suffixes.
- [x] Graphify fresh failure and success-without-SKILL.md remove partial new targets. Retrying
      needs no --replace. Replacement failure restores the original target in both ports.
- [x] Component dispatch avoids APIs unavailable in PowerShell 7.0/7.1; existing exit-code and
      argument forwarding behavior still passes. Verify with a portable minimum runtime if available.
- [x] New regression failures are observed before implementation; relevant checks pass afterward.

## Windows interactive update repair — 2026-10-05

The user supplied a concrete Codex failure after successful MCP merge: strict-mode expansion
of `$codexHome?` in the existing-hook confirmation. Repair the matching installer task with a
local string-boundary fix and lock down the existing-target interactive path, not fresh installs
alone. Preserve the user's URL choices and actual installed configuration.

- [x] Existing Codex hooks can be declined or replaced interactively without an unset-variable error.
- [x] Fix and verify the same `$proj?` ambiguity in Cursor's existing-project confirmation.
- [x] Tests preserve existing URL choices and original hooks on No; Yes installs valid hooks/rules.
- [x] Exercise the actual existing-target command in an isolated interactive Windows terminal.
- [x] No actual user hooks/configuration overwrite, commit, or push as part of this repair.

Publication follow-up: the user subsequently authorized preserving the effective repair,
reviewing the plan, and committing it. The earlier no-commit statement records the initial
repair stage; it does not revoke the later Git authorization. Publish only the two prompt-boundary
fixes and their regression/spec/review evidence, reusing the earlier push authorization. Do not
include unrelated model-routing drafts, raw historical logs or archived task records.

## Scope and risk

Source reading establishes the entry dispatch/profile call chains. Recallium MCP is unavailable.
GitNexus indexing succeeded, but impact traversal returned `partial: true` with a read-only
adapter error, and query failed due to the missing FTS extension. The user explicitly approved
complete source-reference analysis, checksum verification, and Bash/PowerShell regression tests
as the alternative for template migration and duplicate-root deletion. No complete graph
analysis is claimed. Shared backup/path implementations were outside the initial edit scope;
the user's 2026-10-03 repair request authorizes the narrow shared path/rollback changes and their
complete caller regression. Current graph index is stale and does not contain the PowerShell
symbol, so this repair uses the already approved source review plus regression strategy.
