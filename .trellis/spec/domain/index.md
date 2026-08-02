# AI-workflow 安装领域

本包面向多 AI 宿主的可安装 Skill / 配置 / MCP 工作流。

## Language

**Claude Code profile**：
面向 Anthropic Claude Code（CLI/App）的用户级安装组合：skills → `~/.claude/skills`，配对 config → `~/.claude/config`，MCP → `~/.claude.json`，全局规则 → `~/.claude/CLAUDE.md`。
_Avoid_: Claude Desktop 配置、项目级 `.claude/` 初始化（后者属 Trellis）

**claude-merge**：
将本包管理的 MCP 服务器定义增量合并进 Claude Code 用户级 `~/.claude.json` 的安装器组件（bash/PowerShell 对等）。
_Avoid_: 把 Cursor/Codex MCP 文件直接复制到 Claude

**Host profile**：
某一 AI 宿主的完整推荐安装路径（skills + 配对 config + 宿主 MCP/规则等），由交互向导或组件序列执行；宿主之间按 duty mapping 隔离，禁止目录树互拷。
_Avoid_: “把 Cursor 目录装到 Claude”
