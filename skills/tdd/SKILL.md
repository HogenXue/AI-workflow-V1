---
name: tdd
description: "Drive feature and bug-fix implementation with a verified red-green-refactor cycle. Use before writing production code when behavior changes need automated tests."
---

# TDD

在已确认行为后，以测试先行实现功能、修复缺陷或改变既有行为。TDD 是当前项目工作流内的实现方法，不是独立工作流；它不接管需求澄清、PRD、任务生命周期、质量审查或 Git。

## 进入条件和边界

1. 若项目存在 `.trellis/`，先读取当前 Trellis task 的 PRD/计划；不存在 `.trellis/` 时，读取项目已有需求、issue、测试和用户已确认的验收，不为使用 TDD 自动引入 Trellis。
2. Trellis 项目以 PRD 为行为契约；其他项目使用其既有事实来源。不要在 TDD 中重写或创建第二份 Spec；测试暴露需求缺口时，返回当前项目的 planning/需求负责人澄清。
3. 在 Trellis 项目中，Trellis 是 task 状态、计划和 Journal 的唯一来源；每轮只向现有记录写实现证据，不另建任务清单。其他项目遵守其已有记录方式。
4. 按项目配置和改动风险决定是否在修改前使用 GitNexus；TDD 只负责用测试证明行为，不负责需求设计、影响分析或项目管理。
5. 文档、纯配置、生成代码或无法合理自动化测试的改动，不强行制造 RED；说明理由并执行与风险相称的验证。原型若要跳过测试先行，先取得用户同意。

## RED → GREEN → REFACTOR

对每个最小可验证行为重复以下循环。使用仓库既有的测试框架和最小相关测试命令。

1. **RED**：从一个场景或验收标准写一条最小的、描述行为的测试。先运行它，确认它因功能尚未实现而失败；拼写、环境或测试配置错误不算 RED。
2. **GREEN**：只写使该测试通过的最小生产代码。运行该测试，并运行必要的相邻测试；失败时修复实现而不是放宽测试。
3. **REFACTOR**：仅在全绿后消除重复、改善命名或结构；重跑相关测试，保持行为不变。
4. 继续下一个行为，直到已确认的验收标准、错误路径和关键边界都已有对应测试。

不要先写实现再补测试；“测试立即通过”意味着它可能没有验证新增行为，应修正测试并重新确认 RED。

## 交接和完成

- 使用 [TDD 证据模板](templates/tdd-cycle.md) 记录测试、RED 证据、GREEN 证据和相关测试范围。
- 将精简证据写入当前 Trellis task 的 Journal/执行记录，而不是复制 PRD 内容。
- 在宣称完成前，运行与改动相称的测试并报告结果；相关测试全绿后交回 Trellis，由项目原生 `trellis-check` 执行质量检查。P0/P1 修复或豁免后再由 GitNexus 核对 Git 范围。

复杂场景可参考 [Trellis 协作边界](references/trellis-boundary.md) 与 [功能实现示例](examples/feature-cycle.md)。
