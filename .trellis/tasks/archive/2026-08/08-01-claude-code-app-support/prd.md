# Add Claude Code app support

## Problem

AI-workflow-V1 已有 Codex / Cursor 的 profile 安装与 MCP 合并，但缺少 Claude Code App 对等入口。`workflow_check.py` 虽已声明 Claude 共用，安装向导与 `claude-merge` 组件尚未存在。

## Goal

为 Claude Code App 增加与现有 Codex / Cursor 一致的用户级完整 profile 安装能力：Skills、配对 config、用户级 MCP 合并、全局 `CLAUDE.md`、交互向导与 bash/PowerShell 对等，以及文档与测试。

## Non-goals

- 不把 Cursor/Codex 目录树直接复制到 Claude 路径（继续遵守 duty mapping）。
- 不覆盖项目根由 Trellis 管理的 `AGENTS.md` / 项目根 `CLAUDE.md`。
- 不写入项目级 `.claude/`（hooks / settings / agents）；该面由 Trellis `init --claude` 负责。
- 不写项目级 `.mcp.json`。
- 不把 Claude Desktop（非 Claude Code）作为本任务目标。
- Claude 推荐完整安装不自动安装 Graphify；`graphify` 组件仍只写 `~/.agents/skills/graphify`。
- 不静默默认 `git` 根为 project-root。

## Confirmed decisions

- **范围 = 完整用户级 profile 对等**：skills、配对 config、MCP 合并、全局 `CLAUDE.md`、交互向导、bash/PowerShell 对等、文档与测试。
- **MCP 目标 = 用户级**：仅合并到 `~/.claude.json` 的 `mcpServers`。
- **项目级 `.claude/` = 安装器不写**：留给 Trellis。
- **全局规则 = 安装 `~/.claude/CLAUDE.md`**：源 `AGENTS.global.md`；已存在则先时间戳备份再替换。
- **交互菜单 = 多选编号**：`1) Codex  2) Cursor  3) Claude`；输入如 `1`、`1 3`、`1,2,3`。仅当选择含 Cursor 时询问 project-root。
- **Graphify = 不纳入 Claude 推荐安装**：与 Cursor 一致；不扩展 graphify 默认目标。

## Known facts (from repo)

- 交互安装目前仅 Codex / Cursor（`install.sh` / `install.ps1`）。
- MCP 合并共享 `scripts/lib/merge_host_mcp.py`，host 仅 `codex` | `cursor`。
- Claude Code 用户 Skills：`~/.claude/skills`；配对 config：`~/.claude/config`。
- Claude Code 用户 MCP：`~/.claude.json` → `mcpServers`。
- 安装器契约见 `.trellis/spec/scripts/installer-contracts.md`。

## Requirements

1. 新增 Claude Code 安装 profile，与 Codex/Cursor 同级，可被交互向导与组件 CLI 调用。
2. Skills 安装到 `~/.claude/skills`（copy/link/replace/prune 与现有 skills 组件一致）。
3. Config 安装到 `~/.claude/config`，与 skills 根配对。
4. 提供 `claude-merge`（bash + PowerShell）：将本包管理的 MCP 增量合并进 `~/.claude.json`（`mcpServers`）；扩展 `merge_host_mcp.py` 的 `host=claude`；冲突策略、交互 URL 确认与 HTTPS 校验与现有 host 对齐；不写项目 `.mcp.json`。
5. 推荐完整安装写入 `~/.claude/CLAUDE.md`（源：`AGENTS.global.md`）；覆盖前备份；不改写项目根 `CLAUDE.md` / `AGENTS.md`。
6. TTY 无参向导：多选编号选择宿主；仅当选择含 Cursor 时询问 project-root。
7. Claude 推荐完整安装不调用 `graphify` 组件。
8. README / CHANGELOG / installer-contracts 同步 Claude profile 与菜单契约。
9. 测试覆盖：组件分发、多选菜单解析、MCP 合并/冲突/URL 安全、Claude-only 不改项目树与对端宿主树、bash/ps 对等关键路径。

## Acceptance Criteria

- [x] `install.sh` / `install.ps1` 支持多选编号选择含 Claude 的 profile（含推荐完整安装）。
- [x] 组件 `claude-merge` 在 bash 与 PowerShell 可用，诊断前缀与退出码与现有 merge 组件对齐。
- [x] 推荐 Claude 安装写入/更新 `~/.claude/CLAUDE.md`（先备份）；不修改项目根 `CLAUDE.md` / `AGENTS.md`。
- [x] Claude-only 安装：写入 `~/.claude/skills`、`~/.claude/config`、`~/.claude.json`（MCP）、`~/.claude/CLAUDE.md`；不创建/修改项目 `.claude/` 或 `.mcp.json`；不要求 project-root；不调用 graphify；Codex/Cursor 树不变。
- [x] MCP keep/overwrite、交互 URL 确认与 HTTPS 校验有测试。
- [x] 文档写明 Claude Code App 推荐安装路径与更新方式。
- [x] 相关 install 测试（含 `*_ps.py` 关键断言）通过。（本机 pwsh 运行时 23 例 skip；源码契约断言已通过，CI windows 预期覆盖）

## Open questions

（访谈已收敛，无未决需求项。）

## Notes

- Phase 1.1 访谈器：`grill-with-docs`。
- 用户确认本 PRD 后，进入 `design.md` / `implement.md`，再 `task.py start`。
