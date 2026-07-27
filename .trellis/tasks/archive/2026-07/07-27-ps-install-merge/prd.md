# PS install host merge

## Goal

PowerShell 版 `codex-merge` / `cursor-merge`，含 MCP merge（调 Python）与项目级 hooks/rules 契约。

## Depends on

- **Requires** `07-27-ps-install-lib`。
- 可与 components 并行。

## Requirements

- R1: `--project-root` / `--skip-project` / `--interactive` / `--mem0-url` / `--mcp-keep|--mcp-overwrite` / `--replace` 等与 bash 对齐。
- R2: 调用 `scripts/lib/merge_host_mcp.py`；解析 `python`/`python3`；远程 HTTP URL 拒绝且不改目标。
- R3: Codex：用户级 hooks + MCP；不把 cwd git root 当 project root。Cursor：项目 rules/hooks 仅在显式 root；不改仓库根 `AGENTS.md`；不写对端 host 树。
- R4: dangling symlink 备份；冲突/失败时 MCP rollback 语义与 bash 一致。

## Acceptance Criteria

- [ ] 两 merge 脚本在 Windows 上完成与 `test_install_interactive.py` 关键场景对等的行为（由 PS 测试验证）。
- [ ] 不重写 `merge_host_mcp.py` 策略（除非契约级 bug，需同步文档）。

## Out of Scope

- skills/config 安装；`install.cmd`。
