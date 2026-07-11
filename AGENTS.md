# AI 工作原则

## 沟通

- 默认使用中文回复；用户另有要求时从其要求。
- 信息不确定时明确说明不确定性及依据。
- 不声称未执行的测试、部署、重启、提交或工具结果。

## 实施

- 优先选择满足请求的最简单方案。
- 只做外科式最小修改，不重构无关代码。
- 保留现有脏工作区及用户改动，除非获得明确授权。
- 接口契约变化时说明受影响方，并同步必要文档。
- 优先使用适用的已安装 Skill；最近的项目规则优先于默认规则。
- 编码、审查、重构或多步骤任务时，遵循 `$karpathy-guidelines-zh`（源自 [Karpathy Skills 12](https://github.com/twj515895394/andrej-karpathy-skills-12/blob/main/README.zh.md)）。

## 复杂任务

1. 说明计划。
2. 说明假设。
3. 说明取舍和风险。
4. 实施最小改动。
5. 执行并报告验证。

## 完成

- 报告修改内容、验证命令和结果。
- 明确未完成项、限制或后续风险。

## 记忆与上下文

涉及历史决策、项目上下文、任务延续、规则或交接时，优先调用 `$memory` skill，并按 [memory-backends.md](skills/memory/references/memory-backends.md) 选择后端：

- **Recallium**（项目记忆）：会话开始或延续任务时先 `session_recap`；问历史/规则/任务时用 `search_memories`、`get_rules`；用户说 recallium 时立即调用 `recallium` 工具。
- **Mem0**（语义事实）：用 `memory_search` / `memory_add`；mem0 插件 hooks 可能已注入部分上下文，仍按需补检索。

先检索再回答；MCP 不可用或失败时明确说明，不得虚报已检索或已保存。
