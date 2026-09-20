# Design: Grill Me、Trellis、TDD、Trellis Check 与 GitNexus 职责链路

## Ownership boundaries

| Concern | Owner | Persisted location |
| --- | --- | --- |
| 用户显式发起的想法澄清 | `grill-me` Skill | 无状态；不直接持久化 |
| 需求、场景、验收与未决项 | Trellis | `.trellis/tasks/<task>/prd.md` |
| task 级计划、状态与 Journal | Trellis | `.trellis/tasks/<task>/` 与 workspace |
| 测试先行的实现循环 | TDD | 代码与测试 |
| 质量、架构、安全与可维护性检查 | Trellis Check | Trellis task 检查记录与 diff 证据 |
| 高影响修改前的影响分析、提交前范围检查 | GitNexus | 代码图谱与 Git 工作区 |
| 安装分发 | `manifest.yaml` + `scripts/install-skills.sh` | 目标 skills 目录 |
| 全局自动路由 | `trellis/AGENTS.global.md` | 目标 `AGENTS.md` |
| 显式访谈入口 | `grill-me` | 无状态对话；不直接持久化 |

## Conflict resolution

- Trellis 保持唯一状态机和工件所有者。
- Codex 用 Grill Me 实现 Phase 1.1；它与 `trellis-brainstorm` 是替代关系，不是串联关系。
- TDD 是执行方法，可与 Trellis 的上下文加载并存，不创建独立 task 或计划。
- 质量检查只由原生 `trellis-check` 负责；不再安装独立 Review Skill。
- Karpathy Guidelines、Memory、GitNexus 与 Release 是横切能力，不拥有 Trellis 阶段。
- Codex App 的 canonical package root 是 `~/.agents`；另一发现根中的本包同名 Skill 只能通过显式、可回滚的安装选项迁移。
- Codex hooks 采用事件级合并：只管理 Trellis `SessionStart` 条目和对应脚本，保留其他事件及处理器。
- 上游最新 Grill Me 提供行为基线；本包把底层提问方法内置进单一 Skill，并只加入 Trellis 交接和宿主适配。

## Routing state machine

```text
user explicitly invokes grill-me for a loose idea
  -> inspect available facts without creating or changing task state
  -> ask the current decision frontier in dependency-aware rounds
  -> stop branches that require a prototype or external evidence
  -> user confirms the shared-understanding summary
  -> Trellis creates or updates the task and persists confirmed conclusions when authorized
  -> Trellis enters task.py start
  -> GitNexus analyzes impact before high-impact edits
  -> TDD implements from the PRD
  -> trellis-check is the sole quality check after relevant verification passes
  -> GitNexus validates Git scope before high-impact commits
```

Simple changes skip Grill Me. `$grill-me` 仅在用户显式调用时启动；会话保持无状态，确认共同理解后再由 Trellis 持久化结论并继续现有 task 和验证规则。

## Removal boundary

The repository owns only its packaged skills and templates. Removing OpenSpec and Review means deleting their source packages and preventing future installer distribution. It does not directly delete independently installed global copies; explicit `--prune-legacy` and `--prune-other-root` back them up before removal from a selected discovery root.
