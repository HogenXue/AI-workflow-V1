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

- 简单且需求明确的任务直接走 Trellis；复杂、跨模块或需求不明确时，Codex 将 `$grill-me` 视为 Trellis Phase 1.1 的唯一访谈实现，使用后不要再加载 `trellis-brainstorm`。
- Codex 质量阶段使用项目原生 `trellis-check`。
- `$tdd` 是 Trellis 执行阶段的实现方法，Karpathy Guidelines 是横切约束；两者都不创建平行任务或工作流。
- 原生 Trellis helper 未暴露时，手动执行等价的 task/spec 读取、验证或同步步骤，并明确说明降级。
