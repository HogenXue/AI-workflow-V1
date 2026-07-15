# 变更记录

## 未发布

### 新增

- 平台无关的有效配置输出与公开配置键消费者校验。
- Trellis readiness、quality、completion 可执行门禁及新鲜质量证据。
- Ubuntu、macOS 共用的 CI 质量入口。

### 变更

- Recallium 默认地址改为 HTTPS；远端 MCP URL 强制 HTTPS，本机回环地址仍允许 HTTP。
- Memory、GitNexus、Release 优先读取统一有效配置。
- Codex、Cursor、Claude 共用同一个工作流检查器，原生 Trellis 状态机和质量评审保持不变。

### 修复

- `config-check.sh` 不再把嵌套 MCP TOML 节误报为服务器名。
- 修正文档中的 MCP 内容说明、配置路径和运行时依赖。

> 本节记录尚未发布的工作区变更；`manifest.yaml` 版本仍为 `3.0.0`。
