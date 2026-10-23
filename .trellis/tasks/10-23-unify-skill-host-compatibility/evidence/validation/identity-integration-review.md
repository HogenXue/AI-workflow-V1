# Final integration review — Skill catalog and native host preservation

Date: 2026-10-24 (Asia/Shanghai)
Task: `.trellis/tasks/10-23-unify-skill-host-compatibility`
Scope: current catalog/preflight/audit entrypoints, wizard completion gate, and integration with shared MCP/hooks. No repository edits, installation, Git mutation, subagents, or full-suite rerun by this reviewer.

## Spec

Three actionable identity-boundary cases were found before preparing the candidate:

1. **P2: malformed parent Skill hides a valid nested alias.** `scripts/lib/skill_catalog.py:107-116` wraps metadata parsing and descendant traversal in one try block. A malformed `archive-container/SKILL.md` prevents traversal into a valid nested `old-review/SKILL.md` with `name: code-review`. Both preflight and final audit returned success beside a canonical `code-review`. This violates PRD lines 18-19 and the nested-alias contract in installer-contracts.md lines 634-635.
2. **P2: other-root pruning inferred ownership from the directory basename.** Preflight ignored a declared foreign identity at `<other>/code-review`, while the shell prune list still removed the directory. A temporary fixture declaring `independent-report` was backed up and deleted with exit 0. This violates independent-capability preservation and exact owned scope (PRD lines 16-19). Candidate now requires readable valid name/description and exact matching identity before any prune mutation.
3. **P2: canonical target replacement had the same ownership ambiguity.** The analogous target path was eligible for `--replace` despite declaring an independent identity. Per root direction, the candidate refuses canonical slots with missing, malformed, incomplete or mismatched metadata, including preview; it does not treat unknown remnants as package ownership.

The candidate addresses all three cases in shared preflight. Metadata failures are still reported, but no longer suppress descendant traversal. Both shell peers already call this shared gate before their first backup or mutation. Only the directly affected legacy sentinel fixtures were updated to carry valid name/description; their existing sentinel preservation and backup assertions remain.

No additional actionable MCP/hook integration finding was identified in this scoped review. Existing parsed keep/rollback logic and exact managed-hook merge boundaries are compatible with the new gate. This is not a new application runtime/trust/connectivity certification.

## Standards

The shared implementation preserves Bash/PowerShell parity, native Trellis ownership, explicit installation boundaries and recoverable backup behavior. The candidate affects only four paths in mapping.json. No new dependency, parallel task lifecycle or shell-specific identity parser was introduced.

## Verification

- `red.log`: initial 8 catalog cases on original helper, 4 failures demonstrating the nested alias and three unsafe prune variants.
- `green.log`: final catalog suite, **9 passed**; includes nested metadata-error traversal, canonical target missing/malformed/incomplete/foreign identities, and other-root rejection before backups or writes.
- `affected-isolated.log`: **7 directly affected cases passed**, comprising 3 Bash installer cases and the 2 AIHero preview/upgrade cases on Bash and PowerShell. Sentinel assertions still reach their intended replacement/backup stage.
- `powershell-slots.log`: **10 bounded native PowerShell fixture probes passed**, covering replace/prune with missing, malformed, incomplete, foreign and matching metadata.
- Python 3.10 AST syntax check passed for all four candidate files. Actual PowerShell runtime is the previously verified official portable 7.6.7 macOS arm64 runtime. No Windows-specific acceptance was added.

## Verification isolation incident

The first affected-fixture run (`affected.log`) used explicit temporary install targets/backups but omitted an outer HOME/XDG reset for two PowerShell cases. PowerShell created normal runtime directories at `/Users/hogenxue/.cache/powershell` and `/Users/hogenxue/.local/share/powershell` (observed matching mtimes). Root was informed immediately and instructed retaining these normal caches. They were not cleaned or used to alter Skill/MCP settings.

The corrected run (`affected-isolated.log`) sets HOME, USERPROFILE, XDG_CONFIG_HOME, XDG_CACHE_HOME, XDG_DATA_HOME, DOTNET_CLI_HOME, PSModulePath, telemetry opt-outs and an explicit existing PyYAML path. It was already started before root requested limiting the repeat to the two PowerShell cases, so its actual count is seven; no additional repeat was started afterwards. The separate ten-case PowerShell identity probe uses fully isolated home/config paths.

No command from this reviewer targeted real Skills, MCP files or host settings for mutation. There was no pre-run whole-HOME snapshot for the affected-fixture repeat, so this reviewer does not independently claim a whole-HOME byte comparison; root owns real installation preservation evidence.

## Handoff

Apply only the four `candidate_path` files in `mapping.json` after matching each original SHA256. The root repository still matches those expected original hashes. Root owns post-integration targeted tests and the actual local discovery audit; no additional installation of unrelated payload is required for these preflight-only fixes.
