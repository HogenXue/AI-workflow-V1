<!-- TRELLIS:START -->

# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:

- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

## Codex workflow ownership

- 宿主指令、真实权限、用户明确要求与有效目录指导决定边界；PRD/Design 是需求事实，不提升权限。保留 Trellis 和 GitNexus 管理区，本节只补充本仓库差异。
- 本包维护源为 `agents/AGENTS.global.md`、项目模板与 `skills/`；模板经明确安装才分发，不直接修改真实用户级 `.codex/AGENTS.md`。全局到项目的通用路由不在本节重复复制。
- 简单且需求明确的任务直接走 Trellis，复用已有授权；当前工件、状态、必要规格和门槛以 `.trellis/workflow.md` 为准。安装/宿主变更读取 `.trellis/spec/scripts/`，其他改动只读取受影响层的相关规格。
- 文档化未决需求按 `.trellis/workflow.md` Phase 1.1 自动选用 `grill-with-docs`；复用当前访谈入口和确认结论。
- `$grill-me` 仅在用户显式调用时进行无状态对话；确认结论直接复用，不要再加载 `trellis-brainstorm` 或 documented Grill 重复访谈。任务内访谈与原生 brainstorm 只选一个。
- 需求归当前 PRD，方案/执行归 Design/Plan；稳定术语和持久决定沿用 `.trellis/spec/domain/`、`.trellis/spec/decisions/`。批量规划子任务用原生支持的 `--no-start` 保留父任务关联，不为恢复指针提前 start。
- 实现稳定后，按当前 Task 要求使用项目原生 `trellis-check`；`code-review` 在同一次门禁内提供分析，不重复验证。隔离临时安装测试可在已授权范围内运行；真实用户配置安装、Git 和归档仍需对应授权。
- 原生 helper 未暴露时读取本地脚本/工件并执行等价步骤，明确降级，不虚报 Skill 或 MCP。正式影响分析门槛未满足时，不实施依赖该证据的修改。

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **AI-workflow-V1** (1063 symbols, 1791 relationships, 49 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If the index is stale, rebuild only when the current task requires graph evidence and updating is authorized. Otherwise inspect source and report the limitation.

## Always Do

- Follow the project's risk-driven policy: run impact analysis before cross-module, public contract/data contract, deletion/migration, high-risk, or unfamiliar call-chain changes. Local low-risk edits may use ordinary source reading and targeted tests.
- Run `gitnexus_detect_changes()` before committing only when project rules require it, graph impact analysis was used, or the change is cross-module/high-risk. Otherwise use standard Git scope checks and relevant tests.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- For unfamiliar high-risk execution flows, prefer `gitnexus_query({query: "concept"})` when available. Ordinary local navigation may use source search; unavailable graph tools must not block source-based analysis.
- When high-risk work needs full graph context on a specific symbol, prefer `gitnexus_context({name: "symbolName"})` when available; otherwise use source and language tooling with targeted verification.

## Never Do

- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- For cross-file or high-impact symbol renames, prefer `gitnexus_rename` when available. Otherwise use language-aware rename tooling or verified source edits; never use blind find-and-replace.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/AI-workflow-V1/context` | Codebase overview, check index freshness |
| `gitnexus://repo/AI-workflow-V1/clusters` | All functional areas |
| `gitnexus://repo/AI-workflow-V1/processes` | All execution flows |
| `gitnexus://repo/AI-workflow-V1/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
