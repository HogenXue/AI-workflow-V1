# 记忆后端策略

先检索，再基于命中的已验证记录回答；记录来源、范围与不确定性，不能把未命中当作不存在。

仅在用户明确要求保留、确认架构决策、完成可复用排障结论或交接成果时存储。写入前确认项目范围和内容稳定性，避免保存临时状态、凭据或未经验证的推测。

没有可用后端、没有写入权限或无法定位项目时，只报告缺失能力与已完成的只读检查，并请求用户提供上下文或确认人工记录位置；不得声称已经检索、保存或更新记忆。

## 后端分工

| 后端 | 适用场景 | 主要工具 |
| --- | --- | --- |
| Recallium | 项目记忆、任务、规则、决策、进度、会话回顾 | `session_recap`、`search_memories`、`get_rules`、`store_memory` |
| Mem0 | 跨项目语义事实、用户/Agent 维度偏好与结论 | `memory_search`、`memory_add`、`memory_list` |

两者可同时使用：Recallium 负责项目工作流上下文，Mem0 负责细粒度语义事实。mem0 插件 hooks 可能已注入部分 Mem0 上下文，仍应在 memory skill 流程中按需补检索。

## Recallium MCP（项目记忆）

Codex MCP 服务名：`recallium`（`http://www.59005046.xyz:8102/mcp`）。

### 何时优先用 Recallium

- 会话开始或任务延续：先了解项目近期活动与待办。
- 用户询问历史决策、规格、进度、任务或项目规则。
- 用户消息以 `recallium` 开头或明确要求「查 recallium / 项目记忆」。
- 需要记录决策、设计、进度、任务或研究结论（项目维度）。

### 项目名解析

- `project_name` 从当前工作区推断：优先 Git 仓库目录名的小写形式（如 `CodexTamplate` → `codextamplate`）。
- 若 Recallium 中已有明确项目别名且用户指定，以用户指定为准。

### 常用读操作

1. **快速回顾**：`session_recap(project_name=...)` — 最近活动、待办、近期记忆摘要。
2. **语义搜索**：`search_memories(query=..., project_name=..., search_mode="semantic")`。
3. **展开详情**：`expand_memories(memory_ids=[...])` — 在 search 或 recap 命中后使用。
4. **项目规则**：`get_rules(project_name=...)` — 回答前先读项目规则（若存在）。
5. **一键加载**：用户说 recallium 时立即调用 `recallium(project_name=...)`，无需确认。

### 写操作

- 仅在结论已验证、内容稳定且用户明确要求保存时使用 `store_memory`。
- 类型示例：`decision`、`design`、`progress`、`task`、`research`。
- 写入后如需确认，可再 `search_memories` 或 `expand_memories` 闭环验证。

### 故障分层

- 工具不可见：检查 `~/.codex/config.toml` 中 `[mcp_servers.recallium]` 并重启 Codex。
- `Recent memories: 0`：该项目命名空间为空，不等于服务全局故障。
- search 与 write 失败原因可能不同；分别报告，不要笼统称「recallium 不可用」。

## Mem0 MCP（语义事实）

本项目使用自托管 Mem0 MCP，不直接调用 Mem0 Cloud REST API。

- 优先使用 Codex MCP 服务 `mem0` 暴露的 `memory_search`、`memory_add`、`memory_get`、`memory_update`、`memory_delete` 和 `memory_list`。
- 默认身份：`user_id=hogen`、`agent_id=codex`；若当前会话已有明确身份配置，以会话配置为准。
- 每次检索和写入都保留项目范围：

  ```json
  {
    "app_id": "CodexTamplate",
    "project": "<项目名>",
    "repo": "<Git remote 仓库名>",
    "branch": "<当前分支>",
    "skill": "<当前 skill；未知时为 unknown>"
  }
  ```

- `project`、`repo`、`branch` 从当前工作区和 Git 状态解析；`skill` 只有在调用方明确知道时才填写，不要臆测。
- `memory_search` 将上述字段作为 `metadata_filter`，并同时传入 `user_id` 和 `agent_id`。
- `memory_add` 将上述字段作为 `metadata`，并同时传入 `user_id` 和 `agent_id`。
- 写入应简短、可复用，并优先记录结论、范围和验证状态。
