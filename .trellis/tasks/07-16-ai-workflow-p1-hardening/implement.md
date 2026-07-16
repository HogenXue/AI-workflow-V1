# 实施计划：AI 工作流 P1 加固

## 开工前条件

- [x] 用户评审并确认本设计与实施计划。
- [x] 修改生产代码前，成功执行
      `python3 ./.trellis/scripts/task.py start 07-16-ai-workflow-p1-hardening`。
- [x] 再次检查当前脏工作区，保留此前任务已有修改。
- [x] 在本任务内记录精简的 RED/GREEN 证据，不创建第二套任务或规范系统。

## 阶段一：加固 MCP 合并安全（TDD）

- [x] RED：增加 Codex 与 Cursor 测试，证明远端 HTTP Recallium/Mem0 会在目标文件被修改前
      拒绝，同时覆盖本机回环 HTTP 允许场景。
- [x] GREEN：在 `scripts/lib/merge_host_mcp.py` 实现共享 URL 策略，并把两份 Recallium
      模板改为 `https://www.59005046.xyz:8102/mcp`。
- [x] REFACTOR：只保留一个校验器和稳定诊断；运行安装器针对性测试及
      `git diff --check`。
- 回滚点：仅撤销 URL 校验器、模板和对应测试。

## 阶段二：让有效配置可执行（TDD）

- [x] RED：增加 JSON/点路径输出、默认值与项目覆盖、无效配置、缺少 PyYAML、消费者登记
      完整性测试。
- [x] GREEN：新增 `config/effective_config.py`、消费者登记表和校验器导入，同时保持现有
      测试辅助接口兼容。
- [x] REFACTOR：只有针对性测试通过后，才删除校验器中的重复合并/schema 代码。
- [x] 更新相关 Skill/config 说明，优先使用共享输出，同时保留现有“报告并降级”路径。
- 回滚点：配置运行时抽取可以独立撤销，不影响其他阶段。

## 阶段三：增加工作流门禁和质量证据（TDD）

- [x] RED：增加占位 PRD、缺少复杂任务工件、只有种子的上下文、未勾选验收项、缺失或过期
      证据、任务状态保持不变等测试。
- [x] GREEN：实现 `config/workflow_check.py` 的 readiness、quality、completion 子命令，
      同时提供文本和 JSON 结果。
- [x] 验证 quality 不带 `--task` 时对 CI 完全无副作用；带 `--task` 时只写质量证据，不修改
      Trellis 任务状态。
- [x] RED/GREEN：增加确定性工作区指纹测试，覆盖已跟踪、未跟踪和已修改文件，同时排除
      证据文件及易变运行时/索引目录。
- [x] REFACTOR：共享解析器与结果结构，确保所有任务状态操作保持只读。
- [x] 运行 workflow-check 针对性测试，确认不会递归启动完整测试套件。
- 回滚点：检查器与证据测试独立于 Trellis 内部实现。

## 阶段四：集成宿主、诊断和文档

- [x] 更新项目与全局 AGENTS 模板：共享 CLI 存在时由原生 Trellis 质量流程调用；不得新增
      Skill，也不得修改宿主生成 helper。
- [x] 修复 `trellis/config-check.sh` 顶层 MCP 节解析，并增加回归测试。
- [x] 更新 README 与 Trellis README，说明 MCP 安全策略、有效配置、工作流检查、安装和
      运行时依赖以及真实包内容。
- [x] 新增“未发布”变更记录和第三方归属说明；不提升 manifest 版本，不声称已经发布。

## 阶段五：端到端测试与 CI

- [x] 增加临时项目 E2E，覆盖 planning → readiness → 质量证据 → completion，包括证据
      过期失败和任务状态不变。
- [x] 增加 Ubuntu 与 macOS 的 GitHub Actions，统一使用共享质量命令。
- [x] 验证 CI YAML 和本地命令不依赖开发者绝对路径、Recallium 在线状态或 GitNexus 索引。

## 阶段六：最终验证与评审

- [x] 每个 TDD 循环后运行对应针对性测试。
- [x] 运行 `python3 scripts/validate-all-skills.py`。
- [x] 运行 `python3 -m unittest discover -s tests`。
- [x] 对发布的 Shell 脚本运行 Bash 语法检查。
- [x] 对发布的 Python 代码运行编译检查。
- [x] 运行 `git diff --check`。
- [x] 运行共享质量入口并确认写入新鲜证据。
- [x] 勾选所有 PRD 验收项后运行 completion 门禁。
- [x] 执行 Trellis 原生质量评审；修复 P0/P1 后重新运行相关 TDD 和完整检查。
- [x] 本任务属于跨模块高风险修改且已使用图谱分析，因此最终执行 GitNexus 变更范围复核；
      隐藏 `.trellis/` 行为继续以源码核验。
- [x] 报告修改文件、验证命令和结果、已知限制、此前脏工作区文件，并明确未 commit/push。

## 阶段七：用 Grill with Docs 替换 Grill Me（TDD）

- [x] RESEARCH：核对 Matt Pocock 上游当前提交、完整 Skill 清单、组合依赖和许可证，记录与 Trellis 的冲突矩阵。
- [x] RED：把路由测试改为要求 `grill-with-docs`、Trellis PRD 唯一性、`.trellis/spec/domain/` 术语边界和 `.trellis/spec/decisions/` 决策边界，确认旧实现失败。
- [x] GREEN：用 Trellis 兼容 `grill-with-docs` 替换旧目录，引入适配后的 `diagnosing-bugs`、`codebase-design`、`resolving-merge-conflicts`，更新 manifest、安装器期望、AGENTS 模板、README 和归属说明。
- [x] REFACTOR：删除所有活动配置中的 `grill-me` 路由，保留历史 Trellis task 记录不改写；运行 Skill Creator 校验与针对性测试。
- [x] VERIFY：运行完整 Skill 校验、单元测试、Shell/Python 语法、`git diff --check`、workflow quality/completion 和 GitNexus 变更范围复核。
