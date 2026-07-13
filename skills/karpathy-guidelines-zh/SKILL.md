---
name: karpathy-guidelines-zh
description: "Apply Karpathy-inspired guardrails as cross-cutting behavior for coding, review, refactor, and multi-step agent work. Use to reduce silent assumptions, over-engineering, unrelated edits, weak tests, context drift, and hidden failures."
---

# Karpathy 指南

源自 [Karpathy Skills 12 中文说明](https://github.com/twj515895394/andrej-karpathy-skills-12/blob/main/README.zh.md) 的 12 条行为契约（MIT）。

它是横切行为约束，不创建独立阶段、任务或工件，也不替代 Trellis 的项目管理与质量检查或 TDD 的实现循环。除非用户明确覆盖，否则适用于所有任务；非琐碎任务中谨慎优先于速度，简单任务可酌情简化。

完整规则见 [12 条规则](references/guidelines-zh.md)。检查点格式见 [检查点模板](templates/checkpoint.md)；应用示例见 [重构前应用示例](examples/apply-before-refactor.md)。

与项目 `AGENTS.md` 或 `hogen-codex.yaml` 冲突时，项目规则优先。
