# Claude MCP 写入用户级 ~/.claude.json

Claude Code profile 的 MCP 合并目标定为用户级 `~/.claude.json` 的 `mcpServers`，而不是项目 `.mcp.json`。

原因：与 Codex/Cursor「全局 MCP + 可选项目钩子」模型对齐；避免未显式选择 project-root 时误写入仓库；`~/.claude.json` 已是 Claude Code 原生用户 MCP 存放处。项目 MCP 与项目 `.claude/` 仍由 Trellis / 用户另行管理。
