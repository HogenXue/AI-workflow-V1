# AI-workflow-V1

可安装的 AI 协作 Skill 包：18 个独立 Skill、Trellis 兼容的全局 AGENTS 模板，以及共享默认配置（`config/`）。

GitHub：[HogenXue/AI-workflow-V1](https://github.com/HogenXue/AI-workflow-V1)

## 包含内容

| 组件            | 说明                                                                         |
| ------------- | -------------------------------------------------------------------------- |
| **Skills**    | AIHero 主流程与配套技能，以及 Memory/GitNexus；18 项安装清单以 `manifest.yaml` 为准 |
| **AGENTS 模板** | [AGENTS.global.md](agents/AGENTS.global.md)：跨项目通用规则；[AGENTS.project.md](agents/AGENTS.project.md)：项目补充规则；[AGENTS-egm.md](agents/AGENTS-egm.md)：EGM 项目补充规则 |
| **config/**   | 默认配置、有效配置运行时和平台无关工作流门禁；项目可用 `hogen-codex.yaml` 覆盖                         |

Trellis 是任务、工件、状态和最终质量门的唯一所有者。本包安装经过 Trellis 适配的 AIHero 独立技能；同一需求不重复访谈、建规格或审查。记忆由 `memory` 对接 Recallium/Mem0，代码分析按需使用 GitNexus/Graphify；Graphify 单独安装，不在 18 项 manifest 中。

| 阶段/目的 | 可安装入口 | 产物与边界 |
| --- | --- | --- |
| 文档化需求探索 | `grill-with-docs`、`grilling`、`domain-modeling` | 当前 PRD/Design 与既有领域/决定 Spec |
| 综合已确认规格 | `to-spec` | 当前 PRD；不再发一份外部规格 |
| 拆分交付与梳理决定 | `to-tickets`、`wayfinder` | 原生父子任务及当前 Design/Plan 的阻塞/决定地图 |
| 获取证据 | `research`、`prototype` | 当前 Task 的研究或原型，实施仍需对应授权 |
| 实施与审查 | `implement`、`tdd`、`code-review` | 原生执行阶段；Spec/Standards 融入一次 `trellis-check` |
| 会话交接 | `handoff` | 既有 Task/Journal 与工件指针 |
| 既有专项能力 | `grill-me`、`diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts` | 无状态 Grill 仍显式调用，其他能力服务当前任务 |

所有完整宿主安装和 `skills` 组件从同一 manifest 分发。完整安装还更新全局规则；单独安装 `skills` 不更新规则，需另行安装 `agents` 或宿主规则。新增技能内置 Trellis 适配，无需将本仓库 `.trellis/` 或 `.claude/` 复制到其他项目；项目原生文件仍由项目管理。固定上游来源见 [归属说明](THIRD_PARTY_NOTICES.md) 和 `skills/aihero-provenance.json`。

`agents/` 内的文件是分发模板，不按这些文件名自动加载。Codex 实际指导按全局 home 到项目目录分层，近目录指导覆盖较早指导，同目录 override 优先且不会与普通 AGENTS 同时加载。更新模板后需明确安装并启动新会话核对有效来源；已有 override 可能仍是所选来源，安装器不会擅自删除它。项目模板只增补本地差异，放在 Trellis 管理区之外。[OpenAI 官方加载说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## 前置条件

- macOS / Linux：Bash
- Windows：PowerShell 7+（`pwsh`）；可用 `winget install Microsoft.PowerShell` 安装
- `python3 >= 3.10` 与 PyYAML（配置合并、工作流门禁和包校验需要）
- 缺失 GitNexus/Trellis 时需要 Node.js/npm；使用受支持的 Node.js LTS。npm 安装启用
  `--engine-strict`，版本不满足软件包要求时停止。Graphify 的独立环境需要 Python 的 `venv`/pip。

```bash
python3 -m pip install -r requirements-dev.txt
```

## 获取源码

```bash
git clone https://github.com/HogenXue/AI-workflow-V1.git
cd AI-workflow-V1
```

## 安装

### macOS / Linux（bash）

安装统一入口：`scripts/install.sh <deps|skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge>`。TTY 下无参数运行进入交互向导（多选编号：`1` Codex、`2` Cursor、`3` Claude、`4` MiniMax Code、`5` WorkBuddy，如 `1 3` / `4 5`）；非 TTY 无参数则打印用法并以 exit 2 退出。交互向导会按宿主逐项检测已有的 URL 型 MCP：显示当前 URL，并默认沿用；只有用户明确选择替换时才写入模板 URL 或显式指定的 Mem0 URL。Codex hooks 与 MCP 安装到用户级 `~/.codex`；Claude MCP 合并到用户级 `~/.claude.json`，全局规则写入 `~/.claude/CLAUDE.md`；两者都不需要项目路径。Cursor 的项目级 hooks/rules **必须显式选择** `--project-root`（或在交互菜单中选择，且仅当选中 Cursor）；**不会**静默使用当前 Git 根。每个组件独立预览、写入和备份；安装 `agents --apply` 到 Codex 目录时仅会增量确保 `[features].hooks = true`，不会覆盖其他全局配置；Claude 使用 `agents --document-name CLAUDE.md --no-hooks-feature`，不写 `config.toml`。

所有组件在覆盖、删除或迁移现有目标前都会先备份。备份直接写入所选备份目录，命名为 `<原名称>.<UTC 时间戳>.bak`；同一秒内重复执行会追加序号，绝不会覆盖已有备份。目录同样使用 `.bak` 后缀并保留完整内容。备份失败时当前组件立即停止，原目标保持不变。自定义 `--backup-dir` 不能等于正被备份的目标或位于其内部。

默认备份根统一为宿主目录下的 `.ai-workflow-backups`：Skill/config 使用其配对根（如 `~/.agents/.ai-workflow-backups`、`~/.cursor/.ai-workflow-backups`、`~/.claude/.ai-workflow-backups`），Codex AGENTS/MCP 使用 `~/.codex/.ai-workflow-backups`，Claude MCP（`~/.claude.json`）默认也写入 `~/.claude/.ai-workflow-backups`。旧版 `.codex-ultimate-v3-backups` 和 `.trellis-template-backups` 不会自动删除或迁移。

完整安装按组件顺序执行：每个组件保证“先备份、失败时局部回滚”，但不是跨组件的全局事务；后续组件失败时，已成功的前序组件不会自动撤销。不要并发运行多个安装器。历史 `.bak` 由使用者按需归档或删除，安装器不会自动清理。

| 组件           | 写入范围                         | 默认行为            |
| ------------ | ---------------------------- | --------------- |
| `skills`     | manifest 中的 Skill 目录         | dry-run         |
| `graphify`   | `~/.agents/skills/graphify`（第三方 Graphify Skill） | dry-run；需已安装 Graphify CLI |
| `agents`     | `<agents-home>/<document>`（默认 `AGENTS.md`；Claude 用 `CLAUDE.md` + `--no-hooks-feature`） | dry-run；已有文件先备份 |
| `config`     | 指定的配置目录                      | dry-run         |
| `codex-merge` | Codex 全局 MCP + 用户级 `hooks.json` / `hooks/` | 写入 `${CODEX_HOME:-~/.codex}` |
| `cursor-merge` | Cursor MCP + 可选项目 `.cursor` hooks；rules `.mdc` 由 `agents/AGENTS.global.md` 动态生成 | 需显式 project-root 才写项目级 |
| `claude-merge` | Claude 用户级 MCP（`~/.claude.json` 的 `mcpServers`） | 不写项目 `.claude/` / `.mcp.json` |
| `minimax-merge` | MiniMax Code 用户级 MCP（默认 `~/.minimax/mcp.json`） | JSON；保留已有 `mcp/mcp.json` |
| `workbuddy-merge` | WorkBuddy / CodeBuddy 用户级 MCP（默认 `~/.codebuddy/.mcp.json`） | 按现有文件优先级合并；保留其它配置 |

`skills` 与 `config` 默认 **copy**（独立副本，不依赖源码目录）；本地开发可用 **link** 实时同步。

### Windows（PowerShell 7+）

Windows 使用与 bash **行为对等** 的 PowerShell 实现（仅 `pwsh` 7+，不支持 Windows PowerShell 5.1）。入口：

- `scripts\install.cmd` — cmd 启动器，转发到 `pwsh -File scripts\install.ps1`
- `pwsh -File scripts\install.ps1` — 直接调用

组件名、标志与诊断前缀（`ERROR:` / `SKIP:` / `BACKUP:` / `INSTALLED:` / `CONFLICT:` 等）与 bash 对齐。Cursor 项目级 hooks/rules 同样必须显式 `--project-root`（或交互菜单选择），不会静默使用 Git 根。`--link` 失败时回滚并非零退出（不静默降级为 copy）；若无符号链接权限，请开启 [Developer Mode](https://learn.microsoft.com/windows/apps/get-started/enable-your-device-for-development) 或具备 `SeCreateSymbolicLinkPrivilege`。

```powershell
winget install Microsoft.PowerShell
```

```bat
scripts\install.cmd skills --dry-run --target %USERPROFILE%\.agents\skills
scripts\install.cmd skills --copy --replace --target %USERPROFILE%\.agents\skills
scripts\install.cmd cursor-merge --mcp-overwrite --project-root C:\path\to\repo
scripts\install.cmd claude-merge --mcp-overwrite --mem0-url https://example.test/mem0
```

```powershell
pwsh -File scripts\install.ps1 skills --dry-run --target "$env:USERPROFILE\.agents\skills"
pwsh -File scripts\install.ps1 skills --copy --replace --target "$env:USERPROFILE\.agents\skills"
pwsh -File scripts\install.ps1 claude-merge --mcp-overwrite --mem0-url https://example.test/mem0
pwsh -File scripts\install.ps1 --help
```

TTY 下无参数进入交互向导；非 TTY 无参数打印用法并以 exit 2 退出（与 bash 一致）。

### 预览（不写文件）

完整安装向导会在写入宿主配置前自动检测 GitNexus、Graphify、Trellis CLI。已有可用版本会保留；
缺失的 GitNexus/Trellis 通过 npm 全局安装，Graphify 使用 `~/.agents/tools/graphify` 中的独立 Python
环境。安装失败立即停止，完成安装后验证 CLI，当前安装进程自动补充 PATH。
脚本不修改终端启动文件；独立 `deps --apply` 会打印工具路径，必要时将它们加入终端 PATH。
Node.js/npm、Python/venv 本身缺失时会提示先安装，不会自动提权或安装系统运行时。
安装 CLI 不会执行 `trellis init`、GitNexus/Graphify 建图，也不会更改已有项目初始化状态。

只补装依赖：

```bash
bash scripts/install.sh deps --dry-run
bash scripts/install.sh deps --apply
```

Windows 对等命令：

```powershell
scripts\install.cmd deps --dry-run
scripts\install.cmd deps --apply
```

`--dry-run` 是默认模式，不联网安装、不创建工具环境。`--apply` 才执行安装。

```bash
bash scripts/install.sh skills --dry-run --target ~/.agents/skills
```

### Codex App（推荐目录）

```bash
bash scripts/install.sh skills --copy --replace --target ~/.agents/skills
```

### 全局 Graphify Skill

Graphify CLI 已安装时，可将其 Skill 安装到共享的 `~/.agents/skills/graphify`；不会写入任何项目目录：

```bash
bash scripts/install.sh graphify --dry-run
bash scripts/install.sh graphify --apply
```

Codex 的“Recommended full install”同样会执行该全局安装。若目标已存在，需显式传入
`--replace`，安装器会先创建时间戳备份；Graphify 仍是外部依赖，不纳入本包的 `manifest.yaml`。

### Cursor

```bash
bash scripts/install.sh skills --copy --replace --target ~/.cursor/skills
```

### Claude Code App（推荐目录）

完整用户级 profile（Skills、配对 config、`CLAUDE.md`、MCP），不写项目 `.claude/`，也不安装 Graphify：

```bash
bash scripts/install.sh skills --copy --replace --target ~/.claude/skills
bash scripts/install.sh config --copy --replace --target ~/.claude/config
bash scripts/install.sh agents --apply --agents-home ~/.claude --document-name CLAUDE.md --no-hooks-feature
bash scripts/install.sh claude-merge --mcp-overwrite --mem0-url https://example.test/mem0
```

TTY 交互向导选择 `3`（或与其它宿主组合，如 `1 3`）即可一次完成推荐安装。Windows 对等：`scripts\install.cmd` / `pwsh -File scripts\install.ps1`（同一组件序列与标志）。更新时对上述目标重新 copy/merge；重启 Claude Code 会话后生效。

### MiniMax Code 与 WorkBuddy

无参数运行 `bash scripts/install.sh`，选择 `4` **MiniMax Code（mcode）**、`5` **WorkBuddy**，
或 `4 5` 同时安装。Windows 使用 `scripts\install.cmd`，菜单和组件保持对等。
请先安装宿主应用；这里安装的是工作流配置，应用安装与登录由各自官方工具负责。

| 宿主 | Skills / 配套默认配置 | 全局规则 | 用户级 MCP |
| --- | --- | --- | --- |
| MiniMax Code | `~/.minimax/skills` / `~/.minimax/config` | `~/.minimax/AGENTS.md` | 先沿用已有 `mcp.json`，其次 `mcp/mcp.json`；缺失时创建 `mcp.json` |
| WorkBuddy | `~/.codebuddy/skills` / `~/.codebuddy/config` | `~/.codebuddy/CODEBUDDY.md` | 优先已有 `.mcp.json`，其次 `mcp.json`，再 `~/.codebuddy.json`；缺失时创建 `.mcp.json` |

MiniMax Code 数据目录优先使用 `MINIMAX_DATA_DIR`、其次 `MAVIS_DATA_DIR`；命名 profile 可设置
对应数据目录后安装。WorkBuddy 支持 `CODEBUDDY_CONFIG_DIR`；此时配置写入该自定义目录。
`config/` 仅放本包 Skill 默认配置，保留宿主的 `config.yaml` / `settings.json`。
这两个宿主采用原生 `type: stdio/http` MCP 字段，保留其它服务器、headers 和用户配置；
推荐安装不写项目文件、Codex hooks 或 Graphify Skill。WorkBuddy 接入使用官方说明的
代码开发配置兼容机制，配置后重启宿主并确认 Skills/MCP 加载状态。

只预览 MCP 合并（不创建目录或备份）：

```bash
bash scripts/install.sh minimax-merge --dry-run --mcp-keep
bash scripts/install.sh workbuddy-merge --dry-run --mcp-keep
```

确认后使用 `--apply`；Mem0 地址用 `--mem0-url URL`，已有服务器的策略用 `--mcp-keep` 或
`--mcp-overwrite`。组件支持 `--minimax-home PATH` / `--workbuddy-home PATH`、`--mcp-file PATH`
和 `--backup-dir PATH`；环境变量用于完整安装的目录覆盖。Windows 对等示例：

```powershell
scripts\install.cmd minimax-merge --dry-run --mcp-keep
scripts\install.cmd workbuddy-merge --dry-run --mcp-keep
```

配置依据：[MiniMax Code 源码与说明](https://github.com/MiniMax-AI/minimax-code)、
[WorkBuddy 用户级配置兼容](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting)、
[CodeBuddy MCP 文件优先级](https://www.codebuddy.cn/docs/cli/mcp)。

### Codex CLI 独立目录（仅在不使用 App 共享目录时）

```bash
bash scripts/install.sh skills --copy --replace --target ~/.codex/skills
```

Codex 可能同时发现 `~/.agents/skills` 与 `~/.codex/skills`。同一组 Skill 只选择一个目录；本包对 Codex App 默认使用 `~/.agents/skills`，对应配置目录是 `~/.agents/config`。安装器发现另一目录存在同名 Skill 时会警告；只有显式 `--prune-other-root` 才会先备份再移走另一目录中的本包同名 Skill。

旧版本的 `openspec`、`review`、`release` 和 `karpathy-guidelines-zh` 不在当前 manifest 中，普通更新不会删除它们。`grill-with-docs`、`grilling`、`domain-modeling` 已恢复为当前技能，按普通冲突/备份替换处理，`--prune-legacy` 不会清理它们。先预览，再用显式 `--prune-legacy` 备份并移除上述四个旧技能；若两处都曾安装，需要分别处理：

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
| `deps`         | 支持 `--dry-run` / `--apply`；只安装缺失的 GitNexus/Trellis/Graphify CLI并验证可用性 |
| `skills`       | 支持 `--dry-run`、`--copy` / `--link`、`--replace`、`--prune-legacy`、`--prune-other-root`、`--target PATH`、`--backup-dir PATH` |
| `graphify`     | 支持 `--dry-run` / `--apply`、`--replace`、`--backup-dir PATH`；只写 `~/.agents/skills/graphify` |
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
    ├── grill-me/
    ├── tdd/
    ├── diagnosing-bugs/
    ├── codebase-design/
    ├── resolving-merge-conflicts/
    └── graphify/              # 仅执行 graphify 组件后存在
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

全局规则模板位于 `agents/` 目录的 [AGENTS.global.md](agents/AGENTS.global.md)：`agents --apply` 写入 Codex 的 `AGENTS.md`；`agents --apply --document-name CLAUDE.md --no-hooks-feature` 写入 Claude 的 `CLAUDE.md`；`cursor-merge`（含显式 `--project-root`）据此动态生成项目 `.cursor/rules/ai-workflow-global.mdc`。项目根目录的 `AGENTS.md` / `CLAUDE.md` 由 Trellis 初始化和更新时维护，不应以全局模板直接覆盖。[AGENTS.project.md](agents/AGENTS.project.md) 是通用项目补充模板，按目标项目需要手动合并到 Trellis 管理区之外。

项目专属规则（如 EGM 的分层、Git 格式、`egm_docs` 等）应在**该项目仓库**内维护 `AGENTS.md`；Trellis 项目将这些规则追加到 Trellis Managed Block 之外。GitNexus 流程由对应 Skill 承担，索引块由项目内 GitNexus CLI 注入。

[AGENTS-egm.md](agents/AGENTS-egm.md) 位于 `agents/` 目录，是 EGM 项目补充规则的参考模板；它不会由全局 `agents` 安装器自动写入，避免把 EGM 约束注入其他项目。同步时只更新目标 EGM 根 `AGENTS.md` 中 Trellis Managed Block 之外的项目补充内容；覆盖既有内容前必须先备份为 `AGENTS.md.<UTC 时间戳>.bak`。目标项目中的项目规则仍是运行时事实来源，本仓库模板不会自动覆盖它。

## 项目级配置覆盖

在**目标项目**根目录创建 `hogen-codex.yaml`，与包内 `config/defaults.yaml` 合并（项目值优先）。示例：

```yaml
change_policy:
  require_impact_analysis_before_symbol_edit: true
```

输出合并结果或读取单个配置键：

```bash
python3 config/effective_config.py --project-root /path/to/your/project
python3 config/effective_config.py --project-root /path/to/your/project \
  --get change_policy.require_impact_analysis_before_symbol_edit
```

`config/consumers.yaml` 登记每个公开配置键的实际消费者；包校验会拒绝未登记或未知的键。

## Trellis 任务与质量检查

Trellis 项目使用本项目的 `.trellis/scripts/task.py` 管理任务；规划完成时用
`task.py validate <任务目录>` 检查上下文引用。实现稳定后运行项目原生
`trellis-check` 和受影响范围的真实检查命令，在当前任务中记录命令、结果与未覆盖范围。
归档前逐项核对验收标准和证据。CI 直接运行本包 Skill 校验与单元测试。

## 校验 Skill 包

在仓库根目录：

```bash
python3 scripts/validate-all-skills.py
```

## Trellis 集成（可选）

本包提供一个可选的 Trellis 兼容迁移包，详情见 [trellis/README.zh-CN.md](trellis/README.zh-CN.md)。

- 存在 `.trellis/` 的项目：Trellis 是唯一工作流。`grill-me` 只在用户显式调用时进行无状态澄清，结束后由 Trellis 把确认结论写回当前 PRD 和既有 `.trellis/spec/`。TDD 用于需要测试证明的行为变化；Diagnosing Bugs、Codebase Design、Resolving Merge Conflicts 只作为当前 task 内的能力，由原生 `trellis-check` 负责质量检查。GitNexus 仅在项目规则明确要求或高影响变更时做影响/范围检查；局部低风险提交使用标准 Git 检查与相关测试。
- 不存在 `.trellis/` 的项目：继续使用该项目既有的实施工作流。
- 迁移工具默认仅预览；执行 `agents --apply` 时只会增量启用 `~/.codex/config.toml` 的 `[features].hooks`，不会覆盖 MCP、插件或其他配置。

## MCP 与外部依赖

本包包含 Codex TOML 与 Cursor/Claude/MiniMax Code/WorkBuddy JSON 的 MCP 合并模板；安装器按宿主格式增量合并，不会
把一套格式复制到另一宿主。Claude 只改 `~/.claude.json` 的 `mcpServers`，保留其它用户状态字段。
Mem0 与 Recallium 默认地址均为 `https://www.59005046.xyz:8102/mcp`；五个宿主使用相同默认值。
`--mem0-url URL` 可单独覆盖 Mem0 地址，未提供时使用模板默认地址。

TTY 一键安装会分别读取所选宿主的现有 MCP 配置。对本包管理且已有 URL 的 MCP，
安装器逐项询问沿用或替换；直接回车默认沿用。缺少 Mem0 配置时安装默认地址。
非交互组件调用不读取输入，继续由 `--mcp-keep`、`--mcp-overwrite` 和 `--mem0-url` 明确控制。

安全策略：远端 MCP URL 必须使用 HTTPS；`localhost`、`127.0.0.1`、`::1` 以及标准私有
IPv4/IPv6 地址允许明文 HTTP，用于本机或可信局域网内的自托管服务。不安全 URL 会在目标文件修改前失败。

- **memory**：Recallium / Mem0（见 `skills/memory/references/memory-backends.md`）
- **gitnexus**：GitNexus MCP；EGM 等项目需先索引
- **graphify**：可选第三方图谱 CLI/Skill；普通源码查询无需先建图

Skill 不可用时须明确说明限制，不得虚报已执行工具结果。

## 变更与第三方归属

- 未发布变更见 [CHANGELOG.md](CHANGELOG.md)。
- AI Hero 改编内容及保留的历史归属声明见
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。该说明不为本仓库其他内容指定许可证。
