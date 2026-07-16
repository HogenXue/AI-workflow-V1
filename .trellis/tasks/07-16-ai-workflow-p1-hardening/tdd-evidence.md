# TDD 执行证据

## 循环一：MCP 远端明文 HTTP 安全策略

### 行为

- PRD 验收：不安全的远端 Recallium HTTP 配置不会被安装器静默写入；安全策略有自动化测试。
- Trellis task：`07-16-ai-workflow-p1-hardening`

### RED

- 新增测试：Codex/Cursor 在远端 HTTP Mem0 输入下拒绝且不修改目标；回环 HTTP 允许；
  Recallium 模板必须为 HTTPS。
- 命令：针对上述四个 `InteractiveInstallTests` 场景运行 `python3 -m unittest`。
- 结果：4 个场景中 3 个失败。两个宿主仍接受远端 HTTP，Recallium 模板仍为 HTTP；
  回环 HTTP 基线通过。失败原因与待实现行为一致。

### GREEN

- 最小实现：在 `merge_host_mcp.py` 增加共享 URL 校验；HTTPS 全局允许，HTTP 仅允许
  `localhost`、`127.0.0.1`、`::1`；更新 Codex/Cursor Recallium 模板为确认的 HTTPS 地址。
- 命令：重复运行四个针对性场景。
- 结果：4/4 通过。

### REFACTOR

- 重构：Codex TOML 与 Cursor JSON 共用同一校验函数和错误类型，没有复制宿主逻辑。
- 回归：`python3 -m unittest tests.test_install_interactive`，19/19 通过；相关
  `git diff --check` 通过。

### 交接

- Trellis Check：待全部阶段完成后统一执行。
- GitNexus：前置影响分析为 LOW；最终仍按跨模块任务执行范围复核。

## 循环二：统一有效配置运行时

### 行为

- PRD 验收：effective config 有统一命令/模块输出，schema 中每个键都有消费者或被移除。

### RED

- 新增测试：稳定 JSON 输出、点路径读取、未知键失败、消费者登记覆盖、包内登记完整、
  缺少 PyYAML 的可操作错误。
- 命令：`python3 -m unittest tests.test_effective_config`。
- 结果：6/6 失败，原因是共享运行时尚不存在。
- 第二个 RED：校验器必须拒绝消费者登记缺项；新增场景最初返回 0，按预期失败。
- 第三个 RED：Memory/GitNexus/Release 必须优先引用共享 helper；三个 Skill 均按预期失败。

### GREEN

- 最小实现：新增 `config/effective_config.py`、`config/consumers.yaml` 和包初始化文件；
  校验器改为导入共享配置逻辑并检查消费者登记；三个 Skill 优先调用共享 helper，保留
  既有降级行为。
- 命令：重复运行 effective-config 和 validator 测试。
- 结果：35/35 通过；包内六个 Skill 校验全部通过；点路径读取输出 `false`。

### REFACTOR

- 重构：从 `validate-all-skills.py` 删除重复的配置 schema/合并实现，保留原公开函数导入
  兼容现有测试。
- 回归：`python3 scripts/validate-all-skills.py`、消费者校验和相关 `git diff --check`
  全部通过。

### 交接

- `verification.*` 的实际运行时消费将在下一循环由 workflow-check 测试锁定。
- Trellis Check 与 GitNexus 最终范围复核待全部阶段完成后执行。

## 循环三：工作流门禁与新鲜质量证据

### 行为

- PRD 验收：readiness/completion 只读检查返回明确非零状态；统一 quality 入口可生成
  机器证据；临时项目覆盖完整生命周期。

### RED

- 新增临时 Git 项目 E2E：占位 PRD、复杂任务缺少设计/计划、种子上下文、完整 readiness、
  配置关闭复杂工件要求、无任务质量检查、带任务证据、未勾选验收项、证据过期和状态不变。
- 命令：`python3 -m unittest tests.test_workflow_check`。
- 结果：6/6 失败，原因是 `config/workflow_check.py` 尚不存在。

### GREEN

- 最小实现：新增平台无关 `readiness`、`quality`、`completion`；读取统一有效配置；支持
  文本/JSON 输出；质量证据绑定 Git HEAD 和工作区指纹；CI 模式不写任务证据。
- 命令：重复运行 workflow-check E2E。
- 结果：6/6 通过。

### REFACTOR

- 重构：共享任务/PRD/context 解析和问题结构；工作区指纹覆盖已跟踪及未忽略的未跟踪
  文件，排除证据自身与 `.gitnexus`、`.trellis/.runtime`；Python 语法检查使用 AST，
  不写缓存。
- 回归：workflow-check、effective-config、validator 合计 41/41 通过；六个 Skill 校验和
  相关 `git diff --check` 通过。

### 交接

- 当前 E2E 已证明 evidence 文件自身不会让证据立即过期，且后续未跟踪或已跟踪文件修改
  都会触发 `stale_worktree`。
- 默认完整质量配置将在文档/CI 集成完成后统一运行。

## 循环四：集成与自检加固

### 行为

- PRD 验收：诊断输出、宿主接入、CI、文档和安装后的运行时内容一致，且不能生成没有
  实际项目检查支撑的质量证据。

### RED

- `config-check` 嵌套节测试最初输出 `example, example.env`，证明误报存在。
- config 复制安装新增缓存排除断言，最初发现目标中包含 `__pycache__`。
- 非 AI-workflow 临时项目不提供 `--check` 时最初仍生成证据。
- completion 结构校验测试最初接受空 `checks` 的证据。
- TOML 单引号远端 HTTP 测试最初绕过 URL 正则并写入目标。

### GREEN

- 顶层 MCP 节只接受单段服务器名；config 复制模式排除 Python 缓存；非本包项目必须显式
  传入项目质量命令；completion 验证 evidence schema 和非空 passed checks；TOML URL
  解析同时覆盖单双引号。
- 增加共享门禁宿主规则、README/Trellis README、未发布变更记录、第三方归属和
  Ubuntu/macOS CI。

### REFACTOR

- 质量证据不持久化检查 stdout/stderr，只记录检查名称、命令、状态、退出码和耗时。
- AnySearch 核对显示上游 Karpathy 仓库 README 声明 MIT，但根目录当前未显示独立
  LICENSE；NOTICE 如实记录该限制，未给整个仓库推断许可证。
- 回归：六个主要测试模块 100/100 通过；此前统一质量入口已完成 Skill 校验、101 个
  单元测试、10 个 Shell 文件、15 个 Python 文件和 `git diff --check`。

### GitNexus / Trellis 自检

- `detect_changes(scope=all)`：HIGH，126 个变化符号、10 条受影响流程。结果包含此前安装器
  任务的未提交修改；主要真实链路为 MCP merge 和 config validation。
- 主索引不含隐藏 `.trellis/` 和本轮新文件，且旧图谱仍把已抽取的 `validate_config` 显示
  为原位置；因此风险等级作为范围提醒，最终结论以源码、E2E 和完整测试为准。
- 按原生 `trellis-check` 等价流程复核任务 PRD/design/implement、相关 spec、完整 diff、
  错误路径、跨宿主一致性和脏工作区边界；未发现未处理 P0/P1。

## 最终质量证据

- 共享质量入口（带当前任务）通过：9 个 Skill 校验、107 个单元测试、Shell/Python 语法和
  `git diff --check` 全部成功。
- 质量证据写入当前任务 `verification.json`；最终工件更新后再次运行以刷新工作区指纹。
- completion 门禁在最终质量证据刷新后执行。

## 循环五：Grill with Docs 与精选 Matt Skills

### 行为

- PRD 验收：用 `grill-with-docs` 替换 `grill-me`，但 Trellis 继续独占 PRD、Task、Design、
  Plan、Check 与 Git 授权；领域术语和持久决定分别写入 `.trellis/spec/domain/`、
  `.trellis/spec/decisions/`。
- 精选引入 `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts`，保留本包已有
  `tdd`，不安装上游整套工作流。

### RED

- 把路由测试改为要求 `grill-with-docs`、Trellis PRD 唯一性、领域/决定规范分层；旧
  `grill-me` 实现按预期失败。
- 新增 legacy 迁移测试，要求 `--prune-legacy` 先生成 UTC 时间戳 `.bak` 再移除
  `grill-me`；旧 manifest 按预期失败。
- 新增 Skill 包测试，允许上游标准中的可选资源目录，同时仍强制 `SKILL.md` 与
  `agents/openai.yaml`；旧校验器按预期失败。
- 将上游 `CONTEXT.md`/`docs/adr/` 目标改为 Trellis 规范路径后，先更新边界测试并确认旧
  路径实现失败。
- 最终完成审计新增 Memory Skill Recallium URL 断言；旧参考文档仍含远端明文 HTTP，
  针对性测试按预期失败。

### GREEN / REFACTOR

- 基于上游提交 `e9fcdf95b402d360f90f1db8d776d5dd450f9234` 选择并适配四个 Skill；冲突矩阵、
  精选范围和 MIT 归属已记录。
- manifest 只发布 9 个精选 Skill；安装器把 `grill-me` 作为显式 legacy 项处理，并复用
  既有先备份后替换/删除契约。
- Skill Creator `quick_validate.py`：4/4 通过；本包 `validate-all-skills.py`：9/9 通过；
  单元测试：107/107 通过；Shell 语法、50 个 Python 文件解析和 `git diff --check` 通过。
- 本机复制安装完成：9 个 Skill 已安装，`grill-me` 已移除；6 个被覆盖或删除的旧 Skill
  均已验证存在 `20260716T082611Z.bak` 备份。
- 最终完成审计发现 `~/.codex/AGENTS.md` 仍保留旧 `$grill-me` 路由；通过统一安装器更新后，
  当前文件与 `trellis/AGENTS.global.md` 逐字一致，旧文件保存在
  `~/.codex/.ai-workflow-backups/AGENTS.md.20260716T083116Z.bak`，`config.toml` 因 hooks
  已启用而保持不变。
- Memory 参考文档改为 HTTPS 并通过新增回归测试；重新安装 9 个 Skill 时每个原目录均先
  写入 `20260716T083420Z` 或 `20260716T083421Z` 的 `.bak`。本机 Codex Recallium URL
  只改动为 HTTPS，原配置备份为
  `~/.codex/.ai-workflow-backups/config.toml.20260716T083426Z.bak`。

### 交接

- GitNexus `detect_changes(scope=all)` 为 LOW：52 个已索引变更符号、0 条受影响执行流；
  隐藏 `.trellis/` 和新文件继续以源码、Skill Creator 校验和完整测试复核。
- 勾选最终 VERIFY 后已重新刷新共享 quality 证据，completion 门禁通过。

## 循环六：Codex hooks 改为用户级安装

### 行为

- 用户确认 Codex 支持全局 hooks，本包一键安装对 Codex 只安装用户级 hooks 和全局 MCP。
- 项目路径不再是 Codex 安装默认输入；`--project-root`/`--skip-project` 仅兼容接受，不写项目 `.codex/`。
- 覆盖用户级 hooks 时仍必须先生成 UTC 时间戳 `.bak` 备份，未给 `--replace` 时冲突退出并回滚 MCP。

### RED

- 修改 `tests/test_install_interactive.py`：要求 `codex-merge` 在 `--skip-project`、非 Git 目录、Git 根目录和显式 `--project-root` 场景下都写入 `${CODEX_HOME}/hooks.json` 与 `${CODEX_HOME}/hooks/session-start.sh`，且不创建项目 `.codex/`。
- 新增/调整冲突测试：已有用户级 hooks 且未给 `--replace` 时失败，并恢复 `config.toml`。
- 命令：`python3 -m unittest tests.test_install_interactive -v`。
- 结果：6 个 Codex hooks 新契约测试按预期失败，旧实现仍跳过用户 hooks 或写项目 `.codex/`。

### GREEN / REFACTOR

- `scripts/install-codex-merge.sh` 改为始终安装用户级 hooks；`--project-root`/`--skip-project` 只打印兼容提示。
- 生成的 `hooks.json` 使用 `bash <CODEX_HOME>/hooks/session-start.sh` 的稳定用户级路径；模板中的 `python3 .codex/hooks/session-start.sh` 修正为 `bash`。
- `scripts/install.sh` 交互安装只在选择 Cursor 时询问项目路径；Codex 安装计划改为 user hooks + global MCP。
- README 同步说明 Codex 不需要项目路径，Cursor 才需要项目级 `--project-root`。

### 验证

- `python3 -m unittest tests.test_install_interactive -v`：20/20 通过。
- `python3 -m unittest tests.test_install tests.test_install_interactive -v`：42/42 通过。
- `python3 -m unittest discover -s tests -v`：107/107 通过。
- `git diff --check`：通过。
