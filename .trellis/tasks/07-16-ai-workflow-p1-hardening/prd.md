# Harden AI workflow runtime and quality gates

## Goal

把现有 AI 工作流从“提示词约定为主”加固为可执行、可验证的工程契约，同时保持 Trellis 为唯一状态机、六个能力 Skill 不新增平行工作流。

## Requirements

1. Recallium 默认使用已确认的生产 HTTPS MCP 地址 `https://www.59005046.xyz:8102/mcp`；不得默认通过公网明文 HTTP 传输项目记忆，安装器必须拒绝非本机的不安全 HTTP URL。
2. 为 Trellis task 提供机器可执行的 readiness/completion 检查，覆盖 PRD、复杂任务设计/计划、curated context、验收项和质量证据；不直接分叉 Trellis 状态机。
3. 提供 Codex/Cursor/Claude 均可调用的平台无关 `workflow-check` 入口；宿主 Skill 只做适配。
4. 将 `config/defaults.yaml` 与项目 `hogen-codex.yaml` 的合并结果变成可被运行时消费的统一输出；每个公开配置键必须有明确消费者，否则删除。
5. 增加完整工作流 E2E 与 CI，覆盖 Skill 校验、安装器测试、Shell 语法和至少 Linux/macOS 运行环境。
6. 修正文档、版本、许可证和诊断输出中已经确认的不一致，但不增加新的业务 Skill。
7. 保留当前工作区已有修改，不混入或清理其他 active task 的成果。

## Non-goals

- 不引入第二套 task、PRD、Spec 或状态机。
- 不自动部署 Recallium、Trellis 或其他外部服务。
- 不在未经授权时 commit、push、发布或归档其他任务。

## Acceptance Criteria

- [x] 不安全的远端 Recallium HTTP 配置不会被安装器静默写入；安全策略有自动化测试。
- [x] workflow readiness/completion 检查可在不改变 task 状态的情况下返回明确非零状态与缺失证据。
- [x] 平台无关质量入口可运行现有全部验证，并输出机器可判定结果。
- [x] effective config 有统一命令/模块输出，schema 中每个键都有消费者或被移除。
- [x] 至少一条临时项目 E2E 覆盖 planning → readiness → implementation evidence → completion gate。
- [x] CI 定义覆盖 Linux/macOS；本地完整测试、Skill 校验、Shell/Python 静态检查通过。
- [x] README、MCP 说明、版本/变更记录、许可证归属和 config-check 输出一致。

## Confirmed Decisions

- Recallium 生产 MCP 地址为 `https://www.59005046.xyz:8102/mcp`，作为 Codex/Cursor 模板的安全默认值。
- `http://localhost`、`http://127.0.0.1` 和 `http://[::1]` 可用于本机开发；其他明文 HTTP URL 必须拒绝。
- 其余优化保持现有架构：Trellis 是唯一状态机，新增能力采用平台无关检查器和宿主适配，不新增业务 Skill。

## Notes

- 用户已授权优化并实施，但实现必须在 PRD 与设计确认后按 Trellis 进入执行阶段。
- GitNexus 主索引不包含隐藏目录 `.trellis/`；Trellis 内核结论需要源码验证，不能只依赖图谱。
