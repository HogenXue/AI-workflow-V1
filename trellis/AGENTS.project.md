## Local additions

本节由项目维护，应追加在 Trellis 管理区之外；不要编辑其上方由 Trellis 管理的内容。

- 在此记录项目特有的构建、测试、部署、数据处理与安全规则。
- 将长期、可复用的项目标准维护在 `.trellis/spec/`。
- 将当前任务的 PRD、研究、实现与检查产物维护在 `.trellis/tasks/`。
- 将跨会话工作记录维护在 `.trellis/workspace/`。
- 简单且需求明确的任务直接走 Trellis；复杂、跨模块或需求不明确时，Codex 将 `$grill-me` 视为 Phase 1.1 的唯一访谈实现。使用后不要再加载 `trellis-brainstorm`，访谈结论直接写入当前 Trellis PRD。
- Codex 质量阶段使用项目原生 `trellis-check`；P0/P1 返回 TDD 修复并复验。
- TDD 是 Trellis 执行阶段的实现方法；Karpathy Guidelines 是横切约束，两者都不创建平行工作流或工件。
- 无 active task 时先遵守 Trellis 的建 task 同意门槛；简单任务也通过 Trellis 的轻量流程执行并运行针对性验证。
- 不要在本项目同时启动第二套完整工作流。
- 原生 Trellis helper 不可用时执行其等价的读取、验证或 Spec 同步步骤，并明确降级；不得声称已加载不存在的 Skill。
- 项目配置明确要求，或改动涉及高风险、跨模块、公共接口/数据契约、删除迁移或陌生调用链时先用 GitNexus；仅这些情形在提交前运行 GitNexus 范围检查。局部低风险提交使用标准 Git 范围检查与相关测试。
