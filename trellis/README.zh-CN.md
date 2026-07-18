# Trellis 兼容迁移包

本目录为现有 AI-workflow-V1 提供可选的 Trellis 集成。它不会自动安装 Trellis 或初始化项目；执行安装脚本的 `--apply` 时，会增量确保 `~/.codex/config.toml` 的 `[features].hooks = true`。

Codex App 的 Skill 统一安装到 `~/.agents/skills`，配置安装到 `~/.agents/config`。不要把同名 Skill 同时安装到 `~/.codex/skills`；Codex 可能发现两处并产生来源歧义。安装器默认只警告，显式 `--prune-other-root` 才会先备份再移走另一目录中的本包 Skill。

旧版 OpenSpec、Review 与已被替换的 Grill Me 副本不会被普通 `--replace` 删除。使用 `skills --dry-run --prune-legacy` 预览；确认后同时给出 `--copy --replace --prune-legacy`，安装器会先写入时间戳 `.bak` 备份再从当前目标移走。该选项只处理命令指定的一个 `--target`。

## 工作流路由

| 项目状态 | 任务类型 | 工作流 |
| --- | --- | --- |
| 存在 `.trellis/` | 复杂、跨模块或需求不明确 | Trellis 唯一工作流；Codex 用 Grill with Docs 单独实现 Phase 1.1，需求/验收只写 PRD，术语写 `.trellis/spec/domain/`，持久决定写 `.trellis/spec/decisions/` |
| 存在 `.trellis/` | 行为代码实现 | Trellis 执行阶段内采用 TDD，验证后由原生 `trellis-check` 执行质量检查 |
| 存在 `.trellis/` | 复杂 Bug、模块设计、进行中的 Git 冲突 | 在当前 task 内按需使用 Diagnosing Bugs、Codebase Design、Resolving Merge Conflicts，不接管 Trellis/Git 权限 |
| 存在 `.trellis/` | 简单且需求明确 | 直接使用 Trellis 的轻量规划、task 和验证流程，不触发 Grill with Docs |
| 不存在 `.trellis/` | 任意任务 | 项目既有的实施工作流 |

Memory、GitNexus、Release 和 Karpathy Guidelines 在两类项目中都可按需使用；它们是横切能力，不接管工作流。Grill with Docs 与 TDD 只实现各自阶段，Diagnosing Bugs、Codebase Design、Resolving Merge Conflicts 只提供专项方法，不形成第二套状态机；Review 不再作为独立 Skill 分发。

## 先做只读检查

```bash
bash trellis/config-check.sh --codex-home ~/.codex
```

该命令只显示 Trellis、Node、Python 的可用性，以及 Codex 文件是否存在和 MCP 名称。它不会显示配置值、环境变量或密钥。

嵌套节（例如 `[mcp_servers.recallium.env]`）不会被误报为独立服务器。

## 使用共享配置与工作流门禁

完整安装的 config 组件包含 `effective_config.py` 和 `workflow_check.py`。源码仓库可直接运行：

```bash
python3 config/effective_config.py --project-root "$PWD"

python3 config/workflow_check.py --project-root "$PWD" \
  readiness --task .trellis/tasks/<task> --complex
python3 config/workflow_check.py --project-root "$PWD" \
  quality --task .trellis/tasks/<task>
python3 config/workflow_check.py --project-root "$PWD" \
  completion --task .trellis/tasks/<task>
```

三个子命令分别检查规划就绪、生成质量证据和归档前完成条件。它们不替代 Trellis task
状态机或原生 `trellis-check`；readiness/completion 不修改任务状态。CI 运行 quality 时
不传 `--task`，只返回质量结果，不写任务证据。

实现过程中先运行受影响范围的针对性检查；当前 task 的最终 `trellis-check` 后只运行一次
quality。同一提交批次不按 commit 次数重复完整验证，提交已验证的相同内容不会因 HEAD
变化使证据失效；只有证据覆盖的仓库内容随后变化才重新运行。completion 只校验并复用
已有证据，不重新执行质量命令。

Recallium 模板默认使用 `https://www.59005046.xyz:8102/mcp`。远端 URL 必须使用 HTTPS；
仅本机 `localhost`、`127.0.0.1`、`::1` 允许 HTTP。

## 预览 AI 目录中的 AGENTS 模板替换

```bash
bash scripts/install.sh agents --dry-run --agents-home ~/.codex
```

这是默认模式，不创建目录、不写入文件。它只会显示准备复制到 AI 目录根部 `AGENTS.md` 的模板和可能的备份位置。

## 显式替换 AI 目录中的 AGENTS.md

```bash
bash scripts/install.sh agents --apply --agents-home ~/.codex
```

只有 `--apply` 会写入目标 AI 目录的 `AGENTS.md`。若原文件存在，脚本会先把它备份为 `<agents-home>/.ai-workflow-backups/AGENTS.md.<UTC 时间戳>.bak`，再替换为 `AGENTS.global.md`。随后脚本会在 `config.toml` 中增量确保 `[features].hooks = true`（Codex 0.129+）；配置有变化时会先备份为 `config.toml.<UTC 时间戳>.bak`，MCP、插件和其他配置均保持不变。同一秒内重复执行会追加序号，不会覆盖旧备份。旧 `.trellis-template-backups` 目录会保留，不自动迁移或删除。

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

不要对所有项目批量初始化。初始化后，将项目特有规则追加在 Trellis 管理区外；应从根目录的 [AGENTS.project.md](../AGENTS.project.md) 复制 Codex 阶段映射，确保 Grill with Docs 只替代 `trellis-brainstorm`，质量阶段继续由 `trellis-check` 单独负责。

## 模板说明

- [AGENTS.global.md](../AGENTS.global.md)：供全局 Codex 使用的可复制模板，存放在仓库根目录。
- [AGENTS.project.md](../AGENTS.project.md)：供 Trellis 项目追加项目特有规则的补充模板，存放在仓库根目录。
- `config-check.sh`：只读诊断。
- `install.sh`：旧版兼容入口；等价于统一入口的 `scripts/install.sh agents`。
