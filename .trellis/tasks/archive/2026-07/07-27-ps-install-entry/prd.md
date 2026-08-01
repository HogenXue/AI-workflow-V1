# PS install entry and cmd

## Goal

`scripts/install.ps1`（交互 + 分发）与 `scripts/install.cmd`（pwsh 启动器），对等 `install.sh` 入口行为。

## Depends on

- **Requires** components + merge 脚本已存在（至少可 dispatch）。

## Requirements

- R1: 无参 + 非 TTY → usage + exit 2；TTY → agent/mode/project-root/mem0/confirm 流程与 bash 一致。
- R2: `install_profile_codex` / `install_profile_cursor` 编排对等。
- R3: `install.cmd` 查找 `pwsh`，转发 `%*`；找不到则 stderr 提示安装 PS7 并以非零退出。
- R4: 未知组件 → exit 2；支持 `--help`。

## Acceptance Criteria

- [ ] `install.cmd skills --dry-run ...` 在已装 pwsh 的 Windows 上可工作。
- [ ] 非交互无参 exit 2 有测试覆盖。
- [ ] 交互路径可用脚本化 stdin 或组件标志覆盖（与现 bash 测法一致）。

## Out of Scope

- 实现 lib/组件内部细节；写 CI workflow（属 ci-docs）。
