## Local additions

本节由项目维护，应追加在 Trellis 管理区之外；不要编辑其上方由 Trellis 管理的内容。

- 在此记录项目特有的构建、测试、部署、数据处理与安全规则。
- 将长期、可复用的项目标准维护在 `.trellis/spec/`。
- 将当前任务的 PRD、研究、实现与检查产物维护在 `.trellis/tasks/`。
- 将跨会话工作记录维护在 `.trellis/workspace/`。
- 通用 Skill 路由、风险分级、验证范围和最终门禁遵循全局 `AGENTS.md`；本节只补充项目差异，不另设全量复测流程。
- 简单且需求明确的任务直接走 Trellis。`$grill-me` 是唯一 Grill Skill，仅在用户显式调用时进行无状态澄清；结束后由 Trellis 将确认结论写入当前 PRD 和既有 `.trellis/spec/` 位置，且不再加载 `trellis-brainstorm`。
- 实现稳定后，按当前 Task 要求使用项目原生 `trellis-check`；发现 P0/P1 时集中修复、针对性复验，再统一执行必要的最终门禁。
- `$diagnosing-bugs`、`$codebase-design`、`$resolving-merge-conflicts` 只作为当前 Trellis task 内的专项能力，不接管任务状态、质量审查或 Git 授权。
- 配对配置目录存在 `config/workflow_check.py` 时，按全局规则使用 `readiness`、`quality` 与 `completion`。质量检查命令写入当前任务，说明覆盖范围；可用命令清单不是默认必跑清单。非 AI-workflow 包项目必须传入真实的 `--check <名称>=<实际检查命令>`。
- workflow-check 只提供可执行证据，不替代 Trellis 的 task、状态机或原生
  `trellis-check`；helper 不可用时必须说明降级并执行等价检查。
- TDD 是 Trellis 执行阶段的实现方法；Karpathy Guidelines 是横切约束，两者都不创建平行工作流或工件。
- 无 active task 时先区分咨询与实施：纯咨询不建 Task；用户明确要求实施时可在已授权范围内记录轻量 Task 并继续。只有范围、业务决定或高风险操作尚未明确时才询问。
- 不要在本项目同时启动第二套完整工作流。
- 原生 Trellis helper 不可用时执行其等价的读取、验证或 Spec 同步步骤，并明确降级；不得声称已加载不存在的 Skill。
- Graphify 与 GitNexus 按全局风险规则按需使用；项目仅补充实际索引名与必要的影响分析入口。图谱推断必须回到源文件核实；不得为了任务自动生成或更新图谱、安装 hook 或提交图谱产物。
