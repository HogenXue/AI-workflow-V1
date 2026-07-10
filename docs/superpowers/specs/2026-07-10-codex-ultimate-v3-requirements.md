# Codex Ultimate v3 需求

## 问题与范围

现有 `Agents 2.md` 将通用协作规则、工作流和 EGM 专属 GitNexus 内容混在一起，难以维护和迁移。Codex Ultimate v3 要将通用约束压缩为根目录 `AGENTS.md`，并提供可独立触发、可安装和可校验的六个核心 Skill。

本期仅交付 `memory`、`gitnexus`、`openspec`、`review`、`debugging` 和 `release`。不交付 Figma、iOS、小程序、CloudBase、Plugin 或 marketplace 发布。

## 用户故事

- 作为个人开发者，我希望默认采用中文、最小改动、证据化验证的工作流，并能让单个仓库覆盖必要规则。
- 作为维护者，我希望六个 Skill 独立演进，并通过脚本验证其 metadata、目录和配置不失效。
- 作为安装者，我希望复用标准 Skill 名称，明确地备份并替换已有同名 Skill，而不是静默覆盖或留下半完成状态。

## 验收标准

1. 当 Codex 在任意项目工作时，根目录 `AGENTS.md` 应提供约 30 行的中文优先、最小修改、诚实验证和复杂任务说明规则，而不包含 EGM 专属路径或统计数据。
2. 当任务匹配长期上下文、影响分析、规格设计、审查、调试或发布时，系统应有名称分别为 `memory`、`gitnexus`、`openspec`、`review`、`debugging`、`release` 的独立 Skill 可触发。
3. 当一个 Skill 被加载时，它应有有效的 `SKILL.md`、`agents/openai.yaml`、`references/`、`templates/`、`examples/` 和 `scripts/`，并将详细内容置于资源目录而非堆入正文。
4. 当目标仓库存在根目录 `hogen-codex.yaml` 时，Skill 应将其与包内 `config/defaults.yaml` 合并，且项目值覆盖默认值；不存在时应只使用默认值。
5. 当可选工具不可用时，Skill 应报告缺失能力并改走明确的安全替代流程，不得声称已完成对应工具分析或验证。
6. 当运行安装器且未指定 `--replace` 时，安装器应默认 dry-run，并在发现同名 Skill 时停止且不改动目标目录。
7. 当运行安装器并指定 `--replace` 时，安装器应先备份每个冲突目录；任何替换失败时应恢复已替换的目录；全部替换成功后才完成安装。
8. 当运行校验器时，它应检测无效 frontmatter、错误 metadata、缺失资源目录、无效配置和失效相对引用，并以非零状态返回失败。

## 约束

- Skill 名称不得使用 `hogen-` 前缀，且有意复用当前标准名称。
- 安装目标默认是 Codex 的 Skill 目录；脚本必须支持测试时显式传入临时目标目录。
- 校验工具使用 Python 3 和 PyYAML；安装器使用 Bash。
- 当前工作区不是 Git 仓库；实现阶段不得隐式初始化仓库或声称已提交。
