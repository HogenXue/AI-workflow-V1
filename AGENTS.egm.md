# EGM 专属规则（V6-EGM）

> 版本：V6-EGM · 叠加于 CodexTamplate `AGENTS.md` V6
> 冲突时以本文为准。EGM 仓库部署：复制为根目录 `Agents.md`。

---

## 项目结构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- uni-app：移动端。

---

## OpenSpec（强制）

以下变更必须先走 `$openspec`：

- 业务功能变更。
- 行为变更。
- 接口变更。
- 非平凡重构。
- 跨模块修改。

流程：

- `openspec/specs/` 为基线事实来源。
- `openspec/changes/` 存放增量变更（含 `proposal.md`、`design.md`、`tasks.md`）。
- 先更新规范，再小步实现，最后测试验证；代码与规范一致后再归档。

---

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

---

## Skill 默认策略

- 探索代码、改符号前、提交前 → `$gitnexus`（项目名 **EGM**）。
- 规范驱动变更 → `$openspec`。
- 会话延续与项目记忆 → `$memory`。

---

## Git 提交格式

提交前须执行 `$gitnexus` 的 `detect_changes()`。

版本号与风格参考 `egm_docs/RELEASE_NOTE.md`：

```md
## 版本号 - YYYY-MM-DD
- 模块路径 -> 功能入口：变更点。
- 具体行为、规则调整或修复说明。
```

---

## 文档

- 目录：`egm_docs/spec/`
- 文件名：`文档名-作者-YYYYMMDD.md`
- 修改须说明原因、影响范围及关联代码。

---

## 服务重启

禁止 Agent 自动启动或重启本地服务。修改后端或前端后，仅在任务结束时提醒用户自行执行：

```bash
# 修改 egm_backend 后
./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务

# 修改 egm_vue 后
./egm_docs/Shells/auto_startup.sh restart-vue
```

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
