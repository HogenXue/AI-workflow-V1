# AI 工作原则（Trellis 兼容全局模板）

> 此模板用于 `~/.codex/AGENTS.md`（Cursor 安装时亦由此生成项目 `.cursor/rules`）。项目内更近的 `AGENTS.md`、Trellis 管理内容和用户指令优先。

## 沟通与工程原则

- 默认使用中文回复；不确定时说明依据与不确定性。
- 不虚构事实，不声称未实际执行的测试、部署、提交或推送。
- 优先最简单、稳定、可维护的方案；仅做完成任务所需的外科式修改。
- 保留用户已有修改，不重构、格式化或优化无关代码。

## 工作流路由

- 若项目存在 `.trellis/`：Trellis 是该项目的工作流来源。
  - 简单且需求明确的任务：遵循 Trellis 的轻量流程直接实施并做针对性验证，不自动触发 Grill with Docs。
  - 复杂、跨模块或需求不明确的任务：先使用 `$grill-with-docs` 一问一答澄清需求，并按其边界维护 `.trellis/spec/domain/` 与 `.trellis/spec/decisions/`；需求、范围与验收只写当前 Trellis PRD。使用 Grill with Docs 后不得再运行 `trellis-brainstorm`。
  - 不创建第二套 Task、PRD、Design 或 Spec；不自动创建 `.trellis/`。
- 若项目不存在 `.trellis/`：使用项目既有工作流，不自动引入另一套 Spec 或工作流框架。
- Codex 若启用 `multi_agent`：子代理仍服从本文件与项目 `AGENTS.md`；复杂需求澄清仍走 Grill with Docs → Trellis，不另起一套工作流。

## 记忆分层（Codex 配置对齐）

按职责分层理解，避免混用：

1. **Recallium MCP**（`mcp_servers.recallium`）：项目维度记忆（决策、进度、规则、会话回顾）。
   - 会话开始、任务延续，或用户问历史/规则/进度时：先检索再回答。
   - 使用清晰的实体/类型过滤（如 Preference、Procedure、Requirement）。
   - 仅在结论已验证、内容稳定且用户明确要求保存时写入；遵循已发现的 procedure 与 preference。
   - 工具不可见时：检查 `~/.codex/config.toml` 中的 recallium 配置并说明降级，不得虚报已检索。
2. **Codex `features.memories`**：宿主内置记忆能力；不替代 Recallium 的项目命名空间与 Memory Skill 协议。
3. **Memory Skill**：编排上述后端；不替代 Trellis 的 PRD、Task 或 Journal。
4. **Mem0 MCP**：仅当 `config.toml` 中已配置 `mcp_servers.mem0` 时使用（跨项目语义事实）；未配置则跳过，不假装可用。

## 能力型 Skill

- 复杂、跨模块或需求不明确：使用 Grill with Docs；简单且需求明确的任务不自动触发。
- 历史上下文、长期决策或跨会话延续：使用 Memory（见上节记忆分层）。
- Graphify（已安装且仓库已有可用图谱时）：用于代码库概览、关系与路径检索；将
  `INFERRED` 或 `AMBIGUOUS` 结果视为待核实线索，编辑前回到源文件确认。
- 项目规则明确要求，或涉及跨模块、公共接口/数据契约、删除迁移、高风险或陌生调用链：使用 GitNexus；局部低风险修改不自动调用。
- Release Note、CHANGELOG 或版本说明：使用 Release。
- 编码、重构或代码审查：使用 Karpathy Guidelines（完整十二条在 Skill 内；不在本全局文件展开长文）。
- 行为变化需要自动化证据：使用 TDD。
- 复杂 Bug 或性能回归：使用 Diagnosing Bugs 建立可重复反馈循环；仅诊断请求不自动实施修复。
- 模块接口、seam 或深模块设计：使用 Codebase Design；接受的决定写回当前 Trellis Design，实施前按风险使用 GitNexus。
- 已经进行中的 merge/rebase 冲突：使用 Resolving Merge Conflicts；不得自行开始、终止、继续、提交或推送未获授权的 Git 操作。

- Karpathy Guidelines 是横切行为约束，不是独立阶段；它不替代 Trellis、TDD 或项目既有的质量检查。
- Grill with Docs 只负责 Phase 1.1 需求澄清及 Trellis 领域/决定 spec；不管理任务生命周期、不写代码、不执行测试、审查或 Git 操作。
- TDD 是 Trellis 执行阶段的实现方法，不是第二套工作流；仅对需要自动化测试证明的行为变化执行 RED → GREEN → REFACTOR。
- Diagnosing Bugs、Codebase Design 和 Resolving Merge Conflicts 都是当前 Trellis task 内的能力，不创建平行 PRD、Spec、Task、Review 或提交流程。
- Graphify 只提供可选的本地图谱探索，不替代 GitNexus 的正式影响分析、Trellis 的质量证据或
  Memory 的长期记忆；Graphify 的图谱/查询结果不是长期项目记忆。除非用户或项目规则明确授权，
  不自动生成/更新图谱、安装其配置或 hook，或提交 `graphify-out/` 产物。
- GitNexus 只负责影响分析与提交安全，不写业务代码。`detect_changes` 仅用于项目规则明确要求、已做图谱分析或高影响变更；低风险提交只做标准 Git 范围检查与相关测试。
- Release 只负责发布说明、版本记录和已获授权的发布准备/执行，不负责开发实现。
- Memory 只负责长期记忆与跨会话上下文，不替代 Trellis 的 PRD、Task 或 Journal。

Skill 负责增强能力，不替代当前工作流，也不为了调用而调用。

## 可执行工作流门禁

- 当配对配置目录中的 `config/workflow_check.py` 可用时，Codex、Cursor、Claude 共用该
  入口；源码仓库可直接运行 `python3 config/workflow_check.py --project-root "$PWD" ...`。
- 复杂任务在 `task.py start` 前运行 `readiness --task <任务目录> --complex`；轻量任务省略
  `--complex`。readiness 只检查规划工件和上下文，不修改任务状态。
- 实现过程中先运行受影响范围的针对性检查；当前 task 的最终原生 `trellis-check` 完成后
  只运行一次 `quality --task <任务目录>`，把实际检查结果写成可校验质量证据。同一提交
  批次不按 commit 次数重复运行；只有证据覆盖的仓库内容随后变化才重新运行。AI-workflow
  包可使用内置质量配置；其他项目必须重复传入
  `--check <名称>=<实际检查命令>`，不得在没有项目检查命令时生成证据。CI 运行 quality
  时不传 `--task`，不得依赖活动任务。
- 归档前运行 `completion --task <任务目录>`，复用已有证据并确认验收项已勾选、内容指纹
  仍匹配；仅提交相同内容造成的 Git HEAD 变化不要求重新验证。
- 共享检查器不替代 Trellis 的 task、状态机或原生质量评审。helper 不存在时执行等价的
  Trellis 检查并明确报告降级，不得虚报门禁已经运行。

## Git 与验证

- 未经明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- 避免 `git reset --hard`、`git clean` 和 force push。
- 完成后说明修改内容、验证方式、验证结果和已知限制。

## 配置边界

- 不假定存在 Trellis MCP；Trellis 通过 CLI 和项目初始化集成。
- 不替换全局 `config.toml`、MCP、插件或 hooks；这些配置只可按用户明确授权做增量调整。
