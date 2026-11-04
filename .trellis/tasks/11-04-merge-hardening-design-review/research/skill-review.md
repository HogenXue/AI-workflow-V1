# Hardening merge: Skill, global guidance and Memory design review

Active task: `.trellis/tasks/11-04-merge-hardening-design-review`.

## Verified comparison boundary

- Main: `43ca2442e3c98f464f22bd806d1a3047f27f3517`.
- Incoming: `7d685b9c740df2361f8c71f2a65df84a02179884` (`origin/codex/ai-workflow-hardening`).
- Merge base: `3bc7af23029a772d3da9672411b30e3d500e98b0`.
- `git rev-list --left-right --count main...origin/codex/ai-workflow-hardening`: **27 / 7** exclusive commits.

This review uses immutable Git objects for the two sides. The parent was already creating/resolving the uncommitted merge during inspection; its intermediate conflict markers are not reported as final defects. No repository/HOME/index edits, new agents, host installations or full-suite tests were performed by this reviewer. Source snapshots under `sources/main/` and `sources/incoming/` accompany this report for exact line references.

The current PRD explicitly retains main's five hosts and 19 accepted capabilities, and incorporates the incoming ownership-adoption intent. Incoming October task records explain their own implementation decisions; they do not supersede current user instructions or later mainline acceptance.

## Minimal combined design

Retain the complete mainline package and its canonical `agents/` templates. Add the incoming setup capability as a bounded, explicitly invoked **project onboarding adapter** for actual third-party Matt Skill configuration needs. Keep the existing 19 Skills self-contained and directly usable. The resulting catalog can contain 20 names; neither the branch's old ten-name manifest nor its old exclusions should replace main's list.

Preserve the branch's real lock-adoption capability separately from setup: it is explicit opt-in third-party registration ownership, not permission to replace arbitrary Skills or synchronize other host roots. Its code/rollback/peer behavior is reviewed by the main integration work and other scoped reviewers.

## Findings and resolution recommendations

### 1. Canonical global-guidance path must remain on main

**Evidence:** `incoming:AGENTS.global.md:36,45,50-51` are the only substantive root-template delta from the merge base: they qualify Trellis-only routes with non-Trellis fallback. Main already expresses those boundaries in `agents/AGENTS.global.md:23-25,47-49` and scoped Skill bodies. Main's accepted decision explicitly names `agents/AGENTS.global.md` as the distribution source (`.trellis/spec/decisions/aihero-native-trellis.md:21`).

**Conflict if the old snapshot is retained:** incoming root guidance still instructs complexity/cross-module-triggered Grill (`:16,36`), references retired shared `config/workflow_check.py` gates (`:63-76`), and routes to release/Karpathy capabilities absent from the current catalog (`:41-42,48,56`). It also lacks main's explicit/stateless Grill and new retro routing. Those are inherited old contents, not new branch features worth resurrecting.

**Minimum resolution:** retain the main `agents/AGENTS.global.md`, resolve the obsolete root modify/delete conflict as deletion, and port only an actually missing non-Trellis qualifier if found. No second global template or symlink alias is needed. Preserve current root `AGENTS.md` dirty/deletion state independently.

### 2. Setup must remain optional for the already-adapted package

**Evidence:** incoming setup `SKILL.md:31-33` always creates `docs/agents/issue-tracker.md` and `domain.md` in Trellis; `:64-68` adds a prerequisite to read both files before any Matt engineering Skill. Main already includes all adaptation in the packaged Skills (`main:README.md:28`) and explicitly rejects upstream setup/tracker routing as an alternate workflow (`main:.trellis/spec/decisions/aihero-native-trellis.md:13`).

**Practical risk:** installing or selecting setup can introduce another configuration prerequisite for capabilities that already resolve current PRD/Design/Plan and specs themselves. Two pointer documents are not automatically duplicate specifications, but making them universal lifecycle entrypoints contradicts the current distribution design and increases stale routing.

**Minimum resolution:** preserve setup's useful onboarding capability but narrow its trigger to an explicit request to configure third-party/upstream Matt Skills in a target project. First inspect actual consumers and existing configuration. If only this package's adapted Skills are in use, report that no extra setup is required. Reuse existing project pointers; generate the `docs/agents` bridge only when a present upstream consumer actually needs it. These files must contain pointers/adaptation rules, never copied PRDs/domain definitions or another tracker/status system. The generated entry should apply to that consumer, not every packaged engineering Skill.

This is a scoped compatibility bridge, so the accepted decision can distinguish it from automatic upstream setup orchestration without weakening the sole Trellis owner rule.

### 3. Setup invocation and operation names currently differ across hosts

**Evidence:** incoming `skills/setup-matt-pocock-skills/agents/openai.yaml:5-6` is explicit-only in Codex, while `SKILL.md:1-4` has no `disable-model-invocation: true`. Main's deliberately explicit `grill-me` uses both forms. Setup `SKILL.md:40` and `templates/issue-tracker-trellis.md:17` use `implement-spec`; main's accepted manifest and routing use `implement`.

**Minimum resolution:** make the optional setup explicitly invoked across the supported Skill formats by preserving its Codex policy and adding the frontmatter counterpart. Present the name/current operation as `implement`; map `implement-spec` only as an actually detected legacy/upstream consumer, not a presumed installed command. Keep all 19 existing names unchanged. Do not automatically fetch/install upstream Skills or turn setup into the implementation owner.

### 4. Setup should select a proven native instruction entry without silently changing override policy

**Evidence:** incoming setup `SKILL.md:19-23` has useful Codex override discovery, but the Claude fallback says to reuse AGENTS without specifying how that native host will load it. The Skill also permits creation of a new AGENTS entry for a CLAUDE-only project.

**Minimum resolution:** keep inspection of the active host and existing override. Within the explicit project-setup scope, update the actually loaded native entry, or add a minimal native pointer to an existing shared document. If the available host adapter cannot establish the entry, resolve that fact before writing. Preserve managed blocks, user sections, file/symlink boundaries and backup/idempotency behavior. A project setup request is not permission to change global instructions, invocation settings, MCP or hooks. An existing override remains authoritative; setup must not delete it or bypass it by writing an inactive lower-precedence file.

### 5. Memory should combine the branch's no-inferred-consent intent with main's existing authorization

**Evidence:** the branch changes `skills/memory/SKILL.md:15` and `references/memory-backends.md:5` from treating decisions/handoffs as write triggers to requiring explicit save consent. Main independently corrected the same weakness: `main:skills/memory/SKILL.md:15` requires a user request or effective project-rule authorization; `main:.../memory-backends.md:5` separates authorization by backend and excludes automatic Codex local-memory writes. Current user instructions explicitly authorize the configured Recallium rule/search/save protocol after verified implementation.

**Conflict if resolved wholly to incoming:** the imported “only explicit save request” wording can require a new save command even when current project/user instructions already authorize it. It would also disagree with main's retained `store_memory` rule later in the same reference. Conversely, keeping the old merge-base formulation would still allow the agent to treat an important decision as permission.

**Minimum resolution:** retain main's current consent/protocol/fallback behavior and add the branch's useful clarification: an important decision, completed task or handoff is candidate content, not independent write authorization. Reuse applicable existing authorization; assess each backend separately, and never infer permission to modify host-managed local memory. Keep stable verified content, namespace resolution, actual `related_files` and honest saved/not-saved reporting.

### 6. Historical branch notes must not become new executable policy

**Evidence:** incoming `10-20-oneclick-agents-review/skill-compatibility-repairs.md:13-14` records redirecting local `grill-me` and `grilling` to a sole one-question interviewer. Its original task also scoped work to the old ten-Skill catalog and said not to add a Claude installation profile. Main later accepted explicit stateless `grill-me`, supporting `grilling`, 19 capabilities and five native host profiles.

**Minimum resolution:** preserve incoming task records as historical evidence, clearly scoped to their originating checkout/host. Do not propagate their local third-party repair instructions into current packaged Skills. Current design/PRD is the source for this merge. Preserve main's independent `retro`, `implement`, `code-review`, planning and handoff capabilities, plus existing host/profile behavior.

## Adjacent Memory inconsistencies worth a small, explicitly labeled repair

These are **pre-existing on both sides**, not incoming regressions:

- `skills/memory/references/memory-backends.md:20-21` says only loopback HTTP is allowed; the main installer contract already accepts the explicit approved private CIDRs (`.trellis/spec/scripts/installer-contracts.md`, HTTP policy section). Prefer referencing that canonical contract or its actual allowlist rather than retaining a contradictory network rule in the Skill.
- The same reference's `:51` says to inspect `~/.codex/config.toml` and restart Codex when tools are absent. The portable Memory capability should inspect the relevant host only when appropriate and report the limitation; an absent tool does not authorize a restart or configuration write. The current task explicitly excludes live-host mutations.

No additional backend policy, endpoint replacement or host setting change is needed for this merge.

## Provenance and documentation

Keep main's existing AIHero provenance and attribution. The incoming setup note explicitly says its installed upstream source commit was not verified; preserve that limitation rather than claiming it belongs to main's pinned AIHero commit. Update current catalog counts and README routing consistently if setup is added. Keep branch task evidence and old ten-Skill validation numbers as historical, never as the combined package's validation result.

## Proportional verification for the main integration

The following are scenario probes and structural checks, not a request to rerun a second full review:

1. Catalog remains a superset of main's 19 names with one explicit optional setup; its frontmatter/UI policies agree and its relative templates validate.
2. In a fixture with only the adapted package and a Trellis task, setup recognizes that no extra bridge/workflow is needed.
3. In a fixture with a real upstream consumer and legacy `.scratch` pointers, setup updates pointer configuration while preserving old content, managed blocks and canonical task/domain sources; a repeated run is idempotent.
4. In a fixture with a native override or CLAUDE-only shared instructions, setup uses a proven native entry and does not silently overwrite or bypass existing guidance.
5. A Memory request with effective project save authorization proceeds after verification; an important decision with no applicable write authorization does not write; Codex local-memory restrictions remain independent.
6. Clear implementation, explicit stateless Grill, review-only, retro and plain Git sync retain the mainline owners. No incoming historical note triggers another interview or shared workflow checker.

The main task owns lock-adoption behavior, Bash/PowerShell parity, integrated tests, final checks and merge commit/preservation evidence. This review makes no test-passed, installed-host or universal-conflict-free claim.
