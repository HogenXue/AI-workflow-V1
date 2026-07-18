# EGM 项目补充规则（Trellis 兼容）

> 版本：V8-EGM。本文件是 EGM 仓库根目录 `AGENTS.md` 的**项目专属补充**，应放在 Trellis Managed Block 之外。
>
> 优先级：用户指令、目标 EGM 仓库中更近的 `AGENTS.md` 与 Trellis 管理内容优先；本文件补充全局 AI 工作原则，不复制或替代它们。

## 项目边界与架构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- `egm_wechat`：微信小程序。
- `egm_wechat_backend`：微信小程序后端。
- 后端遵循 `Controller → Application → Domain → Infrastructure`：
  - Controller：协议接入、参数校验与响应转换。
  - Application：用例编排、事务边界与跨领域协调。
  - Domain：核心业务规则、领域模型与不变量。
  - Infrastructure：数据库、消息队列、RPC 等技术实现。
- 跨层调用必须保持上述方向；业务规则不应下沉到 Controller 或 Infrastructure。

## 工作流与能力路由

- EGM 已启用 `.trellis/` 时，Trellis 是唯一的任务、PRD、Design、Spec 与工作日志来源。
- 简单且需求明确的修改：走 Trellis 轻量流程，直接实施并做针对性验证。
- 复杂、跨模块或需求不明确：先使用 `$grill-with-docs` 一问一答澄清，访谈结论写入当前 Trellis PRD；除当前 PRD 外，只可维护 `.trellis/spec/domain/` 中的领域术语和 `.trellis/spec/decisions/` 中的持久决策。使用后不得再启动 `trellis-brainstorm`。
- 不在 EGM 中并行启动 OpenSpec、Superpowers 或其他完整工作流，也不创建第二套 Task、PRD、Design 或 Spec。
- 会话延续、历史规则或长期决策：使用 `$memory`；它不替代 Trellis 的 PRD、Task 或 Journal。
- 涉及跨模块、公共接口/数据契约、删除迁移、高风险变更或陌生调用链：先使用 `$gitnexus`（仓库索引名以目标项目实际配置为准）。局部低风险修改不自动调用。
- 需要自动化行为证据时使用 `$tdd`；复杂 Bug 或性能回归使用 `$diagnosing-bugs`；模块边界或接口设计使用 `$codebase-design`。它们均只服务当前 Trellis task，不接管生命周期。

## 文档与质量证据

- 当前任务的需求、研究、设计、实施和检查产物写入 `.trellis/tasks/`；长期复用规则写入 `.trellis/spec/`；跨会话记录写入 `.trellis/workspace/`。
- `egm_docs/spec/` 与 `docs/superpowers/` 是历史参考目录。除修订历史说明外，不在其中创建新的任务产物，也不复制或迁移既有正文。
- 新任务如需引用历史资料，将原文件作为 research context 链接；迁移索引集中维护在对应 Trellis 任务的 `research/legacy-document-register.md`。
- 文档变更应说明原因、影响范围及关联代码或任务。
- 原生 `trellis-check` 完成最终评审后，按项目可用的 `config/workflow_check.py` 对当前 task 运行一次质量门禁；同一提交批次不按 commit 次数重复，只有证据覆盖的仓库内容变化才重新运行。归档前复用证据运行完成门禁。辅助脚本不可用时，执行等价检查并明确说明降级。
- 按影响范围先运行相关模块或测试类，再按风险决定是否运行以下全量检查；不得用全量检查替代针对性测试：
  - 后端聚合测试：`cd egm_backend && mvn test`。
  - 微信小程序后端：`cd egm_wechat_backend && mvn test`。
  - 管理端单元测试：`cd egm_vue && pnpm test`。
  - 管理端生产构建与类型检查：`cd egm_vue && pnpm build:prod`。
  - 微信小程序单元测试：`cd egm_wechat && npm test`；涉及端到端流程时再运行 `npm run test:e2e`。
- 全量检查若因已确认的无关基线问题失败，应记录实际命令和首个失败，不得把针对性测试通过表述为全量通过。

## 实施授权与本地服务

- 用户直接提出修改、修复或实施，即视为对该明确范围的授权，无需重复确认；只读排查、方案说明与风险评估也不需要额外同意。
- 调查后需要扩大修改范围，或涉及远程环境、生产环境、真实数据与其他高风险操作时，必须另行说明影响并取得授权。
- 在用户已授权的实施范围内，允许启动或重启本地服务；不得对远程环境、生产环境或数据执行破坏性操作。
- 修改 `egm_backend` 后，需要全量本地联调时可运行：

  ```bash
  ./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务
  ```

- 修改 `egm_vue` 后，需要重启管理端时可运行：

  ```bash
  ./egm_docs/Shells/auto_startup.sh restart-vue
  ```

## Git 与版本说明

- 未经用户明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- EGM 提交前必须先更新 `egm_docs/RELEASE_NOTE.md`，为本次实际变更确定版本号、实际提交日期和完整变更列表；版本号无法确定时询问用户，不得自行编造。
- Git commit message 必须逐字复用该条目的版本号、日期和变更列表，并使用以下结构：

  ```md
  ## 版本号 - YYYY-MM-DD
  - 模块路径 -> 功能入口：变更点。
  - 具体行为、规则调整或修复说明。
  ```

- Release Note 与 commit message 必须描述同一组变更，不得合并旧条目、遗漏本次包含的模块，或把未完成事项写成已完成。

- 完成后说明实际修改、验证结果与已知限制；不得把未执行的检查、重启或 Git 操作表述为已完成。
