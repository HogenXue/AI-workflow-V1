# Integrate Grill Me with Trellis

## Goal

将 Grill Me 收编为本仓库维护、可自动调用的 Skill，并按明确职责接入工作流：Grill Me 仅澄清复杂需求，OpenSpec 管理行为 Spec，Trellis 管理 task 级 PRD/计划、状态与 Journal，TDD 管理实现，GitNexus 管理影响分析与 Git 收尾。

## Requirements

- 在 `skills/grill-me/` 提供一个仓库内维护的 Skill fork；不再依赖用户机器上手工安装的上游副本作为来源。
- Skill 的 frontmatter 必须允许 Codex 隐式调用；不得保留上游的 `disable-model-invocation: true`。
- Grill Me 只在复杂或需求不清的请求中作为可选前置访谈；简单修改不自动触发。
- Grill Me 每次只提出一个问题；能通过代码库、现有 task 或 project context 回答的问题必须先自行检索，而不是询问用户。
- Grill Me 的访谈结论交给 OpenSpec 维护为正式 Spec；不写入 Trellis task 的 PRD，也不创建平行的 Spec。
- OpenSpec Spec 确认后，才取得用户对创建 Trellis task 的同意。Trellis task 维护 task 级 PRD/计划、状态、Journal 和对该 Spec 的引用；不得复制需求、场景或验收文档，也不得维护第二份任务清单。
- 实施阶段由 TDD 约束测试先行；GitNexus 在修改前用于影响分析、在提交前用于变更范围与 Git 收尾检查。
- `manifest.yaml` 和现有 skills 安装脚本必须将 `grill-me` 分发到目标的 skills 目录；已有目标副本继续由 `--replace` 的备份/覆盖机制处理。
- `trellis/AGENTS.global.md` 必须说明上述自动路由和交接边界，供 `scripts/install.sh agents --apply` 覆盖安装到目标 `AGENTS.md`。
- 新 Skill 必须符合 `scripts/validate-all-skills.py` 的包结构和 metadata contract；安装与路由行为须有自动化测试。
- 仓库内 `openspec` Skill 在检测到 `.trellis/` 时必须采用 trellis-first 边界：仅维护需求、场景和验收 Spec，不创建 OpenSpec 任务清单，并将 task 级 PRD/计划交给 Trellis。

## Acceptance Criteria

- [ ] `manifest.yaml` 包含 `grill-me`，`scripts/install.sh skills --copy --replace` 将其安装到目标目录。
- [ ] `skills/grill-me/` 通过 `python3 scripts/validate-all-skills.py --skill grill-me`，并具备完整的 `agents`、`references`、`templates`、`examples`、`scripts` 目录。
- [ ] `grill-me` 的声明允许隐式调用，描述准确覆盖新功能和需求不清的 planning 场景。
- [ ] 全局 AGENTS 模板规定“复杂需求时 Grill Me → OpenSpec Spec → Trellis task/Journal → TDD → GitNexus”的职责和顺序；GitNexus 明确为跨执行期能力，而非末尾串行步骤。
- [ ] 安装测试断言新 Skill 在 manifest 安装集合中；Skill contract 测试断言自动调用设置与 Trellis 交接文本存在。
- [ ] 现有用户未提交的 README、agents installer 和 agents installer 测试改动保持其原有语义；本任务的改动只在必要位置追加或改用未修改文件。

## Non-goals

- 不在本 task 中运行安装器写入真实的 `~/.codex`，也不删除当前已存在的全局 `grill-me` 副本。
- 不修改 Trellis managed project block，也不让 Trellis task 重复 OpenSpec 的需求、场景或验收内容。
- 不自动启动 task 或自动实施代码；仍以用户对最终 PRD 的明确确认作为启动门槛。
- 不实现对上游 `mattpocock/skills` 的自动同步；本仓库 fork 是后续分发的唯一来源。

## Risks and constraints

- `trellis/AGENTS.global.md` 是全局模板，规则必须足够精确，不能让简单修改也进入长访谈。
- 已有工作区包含未提交的 README、agents installer 和相关测试修改；实现时不得覆盖或回退它们。
- Skill 验证器要求每个 bundled Skill 都具备完整目录结构、`agents/openai.yaml` 和可用 examples/scripts；最小 fork 也必须遵守该契约。

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- 这是跨 Skill、manifest、全局模板、安装与测试的复杂 task；必须在启动前完成 `design.md` 和 `implement.md`。
