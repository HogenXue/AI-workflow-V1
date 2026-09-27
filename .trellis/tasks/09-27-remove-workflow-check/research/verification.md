# 删除 workflow_check 的验证记录

## 范围

- 仓库历史显示该脚本由 CodexTamplate 的 2026-07-16/18 提交加入，属于额外自定义门禁；
  EGM 的 `.agents/skills/trellis-check/SKILL.md` 和 `.trellis/agents/check.md` 仍存在。
- 删除模板源码 `config/workflow_check.py`、其专用测试和本机 Codex 配对安装副本。
- 清理全局/项目 AGENTS、安装说明、配置键/消费者、CI 及相关测试。
- 保留 EGM 既有 `verification.json` 和其他历史任务记录。

## RED

- 修改安装与模板契约断言后，运行 `test_validate_all_skills.py`：7 个断言失败，
  旧 CI、README、AGENTS 和配置仍引用脚本。
- 运行 `test_install.py`：1 个断言失败，config 组件仍安装脚本。

## GREEN

- `python3 -m unittest discover -s tests -p test_validate_all_skills.py`：37 项通过。
- `python3 -m unittest discover -s tests -p test_install.py`：24 项通过；
  覆盖全新安装不带脚本，以及 `--replace` 备份并移走旧脚本。
- `python3 -m unittest discover -s tests -p test_effective_config.py`：6 项通过。
- `python3 scripts/validate-all-skills.py`：9 个当前 Skill 通过。
- 模板和已安装 `effective_config.py --validate-consumers`：均通过。
- CI YAML 解析、模板/生效全局 AGENTS 与 config 文件一致性、任务相关
  `git diff --check`：通过。
- 模板和 `~/.agents/config` 中的脚本均不存在；EGM 既有标签任务
  `verification.json` 仍存在。
- 按项目 Trellis Check 清单核对本任务 PRD、设计、安装器规范、配置加载、CI、
  生效的 AGENTS 与已安装配置；未发现剩余活动调用路径。

## 未运行

- Windows PowerShell 安装测试：本机无 `pwsh`；CI 的 Windows job 保持不变。
- 全部单元测试：本轮只运行受影响测试文件，不把定向通过描述为全量通过。
- 其他宿主重装、commit、push：未执行。

## 并行改动

`README.md` 原有的局域网 MCP 说明修改保留；`scripts/lib/merge_host_mcp.py`、
`tests/test_install_interactive.py` 与根 `AGENTS.md` 的任务外变化未触碰。
