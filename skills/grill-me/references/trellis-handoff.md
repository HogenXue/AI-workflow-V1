# 工作流交接规则

## 状态顺序

```text
复杂需求 / 需求不明确
  -> 检索仓库与现有 OpenSpec 变更
  -> 每次一个问题，持续记录 OpenSpec handoff
  -> OpenSpec 创建或更新 canonical Spec
  -> 用户确认 Spec
  -> 请求用户同意创建 Trellis task
  -> Trellis 记录 Spec 引用、task-level PRD/plan、状态和 Journal
  -> TDD 实现
  -> GitNexus 在修改前分析影响、在提交前检查 Git 范围
```

## 持久化边界

- OpenSpec Spec 是需求、场景和验收的唯一落点；在已有变更中更新，不复制出第二份规格或任务清单。
- Grill Me 负责访谈和交接；Trellis 负责 task 级 PRD/计划、生命周期、状态和 Journal；TDD 负责实现；GitNexus 负责影响与 Git 检查。
- Trellis task 创建在 OpenSpec Spec 确认后；不得以 Grill Me 代替 OpenSpec 或 task 创建。

## 结束条件

只有 OpenSpec Spec 已包含需求、场景、验收标准和未决项并经用户明确确认后，才可请求创建 Trellis task。Trellis PRD/计划必须引用该 Spec 而非复制其行为内容；用户授权实施后才可让 Trellis 进入 `task.py start` 门槛。
