---
name: grill-with-docs
description: "Clarify complex, cross-module, or unclear requirements through a repository-aware, one-question-at-a-time interview while maintaining Trellis domain and decision specs. Use as the sole Codex interviewer for Trellis Phase 1.1; do not combine it with trellis-brainstorm or create a second spec/task workflow."
---

# Grill with Docs

仅用于复杂、跨模块或需求不明确的请求；简单且需求完整的任务直接使用 Trellis 轻量流程。
在 Codex 的 Trellis 项目中，本 Skill 是 Phase 1.1 的唯一访谈器，不是
`trellis-brainstorm` 的前置步骤，也不接管后续生命周期。

## 访谈流程

1. 先取得创建或更新 Trellis task 的同意并解析当前 planning task。读取当前 Trellis PRD、
   `.trellis/spec/domain/` 和相关 `.trellis/spec/decisions/`；能从仓库、任务工件或工具查到的
   事实不得再问用户。
2. 沿决策依赖一次只问一个必要问题，并给出推荐答案和简短理由。等待用户回答后再进入下一个
   分支，不把多个决策打包提问。
3. 每轮把确认的需求、范围、场景、验收和未决项立即写入当前 Trellis PRD。Trellis PRD 是
   这些内容的唯一来源，不另建 Spec、issue 或任务清单。
4. 同步维护 Trellis 长期知识，但严格区分用途：只把稳定的领域术语写入
   `.trellis/spec/domain/`；只把难以逆转、缺少上下文会令人意外、且经过真实权衡的决定写入
   `.trellis/spec/decisions/`。具体格式见
   [领域文档规则](references/domain-docs.md)。
5. 决策树收敛后，确认 PRD 已覆盖问题、目标、非目标、验收标准和未决项，并请求用户确认。
   随后把控制权交回 Trellis，由其维护 Design、Plan、Research、状态、执行和 Journal。

## 边界

- `.trellis/spec/domain/` 只是领域词汇规范，不写实现细节、验收、计划或任务状态。
- `.trellis/spec/decisions/` 只记录持久的决定与原因，不作为第二份 Design 或会话流水账。
- 不写业务代码，不执行测试、质量审查、commit、push 或 task 状态变更。
- 同一 Phase 1.1 只运行一个访谈器；若已运行本 Skill，不再运行 `trellis-brainstorm`，反之亦然。

状态和持久化所有权详见 [Trellis 交接边界](references/trellis-boundary.md)。
