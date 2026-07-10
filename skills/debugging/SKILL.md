---
name: debugging
description: "Investigate bugs, crashes, test failures, and unexpected behavior through reproduction, evidence collection, root-cause isolation, minimal repair, and verification. Use whenever diagnosing or fixing a defect."
---

# Debugging

先读取包内 `config/defaults.yaml`，再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。配置无效、复现条件不足或工作区状态不明确时，先报告限制，只收集可证实的证据。

按[证据闭环](references/evidence-loop.md)先复现，再收集日志、调用路径、输入和环境证据，隔离根因后才提出最小修复。修复后重跑能证明该问题的验证，并明确区分已执行、未执行和无法执行的步骤；不要用猜测代替根因。

调试工具不可用时，使用可访问的日志、测试、代码阅读、`rg` 和只读 Git 状态进行安全降级，并明确这不包含不可用工具的跟踪、性能分析或远端诊断结果。不得声称已经复现、定位根因或完成验证。使用[调试报告模板](templates/debug-report.md)记录证据，参见[运行时错误示例](examples/fix-runtime-error.md)。
