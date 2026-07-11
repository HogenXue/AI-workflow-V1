# Trellis 兼容迁移包

本目录为现有 AI-workflow-V1 提供可选的 Trellis 集成。它不会自动安装 Trellis、初始化项目或修改 `~/.codex/config.toml`。

## 工作流路由

| 项目状态            | 任务类型            | 工作流                                  |
| --------------- | --------------- | ------------------------------------ |
| 存在 `.trellis/`  | 新功能、较大重构或需求不明确  | Trellis Brainstorm，一问一答澄清，生成 PRD 后实现 |
| 存在 `.trellis/`  | 预计少于约 5 分钟的简单修改 | 直接实现并做针对性验证                          |
| 不存在 `.trellis/` | 任意任务            | Superpowers 与 OpenSpec               |

Memory、GitNexus、Release 和 Karpathy Guidelines 在两类项目中都可按需使用；它们是能力型 Skill，不接管工作流。

## 先做只读检查

```bash
bash trellis/config-check.sh --codex-home ~/.codex
```

该命令只显示 Trellis、Node、Python 的可用性，以及 Codex 文件是否存在和 MCP 名称。它不会显示配置值、环境变量或密钥。

## 预览 AI 目录中的 AGENTS 模板替换

```bash
bash scripts/install.sh agents --dry-run --agents-home ~/.codex
```

这是默认模式，不创建目录、不写入文件。它只会显示准备复制到 AI 目录根部 `AGENTS.md` 的模板和可能的备份位置。

## 显式替换 AI 目录中的 AGENTS.md

```bash
bash scripts/install.sh agents --apply --agents-home ~/.codex
```

只有 `--apply` 会写入目标 AI 目录的 `AGENTS.md`。若原文件存在，脚本会先把它备份到 `<agents-home>/.trellis-template-backups/<UTC 时间戳>/AGENTS.md`，再替换为 `AGENTS.global.md`。`config.toml`、MCP、插件和 hooks 均保持不变。

`--agents-home` 用于指定任意 AI 工具的规则目录；`--codex-home` 继续作为 Codex 兼容别名。默认目标仍是 `${CODEX_HOME:-~/.codex}`。

如需自定义备份位置：

```bash
bash scripts/install.sh agents --apply --agents-home ~/.codex --backup-dir ~/CodexBackups
```

## 初始化一个已选定项目

确认 Trellis 已安装，并且你明确选择了目标项目后，再手动执行：

```bash
npm install -g @mindfoldhq/trellis@latest
cd /path/to/project
trellis init --codex -u hogenxue
```

不要对所有项目批量初始化。初始化后，将项目特有规则追加在 Trellis 管理区外；可从 [AGENTS.project.md](AGENTS.project.md) 复制该补充区。

## 模板说明

- [AGENTS.global.md](AGENTS.global.md)：供全局 Codex 使用的可复制模板。
- [AGENTS.project.md](AGENTS.project.md)：供 Trellis 项目追加项目特有规则的补充模板。
- `config-check.sh`：只读诊断。
- `install.sh`：旧版兼容入口；等价于统一入口的 `scripts/install.sh agents`。
