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

- 简单且需求明确的任务直接走 Trellis；复杂、跨模块或需求不明确时，Codex 将 `$grill-with-docs` 视为 Trellis Phase 1.1 的唯一访谈实现，使用后不要再加载 `trellis-brainstorm`。需求只写 Trellis PRD；领域术语与持久决定分别写 `.trellis/spec/domain/`、`.trellis/spec/decisions/`。
- Codex 质量阶段使用项目原生 `trellis-check`。
- `$tdd` 是 Trellis 执行阶段的实现方法，Karpathy Guidelines 是横切约束；两者都不创建平行任务或工作流。
- `$diagnosing-bugs`、`$codebase-design`、`$resolving-merge-conflicts` 只作为当前 Trellis task 内的专项能力，不接管任务状态、质量审查或 Git 授权。
- 原生 Trellis helper 未暴露时，手动执行等价的 task/spec 读取、验证或同步步骤，并明确说明降级。

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **AI-workflow-V1** (1063 symbols, 1791 relationships, 49 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- Follow the project's risk-driven policy: run impact analysis before cross-module, public contract/data contract, deletion/migration, high-risk, or unfamiliar call-chain changes. Local low-risk edits may use ordinary source reading and targeted tests.
- Run `gitnexus_detect_changes()` before committing only when project rules require it, graph impact analysis was used, or the change is cross-module/high-risk. Otherwise use standard Git scope checks and relevant tests.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.

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
