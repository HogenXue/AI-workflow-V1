# Codex Ultimate v3 设计

## 目标

在本仓库维护一套可长期演进的 Codex Skill 源码包。它以个人开发习惯作为默认行为，并允许每个目标仓库通过根目录 `hogen-codex.yaml` 覆盖必要项。

第一期覆盖核心开发闭环：历史上下文、代码影响分析、规格设计、代码审查、调试、发布。它不包含 Figma、iOS、小程序或特定业务系统的专属 Skill；这些留作后续增量模块。

## 设计原则

- 使用中文沟通；对不确定性和未执行的操作明确说明。
- 保持修改最小、可追溯、可验证；不借机重构无关代码。
- 让 Skill 的 `name` 和 `description` 准确描述触发场景，正文保持精简。
- 将详细规则、可复用工件和确定性检查从 `SKILL.md` 分离到资源目录。
- 避免硬编码 EGM 的索引规模、URI、路径或工具版本；通过项目配置和运行时能力检测处理差异。
- 工具不可用时明确降级，不伪造影响分析、测试、发布或提交结果。

## 仓库结构

```text
CodexTamplate/
├── AGENTS.md
├── manifest.yaml
├── config/
│   ├── defaults.yaml
│   └── project-config.schema.yaml
├── skills/
│   ├── memory/
│   ├── gitnexus/
│   ├── openspec/
│   ├── review/
│   ├── debugging/
│   └── release/
├── scripts/
│   ├── install.sh
│   └── validate-all-skills.py
└── docs/superpowers/specs/
    └── 2026-07-10-codex-ultimate-v3-design.md
```

每个 `skills/<name>/` 目录都包含：

```text
SKILL.md
agents/openai.yaml
references/
templates/
examples/
scripts/
```

目录仅包含本 Skill 有实际用途的非空资源。`templates/` 放可复制的输出骨架，`examples/` 放真实触发输入和预期产物，`scripts/` 放稳定且可重复执行的辅助检查。

## 全局 AGENTS.md

根目录 `AGENTS.md` 控制在约 30 行，只定义跨项目的行为边界：

- 中文优先、简单优先、外科式修改。
- 复杂任务先说明计划、假设、取舍和验证方式。
- 不虚报测试、部署、重启、提交或工具分析结果。
- 接口变化说明契约、影响方与文档同步。
- 完成时报告修改、验证、结果及未完成事项。
- 优先使用已安装的适用 Skill；项目级规则优先于全局默认。

功能开发、缺陷处理、审查、发布以及 GitNexus 规则均由对应 Skill 承担，不在 `AGENTS.md` 重复展开。

## 配置模型

配置按以下顺序合并，后者覆盖前者的同名叶子节点：

1. 包内 `config/defaults.yaml`：个人默认工作流。
2. 目标仓库根目录 `hogen-codex.yaml`：项目级覆盖。

配置不得自动向父目录或子目录探测，避免跨仓库误继承。Skill 在执行具体流程前读取这两层配置；如果项目文件不存在，则只使用默认值。

默认配置覆盖语言、变更范围、脏工作区保护、验证报告、复杂变更规格要求和工具能力检测。项目覆盖可设置例如：

- EGM：GitNexus 影响分析和提交前变更检测为严格模式。
- iOS：指定 Xcode scheme、模拟器和构建/测试命令。
- 小程序：指定 CloudBase 或微信相关约束。

配置 schema 定义允许的顶级键、值类型和合并规则，并为未知键输出可读警告而非静默忽略。

## Skill 职责

| Skill | 触发与职责 | 关键资源 |
| --- | --- | --- |
| `memory` | 处理历史决策、长期上下文、完成结论与重要学习。 | 读写安全、检索与记录模板。 |
| `gitnexus` | 进行架构理解、影响评估、worktree 安全、提交前变更检测。 | 能力检测、影响分析和降级流程。 |
| `openspec` | 为中大型改动创建需求、设计、RFC、API 与数据库契约。 | 规格模板和变更分类指南。 |
| `review` | 审查正确性、安全、兼容性、性能和回归风险。 | 分级清单与审查报告模板。 |
| `debugging` | 按复现、定位、最小修复、验证闭环排查问题。 | 证据记录与调试报告模板。 |
| `release` | 管理版本、变更说明、发布前检查、发布后验证和回滚信息。 | 发布检查表与回滚模板。 |

Skill 不使用 `hogen-` 前缀。各 Skill 的 YAML 元数据使用短且领域明确的名称，并在 `description` 中写清触发用语和工作上下文。

## 安装与升级

`manifest.yaml` 记录 v3 版本、Skill 清单、默认启用项和兼容性要求。

`scripts/install.sh` 提供：

- 默认 `--dry-run`，先展示目标、操作及冲突。
- `--link`，以符号链接安装至 Codex 的 Skill 目录，适合持续升级。
- `--copy`，复制稳定副本，适合锁定版本的环境。
- `--replace`，受控覆盖同名的既有 Skill；先将每个冲突目录备份到带时间戳的备份位置，全部替换成功后才清理临时备份。
- 未提供 `--replace` 时，检测到同名目标即退出并给出处理建议。

仓库更新后，链接安装自然使用新内容；副本安装必须重新执行安装脚本。安装脚本不修改目标项目的 `AGENTS.md` 或 `hogen-codex.yaml`。本包有意复用 `memory`、`gitnexus`、`openspec`、`review`、`debugging`、`release` 这六个已存在的 Skill 名称，因此实际替换必须显式使用 `--replace`。

## 校验与错误处理

`scripts/validate-all-skills.py` 校验：

- 每个 Skill 的目录、YAML frontmatter、命名和触发描述。
- `agents/openai.yaml` 与 `SKILL.md` 元数据的一致性。
- 必需资源目录、相对引用和无占位符的示例。
- 默认配置、项目配置 schema 与样例覆盖的可解析性。
- 安装脚本 dry-run 和冲突保护行为。

校验器的 `--root PATH` 始终指向 Skill 包根目录；需要校验其他仓库的覆盖文件时，使用 `--project-root PATH`。默认项目根目录与包根目录相同。无论项目根目录为何处，`config/defaults.yaml` 和 `config/project-config.schema.yaml` 都从包根目录读取，而仅 `hogen-codex.yaml` 从项目根目录读取；项目覆盖会进行嵌套合并，并在合并前后拒绝未知键或类型不匹配。

没有 GitNexus、OpenSpec、Memory 或其他可选工具时，对应 Skill 只可执行安全替代步骤：报告缺失能力、使用普通只读检查或要求用户提供必要信息。任何验证失败或未执行都必须写入最终结果。

## 验收标准

- 根目录 `AGENTS.md` 保持约 30 行，且不包含 EGM 专属数据或过期工具路径。
- 六个独立 Skill 均有正确元数据和完整资源目录。
- 默认配置可被根目录 `hogen-codex.yaml` 以合并方式覆盖。
- 安装脚本在 dry-run、link、copy、冲突和 replace-with-backup 五种路径可预测且不静默覆盖。
- 校验脚本能发现无效 YAML、缺失目录、过时 metadata、错误引用与配置错误。
- 每个 Skill 至少有一个触发示例和一个可复用输出模板或确定性检查脚本。

## 不在本期范围

- Figma、iOS、微信小程序、CloudBase、MCP 集成等领域专属 Skill。
- 自动发布到 marketplace 或封装为 Codex Plugin。
- 目标项目业务代码、基础设施或运行态服务的任何修改。

## 验证记录（2026-07-11）

在临时虚拟环境 `/tmp/codextamplate-validator-venv`（PyYAML 6.0.3）中实际执行：

```bash
/tmp/codextamplate-validator-venv/bin/python -m unittest discover -s tests -v
/tmp/codextamplate-validator-venv/bin/python scripts/validate-all-skills.py
PATH="/tmp/codextamplate-validator-venv/bin:$PATH" bash -c 'set -e; for validator in skills/*/scripts/validate.sh; do "$validator"; done'
bash -n scripts/install.sh skills/*/scripts/validate.sh
git diff --check
```

结果：30 个单元测试全部通过；根校验器输出六个 `OK: <skill>`；六个 Skill wrapper 均通过；Bash 语法检查和 diff 空白检查均通过。负向测试已覆盖外部 `--project-root` 中未知的嵌套覆盖键、配置类型不匹配、空 templates/examples/scripts、示例 TODO/TBD、未引用 `$<skill>` 的 default prompt、缺失/未加引号的 interface 字段，以及缺失 PyYAML 时的可操作错误提示；正向测试覆盖从包根读取 defaults/schema 并与外部项目覆盖进行嵌套合并。
