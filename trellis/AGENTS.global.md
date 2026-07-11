# AI 工作原则（Trellis 兼容全局模板）

> 此模板用于 `~/.codex/AGENTS.md`。项目内更近的 `AGENTS.md`、Trellis 管理内容和用户指令优先。

## 沟通与工程原则

- 默认使用中文回复；不确定时说明依据与不确定性。
- 不虚构事实，不声称未实际执行的测试、部署、提交或推送。
- 优先最简单、稳定、可维护的方案；仅做完成任务所需的外科式修改。
- 保留用户已有修改，不重构、格式化或优化无关代码。

## 工作流路由

- 若项目存在 `.trellis/`：Trellis 是该项目的工作流来源。
  - 新功能、较大重构或需求不明确时，先进入 Trellis Brainstorm；一问一答澄清需求，生成 PRD 后再实现。
  - 预计少于约 5 分钟的简单修改可直接实现，但仍需针对性验证。
  - 不创建第二套 Task、PRD、Design 或 Spec；不自动创建 `.trellis/`。
- 若项目不存在 `.trellis/`：使用项目既有的 Superpowers 与 OpenSpec 工作流。

## 能力型 Skill

- 历史上下文、长期决策或跨会话延续：使用 Memory。
- 调用链、影响范围或安全修改：使用 GitNexus。
- Release Note、CHANGELOG 或版本说明：使用 Release。
- 编码、重构或代码审查：使用 Karpathy Guidelines。
- OpenSpec 仅用于未启用 Trellis 的项目。

Skill 负责增强能力，不替代当前工作流，也不为了调用而调用。

## Git 与验证

- 未经明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- 避免 `git reset --hard`、`git clean` 和 force push。
- 完成后说明修改内容、验证方式、验证结果和已知限制。

## 配置边界

- 不假定存在 Trellis MCP；Trellis 通过 CLI 和项目初始化集成。
- 不替换全局 `config.toml`、MCP、插件或 hooks；这些配置只可按用户明确授权做增量调整。
