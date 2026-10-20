---
name: setup-matt-pocock-skills
description: "Configure Matt Pocock engineering Skills for this repository while preserving its existing workflow, including Trellis task and documentation ownership."
---

# Setup Matt Pocock Skills

为当前项目配置 Matt Skills 的任务来源和领域文档入口。先识别项目工作流，再写配置；
setup 本身不创建开发任务、需求、领域术语或架构决定。它不负责安装或更新全局 Skills。

## 1. 识别项目与宿主

读取项目适用的 `AGENTS.md`、`CLAUDE.md`、已有 `## Agent skills`、`docs/agents/`
和实际任务/领域文档。若有 `.trellis/`，读取 `.trellis/workflow.md`、相关 spec 和当前
task（若存在）。Git remote 只用于了解仓库，不能据此把 Trellis 改成 GitHub Issues。

识别当前宿主：

- Codex：配置入口是项目 `AGENTS.md`，即使同目录已有 `CLAUDE.md` 也优先用 AGENTS。
  只有 CLAUDE 时，创建最小 AGENTS，指向需要共享的现有规则与新配置；避免复制整份规则。
- Claude：使用现有 `CLAUDE.md`；没有时复用现有 AGENTS，或明确选择需要创建的入口。
- 其他宿主：沿用已发现、确实会加载的项目规则入口；宿主无法确定且会影响写入时才询问。

规则追加在 Trellis/GitNexus 等 managed block **外**，保留其内容。

## 2. 确定任务与文档归属

### Trellis 项目

使用 [Trellis 任务配置](templates/issue-tracker-trellis.md) 和
[Trellis 领域文档配置](templates/domain-trellis.md) 作为 `docs/agents/issue-tracker.md`
和 `docs/agents/domain.md` 的起点，按实际目录和现有规则调整：

- Trellis 是任务、PRD、Design/Plan、执行、质量检查、Journal 和归档的唯一工作流。
- 领域术语使用 `.trellis/spec/domain/`，持久决定使用 `.trellis/spec/decisions/`。
  已有不同 Trellis 路径时使用项目事实来源。
- Matt Skills 只提供当前阶段的方法。访谈交给适配版 `grill-with-docs`，行为实现用适配版
  `tdd`，诊断与模块设计服从当前 task；质量阶段使用原生 `trellis-check`。
- `/to-spec` 等输出落到当前 PRD/计划；`/implement-spec` 交回 Trellis 执行流程。
  setup 不启用它的独立分支、合并、PR 或多代理调度流程。
- Trellis 的 task 状态保持原样，不把 triage label 当作新状态机。即使安装了 `triage`，
  也不为 Trellis 创建远端标签或第二套 `triage-labels.md`。

若已有配置指向 GitHub Issues、`.scratch/`、根目录 `GLOSSARY.md` 或 `docs/adr/`，
先指出归属冲突，再在本次适配授权范围内更新配置指针。保留原有内容；旧文档需要迁移时
单独列出待迁移位置，避免未经核对搬移、删除或复制出两份事实来源。

### 非 Trellis 项目

保持项目既有的 tracker、需求来源、术语和决定目录，不自动初始化 `.trellis/`。
在 `docs/agents/issue-tracker.md` 记录 tracker 的实际读写方式，在 `domain.md` 记录
已有文档的读取约定。只有现有规则无法决定 tracker 或文档归属时，才一次询问一个必要问题。
若项目已有配置文档，用入口指针复用它们。远端标签变更需要用户明确选择该操作。

## 3. 预览并写入

展示拟修改文件及关键归属变化。已有明确适配授权且没有未决选择时继续；尚有必要选择时
等待答案。覆盖已有文件前创建 `<原名称>.<UTC时间戳>.bak`，同秒备份追加序号避免覆盖。

在选定的项目规则入口中增加或原位更新以下配置入口，保留其他自定义小节：

```markdown
## Agent skills

Before using a Matt engineering Skill, read `docs/agents/issue-tracker.md` and
`docs/agents/domain.md`. Follow their repository-specific artifact locations and workflow
mappings when a Skill describes upstream defaults.

### Issue tracker

Use this repository's existing workflow. See `docs/agents/issue-tracker.md`.

### Domain docs

Use this repository's canonical domain documentation. See `docs/agents/domain.md`.
```

Trellis 项目把两句说明改为明确的 Trellis 归属。重复运行时更新现有段落；检查已有
`Triage labels` 段落，必要时改为遵循 Trellis 原生状态，并保留旧文件供人工迁移。
非 Trellis 项目只保留实际需要的 tracker/label 约定。

## 4. 验证并交回项目工作流

确认宿主会发现规则入口、所有配置指针指向真实位置或项目明确认可的按需创建位置，
managed block 与用户其他规则保持完整；重复运行不会新增重复段落。
Trellis 配置只引用一套任务/需求与领域文档，没有新建并行 Spec 或执行流程。

报告修改、备份、未迁移旧文档和当前工作流入口。其他项目、全局 AGENTS、MCP、hooks、
Git 操作以及第三方 Skills 的安装不属于 setup 的写入范围。
