# Packaged Skill routing audit and remediation inventory

## Scope and evidence

Task: `.trellis/tasks/10-23-unify-skill-host-compatibility`.

This record consolidates the completed read-only audit of all 18 original packaged Skills and their 18 `agents/openai.yaml` files, plus the new portable `retro` capability. It also records the native Trellis entrypoint conflicts that affected those capabilities. The final source was read selectively to confirm integration; the full audit and test suite were not repeated for this summary.

The current `manifest.yaml` contains 19 distinct Skill names. Every Skill retains a specific owner and uses the project's existing task/artifact locations. Related capabilities are complementary rather than separate lifecycle engines. The existing `grill-me` invocation restrictions remain `disable-model-invocation: true` in frontmatter and `policy.allow_implicit_invocation: false` in Codex metadata. Other existing invocation policies were preserved; `retro` uses normal discovery.

Paths below are relative to the repository root. Runtime installation, live discovery scans and platform/application acceptance are recorded separately by the main task; this inventory does not substitute for those results.

## Per-Skill inventory

| Skill and source | Trigger and responsibility | Boundary retained or clarified | Concrete disposition |
| --- | --- | --- | --- |
| `memory` — `skills/memory/SKILL.md` | Retrieve durable context and save authorized, verified conclusions. | Backend availability is detected, writes follow existing authorization, and memory does not replace PRD, Task or Journal. | Retained existing scoped body and invocation policy. No new memory store or lifecycle introduced. |
| `gitnexus` — `skills/gitnexus/SKILL.md` | Supply graph impact evidence when project policy, user request or change risk calls for it. | Local low-risk source/Git work uses ordinary tools; unavailable graph evidence is reported honestly. | Retained packaged risk-based policy. Aligned conflicting native GitNexus helpers with it. |
| `grill-me` — `skills/grill-me/SKILL.md` | Explicit user-invoked discussion of a loose idea. | Stateless: no files, task mutations, implementation, tests or Git while grilling. Confirmed conclusions return to the normal workflow once. | Retained body and both explicit-only invocation flags. Native brainstorm routing now preserves its confirmed conclusions. |
| `grill-with-docs` — `skills/grill-with-docs/SKILL.md` | Resolve still-unsettled user decisions affecting scope, key design or acceptance in authorized planning. | Clear requests and routine engineering choices proceed without interviews; current PRD/Design/Plan remain canonical. Native brainstorm is an alternative owner, not a second interview. | Retained established routing/body; clarified UI description and example prompt. |
| `grilling` — `skills/grilling/SKILL.md` | Supply prerequisite-ready questions inside an already selected interview. | Does not own task documents, start another interview, implement or grant Git permission. | Retained support-only description/body; clarified UI metadata to distinguish it from the two interview entrypoints. |
| `domain-modeling` — `skills/domain-modeling/SKILL.md` | Clarify ambiguous business vocabulary and durable domain decisions. | Uses existing domain/decision locations. Documentation does not authorize symbol/API renames or refactoring. | Retained body; clarified UI metadata. Design vocabulary no longer overrides established project terms. |
| `to-spec` — `skills/to-spec/SKILL.md` | Synthesize already-agreed requirements into the existing specification. | Does not restart discovery, publish another spec tree or authorize implementation. | Retained body; clarified UI metadata around synthesis. |
| `to-tickets` — `skills/to-tickets/SKILL.md` | Split approved deliverables into independently verifiable native tasks. | Keeps the parent explicit, records blockers, uses supported native child creation, and does not activate children merely to restore a pointer. | Retained body; clarified UI metadata around decomposition rather than interviewing. |
| `wayfinder` — `skills/wayfinder/SKILL.md` | Map unresolved decisions and their prerequisite evidence before deliverables are settled. | Uses current Design and real task state, not a second frontier/status system. Resolved decisions return to ordinary planning. | Retained body; clarified UI metadata around decision mapping. |
| `research` — `skills/research/SKILL.md` | Gather cited primary evidence for a defined research question or needed external fact. | Ordinary source navigation and bug diagnosis keep their existing owners. Research does not authorize production work, provisioning or publication. | Retained body; clarified UI metadata and existing research destination. |
| `prototype` — `skills/prototype/SKILL.md` | Build a bounded disposable demonstration to settle an authorized design question. | Records observations and uncertainty; does not become production behavior automatically. Validation follows the experiment and project rules. | Retained scoped body; clarified UI metadata. Removed the conflicting blanket prototype approval requirement from the TDD capability. |
| `implement` — `skills/implement/SKILL.md` | Execute reviewed, authorized work through native project execution. | Existing planning gates, one implementation owner, proportional checks and native final review; successful checks grant no Git or archive authority. | Retained body; clarified UI metadata. Native workflow and implementation agents now consistently use task-selected checks. |
| `code-review` — `skills/code-review/SKILL.md` | Review a defined task/diff against Spec and Standards. | Includes task-owned earlier commits and new files; read-only review reports findings, and the native check remains the sole gate. | Retained packaged body; clarified UI metadata. Repaired Cursor and channel-runtime check scope, write authority and two-axis reporting. |
| `handoff` — `skills/handoff/SKILL.md` | Record verified state, canonical artifact pointers and the next authorized action. | Does not resume execution, change task state, send cross-chat messages or grant Git permission. | Retained body; clarified UI metadata. Cursor continue now reuses conclusions, evidence and implementation authorization. |
| `retro` — `skills/retro/SKILL.md` | Retrospect on completed work or a resolved debugging cycle using outcomes, causes and prevention lessons. | Active diagnosis, diff acceptance and continuation transfer retain their owners. Analysis does not rerun work, fix code, create tasks, mutate status or perform Git. Writes use existing authorized records. | Added self-contained `SKILL.md` and Codex UI metadata. Native break-loop reuses this analysis when available and has a bounded fallback otherwise. |
| `tdd` — `skills/tdd/SKILL.md` | Use verified RED/GREEN/REFACTOR for behavior changes needing automated evidence. | Project planning owns requirements; proportional validation applies to documentation/configuration and unsuitable automated cases. | Replaced blanket prototype test-first exemption approval with the actual project-policy/authorization boundary. Existing invocation policy preserved. |
| `diagnosing-bugs` — `skills/diagnosing-bugs/SKILL.md` | Establish evidence, reproduce/minimize where feasible, and verify causes of active failures. | Investigation does not imply repair; an authorized fix uses meaningful regression evidence and returns to native quality review. | Limited cleanup to task-created disposable diagnostic artifacts and preserved useful evidence/unrelated files. Existing diagnostic owner retained. |
| `codebase-design` — `skills/codebase-design/SKILL.md` | Compare module interfaces, depth and seams for a real design question. | Methods inform existing design records and do not authorize refactors or rename established domain terms. Supports projects without Trellis. | Removed unconditional Trellis/TDD prerequisites and mandatory vocabulary replacement. Updated supporting design/deepening references, removed fixed agent-count assumptions, and made the UI prompt portable. |
| `resolving-merge-conflicts` — `skills/resolving-merge-conflicts/SKILL.md` | Resolve files in an already-running merge/rebase using both sides' primary intent. | Does not start/abort/continue the Git operation, stage, commit or push without matching authorization. | Retained bounded body and metadata. Simple Git synchronization is routed directly by the native workflow rather than through this conflict capability. |

## Native entrypoint corrections

These were necessary because consistent packaged Skills alone cannot prevent conflicting project-local instructions from being selected.

| Reachable entrypoint | Original conflict | Integrated correction |
| --- | --- | --- |
| `.cursor/skills/trellis-check/SKILL.md`, `.cursor/agents/trellis-check.md` | Unconditional fixes, incomplete work-in-progress scope and fixed lint/typecheck assumptions diverged from the adapted Claude counterpart. | Shared read-only/authorized-fix boundary, task-owned committed/staged/unstaged/new scope, separate Spec and Standards findings, selected verification and truthful coverage. |
| `.claude/skills/trellis-check/SKILL.md`, `.cursor/skills/trellis-check/SKILL.md` | Spec Sync still instructed writing a document whenever a useful lesson was found, even in read-only review. | Read-only reviews recommend updates; document writes require existing corresponding authorization. |
| `.trellis/agents/check.md` | Channel `--agent check` was a separate reachable path with self-fix, uncommitted-only scope and no two-axis review. | Channel review follows the same task scope, Spec/Standards, write-authority and evidence boundaries; no new check owner or automatic state/Git changes. |
| `.trellis/agents/implement.md`, `.cursor/agents/trellis-implement.md` | Fixed lint/typecheck commands and example output could imply unnecessary checks or unsupported success. | Task-selected risk-proportionate checks, actual command/results and explicit unrun coverage; native headers preserved. |
| `.cursor/skills/trellis-brainstorm/SKILL.md`, `.cursor/commands/trellis-continue.md` | Old relentless interview, extra task consent/start confirmation and weak evidence reuse. | Reuse the adapted Claude authorization/decision boundaries while preserving Cursor's `--platform cursor` argument and native command syntax. |
| Both native `trellis-break-loop` Skills | Mandatory spec writes, a nonexistent upstream `src/templates/markdown/spec/` destination and automatic commit. | Route to `retro` once; otherwise use a bounded evidence-based fallback. Existing authorized project records are the only write targets; no automatic fixes, tickets, status or Git actions. |
| Both native finish-work commands | Archive/journal scripts implicitly committed bookkeeping and could include unrelated work. | Explicit `--no-commit` calls, selected completed-task acceptance checks, preservation of unrelated task/workspace changes and independent Git authorization. |
| Native GitNexus guide/CLI/debugging/exploring/refactoring helpers | Graph use and stale-index rebuilding were triggered broadly, including read-only/low-risk requests. | Align with the existing impact-analysis policy: graph when needed, current-source verification, rebuild only within authorized task scope and preserve existing owners. |
| `.trellis/workflow.md` | Detailed execution/check/finish instructions contradicted higher-level scoped authorization and proportional verification. | Task-selected checks, authorized fixes, one retrospective owner, direct routing for focused Git sync, reused implementation/Git authority and explicit caller use of `--no-commit`. |

The workflow now accurately states that archive/journal scripts **can auto-commit by default** and callers must supply `--no-commit` unless existing Git authorization covers the exact resulting changes. It does not claim the CLI defaults were changed.

## Representative intent mapping

| User intent | Primary owner | Expected boundary |
| --- | --- | --- |
| Clear implementation request | Native Trellis execution with `implement` as a capability | Use settled requirements and existing authorization; create only required planning artifacts, then implement and check once. |
| Unresolved planning decision | `grill-with-docs`, or native brainstorm fallback | One interview owner, prerequisite-ready questions and current documents. |
| Explicit `$grill-me` | `grill-me` | Stateless conversation; persistence resumes afterward through the normal workflow. |
| Review-only request | `code-review` inside native check | Findings and coverage only; no code/spec/task edits. |
| Active bug diagnosis | `diagnosing-bugs` | Evidence and cause first; graph is supporting evidence, and repair requires matching authorization. |
| Completed-work retrospective | `retro`; native break-loop delegates the same analysis | Explain outcomes and prevention without re-executing work or auto-committing. |
| Continuation handoff | `handoff` and native continue | Reuse canonical records and valid evidence; handoff alone does not resume or authorize work. |
| Simple Git pull/sync | Existing native Git procedure | Preserve local work and use matching Git authorization; no automatic interview, development task or graph rebuild. |

## Verification performed for these candidate changes

- Initial static audit covered every original packaged `SKILL.md` and UI metadata file, global guidance, native workflow, the nine Cursor/Claude native Skill pairs, relevant native agents/commands and six Claude GitNexus helper Skills.
- The initial Markdown relative-reference scan found no missing targets in the audited Skill entrypoints.
- The first candidate overlay passed the package's structural validator for all 19 manifest Skills including `retro`, covering frontmatter, directory identity, UI metadata constraints and relative resources.
- `retro` also passed the installed skill-creator `quick_validate.py`.
- Candidate whitespace checks, source SHA preconditions, workflow state-block pairing, preserved Cursor platform argument and unchanged explicit `grill-me` policy passed.
- The six-file follow-up passed source SHA/whitespace checks and preserved native identity/provider/labels/tools headers.
- Final selective reads confirmed the 19-name manifest, all 19 descriptions and invocation policies, the design/TDD/diagnostic cleanup corrections, channel read-only boundary, both Spec Sync restrictions and the truthful `--no-commit` caller wording.

These are structural and source-boundary checks. The main task owns integrated fixture tests, independent realistic routing probes, installation verification and final acceptance.

## Preserved behavior and limits

- All 18 existing capabilities remain available. No complementary Skill was removed merely because it works in the same overall development phase.
- Trellis remains the single lifecycle/artifact owner where present; projects without Trellis keep their established workflow.
- Explicit stateless Grill, existing independent skills/plugins, MCP addresses and host-native permissions are not broadened by these guidance changes.
- UI descriptions are distinct and useful, but menu visibility/reload behavior still depends on each host's actual discovery and application state.
- This audit does not prove that arbitrary third-party/plugin Skills or every downstream project instruction is conflict-free. Conflicts outside the package need discovery evidence and precise ownership before migration/removal.
- Descriptions and source rules reduce routing ambiguity; they cannot guarantee identical model behavior on every prompt. Independent behavioral probes and real host evidence remain separate acceptance layers.
- No live installation, application trust/activation, external MCP connectivity, Git publication or Windows runtime success is claimed by this inventory.
