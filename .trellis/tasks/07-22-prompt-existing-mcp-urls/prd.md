# Prompt before replacing existing MCP URLs

## Goal

让一键交互安装在处理 Codex 或 Cursor 的 URL 型 MCP 配置前，先识别已有 URL，并由用户明确选择沿用或替换，避免静默覆盖现有服务地址。

## Requirements

- 仅调整 `scripts/install.sh` 的 TTY 一键安装向导；组件级命令及其显式参数合同保持兼容。
- 根据用户选择的宿主读取实际目标配置：Codex 使用 `${CODEX_HOME:-$HOME/.codex}/config.toml`，Cursor 使用 `$HOME/.cursor/mcp.json`。
- 对已有且使用 URL 的 MCP 逐项展示服务名和当前 URL，并询问沿用还是替换。
- 用户选择沿用时，后续合并不得覆盖该 MCP；用户选择替换时，要求输入新 URL，并由现有 URL 安全校验负责验证。
- 对尚未配置的 URL 型 MCP，保持可选新增行为；不得强制要求输入 URL。
- 选择 Codex + Cursor 时分别尊重两端现有配置；不能用一端的选择静默覆盖另一端。
- 非 URL 型 MCP（例如 command/args）不进入 URL 替换提示，继续由现有 MCP 冲突策略处理。
- 非 TTY 与组件级调用保持确定性，不新增阻塞式提示。
- 保留 preview-first、backup-before-write、失败回滚和现有配置不静默覆盖的安全边界。

## Acceptance Criteria

- [x] Codex 已有 URL 型 MCP 时，一键安装会显示当前 URL，并可选择沿用或替换。
- [x] Cursor 已有 URL 型 MCP 时，一键安装会显示当前 URL，并可选择沿用或替换。
- [x] 选择沿用后，目标 MCP URL 保持不变；选择替换后，仅对应 MCP URL 更新为用户输入值。
- [x] 同一宿主内不同 MCP 可独立选择沿用或替换。
- [x] Codex + Cursor 模式下，两端决策互不污染。
- [x] 没有已有 URL 时，向导仍允许可选新增 Mem0 URL。
- [x] 组件级安装、非交互安装和非 URL 型 MCP 行为无回归。
- [x] 相关自动化测试、Shell 语法检查和 Trellis 质量检查通过。

## Non-goals

- 不改变 MCP fragment 的默认地址或新增 MCP 服务类型。
- 不重写底层配置格式，不迁移已有 command/args 型 MCP。
- 不自动提交、推送或修改用户机器上的真实 Codex/Cursor 配置。
