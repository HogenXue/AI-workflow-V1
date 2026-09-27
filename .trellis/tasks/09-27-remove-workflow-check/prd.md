# 移除共享 workflow_check 工作流检查器

## Goal

删除额外的 `workflow_check.py` 质量门禁，使 Trellis 原生任务流程、项目检查命令和真实测试结果直接承担规划与质量核对，不再安装或要求调用该脚本。

## Requirements

- 删除 `CodexTamplate/config/workflow_check.py` 和当前 Codex 配对目录 `~/.agents/config/workflow_check.py`，未来的 config 组件安装不得再提供该脚本。
- 清理模板、当前生效 `~/.codex/AGENTS.md` 和 EGM 项目级 `AGENTS.md` 中对 `readiness / quality / completion` helper 的调用要求；保留 Trellis task、原生 `trellis-check`、必要定向检查、真实证据和最小验证范围。
- CI 改为直接运行本包的 Skill 校验与单元测试；安装器继续复制其余配置文件。
- 删除仅服务于该脚本的测试和配置项，更新安装/模板/CI 契约测试与说明。
- 保留既有任务下的 `verification.json` 和历史质量记录，作为曾经执行的事实，不追溯删除。
- 不修改 EGM 的标签业务代码、不改动其他并行任务文件，不 commit、push 或安装到其他宿主。

## Acceptance Criteria

- [x] 模板仓库和当前 Codex 配对配置目录均没有可执行的 `workflow_check.py`。
- [x] 模板、当前生效的全局及 EGM 项目级 AGENTS 不再要求调用该 helper；安装说明、CI、配置消费者和测试无失效引用。
- [x] config 组件安装测试证明不会重新安装该脚本，仍能安装 `effective_config.py` 与必要配置文件。
- [x] CI 使用直接检查命令；对应定向测试与配置校验通过。
- [x] EGM 既有 `verification.json` 和任务记录保留；两个仓库的并行未提交改动未被覆盖。
