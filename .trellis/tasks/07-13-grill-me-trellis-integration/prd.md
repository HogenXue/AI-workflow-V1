# Integrate Grill Me with Trellis

## Goal

将 Grill Me 与 TDD 收编为本仓库维护、可自动调用的 Skills，同时保持 Trellis 为唯一工作流。Codex 用 Grill Me 替代 Phase 1.1 的原生访谈，质量检查继续由 `trellis-check` 单独负责。

## Requirements

- 删除仓库内 OpenSpec 与 Review Skill 及其 manifest 分发项；OpenSpec/Review 只允许保留在遗留迁移说明和安装器测试中。
- Grill Me 在新功能、复杂或需求不清的请求中作为 Codex 的 Phase 1.1 访谈实现；简单且需求完整的修改不自动触发。
- Grill Me 的访谈结论写入 Trellis task 的 PRD，包含问题、范围、非目标、验收标准和未决项；不得创建平行 Spec 或任务清单。
- 用户确认 PRD 并授权实施后，Trellis 才能执行 `task.py start`。
- 实施阶段由 TDD 约束测试先行；GitNexus 按项目配置或高风险/跨模块变更做前置影响分析，并在提交前用于变更范围与 Git 收尾检查。
- TDD 相关测试全绿后必须经过原生 `trellis-check` 的质量、架构、安全与可维护性检查；不再安装或调用独立 Review Skill。
- 同一 Trellis 阶段只能有一个负责人：运行 Grill Me 后不再运行 `trellis-brainstorm`；质量阶段只运行 `trellis-check`。
- TDD 是 Trellis 执行阶段的实现方法，Karpathy Guidelines 是横切约束；二者都不创建第二套状态机或工件。
- `manifest.yaml` 和现有 skills 安装脚本必须不再分发 OpenSpec 或 Review；已有目标副本不由本任务直接删除。
- Codex App 的默认包根为 `~/.agents`：Skills 安装到 `~/.agents/skills`，共享配置安装到 `~/.agents/config`；若 `~/.codex/skills` 有同名副本，只能显式备份后移走。
- 新增的 TDD Skill 与 Grill Me Skill 必须符合 `scripts/validate-all-skills.py` 的包结构和 metadata contract。
- 已有用户未提交的 README、agents installer 和 agents installer 测试改动保持其原有语义；本任务的改动只在必要位置更新。

## Acceptance Criteria

- [x] 仓库不存在 `skills/openspec/SKILL.md` 或 `skills/review/SKILL.md`，manifest 与普通安装预览均不包含二者。
- [x] 全局和项目 Trellis 模板明确“复杂需求时 Grill Me → Trellis PRD/计划 → TDD → Trellis Check → GitNexus”的职责和顺序。
- [x] 全局和项目模板明确 Codex 的单阶段负责人规则，不会重复运行 Grill Me/`trellis-brainstorm`，也不会加载独立 Review Skill。
- [x] Grill Me 和 TDD 文档不再要求或引用 OpenSpec。
- [x] OpenSpec 只允许出现在安装器的遗留迁移说明与测试中，不再作为活动工作流或分发项。
- [x] Skill validator、相关单元测试、shell 语法检查和临时目录安装预览通过。
- [x] 安装器默认目标与文档统一为 `~/.agents/skills` / `~/.agents/config`，并支持显式 `--prune-other-root` 解决双目录发现冲突。
- [x] `agents --apply` 在 `config.toml` 不是普通文件时不写入任何目标文件；配置更新失败时恢复已有 `AGENTS.md`，或移除本次新建的 `AGENTS.md`。

## Non-goals

- 不直接删除 `~/.agents/skills` 或 `~/.codex/skills` 下的已安装副本；后续通过显式 `--prune-legacy` / `--prune-other-root` 先备份再清理目标目录。
- 不自动启动 task、提交、推送或修改 Trellis managed project block。
- 不替换现有的 Memory、GitNexus、Release 或 Karpathy Skills。

## Risks and constraints

- 仓库存在用户未提交的 README、agents installer 和相关测试改动；实现时不得覆盖或回退它们。
- Trellis 是唯一持久化工作流；不得通过删除 OpenSpec 引入另一套替代的 Spec 或任务框架。
