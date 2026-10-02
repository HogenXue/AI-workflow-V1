# 记忆后端策略

先检索，再基于命中的已验证记录回答；记录来源、范围与不确定性，不能把未命中当作不存在。

写入须有用户明确请求或现有项目规则的授权；已授权的验证后保存不再要求另一条保存指令。仅记录稳定决定、可复用排障经验和经过验证的交接结论，避免临时状态、凭据或推测。不同后端的授权分别判断；Recallium 的项目规则不自动授权修改 Codex 的本地记忆文件。

没有可用后端、没有写入权限或无法定位项目时，说明缺失能力并继续可独立完成的工作；依赖历史规则才能安全决定的操作等待相关信息。完成时报告保存状态，未保存则建议在后端恢复后保存；不得声称已经检索、保存或更新记忆。

## 后端分工

| 后端 | 适用场景 | 主要工具 |
| --- | --- | --- |
| Recallium | 项目记忆、任务、规则、决策、进度、会话回顾 | `session_recap`、`search_memories`、`get_rules`、`store_memory` |
| Mem0 | 跨项目语义事实、用户/Agent 维度偏好与结论 | `memory_search`、`memory_add`、`memory_list` |

两者可同时使用：Recallium 负责项目工作流上下文，Mem0 负责细粒度语义事实。mem0 插件 hooks 可能已注入部分 Mem0 上下文，仍应在 memory skill 流程中按需补检索。

## Recallium MCP（项目记忆）

Codex MCP 服务名：`recallium`（`https://www.59005046.xyz:8102/mcp`）。远端 Recallium
必须使用 HTTPS；只有本机回环地址可使用明文 HTTP。

### 何时优先用 Recallium

- 会话开始或任务延续：先了解项目近期活动与待办。
- 用户询问历史决策、规格、进度、任务或项目规则。
- 用户消息以 `recallium` 开头或明确要求「查 recallium / 项目记忆」。
- 需要记录决策、设计、进度、任务或研究结论（项目维度）。

### 项目名解析

- 优先沿用用户指定、项目配置或已有记录中的 `project_name`，避免把重命名后的目录当作新的记忆空间。
- 未配置时从 Git 仓库目录名推导候选，并用规则/搜索确认。不能凭目录大小写猜测已有别名或迁移历史记忆。

### 常用读操作

1. **项目规则**：项目要求时，会话开始调用 `get_rules(project_name=...)`。
2. **语义搜索**：项目要求时，修改前调用 `search_memories(query=..., project_name=..., search_mode="semantic")`。
3. **快速回顾**：需要近期活动时使用 `session_recap(project_name=...)`。
4. **展开详情**：命中后按需使用 `expand_memories(memory_ids=[...])`。
5. 仅调用当前服务实际暴露的工具；工具名和参数以当前工具 schema 为准。

### 写操作

- 结论已验证、内容稳定且用户或项目规则已授权时使用 `store_memory`。项目要求实现后保存时，关联实际 `related_files`，记录验证范围与限制。
- 类型示例：`decision`、`design`、`progress`、`task`、`research`。
- 写入后如需确认，可再 `search_memories` 或 `expand_memories` 闭环验证。

### 故障分层

- 工具不可见：检查 `~/.codex/config.toml` 中 `[mcp_servers.recallium]` 并重启 Codex。
- `Recent memories: 0`：该项目命名空间为空，不等于服务全局故障。
- search 与 write 失败原因可能不同；分别报告，不要笼统称「recallium 不可用」。

## Mem0 MCP（语义事实）

本项目使用自托管 Mem0 MCP，不直接调用 Mem0 Cloud REST API。

- 优先使用 Codex MCP 服务 `mem0` 暴露的 `memory_search`、`memory_add`、`memory_get`、`memory_update`、`memory_delete` 和 `memory_list`。
- 从当前后端、宿主或项目配置获取 `user_id`、`agent_id`，沿用已确认的命名空间；不硬编码作者身份。必需身份无法确定时，先完成独立工作，仅在实际记忆操作需要时询问。
- 每次检索和写入都保留项目范围：

  ```json
  {
    "app_id": "<已配置的应用命名空间；可选>",
    "project": "<项目名>",
    "repo": "<Git remote 仓库名>",
    "branch": "<当前分支>",
    "skill": "<当前 skill；未知时为 unknown>"
  }
  ```

- 模板占位符不能直接发送给后端。`app_id` 使用已有配置，未配置且非必需时省略；`project`、`repo`、`branch` 从当前工作区和 Git 状态解析，`skill` 仅在明确知道时填写，不要臆测。
- `memory_search` 将上述字段作为 `metadata_filter`，并同时传入 `user_id` 和 `agent_id`。
- `memory_add` 将上述字段作为 `metadata`，并同时传入 `user_id` 和 `agent_id`。
- 写入应简短、可复用，并优先记录结论、范围和验证状态。
