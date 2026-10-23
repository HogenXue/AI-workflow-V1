# 变更记录

## 未发布

### 新增

- 平台无关的有效配置输出与公开配置键消费者校验。
- 原生 Trellis 任务与上下文校验，以及按任务风险选择的质量验证。
- Ubuntu、macOS 的 Skill 校验和 Python fixture 测试；Windows 的 PowerShell 安装回归。
- Trellis 兼容的 `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts` 能力型 Skill。
- Claude Code App 用户级安装 profile：`claude-merge`、交互多选（Codex/Cursor/Claude）、`~/.claude/CLAUDE.md` 与 `~/.claude.json` MCP 合并（bash / PowerShell 对等）。
- MiniMax Code 与 WorkBuddy 原生安装 profile，以及五宿主的发现路径说明。
- `retro` 复盘 Skill；manifest 共 19 项，复用 Trellis 任务证据与原生 break-loop。
- 共享严格 Skill catalog、安装前身份检查及 `audit-skills` 冲突/漂移/完整性检查。

### 变更

- Recallium/Mem0 默认使用 HTTPS；HTTP 仅允许明确的回环、RFC1918 和 IPv6 ULA 地址。升级默认保留已有 MCP 地址。
- Memory、GitNexus 读取统一有效配置；全局指导、Skills 与原生 Trellis 入口共享职责和授权边界。
- Trellis 保持唯一任务、工件和最终检查来源；审查分别报告 Spec/Standards，检查通过不自动授权提交或归档。
- `grill-me` 保持显式、无状态访谈；`grill-with-docs` 处理获授权规划中的未决问题；已确认需求不重复访谈。
- 交互安装菜单支持多选（`1` Codex / `2` Cursor / `3` Claude / `4` MiniMax / `5` WorkBuddy）；仅选择含 Cursor 时询问 project-root。
- `agents` 支持 `--document-name` 与 `--no-hooks-feature`（Claude 全局规则路径）。
- `agents` 只更新指导文档，保留原生设置和有效 override；hooks 按受管身份合并并保留外部处理器，原生信任审核由宿主负责。

### 修复

- `config-check.sh` 不再把嵌套 MCP TOML 节误报为服务器名。
- 修正文档中的 MCP 内容说明、配置路径和运行时依赖。
- Codex MCP 合并解析合法 TOML 形式并保留无关配置；WorkBuddy 支持 JSONC，keep 模式保持原字节。
- 同名目录替换/迁移校验实际 Skill 身份，阻止别名冲突和误删独立能力；无效父目录不再隐藏嵌套 Skill。
- 原生实现、审查、继续、复盘和 GitNexus 入口不再强制重复规划、固定全量检查、写入或自动 Git 动作。

> 本节记录尚未发布的工作区变更；`manifest.yaml` 版本仍为 `3.0.0`。
