# AI 工作原则（Trellis 兼容全局模板）

> 此模板用于 `~/.codex/AGENTS.md`。项目内更近的 `AGENTS.md`、Trellis 管理内容和用户指令优先。

## 沟通与工程原则

- 默认使用中文回复；不确定时说明依据与不确定性。
- 不虚构事实，不声称未实际执行的测试、部署、提交或推送。
- 优先最简单、稳定、可维护的方案；仅做完成任务所需的外科式修改。
- 保留用户已有修改，不重构、格式化或优化无关代码。

## 工作流路由

- 若项目存在 `.trellis/`：Trellis 是该项目的工作流来源。
  - 复杂需求或需求不明确时，先使用 `$grill-me` 一问一答澄清；简单修改不自动触发它。
  - 澄清后由 OpenSpec 维护正式 Spec（需求、场景和验收的唯一事实来源），且 OpenSpec 不维护任务清单。用户确认 Spec 后，再取得同意创建 Trellis task；Trellis 维护 task 级 PRD/计划、该 Spec 引用、任务状态和 Journal，不复制需求、场景或验收。
  - 实施时使用 TDD 管理测试先行；使用 GitNexus 在修改前分析影响、在提交前检查 Git 范围。用户明确授权实施后，才可运行 `task.py start`。
  - 预计少于约 5 分钟的简单修改可直接实现，但仍需针对性验证。
  - 不创建第二套 Task、PRD、Design 或 Spec；不自动创建 `.trellis/`。
- 若项目不存在 `.trellis/`：使用项目既有的 OpenSpec 与实施工作流。

## 能力型 Skill

- 历史上下文、长期决策或跨会话延续：使用 Memory。
- 调用链、影响范围或安全修改，以及提交前 Git 范围检查：使用 GitNexus。
- Release Note、CHANGELOG 或版本说明：使用 Release。
- 编码、重构或代码审查：使用 Karpathy Guidelines。
- 复杂需求的前置访谈：使用 Grill Me；它交接给 OpenSpec，不替代任何正式 Spec。
- OpenSpec 管理行为 Spec；Trellis 的 task 级 PRD/计划必须引用它，不得复制需求、场景或验收。

Skill 负责增强能力，不替代当前工作流，也不为了调用而调用。

## Git 与验证

- 未经明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- 避免 `git reset --hard`、`git clean` 和 force push。
- 完成后说明修改内容、验证方式、验证结果和已知限制。

## 配置边界

- 不假定存在 Trellis MCP；Trellis 通过 CLI 和项目初始化集成。
- 不替换全局 `config.toml`、MCP、插件或 hooks；这些配置只可按用户明确授权做增量调整。
