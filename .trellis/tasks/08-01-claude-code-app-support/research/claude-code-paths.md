# Research: Claude Code user MCP location

## Finding

本机 Claude Code（native install）用户状态文件为 `~/.claude.json`，其中包含顶层键 `mcpServers`（对象）。与 Cursor 的 `~/.cursor/mcp.json`（根即/含 `mcpServers`）schema 同形，但 Claude 文件还包含大量非 MCP 状态字段。

另存在项目级 `.mcp.json` 与审批流（`claude mcp list` 帮助文案）；本任务 PRD 明确不写项目级。

## Implication for merge

- 读取整个 JSON，只修改 `mcpServers` 子树，写回时保留其他键。
- 不可用「整文件替换为 fragment」策略。
- 备份必须覆盖完整原文件。

## Skills / config pairing

Skill 通过 `../../config` 解析：`~/.claude/skills/<name>` → `~/.claude/config`。与 `~/.agents`、`~/.cursor` 配对规则一致。

## Global rules file

用户级全局指令文件为 `~/.claude/CLAUDE.md`（本机已存在）。与 Codex `~/.codex/AGENTS.md` 职责对应，文件名不同。
