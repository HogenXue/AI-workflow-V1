# Windows PowerShell install scripts (parent)

## Goal

Windows 用户用 PowerShell 7+ 完成与现有 bash `scripts/install*.sh` **完整 1:1** 的安装能力；通过 parent/child 拆分交付并最终集成验收。

## Background

- 现有真相源：bash 安装器 + `.trellis/spec/scripts/installer-contracts.md`。
- 用户选择：完整 1:1、平行 PS 测试 + Windows CI、仅 `pwsh` 7+、`install.ps1` + `install.cmd`。
- 保留 bash；MCP merge 继续复用 `scripts/lib/merge_host_mcp.py`。
- CI：ubuntu/macos `quality` 保留；新增 `windows-ps-install` job。

## Task Map

| Child | Path | Status |
|-------|------|--------|
| Shared lib | `archive/.../07-27-ps-install-lib` | archived |
| Components | `archive/.../07-27-ps-install-components` | archived |
| Host merge | `archive/.../07-27-ps-install-merge` | archived |
| Entry | `archive/.../07-27-ps-install-entry` | archived |
| Tests/CI/docs | `archive/.../07-27-ps-install-ci-docs` | archived |

## Requirements

- R1–R5：见各 child 交付与 parent Decisions；集成审查通过。

## Acceptance Criteria (cross-child)

- [x] AC-P1: 五个 child 均已 archive，产物齐全（`install*.ps1`、`install.cmd`、`test_install_*_ps.py`）。
- [x] AC-P2: Windows + `pwsh` 下 `install.cmd` / `install.ps1` 分发与组件路径可用（entry/components/merge 测试 + dry-run）；完整交互全量 profile 未做 stdin E2E（与 bash 测法一致，靠 profile 函数 + 组件覆盖）。
- [x] AC-P3: 平行 PS 测试覆盖关键契约（project-root、冲突/回滚、备份唯一性、MCP remote HTTP）；dangling symlink 有测试，无特权时显式 skip。
- [x] AC-P4: CI 含 `windows-ps-install`（`windows-latest` + `pwsh`）；ubuntu/macos `quality` 未改意图。**远程 GHA 绿需在首次 push/PR 确认。**
- [x] AC-P5: README + `.trellis/spec/scripts/` 已记录 Windows 入口、`pwsh`、双实现约定。

## Integration Notes

- 功能代码（scripts/tests/README/CI/spec）仍在工作区，需单独提交（archive 仅提交了 task 目录 chore）。
- Symlink 特权限制已写入 spec；不阻塞本 parent 收尾。

## Out of Scope

- 废弃 bash；方案 C；skill 内 `validate.sh`；产品侧 Windows hooks 限制。

## Decisions

- D1–D6：完整 1:1；`--link` 失败回滚；平行测试 + Windows CI；仅 pwsh 7+；ps1+cmd；parent+5 children。
