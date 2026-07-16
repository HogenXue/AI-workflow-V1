# EGM 项目补充规则（Trellis 兼容）

> 版本：V7-EGM。本文件是 EGM 仓库根目录 `AGENTS.md` 的**项目专属补充**，应放在 Trellis Managed Block 之外。
>
> 优先级：用户指令、目标 EGM 仓库中更近的 `AGENTS.md` 与 Trellis 管理内容优先；本文件补充全局 AI 工作原则，不复制或替代它们。

## 项目边界与架构

- `egm_backend`：Spring Boot 微服务后端。
- `egm_vue`：Vue 管理端。
- uni-app：移动端。
- 后端遵循 `Controller → Application → Domain → Infrastructure`：
  - Controller：协议接入、参数校验与响应转换。
  - Application：用例编排、事务边界与跨领域协调。
  - Domain：核心业务规则、领域模型与不变量。
  - Infrastructure：数据库、消息队列、RPC 等技术实现。
- 跨层调用必须保持上述方向；业务规则不应下沉到 Controller 或 Infrastructure。

## 工作流与能力路由

- EGM 已启用 `.trellis/` 时，Trellis 是唯一的任务、PRD、Design、Spec 与工作日志来源。
- 简单且需求明确的修改：走 Trellis 轻量流程，直接实施并做针对性验证。
- 复杂、跨模块或需求不明确：先使用 `$grill-with-docs` 一问一答澄清；它只维护领域术语与持久决策，需求、范围与验收仍只写当前 Trellis PRD。使用后不得再启动 `trellis-brainstorm`。
- 不在 EGM 中并行启动 OpenSpec、Superpowers 或其他完整工作流，也不创建第二套 Task、PRD、Design 或 Spec。
- 会话延续、历史规则或长期决策：使用 `$memory`；它不替代 Trellis 的 PRD、Task 或 Journal。
- 涉及跨模块、公共接口/数据契约、删除迁移、高风险变更或陌生调用链：先使用 `$gitnexus`（仓库索引名以目标项目实际配置为准）。局部低风险修改不自动调用。
- 需要自动化行为证据时使用 `$tdd`；复杂 Bug 或性能回归使用 `$diagnosing-bugs`；模块边界或接口设计使用 `$codebase-design`。它们均只服务当前 Trellis task，不接管生命周期。

## 文档与质量证据

- 当前任务的需求、研究、设计、实施和检查产物写入 `.trellis/tasks/`；长期复用规则写入 `.trellis/spec/`；跨会话记录写入 `.trellis/workspace/`。
- `egm_docs/spec/` 与 `docs/superpowers/` 是历史参考目录。除修订历史说明外，不在其中创建新的任务产物，也不复制或迁移既有正文。
- 新任务如需引用历史资料，将原文件作为 research context 链接；迁移索引集中维护在对应 Trellis 任务的 `research/legacy-document-register.md`。
- 文档变更应说明原因、影响范围及关联代码或任务。
- 原生 `trellis-check` 完成评审后，按项目可用的 `config/workflow_check.py` 运行质量门禁；归档前运行完成门禁。辅助脚本不可用时，执行等价检查并明确说明降级。

## 实施授权与本地服务

- 修改代码、配置、数据或项目文档前，先获得用户对该项实施工作的明确同意；只读排查、方案说明与风险评估不需要额外同意。
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
- EGM 的 Git commit message 必须包含版本号和提交日期，版本号与内容风格参考 `egm_docs/RELEASE_NOTE.md`，并使用与 Release Note 相同的结构：

  ```md
  ## 版本号 - YYYY-MM-DD
  - 模块路径 -> 功能入口：变更点。
  - 具体行为、规则调整或修复说明。
  ```

- 提交前先从 `egm_docs/RELEASE_NOTE.md` 确认目标版本号；无法确定时询问用户，不得自行编造。日期使用实际提交日期。
- Git commit message 与对应 Release Note 应描述同一组变更，不得遗漏实际包含的模块或行为调整。

- 完成后说明实际修改、验证结果与已知限制；不得把未执行的检查、重启或 Git 操作表述为已完成。
