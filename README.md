# AI-workflow-V1

可安装的 AI 协作 Skill 包：通用协作规则（`AGENTS.md` V6）、5 个独立 Skill，以及共享默认配置（`config/`）。

GitHub：[HogenXue/AI-workflow-V1](https://github.com/HogenXue/AI-workflow-V1)

## 包含内容

| 组件 | 说明 |
| --- | --- |
| **Skills** | `memory`、`gitnexus`、`openspec`、`release`、`karpathy-guidelines-zh` |
| **AGENTS.md** | 跨项目通用 AI 工作原则（V6） |
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

安装脚本：`scripts/install.sh`。默认 **copy**（独立副本，不依赖源码目录）；本地开发可用 **link** 实时同步。

### 预览（不写文件）

```bash
bash scripts/install.sh --dry-run --target ~/.agents/skills
```

### Codex App

```bash
bash scripts/install.sh --copy --replace --target ~/.agents/skills
```

### Cursor

```bash
bash scripts/install.sh --copy --replace --target ~/.cursor/skills
```

### Codex CLI

```bash
bash scripts/install.sh --copy --replace --target ~/.codex/skills
```

### 本地开发（link）

在源码仓库内改 Skill 后即时生效，但删除源码目录会导致安装失效：

```bash
bash scripts/install.sh --link --replace --target ~/.agents/skills
```

### 脚本参数

| 参数 | 说明 |
| --- | --- |
| `--dry-run` | 仅预览，默认行为 |
| `--copy` / `--link` | 复制或符号链接（默认读 `manifest.yaml` 的 `default_install_mode: copy`） |
| `--replace` | 覆盖已有 skill/config，旧版备份到 `skills/.codex-ultimate-v3-backups/` |
| `--target PATH` | skills 安装目录 |
| `--backup-dir PATH` | 自定义备份根目录 |

## 安装后目录结构

`--target` 指向 `…/skills` 时，config 装到同级父目录：

```text
~/.agents/
├── config/                 # defaults.yaml、project-config.schema.yaml
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
bash scripts/install.sh --copy --replace --target ~/.agents/skills
bash scripts/install.sh --copy --replace --target ~/.cursor/skills
bash scripts/install.sh --copy --replace --target ~/.codex/skills
```

安装完成后重启 Codex App 或新开 Cursor 会话。

## AGENTS 规则用法

**AGENTS.md**（V6）为跨项目通用协作原则，可放在模板仓库、用户级规则，或复制到具体项目根目录。

项目专属规则（如 EGM 的分层、Git 格式、`egm_docs` 等）应在**该项目仓库**内维护 `Agents.md`，与通用 V6 及 Skill 路由叠加；OpenSpec / GitNexus 流程由对应 Skill 承担，GitNexus 索引块由项目内 GitNexus CLI 注入。

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

## MCP 与外部依赖

本包**不包含** MCP 服务器配置，需在各 IDE 中单独设置：

- **memory**：Recallium / Mem0（见 `skills/memory/references/memory-backends.md`）
- **gitnexus**：GitNexus MCP；EGM 等项目需先索引
- **openspec / release**：按 Skill 说明使用 CLI 或 Markdown 模板

Skill 不可用时须明确说明限制，不得虚报已执行工具结果。
