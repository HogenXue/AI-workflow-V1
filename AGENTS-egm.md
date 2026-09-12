# EGM 项目补充规则（Trellis 兼容）

> 版本：V9-EGM。本文件是 EGM 仓库根目录 `AGENTS.md` 的**项目专属补充**，应放在 Trellis Managed Block 之外。
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
- Skill 路由、风险分级及最终门禁遵循全局 `AGENTS.md`，不额外增加完整工作流。工程数量或跨工程修改本身不构成强制访谈、全量测试或启动完整服务的理由。
- 复杂、跨工程、数据契约或需求不明确的任务，按全局规则主动使用 `$grill-with-docs` 审查需求完整性；只有需要用户决策的未决项才访谈。需求与设计已经明确时记录审查结论并继续当前 Trellis Task。
- OpenSpec、Superpowers 等能力只能作为当前 Trellis Task 内的方法，不创建第二套 Task、PRD、Design、Spec 或审批流程。

## 文档与质量证据

- 当前任务的需求、研究、设计、实施和检查产物写入 `.trellis/tasks/`；长期复用规则写入 `.trellis/spec/`；跨会话记录写入 `.trellis/workspace/`。
- `egm_docs/spec/` 与 `docs/superpowers/` 是历史参考目录。除修订历史说明外，不在其中创建新的任务产物，也不复制或迁移既有正文。
- 新任务如需引用历史资料，将原文件作为 research context 链接；迁移索引集中维护在对应 Trellis 任务的 `research/legacy-document-register.md`。
- 文档变更应说明原因、影响范围及关联代码或任务。
- 最终原生 `trellis-check`、`quality`、`completion` 的执行时机和证据复用遵循全局规则，EGM 不增加第二套门禁。helper 不可用时执行必要等价检查并说明降级。
- 实现期间先运行相关测试类、模块或必要业务链检查，连续相关修改完成一个逻辑批次后统一验证。局部失败修复后只重跑对应检查。
- 以下是可用命令清单，不是默认必跑清单；只有实际影响范围或最终验收要求时才选用，并说明原因：
  - 后端聚合测试：`cd egm_backend && mvn test`。
  - 微信小程序后端：`cd egm_wechat_backend && mvn test`。
  - 管理端单元测试：`cd egm_vue && pnpm test`。
  - 管理端生产构建与类型检查：`cd egm_vue && pnpm build:prod`。
  - 微信小程序单元测试：`cd egm_wechat && npm test`；需要端到端业务证据时再运行 `npm run test:e2e`。
- 全量检查若因已确认的无关基线问题失败，应记录实际命令和首个失败，说明失败与当前变更的关系以及已通过的针对性检查；不得把针对性测试通过表述为全量通过，也不顺手修复无关基线问题。

## 数据库交付

- 仅在数据库结构、索引、约束、初始化数据、菜单权限、存储过程或触发器发生变化时执行本节。
- 同时更新 `egm_docs/Deployment/sql/` 中对应的完整初始化 SQL，并在 `egm_docs/sql_patch/` 新增下一个连续三位编号升级脚本；不得修改已发布的编号脚本。
- 升级脚本必须可重复执行，并用 `-- Initialization-Sync:` 标明同步修改的初始化 SQL。测试数据脚本保持独立。
- 不新增或执行旧式 `patch_*.sql`。交付前运行 `egm_docs/Shells/validate_sql_delivery.sh`，确认部署 SQL 与 `egm_deploy/119.45.198.89/sql/` 的文件清单及内容一致。

## 实施授权与本地服务

- 用户直接提出修改、修复或实施，即视为对该明确范围的授权，无需重复确认；只读排查、方案说明与风险评估也不需要额外同意。
- 调查后需要扩大修改范围，或涉及远程环境、生产环境、真实数据与其他高风险操作时，必须另行说明影响并取得授权。
- 在用户已授权的实施范围内，允许启动或重启本地服务；不得对远程环境、生产环境或数据执行破坏性操作。
- 业务链确实需要完整本地联调时可运行：

  ```bash
  ./egm_docs/Shells/auto_startup.sh 2.自动启动全部服务
  ```

- 管理端运行态验证确实需要重启时可运行：

  ```bash
  ./egm_docs/Shells/auto_startup.sh restart-vue
  ```

## 并行验证协调

- 使用子代理时，只验证各自负责的工程或功能；不得重复运行同一套全量测试、构建或 E2E。
- 完整本地服务链与最终门禁由主代理统一协调，避免多个代理重复启停同一环境。

## Git 与版本说明

- 未经用户明确要求，不 commit、push、merge、rebase、创建 PR 或删除分支。
- 用户要求“提交并推送”但未指定远端时，只推送 Gitee `origin`；GitHub `github` 仅在用户明确要求时推送。
- 仅当用户要求 Git commit 时，提交前必须先更新 `egm_docs/RELEASE_NOTE.md`，为本次实际变更确定版本号、实际提交日期和完整变更列表；版本号无法确定时询问用户，不得自行编造。
- Git commit message 必须逐字复用该条目的版本号、日期和变更列表，并使用以下结构：

  ```md
  ## 版本号 - YYYY-MM-DD
  - 模块路径 -> 功能入口：变更点。
  - 具体行为、规则调整或修复说明。
  ```

- Release Note 与 commit message 必须描述同一组变更，不得合并旧条目、遗漏本次包含的模块，或把未完成事项写成已完成。

- 完成后说明实际修改、验证结果与已知限制；不得把未执行的检查、重启或 Git 操作表述为已完成。
