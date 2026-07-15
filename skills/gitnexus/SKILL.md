---
name: gitnexus
description: "Analyze high-risk code impact, worktrees, and commit scope when graph evidence is needed."
---

# GitNexus

如果 skill 目录上两级存在 `config/effective_config.py`，优先运行该 helper，并通过
`--project-root <目标仓库>` 获取已经校验和合并的配置。helper 不存在时，再读取 skill
目录上两级的 `config/defaults.yaml`（Codex 安装后为 `~/.agents/config/defaults.yaml`；
源码仓库则为包根 `config/defaults.yaml`），并读取目标仓库根目录的 `hogen-codex.yaml`
（若存在）；项目值覆盖默认值。默认配置不存在时使用内置安全默认值
`require_impact_analysis_before_symbol_edit: false` 并继续执行，不把可选 config 组件
缺失当成故障。

检测当前会话是否具备 GitNexus 图谱、影响分析与 `detect_changes` 能力。若有效配置中的 `change_policy.require_impact_analysis_before_symbol_edit` 为 `true`，修改 symbol 前必须分析调用者与受影响流程；为 `false` 时，仅对跨模块、接口/数据契约、删除或迁移、高风险或陌生调用链的修改做前置分析，局部低风险改动可用普通代码阅读与 `rg`。

`detect_changes` 仅在以下情况运行：项目规则显式要求、已进行 GitNexus 影响分析、变更跨模块或涉及公共接口/数据契约/删除迁移，或用户明确要求。低风险提交默认执行标准 Git 范围检查（`git status`、`git diff --check`、`git diff --stat`）和相关测试，不为提交而自动建立索引或运行 GitNexus。

对 HIGH 或 CRITICAL 风险，报告影响范围、证据、未知项及需要的人工确认。

GitNexus 不可用时，明确说明限制，只使用只读的普通 Git 与 `rg` 替代；不要虚报图谱、影响分析或提交前检查已执行。详见 [影响与 worktree](references/impact-and-worktree.md)、[影响报告模板](templates/impact-report.md) 与 [示例](examples/assess-symbol-change.md)。

GitNexus 不负责需求澄清、项目管理或业务代码实现；它只提供影响分析与 Git 安全证据。
