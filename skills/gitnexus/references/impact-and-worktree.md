# 影响分析与 Worktree

修改任何 symbol 前，先用 GitNexus 检查定义、直接调用者、数据或用户流程以及相邻 worktree/分支的影响；先报告范围，再编辑。

若发现 HIGH 或 CRITICAL 风险，必须说明风险等级、受影响流程、证据、未覆盖范围与建议的人工确认或验证。提交前运行 `detect_changes`，将结果纳入提交范围检查。

工具不可用时，只能使用普通 Git 与 `rg` 做只读替代，例如 `git status`、`git log`、`git diff --stat` 与代码文本搜索；必须声明这不含 GitNexus 图谱分析，不能虚报影响结论或 `detect_changes` 已运行。
