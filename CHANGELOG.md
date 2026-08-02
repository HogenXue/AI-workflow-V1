# 变更记录

## 未发布

### 新增

- 平台无关的有效配置输出与公开配置键消费者校验。
- Trellis readiness、quality、completion 可执行门禁及新鲜质量证据。
- Ubuntu、macOS 共用的 CI 质量入口。
- Trellis 兼容的 `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts` 能力型 Skill。
- Claude Code App 用户级安装 profile：`claude-merge`、交互多选（Codex/Cursor/Claude）、`~/.claude/CLAUDE.md` 与 `~/.claude.json` MCP 合并（bash / PowerShell 对等）。

### 变更

- Recallium 默认地址改为 HTTPS；远端 MCP URL 强制 HTTPS，本机回环地址仍允许 HTTP。
- Memory、GitNexus、Release 优先读取统一有效配置。
- Codex、Cursor、Claude 共用同一个工作流检查器，原生 Trellis 状态机和质量评审保持不变。
- 用 `grill-with-docs` 替换 `grill-me`；需求仍只写 Trellis PRD，领域术语与持久决定分别写入 `.trellis/spec/domain/`、`.trellis/spec/decisions/`。
- `grill-me` 作为 legacy Skill 可通过 `--prune-legacy` 在时间戳备份后显式移除。
- 交互安装菜单改为多选编号（`1` Codex / `2` Cursor / `3` Claude）；仅选择含 Cursor 时询问 project-root。
- `agents` 支持 `--document-name` 与 `--no-hooks-feature`（Claude 全局规则路径）。

### 修复

- `config-check.sh` 不再把嵌套 MCP TOML 节误报为服务器名。
- 修正文档中的 MCP 内容说明、配置路径和运行时依赖。

> 本节记录尚未发布的工作区变更；`manifest.yaml` 版本仍为 `3.0.0`。
