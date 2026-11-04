# Combined design review

## Scope and method

Read the pinned main/incoming histories, actual merge conflicts, both originating
PRD/design records and the current Task. Main-session inline implementation owns
writes and one final native trellis-check gate. Parallel specialists supplied
bounded read-only CI, ownership and Skill-routing analysis. Their reports and
source-backed probes are retained under research/; no second task/review lifecycle.

## Spec findings and resolutions

| Finding | Practical effect | Resolution/evidence |
| --- | --- | --- |
| P2: duplicate lock keys accepted | JSON decoding silently discarded an independent registration before adoption. | Shared parser rejects duplicate keys; original bytes remain unchanged. Native RED and GREEN fixture results retained. |
| P2: custom aliases resolve as standard roots | A custom symlink or symlink cwd plus --target . could detach the global lock instead of the caller's adjacent lock. | Shared logical path resolver, verified cwd and samefile guard; explicit/custom/dot/stale-PWD cases tested. |
| P2: ownership has no Windows peer | PowerShell could not perform the branch's ownership action; Windows Python 3.10-3.12 also lacks the used fchmod API. | Both peers/wizards use one Python resolver/update implementation; path chmod, explicit opt-in, read-only preview and rollback fixtures. |
| Integration: old CI/template/routing assumptions | Importing old branch snapshots would call removed workflow_check.py, undo native profiles or duplicate setup/read requirements. | Preserve main CI/native rules and all 19 capabilities; add bounded twentieth setup, current template paths and existing Memory authorization. |

Spec result for the combined authorized design: the identified issues are fixed;
final full-suite and preservation evidence is recorded in verification.md. Existing
MCP, hooks and five-host behavior is covered by the combined fixtures, not a live
host migration. No change to actual host settings is authorized or performed.

## Standards

Both shell peers share ownership semantics and retain no-write preview, backup,
rollback, explicit project-root and native configuration boundaries. Skill setup
is explicit/optional and cannot reintroduce a parallel lifecycle. Historical branch
records are retained rather than rewritten as current acceptance. The canonical
agents/ template replaces the obsolete root path. No graph was available for this
repo; all impact claims are tied to source and fixtures, not fabricated graph data.

No unresolved task-owned Standards finding was identified after integration.
Meaningful acceptance focuses on data preservation and failure behavior, not
implementation mirroring. Native Windows/app discovery, hook trust, MCP connectivity
and remote CI remain outside the local evidence and are not reported as passes.
