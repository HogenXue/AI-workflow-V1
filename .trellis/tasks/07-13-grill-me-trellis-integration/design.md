# Design: Grill Me、OpenSpec 与 Trellis 的职责链路

## Context

上游 Grill Me 的 `SKILL.md` 只有显式 `/grilling` 入口，并声明 `disable-model-invocation: true`。本包需要一个仅用于复杂需求的自动访谈入口。行为 Spec 属于 OpenSpec，Trellis 不复写需求、场景或验收，而是管理 task 级 PRD/计划、生命周期和 Journal。

## Ownership boundaries

| Concern | Owner | Persisted location |
| --- | --- | --- |
| 复杂需求的一问一答澄清 | `grill-me` Skill | OpenSpec handoff |
| 正式需求、场景、验收与变更 Spec | OpenSpec | 项目既有 OpenSpec 目录 |
| task 创建同意、task 级 PRD/计划、状态、执行追踪与 Journal | Trellis | `.trellis/tasks/<task>/` 与 workspace |
| 测试先行的实现循环 | TDD | 代码与测试 |
| 修改前影响分析、提交前范围与 Git 检查 | GitNexus | 代码图谱与 Git 工作区 |
| 安装分发 | `manifest.yaml` + `scripts/install-skills.sh` | 目标 skills 目录 |
| 全局自动路由 | `trellis/AGENTS.global.md` | 目标 `AGENTS.md` |

## Routing state machine

```text
complex or unclear requirement
  -> load grill-me (optional)
  -> inspect repository + ask one question
  -> repeat until the decision tree is resolved
  -> OpenSpec creates or updates the canonical Spec
  -> ask consent to create Trellis task
  -> Trellis records the Spec reference, task-level PRD/plan, status, and Journal
  -> TDD implements from the Spec
  -> GitNexus analyzes impact before edits and validates Git scope before commit
```

Simple changes skip Grill Me and can enter OpenSpec only when their specification risk warrants it. An explicit `$grill-me` request produces an OpenSpec handoff, not a Trellis PRD.

## Skill package design

Create `skills/grill-me/` as a standard bundled Skill package:

- `SKILL.md` declares a precise automatic-invocation description and the Trellis-aware interview protocol. It omits `disable-model-invocation`.
- `agents/openai.yaml` uses the standard quoted interface format, references `$grill-me`, and declares `allow_implicit_invocation: true`.
- `references/trellis-handoff.md` holds the cross-tool state-machine detail so the main Skill remains concise.
- `templates/prd-requirements.md` supplies the handoff headings OpenSpec turns into the canonical Spec.
- `examples/new-feature-session.md` demonstrates the persisted interview-to-confirmation sequence without placeholder text.
- `scripts/validate.sh` runs the repository validator for this skill only.

The fork keeps the upstream behavior that questions are sequential and repository facts should be discovered before querying the user; its added behavior is the OpenSpec handoff plus Trellis status/Journal boundary.

## Distribution and compatibility

`manifest.yaml` is the sole list consumed by `scripts/install-skills.sh`, so adding `grill-me` there makes `scripts/install.sh skills --copy|--link --replace` distribute it along with the existing skills. The installer already backs up conflicts when `--replace` is supplied; no installer code change is required.

The global template gets a narrowly scoped route under “工作流路由”. It must direct only complex or unclear work to the optional Grill Me interview, name OpenSpec as the canonical behavior-Spec owner, and prevent Trellis from duplicating that behavior while retaining task-level planning and Journal.

## Verification strategy

1. Extend manifest/install tests to include `grill-me` in the expected distribution set.
2. Add a focused package contract test for the Skill frontmatter, implicit-invocation agent policy, and required Trellis handoff phrases.
3. Run the bundled Skill validator with PyYAML installed; run the relevant unittest modules and shell syntax checks.
4. Run installer dry-runs against a temporary target to verify the new manifest entry appears without touching the user’s real Codex home.
