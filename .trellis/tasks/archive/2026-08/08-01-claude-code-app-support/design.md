# Design: Claude Code app support

## Overview

在现有 Codex / Cursor profile 旁增加第三宿主 **Claude Code profile**：只写用户级路径，复用 skills/config 组件与共享 MCP merge helper，新增 `claude-merge`，并扩展交互菜单为多选编号。

## Architecture

```text
TTY wizard (1/2/3 multi-select)
  ├─ Codex profile   → ~/.agents/{skills,config} + ~/.codex + graphify + codex-merge
  ├─ Cursor profile  → ~/.cursor/{skills,config} + cursor-merge (+ project-root)
  └─ Claude profile  → ~/.claude/{skills,config,CLAUDE.md} + ~/.claude.json (MCP)
                         NO graphify, NO project .claude/, NO .mcp.json
```

Duty mapping 不变：禁止把 Cursor/Codex 目录树复制到 Claude。

## Component map

| Duty | Claude target | Mechanism |
|------|---------------|-----------|
| Skills | `~/.claude/skills` | 现有 `skills` 组件 + `--target` |
| Config | `~/.claude/config` | 现有 `config` 组件 + `--target` |
| Global rules | `~/.claude/CLAUDE.md` | 扩展 `agents`：`--document-name CLAUDE.md` + `--no-hooks-feature`；`--agents-home ~/.claude` |
| MCP | `~/.claude.json` → `mcpServers` | 新 `claude-merge` + `merge_host_mcp.py --host claude` |
| Graphify | （不装） | profile 不调用 |
| Project `.claude/` | （不写） | Trellis 负责 |

## Key design choices

### 1. MCP merge reuses Cursor JSON shape

`~/.claude.json` 顶层是大型用户状态对象，仅安全地增改 `mcpServers`，保留其余键（与 Cursor merge 对 `mcp.json` 的做法一致）。

- 模板：`trellis/claude/mcp/servers.json`（内容与 Cursor fragment 同 schema：gitnexus / recallium / mem0），独立文件以满足 duty mapping，避免从 `trellis/cursor/` 拷树。
- `merge_host_mcp.py`：将现有 `merge_cursor_json` 泛化为 JSON mcpServers 合并（host 标签用于提示文案），`choices` 增加 `claude`。
- 默认目标：`$HOME/.claude.json`；可用 `--mcp-file` / 环境变量覆盖（对标 Cursor）。
- 备份根：`dirname(mcp_file)/.ai-workflow-backups`（对 `~/.claude.json` 即为 `~/` 下备份目录——**应改为**与 Cursor 一致用宿主目录旁：优先 `~/.claude/.ai-workflow-backups`，即使目标文件在 `~/.claude.json`）。

**Backup-dir decision**：Claude MCP 文件在 `~/.claude.json`（home 根下），若用 `dirname` 会落到 `$HOME/.ai-workflow-backups`。为与「配对宿主备份根」一致，`claude-merge` 默认 `backup_dir=$HOME/.claude/.ai-workflow-backups`（目录可先创建），而不是 `$HOME/.ai-workflow-backups`。

### 2. `agents` 扩展，而不是新组件

Codex `agents` 会写 `AGENTS.md` 并改 `config.toml` hooks。Claude 只需文档：

- 新增 `--document-name`（默认 `AGENTS.md`）
- 新增 `--no-hooks-feature`：跳过 `config.toml` 校验与 hooks 写入
- Claude profile：`agents --apply --agents-home "$HOME/.claude" --document-name CLAUDE.md --no-hooks-feature`

禁止在未带 `--no-hooks-feature` 时把 `--agents-home` 指到 `~/.claude` 仍去改 `config.toml`（若文件不存在会错误创建）——因此 Claude 路径必须传 `--no-hooks-feature`。

### 3. Interactive multi-select

替换固定三项组合菜单：

```text
1) Codex
2) Cursor
3) Claude
Select agents (e.g. 1, 1 3, 1,2,3):
```

解析：空白或逗号分隔；去重；非法编号 → `ERROR: invalid agent choice` exit 2；空选择同错。

project-root：仅 `want_cursor` 时询问（与 PRD 一致）。Codex 用户级 hooks 行为保持现状。

### 4. bash / PowerShell 对等

同一 change set 更新：

- `install.sh` / `install.ps1`（分发、profile、菜单）
- `install-claude-merge.sh` / `.ps1`
- `install-agents.sh` / `.ps1`（document-name / no-hooks）
- `merge_host_mcp.py`
- 测试：`test_install*.py` 与 `*_ps.py`

### 5. Out of scope in this design

- 项目 `.mcp.json`、项目 `.claude/`、Graphify→`~/.claude/skills`
- 修改 Trellis 自带的仓库内 `.claude/` 模板语义

## Risks

| Risk | Mitigation |
|------|------------|
| 损坏 `~/.claude.json` 其他字段 | 只改 `mcpServers`；写前备份；原子写；失败回滚 |
| `agents` 误开 hooks 写进 `~/.claude/config.toml` | Claude 强制 `--no-hooks-feature`；测试断言无新 config.toml hooks 副作用 |
| 菜单解析回归 | 单测覆盖 `1`、`1 3`、`1,2,3`、非法、空 |
| bash/ps 漂移 | 契约写进 installer-contracts；两边同 PR 改 |

## Test plan (design-level)

- Claude profile / `claude-merge`：MCP ADD/KEEP/OVERWRITE、交互 URL、HTTPS 拒绝、备份回滚
- `agents --document-name CLAUDE.md --no-hooks-feature`：写入 CLAUDE.md、不改 config.toml、不碰项目根
- Claude-only：不写 project `.claude/`、不写 `.mcp.json`、不调 graphify、Cursor/Codex 树不变
- 菜单多选解析 + PS 对等关键断言
