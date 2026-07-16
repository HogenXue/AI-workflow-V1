## Local additions

本节由项目维护，应追加在 Trellis 管理区之外；不要编辑其上方由 Trellis 管理的内容。

- 在此记录项目特有的构建、测试、部署、数据处理与安全规则。
- 将长期、可复用的项目标准维护在 `.trellis/spec/`。
- 将当前任务的 PRD、研究、实现与检查产物维护在 `.trellis/tasks/`。
- 将跨会话工作记录维护在 `.trellis/workspace/`。
- 简单且需求明确的任务直接走 Trellis；复杂、跨模块或需求不明确时，Codex 将 `$grill-with-docs` 视为 Phase 1.1 的唯一访谈实现。使用后不要再加载 `trellis-brainstorm`，需求结论直接写入当前 Trellis PRD；领域术语与持久决定分别写 `.trellis/spec/domain/`、`.trellis/spec/decisions/`。
- Codex 质量阶段使用项目原生 `trellis-check`；P0/P1 返回 TDD 修复并复验。
- `$diagnosing-bugs`、`$codebase-design`、`$resolving-merge-conflicts` 只作为当前 Trellis task 内的专项能力，不接管任务状态、质量审查或 Git 授权。
- 配对配置目录存在 `config/workflow_check.py` 时，所有宿主共用该入口：规划确认后、
  `task.py start` 前运行 `readiness`，原生质量评审后运行 `quality`，归档前运行
  `completion`。复杂任务给 readiness 传 `--complex`；非 AI-workflow 包项目给 quality
  重复传入 `--check <名称>=<实际检查命令>`，不得生成没有项目检查支撑的证据。
- workflow-check 只提供可执行证据，不替代 Trellis 的 task、状态机或原生
  `trellis-check`；helper 不可用时必须说明降级并执行等价检查。
- TDD 是 Trellis 执行阶段的实现方法；Karpathy Guidelines 是横切约束，两者都不创建平行工作流或工件。
- 无 active task 时先遵守 Trellis 的建 task 同意门槛；简单任务也通过 Trellis 的轻量流程执行并运行针对性验证。
- 不要在本项目同时启动第二套完整工作流。
- 原生 Trellis helper 不可用时执行其等价的读取、验证或 Spec 同步步骤，并明确降级；不得声称已加载不存在的 Skill。
- 项目配置明确要求，或改动涉及高风险、跨模块、公共接口/数据契约、删除迁移或陌生调用链时先用 GitNexus；仅这些情形在提交前运行 GitNexus 范围检查。局部低风险提交使用标准 Git 范围检查与相关测试。
