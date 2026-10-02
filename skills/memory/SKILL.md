---
name: memory
description: "Retrieve and record durable project context, decisions, learned constraints, and completed outcomes. Use for prior-work questions, architecture decisions, handoffs, and preserving important conclusions."
---

# Memory

如果 skill 目录上两级存在 `config/effective_config.py`，优先运行该 helper，并通过
`--project-root <目标仓库>` 获取已经校验和合并的配置。helper 不存在时，再读取 skill
目录上两级的 `config/defaults.yaml`（Codex 安装后为 `~/.agents/config/defaults.yaml`；
源码仓库则为包根 `config/defaults.yaml`），并读取目标仓库根目录的 `hogen-codex.yaml`
（若存在）；项目值覆盖默认值。默认配置不存在时使用正文中的安全行为继续执行，不把可选
config 组件缺失当成记忆后端故障。

检测当前会话可用的记忆后端及其检索、写入能力。项目要求 Recallium 时，会话开始先调用 `get_rules`，修改前调用 `search_memories`；其他情形按需检索相关历史。不要把 Skill 的存在当作后端可用的证据。写入须有用户请求或现有项目规则的授权；项目已要求在实现完成并验证后保存稳定决定时，直接遵循该授权，无需再询问。保存验证状态，并通过 `related_files` 关联实际文件。

后端不可用、无写入权限或无法确认目标项目时，明确报告缺失能力，继续可独立完成的工作；只有依赖缺失历史才能安全决定时才等待相关信息。完成说明报告记忆是否保存，尚未保存时建议在后端恢复后保存，绝不虚报结果。详见 [后端策略](references/memory-backends.md)、[决策模板](templates/decision.md) 与 [记录示例](examples/record-decision.md)。

Memory 只负责长期记忆与跨会话上下文；它不替代 Trellis 的 PRD、Task、Journal 或项目管理。
