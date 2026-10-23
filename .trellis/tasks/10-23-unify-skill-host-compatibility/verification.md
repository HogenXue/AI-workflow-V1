# Verification and acceptance

Concluded 2026-10-24 (Asia/Shanghai); installation ran on 2026-10-23.

## Scope

The user requested project-wide Skill/host compatibility optimization and then
explicitly selected updating the four existing local profiles. Work is based on
`a45d78432529414a193f20e722d1b9dde728e52c` plus the task's uncommitted changes.
The pre-development baseline distinguishes 61 unrelated dirty paths, including
the intentional root AGENTS deletion and prior task archives. None were reset.

## Implemented result

- Audited all 18 existing packaged Skills and added `retro`, yielding 19 distinct
  capabilities. Native Trellis/Cursor/Claude entrypoints now agree on the primary
  workflow owner, existing authorization, read-only review, proportional checks,
  explicit/stateless Grill and retrospective boundaries.
- Added shared strict catalog validation and host-aware conflict/drift checks.
  Installation audits the selected hosts before reporting completion. Identity
  checks distinguish aliases, nested archives and cross-host copies; unrelated
  capabilities are preserved.
- Hardened native MCP parsing, byte-preserving keep behavior, semantic checks and
  atomic updates. WorkBuddy accepts JSONC; Codex accepts valid TOML spellings and
  rejects unsupported destructive rewrites before publishing.
- Merged package hooks without discarding foreign handlers/scripts. Fingerprint
  ownership permits future upgrades while rejecting unknown customized scripts.
  Guide installation preserves native configuration, explicit hook disablement
  and effective instruction overrides. Bash/PowerShell share behavioral helpers.
- Updated native templates, README, installer contracts, changelog and Windows
  CI coverage. Official sources and individual Skill dispositions are retained
  in `evidence/research/`.

## Source and fixture checks

| Gate | Result and evidence |
| --- | --- |
| Package validation | `python3 scripts/validate-all-skills.py`: all 19 passed. |
| Integrated Python fixture suite | `python3 -m unittest discover -s tests`: 277 total, 197 passed, 80 runtime/platform skips. Log: `evidence/validation/full-suite-second.log`. Inherited host overrides were cleared and fixtures used temporary homes. |
| Supplementary native PowerShell | Portable official PowerShell 7.6.7 on macOS arm64: 79 selected cases, 71 initially passed, 7 Windows-only skips and one macOS fixture-name failure. Corrected executable naming and reran that case successfully: 72 passed, 7 skipped in the combined evidence. This is not Windows runtime acceptance. |
| Final identity integration | After the last shared-preflight change, all **68 tests passed** across `test_skill_catalog`, `test_aihero_install`, `test_install`, `test_install_components_ps`, and `test_install_wizard`, with native portable PowerShell enabled and isolated HOME/XDG. See `evidence/validation/final-identity-integration.log`; these overlap earlier suites and must not be added as unique coverage. |
| Skill routing | Seven representative intents analyzed; isolated no-index read-only review found the seeded behavior bug and preserved all seven fixture files. Four reachable native guidance conflicts were repaired and specifically rechecked. This is source/behavioral reasoning, not probabilistic model-evaluation coverage. |
| Bash syntax | Changed shell entrypoints, components and Codex context hook passed `bash -n`. |
| Native task context | `python3 .trellis/scripts/task.py validate .trellis/tasks/10-23-unify-skill-host-compatibility` passed. |
| Original work and Git | All 61 original dirty paths matched before journal append; HEAD unchanged, staging empty. `git diff --check` passed. |

The first integrated run exposed stale tests for intentionally changed native
preservation contracts and dependency fixtures. Those assertions were updated
to verify the new contract, then the complete suite passed. The PowerShell
fixture failure came from using a Windows `.cmd` filename on macOS; production
installer behavior was unchanged by that fixture correction. Logs retain the
original result and its narrow superseding check.

Final review found and fixed three related identity cases: invalid parent
metadata hid nested aliases; other-root pruning and canonical target replacement
could each mistake an unrelated identity for package ownership. The shared gate
now continues nested discovery and refuses missing/malformed/incomplete/foreign
identities before any writes. Candidate RED evidence, 9 catalog tests, 7 directly
affected fixtures and 10 PowerShell identity probes are retained. The main-session
68-case check above validates the merged files. Final real-home preflight and
strict audit both passed, with **zero conflicts, zero drift and all 19 capabilities
present per selected host**.

One candidate-review PowerShell test invocation omitted its outer HOME/XDG reset
and created normal PowerShell cache directories. No command targeted actual
Skill/MCP/settings for mutation; no whole-HOME no-write claim is made for that
invocation. The reviewer corrected isolation and repeated the affected fixtures;
the final main-session check used full isolation. The incident is retained in
`evidence/validation/identity-integration-review.md`; caches were left intact.

## Actual local installation

`bash scripts/install.sh` ran in a real PTY, selected profiles `1 2 4 5`, full
mode, and exited 0. Cursor project scope was explicitly skipped because no
additional project root was requested. Existing CLIs were retained. Managed
Skills/defaults/guides were replaced with backups; Graphify replacement and
every MCP overwrite/URL replacement were declined.

- 76 installed Skill trees (19 per host), four configuration payloads and three
  global guides matched their source.
- All 21 existing MCP definitions, 11 URL values and all four MCP files were
  unchanged; native non-MCP values were also retained.
- 150 protected paths and 561 tracked repository paths matched the pre-install
  snapshot. All 88 new timestamped backups matched their original target.
- Foreign Codex hook configuration was preserved. The installed Bash helper
  emitted the current Task from the root and nested directory; the Python helper
  did the same from the nested directory, all with exit 0.
- Codex 0.154.0 `skills/list` returned each of the 19 manifest Skills exactly
  once, enabled, from `~/.agents/skills`, including `retro`.

`installed-verification.json` and `evidence/` contain source fingerprints,
before/after inventories, sanitized logs, backup mappings and native probe
results. Private raw configuration, source archive and transcripts remain in the
restricted durable directory named by `private-evidence-path.txt`.

Only the repository-side preflight/audit helper changed after that installation.
`evidence/final-source-package.json` verifies that every distributed Skill, guide,
configuration and hook remains identical to the installed payload, so reinstalling
unchanged files was unnecessary. Both source versions are fingerprinted and
privately archived.

## Native check: Spec

Result: **passed for the documented package/installation acceptance scope**.
All actionable task-owned findings were repaired and rechecked.

The selected acceptance scope covers packaged capabilities and five installer
profiles, with real installation to the four requested hosts. Preserving personal
Skills/plugins and existing MCP data is part of acceptance; arbitrary third-party
workflow equivalence is not established by a managed-name scan. The native
discovery result and preserved settings support the stated installation result,
without promoting it to all-application runtime acceptance.

## Native check: Standards

Result: **passed**, with no unresolved task-owned standard violation found.

Shared helpers are used by both shell peers, native paths/formats are retained,
project-scoped writes require an explicit root, failure cases use fixtures,
secrets stay outside repository evidence, and the native task owns all records.
GitNexus had no index for this repository; impact inspection used current source
call paths and integration fixtures without rebuilding a graph or claiming graph
evidence. No independent task lifecycle was introduced.

## Remaining boundaries

- Native Windows execution and CI on the remote branch: `not_run` locally.
- Cursor/MiniMax/WorkBuddy application loading, desktop menu refresh, real model
  routing and host invocation-policy enforcement: `not_run`.
- Codex native hook trust and actual session event activation: `not_run`; the
  installer does not bypass `/hooks` review.
- External MCP business connectivity: `not_run`; byte preservation is verified.
- Existing independent `miniprogram-ui-ux-design` files under `.codex/skills` and
  `.codebuddy/skills` lack YAML frontmatter. They were retained and reported as
  warnings; Codex reports its copy as a parser error. This is outside the managed
  package and prevents a claim that every personal Skill is valid.
- Full closed-inline Codex `mcp_servers = {...}` parent rewrites are rejected;
  keep mode supports them. JSONC updates preserve data but normalize comments
  away. Python 3.10 requires the declared `tomli` dependency.
- At the implementation/installation checkpoint, no commit, push, PR, task
  archive, app restart, plugin removal or unrelated Skill deletion was performed.
  The user subsequently authorized scoped commit/push on 2026-10-24.

## Continuation

The user authorized scoped Git publication on 2026-10-24. Include the 78 recorded
source paths, current Task artifacts and only Session 11 from shared records;
exclude prior dirty tasks/archives, root AGENTS deletion and Sessions 9/10.
Keep this task active; archive was not requested.
Do not repeat successful checks solely because task/journal bookkeeping changes.

External Recallium memory saved successfully as **#1444** with related source and
verification files. Codex host memory files were not changed.
