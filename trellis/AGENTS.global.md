# AI 工作原则（Trellis 兼容全局模板）

> 此模板用于 `~/.codex/AGENTS.md`。项目内更近的 `AGENTS.md`、Trellis 管理内容和用户指令优先。

## 沟通与工程原则

- 默认使用中文回复；不确定时说明依据与不确定性。
- 不虚构事实，不声称未实际执行的测试、部署、提交或推送。
- 优先最简单、稳定、可维护的方案；仅做完成任务所需的外科式修改。
- 保留用户已有修改，不重构、格式化或优化无关代码。

## 工作流路由

- 若项目存在 `.trellis/`：Trellis 是该项目的工作流来源。
  - 简单且需求明确的任务：遵循 Trellis 的轻量流程直接实施并做针对性验证，不自动触发 Grill Me。
  - 复杂、跨模块或需求不明确的任务：先使用 `$grill-me` 一问一答澄清需求；结论写入当前 Trellis PRD，随后继续 Trellis 的既有规划和执行流程。使用 Grill Me 后不得再运行 `trellis-brainstorm`。
  - 不创建第二套 Task、PRD、Design 或 Spec；不自动创建 `.trellis/`。
- 若项目不存在 `.trellis/`：使用项目既有工作流，不自动引入另一套 Spec 或工作流框架。

## 能力型 Skill

- 复杂、跨模块或需求不明确：使用 Grill Me；简单且需求明确的任务不自动触发。
- 历史上下文、长期决策或跨会话延续：使用 Memory。
- 调用链、影响范围或安全修改：使用 GitNexus。
- Release Note、CHANGELOG 或版本说明：使用 Release。
- 编码、重构或代码审查：使用 Karpathy Guidelines。
- 行为变化需要自动化证据：使用 TDD。

- Karpathy Guidelines 是横切行为约束，不是独立阶段；它不替代 Trellis、TDD 或项目既有的质量检查。
- Grill Me 只负责需求澄清，不管理任务生命周期、不写代码、不执行测试、审查或 Git 操作。
- TDD 是 Trellis 执行阶段的实现方法，不是第二套工作流；仅对需要自动化测试证明的行为变化执行 RED → GREEN → REFACTOR。
- GitNexus 只负责影响分析与提交安全，不写业务代码。
- Release 只负责发布说明、版本记录和已获授权的发布准备/执行，不负责开发实现。
- Memory 只负责长期记忆与跨会话上下文，不替代 Trellis 的 PRD、Task 或 Journal。

Skill 负责增强能力，不替代当前工作流，也不为了调用而调用。

## Git 与验证

- 未经明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- 避免 `git reset --hard`、`git clean` 和 force push。
- 完成后说明修改内容、验证方式、验证结果和已知限制。

## 配置边界

- 不假定存在 Trellis MCP；Trellis 通过 CLI 和项目初始化集成。
- 不替换全局 `config.toml`、MCP、插件或 hooks；这些配置只可按用户明确授权做增量调整。
