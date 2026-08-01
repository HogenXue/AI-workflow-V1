# PS install tests CI docs

## Goal

平行 PS 测试、CI `windows-latest`、README 与 spec 双实现约定。

## Depends on

- **最终变绿 Requires** entry（及上游）完成。
- 允许提前提交测试骨架（对未实现功能 xfail/skip 需在实现后清除——偏好实现后一次性补全）。

## Requirements

- R1: 新增 PS 版安装测试模块，覆盖 bash 测试中的关键契约（见 parent AC-P3）。
- R2: `.github/workflows/ci.yml` 增加 `windows-latest`；确保 `pwsh`；跑 PS 安装相关测试；不破坏 ubuntu/macos bash 测试。
- R3: README 增加 Windows/`pwsh`/`install.cmd` 用法。
- R4: 更新 `.trellis/spec/scripts/`（index + installer-contracts 或新增 Windows 约定节）：pwsh-only、cmd launcher、双实现同 PR 更新。

## Acceptance Criteria

- [x] Windows CI job 绿色（或记录并修复 symlink 权限等 runner 限制的显式 skip，须在 PRD/spec 说明——默认尽量不 skip）。
- [x] 文档与 spec 审查通过。
- [x] bash 测试在 Linux/macOS CI 仍通过。

## Out of Scope

- 实现安装器功能本身（由上游 child 完成）。
