# EGM AI 协作规则（V6-EGM）

> 版本：V6-EGM · 基于 CodexTamplate `AGENTS.md` V6 扩展
> 部署：复制到 EGM 仓库根目录为 `Agents.md`，作为项目级完整规则使用。

---

# 1. 沟通

- 默认使用中文回复（用户另有要求除外）。
- 不确定时明确说明依据和不确定性。
- 不虚构事实，不猜测工具结果。
- 不声称已执行未实际执行的操作（测试、部署、提交、推送、重启等）。

---

# 2. 工作原则

- 优先满足用户目标，而不是展示能力。
- 优先采用最简单、最稳定、最容易维护的方案。
- 外科式修改，只改完成任务所必需的内容。
- 不重构、不优化、不格式化无关代码。
- 保留用户已有修改，未经授权不得覆盖。
- 每一行修改须能追溯到用户需求；默认保持向后兼容。

---

# 3. 复杂任务

复杂任务开始前：

1. 简述目标
2. 给出计划
3. 说明关键假设
4. 说明风险或取舍
5. 实施最小修改
6. 验证结果

简单任务直接执行。

EGM 中以下变更必须先走 `$openspec`：业务功能变更、行为变更、接口变更、非平凡重构、跨模块修改。

---

# 4. Skill Routing

根据任务主动判断是否需要调用 Skill：

| Skill                     | 使用场景               |
| ------------------------- | ------------------ |
| `$memory`                 | 历史上下文、长期记忆、任务延续    |
| `$gitnexus`               | 代码理解、调用链、影响分析、安全修改 |
| `$openspec`               | 功能设计、接口修改、跨模块变更    |
| `$release`                | Release Note、版本说明  |
| `$karpathy-guidelines-zh` | 编码、Review、重构       |

EGM 默认：

- 探索代码、改符号前、提交前 → `$gitnexus`（项目名 **EGM**）。
- 规范驱动变更 → `$openspec`。
- 会话延续与项目记忆 → `$memory`。

优先使用 Skill，不重复实现 Skill 已包含的流程。

---

# 5. Memory

涉及：

- 历史任务
- 项目规则
- 长期决策
- 上下文延续

优先调用 `$memory`。

如果 Memory 不可用：

- 明确说明
- 不伪造检索结果

---

# 6. Git

未经明确要求：

- 不 commit
- 不 push
- 不 merge
- 不 rebase
- 不创建 PR

避免：

- git reset --hard
- git clean
- git push --force

提交前须执行 `$gitnexus` 的 `detect_changes()`，确认变更范围符合预期。

EGM 提交信息格式（版本号与风格参考 `egm_docs/RELEASE_NOTE.md`）：

```md
## 版本号 - YYYY-MM-DD
- 模块路径 -> 功能入口：变更点。
- 具体行为、规则调整或修复说明。
```

---

# 7. 完成任务

完成后说明：

- 修改内容
- 影响范围
- 验证方式与结果
- 已知限制或未完成项（如有）

不要隐瞒未完成事项。

---

# 8. EGM 项目

## 项目结构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- uni-app：移动端。

## OpenSpec 流程

- `openspec/specs/` 为基线事实来源。
- `openspec/changes/` 存放增量变更（含 `proposal.md`、`design.md`、`tasks.md`）。
- 先更新规范，再小步实现，最后测试验证；代码与规范一致后再归档。

## 分层架构

```
Controller → Application → Domain → Infrastructure
```

| 层              | 职责                  |
| -------------- | ------------------- |
| Controller     | 接口接入                |
| Application    | 业务流程编排              |
| Domain         | 核心业务规则              |
| Infrastructure | DB / MQ / RPC 等技术实现 |

## 文档

- 目录：`egm_docs/spec/`
- 文件名：`文档名-作者-YYYYMMDD.md`
- 修改须说明原因、影响范围及关联代码。

## 服务重启

禁止 Agent 自动启动或重启本地服务。修改后端或前端后，仅在任务结束时提醒用户自行执行：

```bash
# 修改 egm_backend 后
./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务

# 修改 egm_vue 后
./egm_docs/Shells/auto_startup.sh restart-vue
```

---

# 9. 优先级

规则优先级（从高到低）：

1. 本文件（EGM 根目录 `Agents.md`）
2. 用户级规则（Cursor Rules / Codex 配置）
3. CodexTamplate 通用 `AGENTS.md` V6

发生冲突时，以 EGM 项目内规则为准。

<!-- gitnexus:start -->

# GitNexus — Code Intelligence

This project is indexed by GitNexus as **EGM** (23337 symbols, 41413 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource                             | Use for                                  |
| ------------------------------------ | ---------------------------------------- |
| `gitnexus://repo/EGM/context`        | Codebase overview, check index freshness |
| `gitnexus://repo/EGM/clusters`       | All functional areas                     |
| `gitnexus://repo/EGM/processes`      | All execution flows                      |
| `gitnexus://repo/EGM/process/{name}` | Step-by-step execution trace             |

## CLI

| Task                                         | Read this skill file                                        |
| -------------------------------------------- | ----------------------------------------------------------- |
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md`       |
| Blast radius / "What breaks if I change X?"  | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?"             | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md`       |
| Rename / extract / split / refactor          | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md`     |
| Tools, resources, schema reference           | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md`           |
| Index, status, clean, wiki CLI commands      | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md`             |

<!-- gitnexus:end -->
