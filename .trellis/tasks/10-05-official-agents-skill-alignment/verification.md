# Official-guidance alignment verification

Date: 2026-10-05. Implementation and scoped verification complete. The native child task remains in progress pending authorized Git/finish steps.

## Changes and sources

Official AGENTS/Skills documentation, instruction/description guidance and evaluation guidance were searched on official domains and opened before designing the changes. Findings and links are in `research/official-guidance.md`.

- Global source template condensed from 386 lines/15,450 bytes to 74 lines/about 9.2 KiB. Authority/loading facts replace the former custom PRD priority ladder. Repeated validation/authorization prose is consolidated; Trellis, parent-context, explicit Grill, native check, memory and Git/config boundaries remain.
- Project source template reduced to local destinations, conditional specifications and checks. Root additions preserve both managed blocks; EGM retains domain-specific rules, with its authority header corrected.
- Eleven new descriptions now front-load distinct goals and adjacent-request exclusions. Existing seven descriptions, all 18 skill names, invocation policies and runtime installer code are unchanged.
- A stable decision is recorded in `.trellis/spec/decisions/codex-instruction-skill-boundaries.md` and linked from the guide index. README explains template-vs-runtime discovery and override/session behavior.

## Native Spec / Standards review

No unresolved finding in this task's hunks. Global/project guidance distinguishes host authority, directory scope, task facts and skill methods. The native workflow remains the sole state/artifact owner; neither a capability invocation nor a successful check grants extra permissions. Overlapping goals have one primary action owner and complementary methods rather than a mandatory skill stack.

Reviewed against current task acceptance, official source facts, existing integration decision, relevant template/distribution contracts, and skill-creator guidance. No API/model/configuration setup, plugin migration, new runtime dependency, real global installation, Git operation or graph rebuild was introduced. Native `trellis-check` instructions were applied directly in inline mode; no unavailable native tool invocation is claimed.

## Checks performed

- `python scripts/validate-all-skills.py`: all 18 skill/config-consumer structures passed.
- Existing routing suite: 5 tests passed.
- Existing structure/metadata/template suite: 35 tests passed.
- Native child task context validation passed.
- Scoped `git diff --check` passed, with line-ending notices only.

## Independent routing sample

An independent evaluator read the current global guidance and the 18-name/description/invocation-policy catalog, then classified 22 user prompts without reading golden expectations or the full skill bodies during this pass. Eighteen positive cases cover the package capabilities; four adjacent requests should use no workflow skill.

Expected-vs-observed primary routes: 22/22 matched, including all four negative controls. Optional support did not duplicate the primary action. The evaluator did not add TDD to an implementation prompt lacking behavior-risk evidence. Full inputs, observed choices and scoring are in `research/routing-*.json`.

This is a single routing-classification sample, not a universal guarantee of future host/model selection or execution. The previous isolated code-review/to-spec behavior probes remain valid because their bodies did not change. External plugin skills are outside this 18-skill package evaluation.

## Isolated distribution

Real PowerShell `install-agents.ps1 --apply --no-hooks-feature` ran in a temporary host root beside a seeded Trellis project. Current global source copied byte-for-byte; the old global was preserved in a timestamped backup. Existing host `AGENTS.override.md`, project managed AGENTS block and native workflow hashes stayed identical. Evidence: `research/distribution-probe.json`.

No fresh Codex session was launched to test runtime instruction discovery; discovery claims come from the fetched official documentation. The probe confirms distribution/preservation, not that an existing override selects the new global file. Real installed guidance requires explicit installation and new-session source verification.

## Limits and continuation

Runtime installer logic was not changed, so prior package installation evidence was reused rather than rerunning the platform-dependent broad suite. Its documented Windows/Git Bash baseline failures are still recorded in the parent task; this report does not declare that suite green.

A long shell-based template write was rejected by automatic review with only `blocked by policy`. The authorized edit was completed using explicit file patches, review snapshots and literal-path copying. No rejected command executed and no permission escalation occurred.

Keep parent/child task records and user modifications intact. Commit/archive only with required authorization. Reuse this evidence while the covered descriptions/templates remain unchanged; validate affected coverage after material edits. The stable official-guidance integration outcome and actual limits were stored successfully as Recallium feature memory #1252 with related files; memory remains supplementary to this canonical task record.
