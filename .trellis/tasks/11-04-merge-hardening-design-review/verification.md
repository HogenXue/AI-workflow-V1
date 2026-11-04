# Verification and continuation

## Scope and native review

The user authorized merging origin/codex/ai-workflow-hardening into local main,
reviewing the combined design and optimizing verified issues. Inputs are pinned
in research/merge-inputs.json: main 43ca244 and incoming 7d685b9, with 27/7 exclusive
commits. Current five-host support and all 19 prior Skills remain; one explicit,
optional project-compatibility setup is added (20 total). Already adapted Skills
need no additional bridge. The canonical agents/ template and existing Memory
write-authorization boundary stay intact. Incoming branch history is retained as
evidence rather than replacing main's native Session IDs.

**Spec: passed for the source/fixture acceptance scope.** Reproduced and fixed
three P2 problems: duplicate JSON keys could lose independent registrations;
custom symlink/dot targets could select a different lock; ownership lacked a
PowerShell peer and used an API unavailable on supported Windows Python 3.10-3.12.
Shared parsing/resolution now validates logical cwd against physical cwd. Tests
cover explicit adoption, opt-out/preview, unrelated-data retention, exact backup,
malformed rejection and forced apply-failure rollback through both real peers.

**Standards: passed.** Shared helpers prevent shell drift; Trellis owns the single
lifecycle/quality gate. Preserve main's direct validation/test CI and Windows job;
fix both pip cache dependency paths and retain detailed unittest output. Known
specialist findings are closed (research/closure-review.md). No graph exists for
this repo; impact inspection used actual source call paths and fixture evidence.

## Actual checks

| Check | Result |
| --- | --- |
| Complete isolated regression | **312 total: 305 passed, 7 Windows-only skips**, 158.922 seconds; evidence/integration-final.log. Both Bash and native portable PowerShell were available. |
| Ownership RED/GREEN | Initial native RED: 5 failures plus 1 platform error; initial GREEN: 9 passed. Follow-up relative-cwd RED: 1 failure; final ownership suite: **12 passed**, including both rollback peers. |
| Current interactive protocol | **38 passed**; adapted incoming fixtures to main's current menu/dependency contract. |
| Skill package | All **20 passed** via scripts/validate-all-skills.py. |
| Structure | Bash syntax, current Task context, selected whitespace and resolved-index checks passed. CI cache/suite selection assertions passed. |
| Existing work | **67 original paths match** content hashes, modes, symlink targets or absence after restore; merge index and incoming tip unchanged. |
| Recovery procedure | Isolated Git fixture first proved stash application preserves a resolved staged merge and MERGE_HEAD; actual restore then passed. |

The first full regression had four incoming Graphify fixture failures because its
fake CLI lacked the current dependency --help probe. Corrected the harmless fake;
38-case module and final full run passed. Strict Skill identity validation was
preserved; old sentinels received valid metadata so rollback assertions reach the
intended failure stage. An initial Python-only attempt encountered PyYAML lookup
under changed HOME; meaningful RED/GREEN and final runs use the isolated driver
with the existing dependency path. Overlapping suites are not additive coverage.

Portable PowerShell 7.6.7 macOS arm64 was privately downloaded and matched official
checksums/release digest and Microsoft code signature. The retained runner isolates
HOME/USERPROFILE/XDG/DOTNET/PSModulePath. No global runtime installation or real host
configuration update occurred. Actual Windows runtime acceptance is not claimed.

Git stash restored one JSON file as 0644 instead of its original 0600. Its content
hash matched; original permissions were restored, then all 67 paths were rechecked.
research/preservation.json records the exact path and modes. Original source/work
backups remain in the restricted private audit directory below.

## Git handoff

The local merge commit is authorized. Its exact incoming tip and reviewed index
are checked before committing; final delivery checks both parents, incoming
ancestry, scoped files and staging. The commit graph is the durable source of the
actual merge result. Private Git receipts and original baseline remain at:
/Users/hogenxue/.local/state/codextamplate/project-audits/2026-11-04-qmu3dcf0.

Existing archive moves, old Task work, deleted GitNexus guides/root AGENTS and
Sessions 9/10 are excluded from merge staging and restored. The recovery stash is
retained. This Task owns continuation evidence without rewriting shared Journal.
No push, live host install, app restart, graph rebuild, unrelated cleanup or Task
archive was requested. Native Windows, application loading/trust, external MCP
connectivity and remote CI are **not_run**. Reuse valid checks for later delivery.
