# 运行时加固调研记录

## 已检查范围

- MCP 模板与宿主合并链路：
  - `trellis/codex/mcp/*.toml`
  - `trellis/cursor/mcp/servers.json`
  - `scripts/lib/merge_host_mcp.py`
  - `scripts/install-{codex,cursor}-merge.sh`
- 有效配置链路：
  - `config/defaults.yaml`
  - `config/project-config.schema.yaml`
  - `scripts/validate-all-skills.py`
  - 各 Skill 的配置读取说明
- Trellis 任务生命周期与宿主辅助能力：
  - `.trellis/workflow.md`
  - `.trellis/scripts/common/task_store.py`
  - 自动生成的 `.claude` / `.cursor` `trellis-check` 辅助文件
- 质量检查范围：
  - 现有单元测试、Skill 校验器、Shell 脚本和 Python 模块
  - `trellis/config-check.sh`
  - README、manifest 和第三方归属说明

## 已确认问题

1. Codex 与 Cursor 模板中的 Recallium 仍使用远端明文 HTTP。用户已确认生产地址为
   `https://www.59005046.xyz:8102/mcp`。
2. 宿主合并器会直接写入内置或用户提供的 MCP URL，没有传输安全校验。校验应放在共享
   Python 合并边界中，避免 Codex 与 Cursor 两套逻辑产生偏差。
3. Shell 安装器已经在合并器修改目标文件前完成备份。因此 URL 校验失败可以在原文件
   未被修改的情况下退出，并继续满足现有时间戳备份契约。
4. 有效配置合并逻辑只存在于 `scripts/validate-all-skills.py`。GitNexus 显示
   `load_effective_config` 只有一个生产调用者，即校验器主入口；当前没有运行时命令负责
   输出合并后的配置。
5. Trellis 的 `task.py start` 与 `task.py archive` 是唯一状态机入口。工作流文档描述了
   规划和完成门禁，但项目没有只读、可执行的检查器来验证 PRD、设计、计划、上下文、
   验收项和新鲜的质量证据。
6. 仓库中的 `.claude` 与 `.cursor` Trellis 辅助文件由 Trellis 生成，并受模板哈希管理。
   直接修改会在后续 `trellis update` 时被覆盖，因此项目自己的适配逻辑必须放在这些
   生成文件之外。
7. 主 GitNexus 索引不包含隐藏的 `.trellis/` 路径。图谱可用于可见 Python 代码，但
   Trellis 生命周期结论必须通过源码核对，不能只依赖图谱推断。
8. GitNexus 将 `merge_codex_toml`、`merge_cursor_json`、`write_atomic`、
   `load_effective_config` 和 `validate_config` 的影响等级评为 LOW。其直接调用者仅位于
   各自本地 CLI 或加载链路中，先跑针对性回归、再跑完整测试即可覆盖风险。
9. `trellis/config-check.sh` 会把 `[mcp_servers.<名称>.env]` 等嵌套 TOML 节误报为 MCP
   服务器名。匹配规则应只接受 `mcp_servers.` 后恰好一段名称。
10. README 声称本包不包含 MCP 配置，但两个宿主安装器实际上都会合并内置 MCP 模板；
    README 还保留了错误路径 `CodexTamplate`。manifest 版本为 `3.0.0`，但没有变更记录，
    也没有说明 Karpathy 衍生材料的 MIT 第三方归属。

## 对设计的约束

- 在 MCP 条目进入合并前统一校验 URL。只允许 HTTPS 和本机回环 HTTP：`localhost`、
  `127.0.0.1`、`::1`。
- 将有效配置逻辑抽取到 `config/` 下可安装、可导入的模块中；保持校验器现有接口兼容。
- 新增一个平台无关的工作流检查 CLI。readiness 和 completion 不得修改 Trellis 任务状态；
  quality 只允许在活动任务目录写入机器可读证据。
- 质量证据必须绑定当前 Git HEAD 和确定性的工作区指纹，防止代码变更后继续复用旧成功结果。
- 原生 Trellis helper 继续负责质量评审。项目或全局规则只负责让 Codex、Cursor、Claude
  在可用时调用共享检查器，不引入新 Skill 或第二套状态机。
- CI 必须调用与本地相同的质量入口。工作流检查器自身的测试注入最小命令，避免测试套件
  递归调用自身。
