---
name: grill-me
description: "Clarify complex requirements through a repository-aware, one-question-at-a-time interview before OpenSpec creates the canonical Spec. Use for complex or unclear changes in a Trellis project."
---

# Grill Me

仅对复杂需求或需求不明确的请求执行本流程；简单修改不自动触发。显式 `$grill-me` 请求也遵循本流程。

1. 先检索仓库、已有 OpenSpec 变更和项目上下文；能由它们回答的问题不得再问用户。
2. 每次只问一个必要问题，等待回答后再继续。每轮把确认结论收集到 [OpenSpec 交接模板](templates/prd-requirements.md)。
3. 决策树收敛后，交给 OpenSpec 创建或更新 canonical Spec，包含需求、场景、验收标准和未决项；不要将这些行为规范复制进 Trellis task 的 PRD。
4. Spec 经用户确认后，才请求同意创建 Trellis task。Trellis 维护 task 级 PRD/计划、该 Spec 的引用、任务状态和 Journal；不重复需求、场景或验收，也不维护第二份任务清单。
5. Trellis 执行阶段遵守 TDD；在修改前和提交前分别使用 GitNexus 进行影响分析与 Git 范围检查。只有用户授权实施后才可调用 `task.py start`。

详细交接状态见 [工作流交接规则](references/trellis-handoff.md)，示例见 [复杂需求访谈](examples/new-feature-session.md)。
