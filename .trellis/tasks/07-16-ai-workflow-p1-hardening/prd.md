# Harden AI workflow runtime and quality gates

## Goal

把现有 AI 工作流从“提示词约定为主”加固为可执行、可验证的工程契约，同时保持 Trellis 为唯一状态机；选择性引入能力型 Skill，但不新增平行工作流。

## Requirements

1. Recallium 默认使用已确认的生产 HTTPS MCP 地址 `https://www.59005046.xyz:8102/mcp`；不得默认通过公网明文 HTTP 传输项目记忆，安装器必须拒绝非本机的不安全 HTTP URL。
2. 为 Trellis task 提供机器可执行的 readiness/completion 检查，覆盖 PRD、复杂任务设计/计划、curated context、验收项和质量证据；不直接分叉 Trellis 状态机。
3. 提供 Codex/Cursor/Claude 均可调用的平台无关 `workflow-check` 入口；宿主 Skill 只做适配。
4. 将 `config/defaults.yaml` 与项目 `hogen-codex.yaml` 的合并结果变成可被运行时消费的统一输出；每个公开配置键必须有明确消费者，否则删除。
5. 增加完整工作流 E2E 与 CI，覆盖 Skill 校验、安装器测试、Shell 语法和至少 Linux/macOS 运行环境。
6. 修正文档、版本、许可证和诊断输出中已经确认的不一致，但不增加新的业务 Skill。
7. 保留当前工作区已有修改，不混入或清理其他 active task 的成果。
8. 用 Trellis 兼容的 `grill-with-docs` 替换 `grill-me`：继续作为 Codex Phase 1.1 的唯一访谈器，同时仅把领域术语写入 `.trellis/spec/domain/`、把难以逆转且存在真实权衡的决定写入 `.trellis/spec/decisions/`；需求与验收仍只写当前 Trellis PRD。
9. 选择性引入并适配 `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts`；保留本包现有 `tdd`，不安装上游同名版本。所有新增能力必须归属于当前 Trellis task，不能接管 task 状态、质量阶段或 Git 授权。
10. 评估 Matt Pocock 当前整套 Skills 与 Trellis 的冲突，形成可执行的保留、适配和禁止清单；未经单独确认不得安装整套 Skills，也不得引入 `to-spec`、`to-tickets`、`implement`、`code-review` 或第二套 issue/task 状态机。

## Non-goals

- 不引入第二套 task、PRD、Spec 或状态机。
- 不自动部署 Recallium、Trellis 或其他外部服务。
- 不运行 `setup-matt-pocock-skills`，不创建 `docs/agents/`、`.scratch/` 或外部 issue 作为 Trellis task 的替代品。
- 不安装上游整套 Skills；本次只维护经过 Trellis 边界适配的精选能力集。
- 不加入参考方案中的可选 `prototype`，除非用户后续单独确认。
- 不在未经授权时 commit、push、发布或归档其他任务。

## Acceptance Criteria

- [x] 不安全的远端 Recallium HTTP 配置不会被安装器静默写入；安全策略有自动化测试。
- [x] workflow readiness/completion 检查可在不改变 task 状态的情况下返回明确非零状态与缺失证据。
- [x] 平台无关质量入口可运行现有全部验证，并输出机器可判定结果。
- [x] effective config 有统一命令/模块输出，schema 中每个键都有消费者或被移除。
- [x] 至少一条临时项目 E2E 覆盖 planning → readiness → implementation evidence → completion gate。
- [x] CI 定义覆盖 Linux/macOS；本地完整测试、Skill 校验、Shell/Python 静态检查通过。
- [x] README、MCP 说明、版本/变更记录、许可证归属和 config-check 输出一致。
- [x] manifest、安装器、文档和测试只暴露 `grill-with-docs`，不再安装或路由到 `grill-me`。
- [x] `grill-with-docs` 明确保持 Trellis PRD/Task/Design/Plan 的唯一所有权，领域文档不会成为第二份需求或规格。
- [x] `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts` 已作为 Trellis 当前任务内的能力引入，且不会自动创建任务、审查、提交或推送。
- [x] Matt Pocock 40 个上游 Skill 的冲突评估已记录，整套安装被明确判定为不适合直接叠加到 Trellis。
- [x] 本机实际生效的 `~/.codex/AGENTS.md` 与 `~/.agents/skills` 已切换到 `grill-with-docs`；被覆盖或删除的旧文件均保留 UTC 时间戳 `.bak` 备份。
- [x] Memory Skill、MCP 模板和本机 `~/.codex/config.toml` 均使用 Recallium HTTPS 地址；本机配置修改前已生成 UTC 时间戳 `.bak` 备份。

## Confirmed Decisions

- Recallium 生产 MCP 地址为 `https://www.59005046.xyz:8102/mcp`，作为 Codex/Cursor 模板的安全默认值。
- `http://localhost`、`http://127.0.0.1` 和 `http://[::1]` 可用于本机开发；其他明文 HTTP URL 必须拒绝。
- 其余优化保持现有架构：Trellis 是唯一状态机，新增能力采用平台无关检查器和宿主适配，不新增业务 Skill。
- `grill-with-docs` 采用 Matt Pocock 上游 `e9fcdf95b402d360f90f1db8d776d5dd450f9234` 的 grilling/domain-modeling 语义，并增加 Trellis 持久化边界。
- 精选能力集为本包既有能力加 `grill-with-docs`、`diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts`；上游 `tdd` 因同名和流程语义冲突不安装。
- `.trellis/spec/domain/` 只保存项目领域词汇，`.trellis/spec/decisions/` 只保存满足难以逆转、缺少上下文会令人意外、且经过真实权衡三个条件的决定；Trellis PRD 仍是需求和验收的唯一来源。

## Notes

- 用户已授权优化并实施，但实现必须在 PRD 与设计确认后按 Trellis 进入执行阶段。
- GitNexus 主索引不包含隐藏目录 `.trellis/`；Trellis 内核结论需要源码验证，不能只依赖图谱。
- 当前网络环境把 Recallium 域名解析到 `198.18.0.22`，HTTPS 握手以 unexpected EOF 结束；
  因此本任务只验证配置与传输策略，不声称外部 Recallium 服务已经连通。外部服务部署本就属于 Non-goals。
