---
name: openspec
description: "Create and maintain requirements, technical designs, RFCs, API contracts, and database contracts for medium or large changes. Use before architecture-heavy, cross-module, data-model, or interface changes."
---

# OpenSpec

先读取 skill 目录上两级的 `config/defaults.yaml`（安装后如 `~/.agents/config/defaults.yaml`，源码仓库则为包根 `config/defaults.yaml`），再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。配置文件无效或包含未知项时，报告限制并仅采用可解析的默认值。

按[变更分类](references/change-classification.md)确认是否需要规格：中大型、跨模块、数据模型或接口变更先定义问题、范围、验收条件、设计、风险和验证，再开始实施。小型且局部的改动可说明不建规格的理由，并保留最小验证计划。

检测 OpenSpec CLI 和目标仓库既有规格的可用性。可用时遵循项目的规格目录和校验命令，创建或维护需求、技术设计、RFC 与 API/数据库契约；不可用时使用[变更规格模板](templates/change-spec.md)在仓库约定的位置编写 Markdown，并明确未执行 CLI 校验。

若项目存在 `.trellis/`，采用 trellis-first 边界：OpenSpec 是需求、场景和验收的唯一行为 Spec 来源，但不维护任务清单。将已确认 Spec 交给 Trellis；Trellis 维护 task 级 PRD/计划、状态和 Journal，并且只引用该 Spec，不能复制其需求、场景或验收内容。若 OpenSpec CLI 的默认流程会生成任务工件，使用项目已有的自定义 schema；没有该 schema 时只维护行为 Spec，不执行会生成第二份任务清单的步骤。

OpenSpec 不可用时，只执行人工规格与只读文件检查；不得声称已创建 CLI 变更、已校验规格或已获得工具分析结果。交付时列出变更边界、未覆盖项、已执行验证与未执行步骤。参见[API 变更示例](examples/design-api-change.md)。
