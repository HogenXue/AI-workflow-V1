# AIHero / Trellis compatibility audit

Date: 2026-10-05. Follow-up to the user's request to ensure integration does not conflict with Trellis. Reuses the current packaging task and prior evidence; no second workflow or task was created.

## Ownership and routing

Reviewed all eleven new skill bodies, global routing, native phase guidance, task-create semantics and installation boundaries. Requirements/design/plans, native state and final checks remain Trellis-owned. Documented Grill/native brainstorm run as alternatives, not sequential interviews. `grill-me` stays explicit/stateless. Spec synthesis and wayfinding reuse canonical artifacts. `implement` follows native activation/dispatch; review analysis executes inside the same native check and read-only requests do not authorize fixes. Research/prototype/handoff do not authorize implementation, Git or a second tracker.

## Finding and correction

The initial `to-tickets` command guidance used native `create --parent` without preserving session context. Trellis's default create changes the session active-task pointer to the newly created child, although its status stays `planning`. During batch slicing this could incorrectly shift planning away from the parent.

Updated `to-tickets`, the project global template, native workflow/brainstorm, and the stable integration decision to use supported `create --parent ... --no-start`, keep the parent path explicit, and verify parent context/child status. Do not run `start` merely to restore a pointer, because it can advance status. The skill also checks native option availability and reports incompatible versions instead of inventing flags.

No native runtime code, installer logic, task schema or status was changed. These are local instruction corrections; no graph refresh/impact analysis was required.

## Actual native probes

`research/trellis-context-probe.json` records execution of the repository's copied native task scripts in an isolated root/session:

- Default parent/child create reproduced the active-task switch.
- A second parent with two children created via `--no-start` retained exactly the same active-task output.
- Every created task remained `planning`; no task was activated into implementation.

`research/trellis-install-preservation.json` records real PowerShell skill/global-template installation into an isolated host root beside a seeded Trellis project:

- All 18 skill folders installed.
- Distributed global template and corrected `to-tickets` body matched current source bytes.
- SHA-256 of the project's root AGENTS managed block, native workflow and existing task JSON stayed unchanged.

These probes do not mutate real user-level Codex configuration or the current repository's task pointer.

## Verification

- All 18 packaged skills/config consumer structures passed.
- Five routing tests and 35 skill/structure tests passed after the instruction correction.
- Scoped whitespace check passed; only Git line-ending notices.
- No repeated broad installation suites: the prior installer evidence remains valid because executable installers are unchanged. Their pre-existing Windows/Git Bash limitations remain as recorded in `verification.md`.

No unresolved workflow/ownership conflict was found within the inspected instructions and tested native version after this correction. Future model behavior or unsupported Trellis versions are not guaranteed by static rules; the option check and native project gates remain authoritative.
