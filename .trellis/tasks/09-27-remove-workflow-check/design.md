# 删除工作流检查器设计

## 当前链路

`config/workflow_check.py` 位于 CodexTamplate，config 组件安装会复制整个 `config/` 到 `~/.agents/config`。模板版与当前生效的全局 AGENTS、AGENTS.project、README、Trellis 说明、CI 和测试均引用它。EGM 仓库从未跟踪该脚本，但此前可跨仓调用模板副本。

## 删除边界

1. 源码及已安装副本均删除。源码由 Git 恢复；已安装副本可由历史 Git 版本重新安装，当前不保留运行副本。
2. 删除 helper 专用的 `verification.report_unexecuted_steps`、`verification.require_spec_for_complex_change` 配置键、消费者登记和独立测试；保留 `effective_config.py` 及其他配置合同。
3. 全局 AGENTS 模板、当前 Codex 全局规则、EGM 项目补充模板与实际项目规则中删除 helper 的执行步骤与基于指纹的证据复用规则。Trellis task 状态仍由 `task.py` 管理；实现完成后使用项目 `trellis-check` 与受影响范围的真实检查命令，并在当前任务记录结果。归档前核对验收项、实际证据和未覆盖边界。
4. CI 改为直接运行 `scripts/validate-all-skills.py` 与 `unittest discover`。既有 Windows 安装测试 job 保持。
5. 安装器仍复制 config 组件中其余文件；测试断言目标不包含 helper。
6. 历史任务报告和既有 `verification.json` 是审计记录，不回写或删除。

## 兼容与风险

- 已安装的其他宿主如 Cursor/Claude 本机未发现该脚本；本次仅删除确认存在的 Codex 配对副本。
- EGM 任务的既有证据会保留，但后续不再尝试通过该 helper 生成新证据。
- 当前模板 README 已有并行修改，编辑时仅处理 workflow-check 相关段落。
