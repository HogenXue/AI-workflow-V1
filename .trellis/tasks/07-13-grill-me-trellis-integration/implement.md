# Grill Me、Trellis、TDD、Trellis Check 与 GitNexus 实施计划

## Goal

维护一个没有 OpenSpec/Review 平行流程的单一 Trellis 工作流，并通过仓库安装器分发 Grill Me 和 TDD Skills。

## Task 1: Remove packaged duplicate workflows

- [x] 删除 `skills/openspec/` 的已跟踪文件和空目录。
- [x] 删除独立 `skills/review/`，由原生 `trellis-check` 单独负责质量门。
- [x] 从 manifest、安装测试和 bundled Skill contract 中移除 `openspec`。
- [x] 删除所有面向用户的 OpenSpec 路由和文档引用。

## Task 2: Reconnect the remaining workflow

- [x] 更新 Grill Me：将访谈结论写入 Trellis `prd.md`，在 PRD 确认后等待实施授权。
- [x] 更新 TDD：从 Trellis PRD 获取需求、场景和验收标准；需求缺口返回 Trellis planning。
- [x] 删除独立 Review Skill：TDD 后由原生 `trellis-check` 检查质量、架构、安全与可维护性，P0/P1 修复或豁免后才可进入提交前检查。
- [x] 更新全局和项目模板：`Grill Me → Trellis → TDD → Trellis Check → GitNexus`，不创建平行工件。
- [x] 消除与 Trellis 原生 helper 的重复：Codex 规划阶段只运行 Grill Me/`trellis-brainstorm` 之一，质量阶段只运行 `trellis-check`。
- [x] 将 TDD 定位为实现方法、Karpathy Guidelines 定位为横切约束，避免生成第二套工作流。

## Task 3: Verify package behavior

- [x] 运行 skill validator 与相关单元测试。
- [x] 对安装脚本运行 shell 语法检查，并在临时目录执行 skills dry-run。
- [x] 将 Codex App 默认安装根恢复为 `~/.agents`，并验证另一 Skill 根的显式备份迁移。
- [x] 检查 OpenSpec 引用只存在于遗留迁移说明和测试，不再参与活动路由或分发。
- [x] 检查 diff，确保未回退用户已有的 hooks 相关修改。
- [x] 补齐 `agents --apply` 的异常路径：拒绝非普通 `config.toml`，并在 hooks 配置写入失败时回滚本次 AGENTS 安装。
