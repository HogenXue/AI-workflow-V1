---
name: review
description: "Review code changes for correctness, security, compatibility, maintainability, performance, and regression risk. Use for pull-request review, pre-merge review, release review, or a focused review of changed files."
---

# Review

先读取包内 `config/defaults.yaml`，再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。配置无效、缺少基线或范围不明确时，先报告限制，并缩小为可证实的文件范围。

确认审查基线、待审 diff、测试状态和接口/数据契约。按[严重性准则](references/review-severity.md)优先审查正确性、安全性、兼容性、回归风险、性能与可维护性；每项发现必须给出可定位的证据、实际影响和可执行建议，而非泛泛评价。

使用[审查报告模板](templates/review-report.md)按严重性排序。没有发现时，也要说明已审范围、使用的证据和未覆盖范围；不要把未运行的测试或未读的模块表述为已验证。

审查工具不可用时，使用普通 Git diff、代码阅读、`rg` 和可运行的本地测试作安全替代，并明确这不包含外部 PR、CI 或静态分析平台结果。不得虚报已读取远端评论、已通过 CI 或已执行工具扫描。参见[拉取请求审查示例](examples/review-pull-request.md)。
