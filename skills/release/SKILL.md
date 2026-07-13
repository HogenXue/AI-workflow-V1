---
name: release
description: "Plan, verify, execute, and report releases with versioning, change notes, rollback readiness, and post-release checks. Use for release preparation, deployment, rollout, rollback, or release-status verification."
---

# Release

读取 skill 目录上两级的 `config/defaults.yaml`（Codex 安装后为 `~/.agents/config/defaults.yaml`；源码仓库则为包根 `config/defaults.yaml`），再读取目标仓库根目录的 `hogen-codex.yaml`（若存在）；项目值覆盖默认值。默认配置不存在时使用正文中的保守发布门禁继续执行，不把可选 config 组件缺失当成发布授权。发布范围、版本、目标环境、批准状态或回滚路径不明确时，先报告限制，不能将准备工作表述为已发布。

按[发布门禁](references/release-gates.md)确认范围、版本与变更说明，完成可执行的构建、测试和迁移检查，准备可操作的回滚，再执行已获授权的发布或灰度。发布后记录实际操作与结果，完成健康检查并列出风险、观察窗口和未执行事项。

发布工具不可用时，只能用本地构建、测试、版本文件、变更记录和只读部署配置进行准备或状态核对，并明确未执行部署、远端监控、回滚或生产验证。不得虚报发布成功、生产健康、变更已上线或回滚已演练。使用[发布清单模板](templates/release-checklist.md)记录状态，参见[发布准备示例](examples/prepare-release.md)。

Release 负责发布说明、版本记录与已获授权的发布工作；不负责需求设计、项目管理或开发实现。

Release 消费已完成的 Trellis Check、测试与 GitNexus 证据，负责版本、变更说明、发布/回滚和上线验证；不重复 Trellis 的代码质量检查。证据缺失时退回对应负责人，不在发布阶段补写业务代码。
