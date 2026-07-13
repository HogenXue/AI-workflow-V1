# 复杂需求访谈示例

用户提出“增加门店库存调拨”后，Agent 取得创建 Trellis task 的同意并加载 Grill Me，将它作为 Phase 1.1 的唯一访谈器，然后检查现有库存和审批代码。

Agent 一次只问一个仓库无法回答的问题：“跨门店调拨是否必须经过审批？”用户确认“必须审批”。Agent 将该结论写入当前 Trellis task 的 PRD，然后继续询问下一项必要决策。

访谈完成后，Trellis PRD 汇总需求、场景、验收标准和未决项。此时不再运行 `trellis-brainstorm`；用户确认 PRD 后，Trellis 继续维护 Design、Plan、状态和 Journal。
