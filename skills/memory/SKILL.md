---
name: memory
description: "Retrieve and record durable project context, decisions, learned constraints, and completed outcomes. Use for prior-work questions, architecture decisions, handoffs, and preserving important conclusions."
---

# Memory

先读取包内 `config/defaults.yaml`，再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。

检测当前会话可用的记忆后端及其检索、写入能力。先检索已有上下文，再回答或记录；不要把 Skill 的存在当作后端可用的证据。仅在用户明确要求保留、已完成重要决策或需要交接时，记录经过验证的稳定结论。

后端不可用、无写入权限或无法确认目标项目时，明确报告缺失能力，请用户提供必要上下文或确认记录位置；只执行安全的只读或人工替代，绝不虚报检索或存储结果。详见 [后端策略](references/memory-backends.md)、[决策模板](templates/decision.md) 与 [记录示例](examples/record-decision.md)。
