# EGM 专属规则（V7-EGM · Trellis 兼容）

> 版本：V7-EGM · 叠加于 CodexTamplate 全局规则。
> 冲突时以本文为准。若 EGM 已启用 Trellis，应将本文件内容追加在根目录 `AGENTS.md` 的 Trellis Managed Block 之外。

---

## 项目结构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- uni-app：移动端。

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

- 存在 `.trellis/` 时：新功能、较大重构或需求不明确 → Trellis Brainstorm，一问一答澄清并生成 PRD 后再实现；预计少于约 5 分钟的简单修改可直接实现并做针对性验证。
- 不存在 `.trellis/` 时：规范驱动变更 → `$openspec`。
- 会话延续与项目记忆 → `$memory`。
- 探索代码、改 symbol 前、提交前 → `$gitnexus`（项目名 **EGM**）。
- Trellis 项目中不启动 Superpowers 或 OpenSpec 的完整工作流，避免重复 Task、PRD、Design 或 Spec。

---

## Git 提交格式

版本号与风格参考 `egm_docs/RELEASE_NOTE.md`：

必须以以下格式提交commit

```md
## 版本号 - YYYY-MM-DD
- 模块路径 -> 功能入口：变更点。
- 具体行为、规则调整或修复说明。
```

---

## 文档

- Trellis 已启用：新的需求、设计、实施计划和研究资料写入 `.trellis/tasks/`；长期可复用规则写入 `.trellis/spec/`；跨会话记录写入 `.trellis/workspace/`。
- `egm_docs/spec/` 与 `docs/superpowers/` 是历史参考目录。除修订历史说明外，不在其中创建新的 OpenSpec/Superpowers 任务产物，也不移动或复制其既有正文。
- 历史资料的统一入口是 `.trellis/tasks/archive/` 中的相关任务，或迁移任务的 `research/legacy-document-register.md`；新任务按需把原文件作为 research context 链接。
- 文档修改须说明原因、影响范围及关联代码。

---

## 服务重启

允许Agent 自动启动或重启本地服务

```bash
# 修改 egm_backend 后
./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务

# 修改 egm_vue 后
./egm_docs/Shells/auto_startup.sh restart-vue
```

## 代码修改

修改之前都需要提示是否同意才能继续

---

## Trellis 项目补充

- 本节来自 `trellis/AGENTS.project.md`，用于 EGM 已启用 Trellis 时的项目级补充；不要编辑 Trellis Managed Block 内的内容。
  - 项目特有的构建、测试、部署、数据处理与安全规则维护在本文件。
  - 长期、可复用的项目标准维护在 `.trellis/spec/`。
  - 当前任务的 PRD、研究、实现与检查产物维护在 `.trellis/tasks/`。
  - 跨会话工作记录维护在 `.trellis/workspace/`。
  - 简单且需求明确的任务直接走 Trellis；复杂、跨模块或需求不明确时，Codex 将 `$grill-me` 视为 Phase 1.1 的唯一访谈实现，使用后不要再加载 `trellis-brainstorm`。
  - Codex 质量阶段使用项目原生 `trellis-check`。
  - 无 active task 时先遵守 Trellis 的建 task 同意门槛；用户选择不创建 task 后，简单修改才可直接实现并验证。
  - 不要在本项目同时启动第二套完整工作流。
  - TDD 是 Trellis 执行阶段的实现方法；Karpathy Guidelines 是横切约束。
  - 本项目已要求 symbol 修改前使用 GitNexus；Trellis Check 通过后再做提交前范围检查。
- <!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **EGM** (24006 symbols, 42609 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/EGM/context` | Codebase overview, check index freshness |
| `gitnexus://repo/EGM/clusters` | All functional areas |
| `gitnexus://repo/EGM/processes` | All execution flows |
| `gitnexus://repo/EGM/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
