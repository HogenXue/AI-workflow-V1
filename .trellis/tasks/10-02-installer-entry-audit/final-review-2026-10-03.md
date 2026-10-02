# Final installer review — 2026-10-03

## Disposition

**Not ready for final acceptance.** The existing 115-test scope passes, but isolated failure
probes reproduce one data-loss/success-reporting defect and one retry/rollback defect. A third
runtime compatibility defect is confirmed by source/API review. Installer production files were
not changed during this review. The earlier implementation authorization does not turn this
final review into an unrequested patch.

Reviewed base: `d42123dc50d95ec8331f99eac4421790b82a2629`, with the current installer working-tree
changes and task-owned new files. Other workflow/Skill changes remain outside the review scope.

## Spec findings

### P1 — Parent directory links bypass source overlap protection

Location: `scripts/install-lib.ps1:303`; destructive consumer: `scripts/install-config.ps1:144`.

`Resolve-Path(...).ProviderPath` retains a logical path through a directory symlink rather than
resolving its physical ancestors. `Install-LibPathsOverlap` consequently considers the package
config source and an aliased target distinct.

Reproduction copied the real PowerShell config/lib scripts into a temporary package, created
`package/config/must-preserve.txt`, and made a directory symlink `alias -> package`. Executing
`install-config.ps1 --copy --replace --target alias/config --backup-dir <fixture backup>` returned
`0` and printed `INSTALLED`, but `package/config` was empty afterward. A backup existed; the
original package data was still removed and the empty install was reported as success.

Required fix: canonicalize existing path components through directory links/junctions before
the overlap check, reject physical source/target overlap before backup/removal, and add a
regression proving the package source marker survives with a nonzero refusal status.

The Bash fixture on Windows/Git Bash returned an error and restored the marker. That result is
not a native Linux/macOS source-overlap validation and is not used to broaden the P1 finding.

### P2 — Fresh Graphify Skill failure leaves a conflicting partial target

Locations: `scripts/install-graphify.ps1:114` and `scripts/install-graphify.sh:80`;
the missing-`SKILL.md` branches have the same fresh-target omission.

Both implementations perform cleanup/restore only when an old backup exists. A simulated
Graphify CLI created `partial.tmp` under the new Skill destination and exited `23`. Both
installers returned `1`, but retained that directory without `SKILL.md`. Retrying `--apply`
returned `1` with `CONFLICT` instead of allowing a clean retry.

Required fix: distinguish pre-existing and newly created targets. Restore a pre-existing backup
on failure; remove a newly created partial target. Apply the same contract to CLI failure and
success-without-`SKILL.md`, in both shell implementations.

## Standards finding

### P2 — Declared PowerShell 7+ support requires a newer API

Location: `scripts/install.ps1:57`; minimum-version guard: `scripts/install-lib.ps1:6`.

The component dispatcher unconditionally uses `System.Environment.ProcessPath`. That public
property is present in .NET 6 source but absent in .NET 5. PowerShell 7.1 is built on .NET 5;
PowerShell 7.0 also predates .NET 6. The major-version-only guard nevertheless accepts both.
Component execution on those accepted runtimes cannot use the dispatcher as written.

Required fix: use an executable-path lookup compatible with the declared minimum, or consistently
raise and enforce the documented minimum. This is source-verified; no old runtime was installed
or executed. Current test host: PowerShell 7.6.5.

Primary evidence:
- https://raw.githubusercontent.com/dotnet/runtime/v5.0.0/src/libraries/System.Private.CoreLib/src/System/Environment.cs
- https://raw.githubusercontent.com/dotnet/runtime/v6.0.0/src/libraries/System.Private.CoreLib/src/System/Environment.cs
- https://devblogs.microsoft.com/powershell/announcing-powershell-7-1/

## Checks and evidence

| Check | Result |
| --- | --- |
| Existing task-scoped unittest suite | 115 passed in 38.670 seconds |
| All `scripts/install*.ps1` syntax | Passed |
| All `scripts/install*.sh` Bash syntax | Passed |
| Skill validator | All 7 current manifest Skills passed |
| Configuration consumer validation | Passed |
| `git diff --check` | Passed |
| Temporary source-alias probe | Confirmed P1 on PowerShell |
| Temporary fresh Graphify failure/retry probes | Confirmed P2 on both implementations |

Regression suite patterns: `test_install_*_ps.py`, `test_install_dependencies.py`,
`test_install_wizard.py`, `test_validate_all_skills.py`, `test_effective_config.py`,
`test_grill_with_docs_trellis_route.py`.

The executable fixture is `final_review_probes.py`, and its observed output is
`final-review-probes.json`. Fixture deletion/removal affected only copies in a unique temporary
directory. Real package sources and real host profiles were never install targets.

## Boundaries

- No installer production fix, commit, push, or real npm/PyPI tool download was performed.
- Native Linux/macOS full suites remain unrun. Docker CLI is present, but its Linux engine is not
  running; it was not started as part of this review. Git Bash results are labelled separately.
- Recallium/Mem0 MCP tools are unavailable, so no rules/history query or remote memory save is
  claimed. Preserve this report and save verified findings to Recallium when the backend returns.
- The existing 2026-10-02 implementation verification is historical evidence, not an override of
  these newly reproduced final-review findings.
