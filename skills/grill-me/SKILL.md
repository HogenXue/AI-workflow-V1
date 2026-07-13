---
name: grill-me
description: "Clarify complex, cross-module, or unclear requirements through a repository-aware, one-question-at-a-time interview. Use as the sole Codex interviewer for Trellis Phase 1.1; do not combine it with trellis-brainstorm."
---

# Grill Me

仅用于复杂、跨模块或需求不明确的请求；简单且需求完整的任务直接使用 Trellis，不自动触发本 Skill。显式 `$grill-me` 请求也遵循本流程。

在 Codex 的 Trellis 项目中，本 Skill 就是 Phase 1.1 的访谈实现，不是 `trellis-brainstorm` 的前置步骤。若本阶段已由其中一个访谈器完成，不得串联或再次加载另一个。

1. 先取得创建或更新 Trellis task 的同意，并解析当前 planning task；能由仓库、已有 task 或项目上下文回答的问题不得再问用户。
2. 每次只问一个必要问题，等待回答后再继续。每轮把确认结论写入该 task 的 [Trellis PRD 模板](templates/prd-requirements.md)。
3. 决策树收敛后，确认 PRD 已包含问题、范围、非目标、验收标准和未决项；不得创建第二份 Spec 或任务清单。
4. PRD 收敛后，将控制权交回 Trellis planning，由 Trellis 维护 Design、Plan、Research、状态和 Journal。只有用户确认规划并授权实施后才可调用 `task.py start`。

Grill Me 不管理 task 生命周期、不写代码、不执行测试、审查或 Git 操作。

详细交接状态见 [工作流交接规则](references/trellis-handoff.md)，示例见 [复杂需求访谈](examples/new-feature-session.md)。
