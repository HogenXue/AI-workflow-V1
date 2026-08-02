# Implement: Claude Code app support

## Order

依赖：步骤 1 → 2/3 可并行 → 4 → 5 → 6 → 7。

### 1. 扩展 MCP merge helper

- [ ] `scripts/lib/merge_host_mcp.py`：`--host` 增加 `claude`；JSON mcpServers 路径与 Cursor 共用实现，提示文案用 host 名。
- [ ] 新增 `trellis/claude/mcp/servers.json`（与 Cursor fragment 同 schema）。
- [ ] 单测：claude host ADD/KEEP/冲突/URL 校验（可挂在现有 merge 测试旁）。

### 2. 新增 `claude-merge` 组件（bash + ps）

- [ ] `scripts/install-claude-merge.sh` / `install-claude-merge.ps1`：对标 `cursor-merge` 的 MCP 部分；**无** project hooks/rules。
- [ ] 默认 MCP 目标 `$HOME/.claude.json`；`--mcp-file` 可覆盖。
- [ ] 默认 backup-dir：`$HOME/.claude/.ai-workflow-backups`（即使 mcp 文件在 home 根）。
- [ ] 标志：`--dry-run/--apply`、`--mcp-keep/--mcp-overwrite`、`--mem0-url`、`--replace`（若保留与 cursor 对齐的表面旗标则文档说明无项目步骤）、`--interactive`、`--backup-dir`。
- [ ] 接受但忽略 `--project-root` / `--skip-project`（兼容多宿主向导传参），打印 SKIP 说明可选。

### 3. 扩展 `agents` 组件

- [ ] bash + ps：`--document-name`（默认 `AGENTS.md`）、`--no-hooks-feature`。
- [ ] `--no-hooks-feature` 时：只安装文档，不做 `config.toml` 校验/写入。
- [ ] 测试：Claude 文档安装与 Codex hooks 路径互不干扰。

### 4. 入口与 profile

- [ ] `install.sh` / `install.ps1`：组件表增加 `claude-merge`。
- [ ] 新增 `install_profile_claude`：skills → `~/.claude/skills`；config → `~/.claude/config`；agents → CLAUDE.md + no-hooks；claude-merge；**不**调 graphify。
- [ ] 交互菜单改为多选编号解析；summary 含 Claude 行；仅 Cursor 时要 project-root。

### 5. 契约与文档

- [ ] 更新 `.trellis/spec/scripts/installer-contracts.md`（Claude profile map、菜单、MCP、backup-dir）。
- [ ] 更新 `README.md`、`CHANGELOG.md`。

### 6. 测试补齐

- [ ] `tests/test_install_interactive.py`：多选、Claude profile、不写项目树。
- [ ] `tests/test_install.py` 或专用模块：claude-merge / agents 新旗标。
- [ ] `tests/test_install_*_ps.py`：入口分发与 merge/agents 对等断言。

### 7. 验证

- [ ] `python3 -m unittest` 相关 install 测试（含可跑的 `*_ps.py`）。
- [ ] `python3 scripts/validate-all-skills.py`（若未改 skills 可作回归）。
- [ ] dry-run 手工抽查：`bash scripts/install.sh claude-merge --dry-run`。

## Success criteria

满足 `prd.md` 全部 Acceptance Criteria；design 中的风险缓解有对应测试或显式断言。

## Out of scope during implement

- Graphify 目标路径扩展
- 项目 `.mcp.json` / 项目 `.claude/` 安装
- 重构无关 installer 逻辑
