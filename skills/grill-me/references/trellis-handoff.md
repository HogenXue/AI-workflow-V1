# 工作流交接规则

## 状态顺序

```text
复杂 / 跨模块 / 需求不明确
  -> 请求用户同意创建或更新 Trellis task
  -> 检索仓库与当前 task
  -> Grill Me 作为 Phase 1.1 的唯一访谈器
  -> 每次一个问题，持续记录 Trellis PRD
  -> 用户确认 PRD
  -> Trellis 完成 Design / Plan / Research 并进入执行
```

## 持久化边界

- Trellis task 的 PRD 是需求、场景和验收的唯一落点；不得复制出第二份规格或任务清单。
- Grill Me 只负责 Phase 1.1 的访谈和 PRD 收敛；Trellis 负责其余 planning、生命周期、状态和 Journal。
- 简单且需求明确的任务跳过 Grill Me，直接使用 Trellis 的轻量流程。
- 在 Codex 中运行 Grill Me 后，不再运行 `trellis-brainstorm`；反之亦然。两个访谈器不得串联。
- 不得以 Grill Me 代替 Trellis task 创建或用户确认。

## 结束条件

只有 Trellis PRD 已包含需求、场景、验收标准和未决项并经用户明确确认后，用户授权实施时才可让 Trellis 进入 `task.py start` 门槛。
