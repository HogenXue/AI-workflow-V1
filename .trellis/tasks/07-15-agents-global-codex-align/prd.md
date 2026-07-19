# Align AGENTS.global.md with Codex config

## Goal

更新 `trellis/AGENTS.global.md`，并入本机现装 AGENTS 中的 **Recallium 短协议**，补齐 memories / multi_agent 分层；然后对本机执行 `agents --apply`（先备份）使 `~/.codex/AGENTS.md` 与模板一致。

## Background

- Codex MCP：`gitnexus`、`recallium`；无 `mem0`
- Features：`memories=true`、`multi_agent=true`；无 `hooks=true`
- `~/.codex/AGENTS.md` 与仓库模板分叉（英文 Recallium 短段 + 长篇 Karpathy）
- Cursor `cursor-merge` 从同一 `AGENTS.global.md` 动态生成 `.mdc`

## Requirements

1. 将现装 AGENTS 顶部 **Recallium 短协议**收敛进模板（先搜、按类型、稳定结论后 store、遵循已发现 procedure/preference）——中文表述，与 Memory skill 一致；**不**整篇粘贴英文 Karpathy。
2. 明确分层：Codex `features.memories` vs Recallium MCP vs Memory Skill；仅当存在 `mem0` MCP 时走 Mem0。
3. 补一句 `multi_agent`：与 Trellis 子代理 / Grill Me 的边界（短）。
4. 保留配置边界：不擅自整换 config.toml/MCP/hooks；不假定 Trellis MCP。
5. 执行 `bash scripts/install.sh agents --apply --agents-home ~/.codex`（或等价），确保备份现装 `AGENTS.md`；hooks 特性按现有 agents 脚本增量处理。
6. 体量保持短；中文为主。

## Out of scope

- 安装/配置 mem0 MCP 或强制 `hooks=true`（除非 apply 脚本既有 hooks 增量）
- 重写 Skill 包
- 把整篇英文 Karpathy 并入全局 AGENTS

## Acceptance Criteria

- [x] `AGENTS.global.md` 含 Recallium 短协议 + memories 分层 + multi_agent 边界
- [x] 不含整篇 Karpathy 英文稿
- [x] `agents --apply` 后 `~/.codex/AGENTS.md` 与模板一致，且存在备份
- [x] 与 Memory skill / 配置边界段落不矛盾
- [x] 检查 PASS（措辞「按职责分层」；hooks 增量属既有 apply 行为）

## Decisions

| # | Topic | Choice |
| --- | --- | --- |
| 1 | 范围 | **C**：改模板 + apply；并入现装 Recallium 短协议 |

## Open questions

无阻塞项（Recallium 吸收强度：短协议，非旧文全文）。

## Addendum — Graphify integration (2026-07-19)

用户已在本机安装 Graphify。优化两个根目录模板，使其在不改变 GitNexus、Memory 或 Trellis
职责的前提下，提供一致的图谱使用边界。

### Requirements

1. `AGENTS.global.md` 将 Graphify 定义为已有本地图谱时的可选概览与关系检索能力；要求回到源文件核实
   `INFERRED` / `AMBIGUOUS` 结论。
2. `AGENTS.project.md` 说明 Graphify 不替代 GitNexus 的正式影响分析，也不替代 Trellis 质量证据或
   Recallium / Memory 的长期项目记忆。
3. 两个模板都禁止在未获当前任务或项目规则授权时自动生成/更新图谱、安装 Graphify 配置或 hook、提交
   `graphify-out/` 产物。

### Acceptance criteria

- [x] 两个模板有一致的 Graphify 职责和边界，且 GitNexus 仍是正式影响分析入口。
- [x] 回归测试覆盖上述边界。

## Addendum — Global Graphify installation (2026-07-19)

用户要求将 Graphify Skill 写入全局 `~/.agents/skills/`，并将安装行为纳入统一一键安装入口。

### Requirements

1. 新增显式 `graphify` 安装组件：默认 dry-run，`--apply` 仅调用已安装的 Graphify CLI，将 Skill
   安装到用户级 Agent Skills 根目录。
2. Codex 的推荐完整安装应包含该组件；不把第三方 Graphify Skill 纳入本包 `manifest.yaml`，也不把它
   写入项目目录。
3. 若 Graphify CLI 缺失或外部安装失败，清晰报错，不静默跳过。
4. `graphify-out/` 是本地图谱生成物，默认忽略；显式 `git add -f` 才允许作为项目产物提交。

### Acceptance criteria

- [x] `graphify --apply` 路由到 `graphify install --platform agents`，并有回归测试。
- [x] Codex 一键完整安装与 README 明确包含全局 Graphify Skill。

## Notes

- Lightweight：PRD-only 即可；用户审阅后 `task.py start`
