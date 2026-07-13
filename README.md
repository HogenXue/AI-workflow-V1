# AI-workflow-V1

可安装的 AI 协作 Skill 包：6 个独立 Skill、全局 AGENTS 模板，以及共享默认配置（`config/`）。

GitHub：[HogenXue/AI-workflow-V1](https://github.com/HogenXue/AI-workflow-V1)

## 包含内容

| 组件            | 说明                                                                         |
| ------------- | -------------------------------------------------------------------------- |
| **Skills**    | `memory`、`gitnexus`、`release`、`karpathy-guidelines-zh`、`grill-me`、`tdd` |
| **AGENTS 模板** | [trellis/AGENTS.global.md](trellis/AGENTS.global.md)：跨项目通用规则与 Skill 路由 |
| **config/**   | 默认工作流配置；项目可用 `hogen-codex.yaml` 覆盖                                         |

Trellis 是项目工作流；6 个 Skill 按阶段或能力增强它。Codex 用 Grill Me 实现 Phase 1.1、用 TDD 实现行为代码；质量门由原生 `trellis-check` 负责。

## 前置条件

- macOS / Linux，Bash
- 可选：`python3 >= 3.10` 与 PyYAML（仅校验脚本需要）

```bash
python3 -m pip install -r requirements-dev.txt
```

## 获取源码

```bash
git clone https://github.com/HogenXue/AI-workflow-V1.git
cd AI-workflow-V1
```

## 安装

安装统一入口：`scripts/install.sh <skills|agents|config>`。每个组件独立预览、写入和备份；安装 `agents --apply` 到 Codex 目录时仅会增量确保 `[features].hooks = true`，不会覆盖其他全局配置。

| 组件       | 写入范围                      | 默认行为            |
| -------- | ------------------------- | --------------- |
| `skills` | manifest 中的 Skill 目录      | dry-run         |
| `agents` | `<agents-home>/AGENTS.md` | dry-run；已有文件先备份 |
| `config` | 指定的配置目录                   | dry-run         |

`skills` 与 `config` 默认 **copy**（独立副本，不依赖源码目录）；本地开发可用 **link** 实时同步。

### 预览（不写文件）

```bash
bash scripts/install.sh skills --dry-run --target ~/.agents/skills
```

### Codex App（推荐目录）

```bash
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
```

### Cursor

```bash
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
```

### Codex CLI 独立目录（仅在不使用 App 共享目录时）

```bash
bash scripts/install.sh skills --copy --replace --target ~/.codex/skills
```

Codex 可能同时发现 `~/.agents/skills` 与 `~/.codex/skills`。同一组 Skill 只选择一个目录；本包对 Codex App 默认使用 `~/.agents/skills`，对应配置目录是 `~/.agents/config`。安装器发现另一目录存在同名 Skill 时会警告；只有显式 `--prune-other-root` 才会先备份再移走另一目录中的本包同名 Skill。

旧版本安装的 OpenSpec 与 Review 不在当前 manifest 中，普通更新不会删除它们。先预览，再用显式 `--prune-legacy` 将它们移动到备份目录；若两处都曾安装，需要分别处理：

```bash
bash scripts/install.sh skills --dry-run --prune-legacy --target ~/.agents/skills
bash scripts/install.sh skills --copy --replace --prune-legacy --prune-other-root --target ~/.agents/skills

bash scripts/install.sh skills --dry-run --prune-legacy --target ~/.codex/skills
bash scripts/install.sh skills --copy --replace --prune-legacy --target ~/.codex/skills
```

### 本地开发（link）

在源码仓库内改 Skill 后即时生效，但删除源码目录会导致安装失效：

```bash
bash scripts/install.sh skills --link --replace --target ~/.agents/skills
```

### 安装全局 AGENTS 模板

以下命令会替换 AI 工具目录中的 `AGENTS.md`；已有文件会先备份。对 Codex 目录执行 `--apply` 时，脚本会增量确保 `config.toml` 中的 `[features].hooks = true`（Codex 0.129+），保留 MCP、插件和其他配置：

```bash
bash scripts/install.sh agents --dry-run --agents-home ~/.codex
bash scripts/install.sh agents --apply --agents-home ~/.codex
```

### 显式安装默认配置

配置独立安装，避免意外修改现有配置。目标已存在时，需同时给出 `--replace`：

```bash
bash scripts/install.sh config --dry-run --target ~/.agents/config
bash scripts/install.sh config --copy --replace --target ~/.agents/config
```

### 脚本参数

| 参数       | 说明                                                                                       |
| -------- | ---------------------------------------------------------------------------------------- |
| `skills` | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--prune-legacy`、`--prune-other-root`、`--target PATH`、`--backup-dir PATH` |
| `agents` | 支持 `--dry-run` / `--apply`、`--agents-home PATH`、`--backup-dir PATH`；`--codex-home` 是兼容别名 |
| `config` | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--target PATH`、`--backup-dir PATH`       |

## 安装后目录结构

各组件独立安装。例如：

```text
~/.agents/
├── config/                 # 仅执行 config 组件后存在
└── skills/
    ├── memory/
    ├── gitnexus/
    ├── release/
    ├── grill-me/
    ├── tdd/
    └── karpathy-guidelines-zh/
```

Skill 内读取默认配置：`../../config/defaults.yaml`（与源码仓库 `CodexTamplate/config/` 路径一致）。

## 更新与重装

在源码目录拉取最新后，对实际使用的目标重新 copy 安装。Codex App 只更新 `~/.agents/skills`；不要再把同一组 Skill 复制到 `~/.codex/skills`：

```bash
git pull
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
```

安装完成后重启 Codex App 或新开 Cursor 会话。

## AGENTS 规则用法

全局规则模板位于 [trellis/AGENTS.global.md](trellis/AGENTS.global.md)，可通过 `scripts/install.sh agents` 安装到 AI 工具目录。项目根目录的 `AGENTS.md` 由 Trellis 初始化和更新时维护，不应以全局模板直接覆盖。

项目专属规则（如 EGM 的分层、Git 格式、`egm_docs` 等）应在**该项目仓库**内维护 `Agents.md`；Trellis 项目将这些规则追加到 Trellis Managed Block 之外。GitNexus 流程由对应 Skill 承担，索引块由项目内 GitNexus CLI 注入。

## 项目级配置覆盖

在**目标项目**根目录创建 `hogen-codex.yaml`，与包内 `config/defaults.yaml` 合并（项目值优先）。示例：

```yaml
change_policy:
  require_impact_analysis_before_symbol_edit: true
verification:
  require_spec_for_complex_change: true
```

校验合并结果：

```bash
python3 scripts/validate-all-skills.py --project-root /path/to/your-project
```

## 校验 Skill 包

在仓库根目录：

```bash
python3 scripts/validate-all-skills.py
```

## Trellis 集成（可选）

本包提供一个可选的 Trellis 兼容迁移包，详情见 [trellis/README.zh-CN.md](trellis/README.zh-CN.md)。

- 存在 `.trellis/` 的项目：Trellis 是唯一工作流。Codex 用 `grill-me` 实现 Phase 1.1，用 TDD 实现需要测试证明的行为变化，由原生 `trellis-check` 负责质量检查。GitNexus 仅在高影响编辑前和提交前做影响/范围检查。
- 不存在 `.trellis/` 的项目：继续使用该项目既有的实施工作流。
- 迁移工具默认仅预览；执行 `agents --apply` 时只会增量启用 `~/.codex/config.toml` 的 `[features].hooks`，不会覆盖 MCP、插件或其他配置。

## MCP 与外部依赖

本包**不包含** MCP 服务器配置，需在各 IDE 中单独设置：

- **memory**：Recallium / Mem0（见 `skills/memory/references/memory-backends.md`）
- **gitnexus**：GitNexus MCP；EGM 等项目需先索引
- **release**：按 Skill 说明使用 CLI 或 Markdown 模板

Skill 不可用时须明确说明限制，不得虚报已执行工具结果。
