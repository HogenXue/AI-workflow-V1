# Task-scoped Trellis review

Reviewed on 2026-10-02 using the project's native `.claude/skills/trellis-check/SKILL.md` in the main session. No dedicated Trellis command/agent or memory MCP is exposed. The review checks requirements and applicable installer/skill contracts; unrelated concurrent source changes are excluded from this task's completion claim.

## Result

The retained package is seven skills: Memory, GitNexus, Grill Me, TDD, Diagnosing Bugs, Codebase Design, and Resolving Merge Conflicts. Trellis keeps task/spec/journal ownership; the five selected AI Hero capabilities augment that workflow. Graphify is retained separately in the shared user skill root. Recallium/Mem0 integration instructions remain; no MCP settings, hooks, official plugins, system skills, or other repositories were removed.

Retired source skills: release and karpathy-guidelines-zh. Removed personal directories: Codex AnySearch, shared AnySearch, personal PDF, Playwright, and AI Supply Chain Bottleneck Hunter. All were moved into a recoverable backup directory after exact backup verification. Graphify moved from the Codex-specific user root to the shared root. The current Codex-specific skill root contains only system skills; the shared root contains exactly the seven package skills plus Graphify.

Ordinary installation preserves legacy skills. Explicit `--prune-legacy` in both Bash and PowerShell backs them up and removes them. Package consumer/documentation/test references are synchronized; historical notices and migration names are intentionally retained.

## Changes checked

- Current project Grill route and TDD reference agree with manual, stateless Grill and Trellis persistence.
- Memory authorization distinguishes existing project authorization from a fresh save request; backend identities and namespaces are not hardcoded.
- Local GitNexus instructions use risk-driven analysis and verify affected contracts rather than asserting every caller breaks.
- Trellis check scope distinguishes this task's failures from unrelated work.
- Graphify entrypoint reduced from 699 to 44 lines; detailed procedures remain in references, with Windows commands and explicit extraction/backend boundaries.
- Validator diagnostics use POSIX spelling; Bash test assertions compare actual path meaning on Git Bash rather than assuming one printed path spelling.
- Native skills/config installers copied the current package; installed skill/config hashes match source, and installed workflow_check.py is absent.

## Evidence

| Check | Result |
| --- | --- |
| `python -B scripts/validate-all-skills.py` | 7/7 passed |
| Validator/package contract tests (`test_validate_all_skills.py`) | 35/35 passed |
| Grill/Trellis route tests | 5/5 passed |
| Effective configuration tests | 6/6 passed |
| PowerShell component installer tests | 6/6 passed, including explicit legacy pruning and backup recovery |
| Selected Bash installer tests on Git Bash | 7/7 passed, including copy/conflict/default target/backup/legacy pruning |
| `config/effective_config.py --validate-consumers` | Passed |
| Native `task.py validate` | Passed; main-session execution uses no dispatch context entries |
| Scoped `git diff --check` | Passed |
| Installed/source file hashes, retained roots, official PDF presence | Passed |
| Graphify query/path/explain on a two-node local fixture | Passed; no API call or real repository graph rebuild |

59 selected regression tests passed. No full-repository suite or Linux/macOS CI run is claimed. The two initial Bash assertion failures were Windows printed-path differences and passed after semantic path comparison. The initial graph fixture incorrectly used numeric confidence; the corrected Graphify evidence-label fixture passed. Offline AnySearch docs succeeded before its later authorized removal, with a requests dependency warning; no dependency upgrade was performed.

GitNexus CLI status matches HEAD. `_manifest_skills` and `validate_consumers` upstream impact checks returned LOW. Concept search failed because FTS is unavailable; source reading supplemented graph evidence for current dirty/unindexed files. No index rebuild occurred.

## Recovery and limitations

Exact and moved backups are under `C:/Users/hogen/.agents/.ai-workflow-backups/skills-cleanup-20261002-01a0fcf4`; `sources.json` and `expanded-sources.json` map original paths. Installer-generated backups are in its `installer/` subdirectory, including the complete prior shared config. Restore only the selected files needed for rollback, preserving subsequent work.

Official plugin cleanup was presented as an optional scope choice; no removal answer arrived, so the recommended preservation scope was used. Current skill catalogs may need a new chat/restart to reflect removed and newly installed paths.

Recallium and Mem0 tools are not exposed. No project memory was retrieved or saved. Recommend saving the stable retained-tool split, cleanup scope, and validated results to Recallium when available. No local Codex memory files were updated. No commit, push, deployment, or unrelated cleanup was performed.

## Authorized publication

The user subsequently requested commit and push on 2026-10-02. The publication snapshot contains only this task's changes: 20 modified files, 12 retired-skill deletions, and seven task records. It excludes the concurrent agents-template relocation, installer entry/dependency work, and separate AIHero/Trellis task changes. Shared files are staged by task-owned content; the published tree uses the existing root template paths until the independent relocation is published. Working files are not restored or overwritten for this staging.

The actual publication snapshot passed 7/7 skill validation and 58 selected tests: 34 package/validator, five Grill routing, six effective-config, six PowerShell component installer, and seven Bash installer checks. The extra directory-relocation test in the dirty working tree belongs to the other task and is excluded. Remote main and local main matched before staging. GitNexus staged-change verification returned MEDIUM (28 indexed symbols, three validation flows); the changed validator and installer/test scenarios have targeted passing evidence. Git scope review covers all 39 files, including documents not represented by graph symbols. Staged whitespace and exact-allowlist checks passed. Commit and remote SHA verification are reported in the publication response.
