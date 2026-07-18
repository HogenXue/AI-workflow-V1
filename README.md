# AI-workflow-V1

可安装的 AI 协作 Skill 包：9 个独立 Skill、全局 AGENTS 模板，以及共享默认配置（`config/`）。

GitHub：[HogenXue/AI-workflow-V1](https://github.com/HogenXue/AI-workflow-V1)

## 包含内容

| 组件            | 说明                                                                         |
| ------------- | -------------------------------------------------------------------------- |
| **Skills**    | `memory`、`gitnexus`、`release`、`karpathy-guidelines-zh`、`grill-with-docs`、`tdd`、`diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts` |
| **AGENTS 模板** | [AGENTS.global.md](AGENTS.global.md)：跨项目通用规则；[AGENTS-egm.md](AGENTS-egm.md)：EGM 项目补充规则 |
| **config/**   | 默认配置、有效配置运行时和平台无关工作流门禁；项目可用 `hogen-codex.yaml` 覆盖                         |

Trellis 是项目唯一工作流；9 个 Skill 按阶段或能力增强它。Codex 用 Grill with Docs 实现 Phase 1.1，用 TDD 实现行为代码，并按需调用诊断、深模块设计和冲突解决能力；质量门由原生 `trellis-check` 负责。

## 前置条件

- macOS / Linux，Bash
- `python3 >= 3.10` 与 PyYAML（配置合并、工作流门禁和包校验需要）

```bash
python3 -m pip install -r requirements-dev.txt
```

## 获取源码

```bash
git clone https://github.com/HogenXue/AI-workflow-V1.git
cd AI-workflow-V1
```

## 安装

安装统一入口：`scripts/install.sh <skills|agents|config|codex-merge|cursor-merge>`。TTY 下无参数运行进入交互向导（可多选 Codex/Cursor）；非 TTY 无参数则打印用法并以 exit 2 退出。Codex hooks 与 MCP 安装到用户级 `~/.codex`；不需要项目路径。Cursor 的项目级 hooks/rules **必须显式选择** `--project-root`（或在交互菜单中选择）；**不会**静默使用当前 Git 根。每个组件独立预览、写入和备份；安装 `agents --apply` 到 Codex 目录时仅会增量确保 `[features].hooks = true`，不会覆盖其他全局配置。

所有组件在覆盖、删除或迁移现有目标前都会先备份。备份直接写入所选备份目录，命名为 `<原名称>.<UTC 时间戳>.bak`；同一秒内重复执行会追加序号，绝不会覆盖已有备份。目录同样使用 `.bak` 后缀并保留完整内容。备份失败时当前组件立即停止，原目标保持不变。自定义 `--backup-dir` 不能等于正被备份的目标或位于其内部。

默认备份根统一为宿主目录下的 `.ai-workflow-backups`：Skill/config 使用其配对根（如 `~/.agents/.ai-workflow-backups`、`~/.cursor/.ai-workflow-backups`），Codex AGENTS/MCP 使用 `~/.codex/.ai-workflow-backups`。旧版 `.codex-ultimate-v3-backups` 和 `.trellis-template-backups` 不会自动删除或迁移。

完整安装按组件顺序执行：每个组件保证“先备份、失败时局部回滚”，但不是跨组件的全局事务；后续组件失败时，已成功的前序组件不会自动撤销。不要并发运行多个安装器。历史 `.bak` 由使用者按需归档或删除，安装器不会自动清理。

| 组件           | 写入范围                         | 默认行为            |
| ------------ | ---------------------------- | --------------- |
| `skills`     | manifest 中的 Skill 目录         | dry-run         |
| `agents`     | `<agents-home>/AGENTS.md`    | dry-run；已有文件先备份 |
| `config`     | 指定的配置目录                      | dry-run         |
| `codex-merge` | Codex 全局 MCP + 用户级 `hooks.json` / `hooks/` | 写入 `${CODEX_HOME:-~/.codex}` |
| `cursor-merge` | Cursor MCP + 可选项目 `.cursor` hooks；rules `.mdc` 由 `AGENTS.global.md` 动态生成 | 需显式 project-root 才写项目级 |

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

旧版本安装的 OpenSpec、Review 与已被替换的 Grill Me 不在当前 manifest 中，普通更新不会删除它们。先预览，再用显式 `--prune-legacy` 将它们移动到时间戳 `.bak` 备份目录；若两处都曾安装，需要分别处理：

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

| 参数             | 说明                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------- |
| `skills`       | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--prune-legacy`、`--prune-other-root`、`--target PATH`、`--backup-dir PATH` |
| `agents`       | 支持 `--dry-run` / `--apply`、`--agents-home PATH`、`--backup-dir PATH`；`--codex-home` 是兼容别名 |
| `config`       | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--target PATH`、`--backup-dir PATH`       |
| `codex-merge`  | `--mcp-keep` / `--mcp-overwrite`、`--mem0-url`、`--codex-home PATH`、`--replace`；兼容接受但忽略 `--project-root` / `--skip-project` |
| `cursor-merge` | 同上，另支持 `--mcp-file`；不修改项目根 `AGENTS.md` |

## 安装后目录结构

各组件独立安装。例如：

```text
~/.agents/
├── config/                 # 仅执行 config 组件后存在
└── skills/
    ├── memory/
    ├── gitnexus/
    ├── release/
    ├── grill-with-docs/
    ├── tdd/
    ├── diagnosing-bugs/
    ├── codebase-design/
    ├── resolving-merge-conflicts/
    └── karpathy-guidelines-zh/
```

Skill 优先通过 `../../config/effective_config.py` 读取已校验并合并的有效配置；helper 不存在时
才按各 Skill 的保守降级规则读取 `../../config/defaults.yaml`。源码仓库对应路径为
`AI-workflow-V1/config/`。

## 更新与重装

在源码目录拉取最新后，对实际使用的目标重新 copy 安装。Codex App 只更新 `~/.agents/skills`；不要再把同一组 Skill 复制到 `~/.codex/skills`：

```bash
git pull
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
```

安装完成后重启 Codex App 或新开 Cursor 会话。

## AGENTS 规则用法

全局规则模板位于根目录的 [AGENTS.global.md](AGENTS.global.md)：`agents --apply` 写入 Codex 的 `AGENTS.md`；`cursor-merge`（含显式 `--project-root`）据此动态生成项目 `.cursor/rules/ai-workflow-global.mdc`。项目根目录的 `AGENTS.md` 由 Trellis 初始化和更新时维护，不应以全局模板直接覆盖。

项目专属规则（如 EGM 的分层、Git 格式、`egm_docs` 等）应在**该项目仓库**内维护 `AGENTS.md`；Trellis 项目将这些规则追加到 Trellis Managed Block 之外。GitNexus 流程由对应 Skill 承担，索引块由项目内 GitNexus CLI 注入。

[AGENTS-egm.md](AGENTS-egm.md) 位于根目录，是 EGM 项目补充规则的参考模板；它不会由全局 `agents` 安装器自动写入，避免把 EGM 约束注入其他项目。同步时只更新目标 EGM 根 `AGENTS.md` 中 Trellis Managed Block 之外的项目补充内容；覆盖既有内容前必须先备份为 `AGENTS.md.<UTC 时间戳>.bak`。目标项目中的项目规则仍是运行时事实来源，本仓库模板不会自动覆盖它。

## 项目级配置覆盖

在**目标项目**根目录创建 `hogen-codex.yaml`，与包内 `config/defaults.yaml` 合并（项目值优先）。示例：

```yaml
change_policy:
  require_impact_analysis_before_symbol_edit: true
verification:
  require_spec_for_complex_change: true
```

输出合并结果或读取单个配置键：

```bash
python3 config/effective_config.py --project-root /path/to/your/project
python3 config/effective_config.py --project-root /path/to/your/project \
  --get change_policy.require_impact_analysis_before_symbol_edit
```

`config/consumers.yaml` 登记每个公开配置键的实际消费者；包校验会拒绝未登记或未知的键。

## 可执行工作流门禁

`config/workflow_check.py` 是 Codex、Cursor、Claude 共用的确定性入口，不创建第二套 task
或状态机，也不替代原生 `trellis-check`：

```bash
# 复杂任务规划确认后、task.py start 前
python3 config/workflow_check.py --project-root "$PWD" \
  readiness --task .trellis/tasks/<task> --complex

# 当前 task 的最终 trellis-check 和针对性测试完成后，写入一次质量证据
python3 config/workflow_check.py --project-root "$PWD" \
  quality --task .trellis/tasks/<task>

# 归档前检查验收项和证据是否仍与当前代码一致
python3 config/workflow_check.py --project-root "$PWD" \
  completion --task .trellis/tasks/<task>
```

CI 调用 `quality` 时不传 `--task`，因此不会依赖或写入活动任务目录。带任务运行产生的
`verification.json` 会记录 Git HEAD 作为审计元数据，并以工作区内容指纹判断新鲜度。
同一提交批次不按 commit 次数重复完整验证：提交已验证的相同内容只改变 HEAD，不会让
completion 失败；之后任何已跟踪或未忽略的未跟踪内容变化仍会要求重新验证。实现过程中
应先运行受影响范围的针对性检查，最终完整质量入口每个 task 只运行一次，除非内容变化。

内置 quality 配置只对本 AI-workflow 包自动启用。安装到其他项目后，必须按实际技术栈
重复传入 `--check '<名称>=<命令>'`；没有显式项目检查时命令会失败，不会生成质量证据。

## 校验 Skill 包

在仓库根目录：

```bash
python3 scripts/validate-all-skills.py
```

## Trellis 集成（可选）

本包提供一个可选的 Trellis 兼容迁移包，详情见 [trellis/README.zh-CN.md](trellis/README.zh-CN.md)。

- 存在 `.trellis/` 的项目：Trellis 是唯一工作流。Codex 用 `grill-with-docs` 实现 Phase 1.1；需求和验收只写当前 PRD，领域术语写入 `.trellis/spec/domain/`，持久且难以逆转的决定写入 `.trellis/spec/decisions/`。TDD 用于需要测试证明的行为变化；Diagnosing Bugs、Codebase Design、Resolving Merge Conflicts 只作为当前 task 内的能力，由原生 `trellis-check` 负责质量检查。GitNexus 仅在项目规则明确要求或高影响变更时做影响/范围检查；局部低风险提交使用标准 Git 检查与相关测试。
- 不存在 `.trellis/` 的项目：继续使用该项目既有的实施工作流。
- 迁移工具默认仅预览；执行 `agents --apply` 时只会增量启用 `~/.codex/config.toml` 的 `[features].hooks`，不会覆盖 MCP、插件或其他配置。

## MCP 与外部依赖

本包包含 Codex TOML 与 Cursor JSON 的 MCP 合并模板；安装器按宿主格式增量合并，不会
把一套格式复制到另一宿主。Recallium 默认地址为
`https://www.59005046.xyz:8102/mcp`。

安全策略：远端 MCP URL 必须使用 HTTPS；只有 `localhost`、`127.0.0.1`、`::1` 允许
明文 HTTP，用于本机开发。不安全 URL 会在目标文件修改前失败。

- **memory**：Recallium / Mem0（见 `skills/memory/references/memory-backends.md`）
- **gitnexus**：GitNexus MCP；EGM 等项目需先索引
- **release**：按 Skill 说明使用 CLI 或 Markdown 模板

Skill 不可用时须明确说明限制，不得虚报已执行工具结果。

## 变更与第三方归属

- 未发布变更见 [CHANGELOG.md](CHANGELOG.md)。
- Karpathy 衍生材料的来源与许可证声明见
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。该说明不为本仓库其他内容指定许可证。
