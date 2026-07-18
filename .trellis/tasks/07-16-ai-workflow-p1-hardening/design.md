# 技术设计：AI 工作流 P1 加固

## 1. 设计目标

- 把最高风险的提示词约定转化为确定性、可执行检查。
- 保持 Trellis 为唯一任务生命周期和状态权威。
- Codex、Cursor、Claude 共用同一套核心契约，不把逻辑复制到各宿主生成文件中。
- 保留当前工作区中已经实现的安装器备份与回滚保证。
- 缺少证据或工具时明确失败，不静默跳过。

## 2. 架构与职责边界

```text
内置或用户提供的 MCP 配置
          |
          v
共享 URL 安全策略 -> 宿主合并器 -> 现有 Shell 备份/回滚 -> 宿主配置文件

defaults.yaml + hogen-codex.yaml
          |
          v
config/effective_config.py -> 校验器 / Skills / 工作流检查器

Trellis 任务工件 + 仓库质量检查
          |
          v
平台无关工作流检查器 -> verification.json
          |
          v
现有 Trellis 检查与归档指引（Trellis 仍是状态所有者）
```

本次实现不得修改 `.trellis/scripts/**`、`.trellis/workflow.md`，也不得修改由 Trellis
生成的 `.claude` / `.cursor` helper。项目拥有的全局或项目 AGENTS 模板可以说明原生
helper 如何调用共享检查器。

## 3. MCP 传输安全契约

### 3.1 校验入口

在 `scripts/lib/merge_host_mcp.py` 增加唯一 URL 校验器。所有包含 URL 的 MCP 条目在新增
或覆盖前都必须通过该校验器。

### 3.2 允许的 URL

- `https://<主机>/...`
- `http://localhost/...`
- `http://127.0.0.1/...`
- `http://[::1]/...`

远端明文 HTTP、缺少主机名、使用不支持协议的 URL 必须输出稳定的 `ERROR:` 诊断并以
非零状态退出。`keep` 策略保留的既有条目不会被重新写入，因此不作为新输入重新校验。

Codex 和 Cursor 的 Recallium 模板统一改为已确认的生产 HTTPS 地址。Mem0 用户输入采用
相同 URL 策略，避免任一宿主路径绕过安全边界。

### 3.3 事务行为

合并器必须在 `write_atomic` 前完成校验。Shell 调用者继续使用当前时间戳备份与回滚机制；
Python 层不引入第二套备份实现。

## 4. 有效配置契约

### 4.1 共享模块

新增 `config/effective_config.py`，作为以下能力的唯一所有者：

- YAML 加载以及缺少 PyYAML 时的可操作错误提示；
- schema 校验；
- 默认配置与项目配置的递归合并；
- 点路径配置读取；
- 面向 `--project-root` 和可选 `--get` 的稳定 JSON 输出。

`scripts/validate-all-skills.py` 导入并重新导出相关函数，确保现有 API 级测试和调用方式
继续兼容。`config` 安装器已经复制整个配置目录，因此运行时 helper 会随
`defaults.yaml` 一起安装，不需要新增安装组件。

### 4.2 消费者登记表

在 `config/` 下增加一个小型声明式消费者登记表，并扩展校验逻辑：schema 的每个叶子键
必须至少有一个命名消费者，登记表也不得包含 schema 中不存在的键。

| 配置键 | 消费者 |
| --- | --- |
| `language` | AGENTS / Skill 回复语言策略 |
| `change_policy.minimal_change` | Karpathy Guidelines |
| `change_policy.preserve_dirty_worktree` | AGENTS / Karpathy Guidelines |
| `change_policy.require_impact_analysis_before_symbol_edit` | GitNexus Skill |
| `verification.report_unexecuted_steps` | 工作流检查器诊断输出 |
| `verification.require_spec_for_complex_change` | 工作流 readiness 检查 |
| `tools.missing_tool_policy` | Memory、GitNexus、Release 降级行为 |

当前手工描述“两份 YAML 合并”的 Skills 改为优先调用共享 helper；如果可选 config 组件或
PyYAML 不可用，则继续使用已经定义的保守降级行为。

## 5. 平台无关工作流检查器

### 5.1 位置与接口

新增 `config/workflow_check.py`，随配对的 config 组件一起安装。它接受 `--project-root`
和任务路径，默认输出适合人工阅读的诊断，并支持 JSON 输出供自动化使用。

提供三个子命令：

1. `readiness`
   - 任务存在且状态为 `planning`；
   - PRD 的 Goal、Requirements、Acceptance Criteria 均存在且不是占位内容；
   - 传入 `--complex` 时，如果有效配置要求复杂任务规范，则必须存在 `design.md` 和
     `implement.md`；
   - 如果任务包含上下文清单，则 implement/check 两份清单都必须包含真实存在的 spec
     或 research 条目，不能只有种子示例。
2. `quality`
   - 运行仓库质量配置或显式注入的检查命令；
   - 记录命令、退出状态和耗时；
   - 显式传入 `--task` 时，只在所有必要检查通过后写入
     `<任务目录>/verification.json`；不传 `--task` 时只返回相同检查结果，不写证据，
     避免 CI 依赖活动任务目录；
   - 证据记录 Git HEAD 作为审计元数据，并记录确定性的工作区内容指纹。指纹覆盖已跟踪及
     未忽略的未跟踪文件，排除证据文件和易变的运行时/索引目录。
3. `completion`
   - 任务状态为 `in_progress`；
   - PRD Acceptance Criteria 章节内所有验收复选框均已勾选；
   - 质量证据成功，并与当前工作区内容完全匹配；仅提交相同内容造成的 HEAD 变化不使证据
     失效，验证后任何受覆盖内容变化仍使证据失效；
   - 一次性报告所有缺失或过期项，且绝不修改任务状态。

AI-workflow 默认质量配置运行：

- `python3 scripts/validate-all-skills.py`；
- `python3 -m unittest discover -s tests`；
- 对发布的 Shell 脚本执行 Bash 语法检查；
- 对发布的 Python 代码执行编译检查；
- `git diff --check`。

测试 `quality` 时注入最小命令，不调用默认完整配置，避免测试套件递归执行自身。

完整质量检查以 Trellis task 为单位：实现阶段先运行受影响范围的针对性测试，最终
`trellis-check` 后只运行一次 `quality --task`。同一提交批次不按 commit 数量重复运行；
只有质量检查覆盖的仓库内容随后变化才重新运行。`completion` 只复用并校验已有证据，
不重新执行质量命令。

### 5.2 宿主集成

- 现有 Trellis `trellis-check` 继续担任质量评审者。
- 项目或全局 AGENTS 规则要求：共享 helper 存在时调用它；不存在时明确说明限制，并降级到
  原生 Trellis 检查。
- 不增加第七个业务 Skill，也不修改任何宿主生成 helper。

## 6. CI 与端到端测试

新增 GitHub Actions，在 Ubuntu 和 macOS 上使用受支持的 Python 运行时。两个环境都调用
同一个不带 `--task` 的工作流质量入口，不维护第二份验证命令清单。

新增临时仓库端到端测试，证明：

1. planning 任务缺少工件或上下文时 readiness 失败；
2. 规划工件完整后 readiness 通过；
3. quality 生成绑定证据，但不修改任务状态；
4. 存在未勾选验收项时 completion 失败；
5. 验收项全部勾选且证据新鲜时 completion 通过；
6. 后续任意工作区修改会让证据过期，completion 再次失败。

## 7. 文档、诊断与第三方归属

- 修复 README 中关于 MCP/config 的矛盾说明和错误路径。
- 记录 Recallium HTTPS 默认值、本机 HTTP 例外、effective-config 命令、workflow-check
  命令和 CI 入口。
- 新增“未发布”变更记录，不修改 `manifest.yaml` 版本，也不声称已经发布。
- 为源自 MIT 项目的 Karpathy 材料增加第三方归属说明，但不擅自给整个仓库指定许可证。
- 收紧 `trellis/config-check.sh`，只列出顶层 MCP 服务器节，并增加嵌套节回归测试。

## 8. 兼容性、上线与回滚

- 现有配置键和安装 CLI 参数保持兼容。
- 可选配置运行时缺失时必须报告限制，并采用现有保守降级行为。
- URL 策略会有意收紧：以前可写入的远端 HTTP 现在会在修改前失败；本机回环开发仍受支持。
- 工作流检查器为附加能力，不拦截或替换 `task.py` 内部逻辑。
- 回滚按文件执行：撤销新增模块、测试、文档并恢复 MCP 模板。现有安装器备份不得删除。

## 9. 风险与控制措施

| 风险 | 控制措施 |
| --- | --- |
| 工作区指纹误判证据过期 | 明确定义确定性排除项，并增加修改后失效的 E2E |
| 测试递归执行 | workflow-check 单元测试和 E2E 使用注入命令 |
| Trellis 生成文件被覆盖 | 不修改生成 helper 或 `.trellis` 运行时 |
| 配置加载器抽取破坏校验器 | 保留导出函数名，先跑针对性测试再跑完整测试 |
| Codex/Cursor MCP 行为漂移 | 共用一个 URL 校验器，并断言两份模板 |
| 脏工作区范围混淆 | 不清理现有修改，最终单独列出本任务文件与此前修改 |

## 10. Grill with Docs 与 Trellis 边界

`grill-with-docs` 作为对现有 `grill-me` 的原位能力替换。为避免把上游组合依赖扩散为
另一条自动工作流，该 Skill 把以下能力限定在 Trellis Phase 1.1：

1. grilling：一次只问一个决策问题，先查事实，并给出推荐答案；
2. domain modeling：术语确认后即时维护 `.trellis/spec/domain/`，只记录领域词汇；
3. decision record：仅在决定难以逆转、缺少上下文会令人意外、且存在真实权衡时写入 `.trellis/spec/decisions/`。

持久化所有权固定为：

| 工件 | 唯一用途 | 禁止内容 |
| --- | --- | --- |
| `.trellis/tasks/*/prd.md` | 需求、范围、场景、验收和未决项 | 不复制到 issue 或另一份 Spec |
| `.trellis/spec/domain/*.md` | 领域术语及应避免的同义词 | 不写实现计划、验收或任务状态 |
| `.trellis/spec/decisions/*.md` | 难以逆转的架构/边界决定及原因 | 不写普通实现细节或会话流水账 |
| Trellis Design/Plan/Journal | 技术设计、实施步骤、状态和证据 | 不由 Grill with Docs 接管生命周期 |

不引入上游 `setup-matt-pocock-skills`、`ask-matt`、`to-spec`、`to-tickets`、`implement`、
`code-review` 或 `wayfinder`。这些 Skill 会建立 issue/spec/ticket/执行/审查/提交链，与 Trellis
的 Phase 1–3 重叠。完整冲突矩阵见
`research/matt-pocock-skills-conflicts.md`。

额外引入三个能力型 Skill：

| Skill | Trellis 内职责 | 禁止接管 |
| --- | --- | --- |
| `diagnosing-bugs` | 复现、最小化、假设、观测和回归测试；陌生调用链先用 GitNexus，行为修复回到本包 TDD | task 状态、独立修复流程、commit/PR |
| `codebase-design` | 提供深模块、接口、seam、locality 等设计词汇；落地变更先回到 Trellis 规划和 GitNexus 影响分析 | 自动重构、独立 Design/Spec |
| `resolving-merge-conflicts` | 在用户已启动 merge/rebase 后逐冲突按意图解决并验证 | 自行发起 merge/rebase、abort、commit、push |

本包现有 `tdd` 保持不变，上游同名版本不安装；可选 `prototype` 本次不加入。
