# Matt Pocock Skills 与 Trellis 冲突评估

## 核对范围

- 说明页：<https://www.aihero.dev/skills-setup-matt-pocock-skills>
- 上游仓库：<https://github.com/mattpocock/skills>
- 核对提交：`e9fcdf95b402d360f90f1db8d776d5dd450f9234`（2026-07-14）
- 上游许可证：MIT，Copyright (c) 2026 Matt Pocock
- 当前仓库共 40 个 Skill：17 engineering、5 productivity、4 misc、2 personal、4 deprecated、8 in-progress。

## 结论

不能把整套 Skills 原样安装到本项目。Matt 主流程是
`grill-with-docs → to-spec → to-tickets → implement → code-review → commit`，而 Trellis 已拥有
PRD、Task、Design、Plan、Research、执行、质量检查和提交门槛。直接叠加会产生两个工件树、
两个路由器和两个生命周期所有者。

## 冲突矩阵

| 上游 Skill/类别 | 与 Trellis 的冲突 | 处理结论 |
| --- | --- | --- |
| `setup-matt-pocock-skills` | 写 `AGENTS.md`/`CLAUDE.md` 和 `docs/agents/`，另建 issue tracker、标签和 domain 配置根 | 禁止直接运行；项目规则仍由 AGENTS + `.trellis/` 管理 |
| `ask-matt` | 把请求路由到 Matt 主流程，绕开 Trellis Phase 1–3 | 不安装 |
| `to-spec` | 在 issue tracker 发布第二份 PRD/Spec | 不安装；使用当前 Trellis `prd.md` |
| `to-tickets` | 创建 GitHub/Linear/`.scratch` tickets 与阻塞图，复制 Trellis task/plan | 不安装 |
| `implement` | 自己驱动 TDD、review、测试和 commit，接管 Trellis Phase 2/3 | 不安装 |
| `code-review` | 并行子代理审查，重复项目原生 `trellis-check` | 不安装；质量阶段只用 `trellis-check` |
| `wayfinder` | 用 issue map、子 issue、claim/close 状态建立第二套大型工作状态机 | 不安装 |
| 上游 `tdd` | 与本包同名；且把 refactor 交给 code-review，和本包 RED→GREEN→REFACTOR/Trellis 边界不同 | 保留本包 `tdd`，不覆盖 |
| 上游 `grill-me` | 与替换目标相反，且是无代码库的无状态访谈器 | 删除本包旧 Skill，不安装上游同名项 |
| `git-guardrails-claude-code` | 写 Claude hooks，可能覆盖 Trellis 管理的 hooks | 不安装到本项目 |
| deprecated / in-progress / personal | 不稳定、已弃用或个人环境专用，会扩大自动触发面 | 整类排除 |

## 可适配但不能原样接管

| 能力 | 适配边界 |
| --- | --- |
| `grill-with-docs` + `grilling` + `domain-modeling` | 只替代 Trellis Phase 1.1，PRD 仍唯一；把上游 `CONTEXT.md`/ADR 目标改为 `.trellis/spec/domain/` 与 `.trellis/spec/decisions/` |
| `research` | 研究必须写当前 Trellis task 的 `research/`；是否使用子代理服从宿主与用户授权 |
| `diagnosing-bugs` | 只能作为诊断方法；任务、修复和证据仍归 Trellis，调用链先用 GitNexus，行为修复走本包 TDD |
| `triage` | 最多用于外部 issue 入口；不能把 triage 状态当成 Trellis task 状态，也不能自动转入上游 `implement` |
| `improve-codebase-architecture` / `codebase-design` | 可作为设计词汇和候选报告；选中变更后必须回到 Trellis task，并按风险运行 GitNexus |
| `prototype` | 只能回答一个设计问题；产物默认可丢弃，结论回写 Trellis PRD/Design，跳过 TDD 需用户同意 |
| `handoff` | 可作会话桥接，但只能引用 Trellis 工件，不成为任务状态或第二份规格 |

## 可选的低冲突能力

`resolving-merge-conflicts`、`writing-great-skills`、`teach` 在显式调用、遵守项目 Git/文件边界时
可以独立使用。`migrate-to-shoehorn`、`scaffold-exercises`、`setup-pre-commit` 与本项目目标无关，
即使无直接状态机冲突，也不应因“整套安装”进入默认能力面。

## 本次落地

采用“一个主流程 + 精选能力”方案：Trellis 继续拥有完整生命周期；用经过边界适配的
`grill-with-docs` 替换 `grill-me`，并引入 `diagnosing-bugs`、`codebase-design`、
`resolving-merge-conflicts`。保留本包 `tdd`，不安装上游同名版本；可选 `prototype` 暂不加入。
不上游整套，不运行其 setup，不新增 `docs/agents/` 或 `.scratch/`。
