# AI 协作规则

## 1. 基本规则

- 始终使用中文回复。
- 不确定时明确说明，不假装确定。
- 简单优先，只做用户要求的事情。
- 外科式修改，只修改必要代码。
- 不主动重构、格式化或优化无关代码。
- 复杂任务先说明：
  - 计划。
  - 假设。
  - 取舍。
  - 验证方式。

禁止：

- 声称未执行的测试已经完成。
- 声称未执行的部署、重启、提交已经完成。

------------------------------------------------------------------------

# 2. 通用开发原则

## Bug 修复

流程：

    复现
    
    ↓
    
    定位
    
    ↓
    
    修复
    
    ↓
    
    验证

## 功能开发

流程：

    明确目标
    
    ↓
    
    设计方案
    
    ↓
    
    实现
    
    ↓
    
    测试

## 接口变化

必须：

- 明确接口契约变化。
- 同步影响方。
- 更新相关文档。

## 重构

要求：

- 保持已有行为。
- 控制修改范围。
- 提供验证结果。

------------------------------------------------------------------------

# 3. 代码设计原则

优先：

- 简单方案。
- 小步修改。
- 可维护性。
- 向后兼容。

避免：

- 无需求重构。
- 过度设计。
- 引入无必要依赖。

推荐分层：

    Controller
    
    ↓
    
    Application
    
    ↓
    
    Domain
    
    ↓
    
    Infrastructure

职责：

Controller：

负责接口接入。

Application：

负责业务流程编排。

Domain：

负责核心业务规则。

Infrastructure：

负责数据库、消息、外部服务等技术实现。

------------------------------------------------------------------------

# 4. Skill 使用规则

项目提供通用 AI 能力：

    ./Users/hogenxue/.codex/skills/

包括：

## OpenSpec

负责：

- 需求变更管理。
- 设计流程。
- 规范维护。

规则：

    ./Users/hogenxue/.codex/skills/openspec/SKILL.md

------------------------------------------------------------------------

## GitNexus

负责：

- 代码理解。
- 调用关系分析。
- 修改影响评估。

规则：

    ./Users/hogenxue/.agents/skills/gitnexus/SKILL.md

------------------------------------------------------------------------

## Memory

负责：

- 长期上下文。
- 经验沉淀。
- 历史决策。

规则：

```
./Users/hogenxue/.agents/skills/memory/SKILL.md
```

------------------------------------------------------------------------

# 5. 任务执行原则

开始任务：

先判断：

- 是否需要设计。
- 是否需要规范变更。
- 是否需要历史经验。

复杂任务：

优先：

    分析
    
    ↓
    
    方案
    
    ↓
    
    实施
    
    ↓
    
    验证

不要：

直接修改大量代码。

------------------------------------------------------------------------

# 6. 文档规范

项目文档遵循：

- 清晰。
- 可追溯。
- 与代码同步。

文档修改：

必须说明：

- 修改原因。
- 影响范围。
- 关联代码。

------------------------------------------------------------------------

# 7. Git 规范

提交信息应该包含：

- 版本或变更标识。
- 修改内容。
- 影响说明。

推荐格式：

```md
## 版本号 - 日期

- 修改模块：
- 变更内容：
- 影响说明：
```

禁止：

- 无意义提交信息。
- 隐藏重大修改。

------------------------------------------------------------------------

# 8. 自动执行规则

允许执行开发相关命令。

执行前：

确认命令目的。

执行后：

说明：

- 执行了什么。
- 结果如何。
- 是否存在风险。

------------------------------------------------------------------------

# 9. 测试与验证

完成任务后：

说明：

- 修改内容。
- 验证方式。
- 测试结果。
- 未完成事项。

不要：

把推测当成验证结果。

------------------------------------------------------------------------

# 10. 修改原则

每次修改必须：

- 来源明确。
- 范围可控。
- 结果可验证。

优先：

    小修改
    
    ↓
    
    快速验证
    
    ↓
    
    持续迭代

避免：

    一次性大规模修改

<!-- gitnexus:start -->

# GitNexus — Code Intelligence

This project is indexed by GitNexus as **EGM** (23082 symbols, 40857 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

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
