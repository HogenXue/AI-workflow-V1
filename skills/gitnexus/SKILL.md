---
name: gitnexus
description: "Analyze code relationships, change impact, worktrees, commit scope, and release branches. Use before changing symbols, reviewing blast radius, working with Git worktrees, or validating affected flows before a commit."
---

# GitNexus

读取 skill 目录上两级的 `config/defaults.yaml`（Codex 安装后为 `~/.agents/config/defaults.yaml`；源码仓库则为包根 `config/defaults.yaml`），再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。默认配置不存在时使用内置安全默认值 `require_impact_analysis_before_symbol_edit: false` 并继续执行，不把可选 config 组件缺失当成故障。

检测当前会话是否具备 GitNexus 图谱、影响分析与 `detect_changes` 能力。若有效配置中的 `change_policy.require_impact_analysis_before_symbol_edit` 为 `true`，修改 symbol 前必须分析调用者与受影响流程；为 `false` 时，仅对跨模块、接口/数据契约、高风险或陌生调用链的修改做前置分析，局部低风险改动可用普通代码阅读与 `rg`。提交前运行可用的 `detect_changes`。对 HIGH 或 CRITICAL 风险，报告影响范围、证据、未知项及需要的人工确认。

GitNexus 不可用时，明确说明限制，只使用只读的普通 Git 与 `rg` 替代；不要虚报图谱、影响分析或提交前检查已执行。详见 [影响与 worktree](references/impact-and-worktree.md)、[影响报告模板](templates/impact-report.md) 与 [示例](examples/assess-symbol-change.md)。

GitNexus 不负责需求澄清、项目管理或业务代码实现；它只提供影响分析与 Git 安全证据。
