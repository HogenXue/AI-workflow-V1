# 评估符号修改

## 用户请求

“修改 `calculateDiscount` 前，请评估哪些下单和优惠券流程会受到影响。”

## 工作流

1. 读取默认配置与项目 `hogen-codex.yaml`，以项目值覆盖默认值。
2. 检测 GitNexus 能力；可用时分析 symbol、直接调用者和受影响流程。
3. 按影响报告模板标注风险；HIGH 或 CRITICAL 时列出证据、未知项和人工确认需求。
4. 提交前运行 `detect_changes`；若工具不可用，只用只读 Git 与 `rg`，并声明图谱分析限制。

## 最终报告

已识别 `calculateDiscount` 的直接调用者及其结算、优惠券校验流程。风险为 HIGH：规则变化可能改变订单金额；提交前需执行 `detect_changes` 并回归相关流程。若 GitNexus 不可用，应报告只完成了 Git/`rg` 的只读替代，不能宣称图谱分析已完成。
