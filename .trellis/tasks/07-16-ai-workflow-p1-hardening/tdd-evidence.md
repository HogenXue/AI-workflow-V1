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

- 共享质量入口（带当前任务）通过：六个 Skill 校验、104 个单元测试、10 个 Shell 文件、
  15 个 Python 文件和 `git diff --check` 全部成功。
- 质量证据写入当前任务 `verification.json`；最终工件更新后再次运行以刷新工作区指纹。
- completion 门禁在最终质量证据刷新后执行。
