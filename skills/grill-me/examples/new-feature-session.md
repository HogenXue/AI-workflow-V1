# 复杂需求访谈示例

用户提出“增加门店库存调拨”后，Agent 判断其涉及跨门店库存与审批，因此加载 Grill Me，先检查现有库存和审批代码。

Agent 一次只问一个仓库无法回答的问题：“跨门店调拨是否必须经过审批？”用户确认“必须审批”。Agent 将该结论交给 OpenSpec 变更 Spec，然后继续询问下一项必要决策。

访谈完成后，OpenSpec Spec 汇总需求、场景、验收标准和未决项。用户确认该 Spec 后，Agent 才请求同意创建 Trellis task；Trellis 维护 task 级 PRD/计划、状态、Journal 和 Spec 引用，但不复制行为规范。实施采用 TDD，GitNexus 在修改前及提交前分别检查影响与 Git 范围。
