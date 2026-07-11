# AI-workflow-V1

可安装的 AI 协作 Skill 包：5 个独立 Skill、全局 AGENTS 模板，以及共享默认配置（`config/`）。

GitHub：[HogenXue/AI-workflow-V1](https://github.com/HogenXue/AI-workflow-V1)

## 包含内容

| 组件 | 说明 |
| --- | --- |
| **Skills** | `memory`、`gitnexus`、`openspec`、`release`、`karpathy-guidelines-zh` |
| **AGENTS 模板** | [trellis/AGENTS.global.md](trellis/AGENTS.global.md)：跨项目通用规则，兼容 Trellis 路由 |
| **config/** | 默认工作流配置；项目可用 `hogen-codex.yaml` 覆盖 |

OpenSpec、GitNexus 等流程细节在对应 Skill 中，不在 `AGENTS.md` 重复展开。

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

安装统一入口：`scripts/install.sh <skills|agents|config>`。每个组件独立预览、写入和备份；不会因为安装 Skills 或 AGENTS 而顺带覆盖全局配置。

| 组件 | 写入范围 | 默认行为 |
| --- | --- | --- |
| `skills` | manifest 中的 Skill 目录 | dry-run |
| `agents` | `<agents-home>/AGENTS.md` | dry-run；已有文件先备份 |
| `config` | 指定的配置目录 | dry-run |

`skills` 与 `config` 默认 **copy**（独立副本，不依赖源码目录）；本地开发可用 **link** 实时同步。

### 预览（不写文件）

```bash
bash scripts/install.sh skills --dry-run --target ~/.agents/skills
```

### Codex App

```bash
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
```

### Cursor

```bash
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
```

### Codex CLI

```bash
bash scripts/install.sh skills --copy --replace --target ~/.codex/skills
```

### 本地开发（link）

在源码仓库内改 Skill 后即时生效，但删除源码目录会导致安装失效：

```bash
bash scripts/install.sh skills --link --replace --target ~/.agents/skills
```

### 安装全局 AGENTS 模板

以下命令仅替换 AI 工具目录中的 `AGENTS.md`；已有文件会先备份，`config.toml`、MCP、插件和 hooks 不会修改：

```bash
bash scripts/install.sh agents --dry-run --agents-home ~/.codex
bash scripts/install.sh agents --apply --agents-home ~/.codex
```

### 显式安装默认配置

配置独立安装，避免意外修改现有配置。目标已存在时，需同时给出 `--replace`：

```bash
bash scripts/install.sh config --dry-run --target ~/.codex/config
bash scripts/install.sh config --copy --replace --target ~/.codex/config
```

### 脚本参数

| 参数 | 说明 |
| --- | --- |
| `skills` | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--target PATH`、`--backup-dir PATH` |
| `agents` | 支持 `--dry-run` / `--apply`、`--agents-home PATH`、`--backup-dir PATH`；`--codex-home` 是兼容别名 |
| `config` | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--target PATH`、`--backup-dir PATH` |

## 安装后目录结构

各组件独立安装。例如：

```text
~/.agents/
├── config/                 # 仅执行 config 组件后存在
└── skills/
    ├── memory/
    ├── gitnexus/
    ├── openspec/
    ├── release/
    └── karpathy-guidelines-zh/
```

Skill 内读取默认配置：`../../config/defaults.yaml`（与源码仓库 `CodexTamplate/config/` 路径一致）。

## 更新与重装

在源码目录拉取最新后，对各 agent 重新 copy 安装：

```bash
git pull
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
bash scripts/install.sh skills --copy --replace --target ~/.codex/skills
```

安装完成后重启 Codex App 或新开 Cursor 会话。

## AGENTS 规则用法

全局规则模板位于 [trellis/AGENTS.global.md](trellis/AGENTS.global.md)，可通过 `scripts/install.sh agents` 安装到 AI 工具目录。项目根目录的 `AGENTS.md` 由 Trellis 初始化和更新时维护，不应以全局模板直接覆盖。

项目专属规则（如 EGM 的分层、Git 格式、`egm_docs` 等）应在**该项目仓库**内维护 `Agents.md`；Trellis 项目将这些规则追加到 Trellis Managed Block 之外。OpenSpec / GitNexus 流程由对应 Skill 承担，GitNexus 索引块由项目内 GitNexus CLI 注入。

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

- 存在 `.trellis/` 的项目：新功能、较大重构或需求不明确时使用 Trellis Brainstorm → PRD → 实现；简单小改动可直接实现。
- 不存在 `.trellis/` 的项目：继续使用 Superpowers 与 OpenSpec。
- 迁移工具默认仅预览；它不会覆盖 `~/.codex/config.toml`、MCP、插件或 hooks。

## MCP 与外部依赖

本包**不包含** MCP 服务器配置，需在各 IDE 中单独设置：

- **memory**：Recallium / Mem0（见 `skills/memory/references/memory-backends.md`）
- **gitnexus**：GitNexus MCP；EGM 等项目需先索引
- **openspec / release**：按 Skill 说明使用 CLI 或 Markdown 模板

Skill 不可用时须明确说明限制，不得虚报已执行工具结果。
