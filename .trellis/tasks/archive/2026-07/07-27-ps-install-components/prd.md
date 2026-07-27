# PS install components

## Goal

PowerShell 版 `skills` / `config` / `graphify` / `agents` 组件，行为与对应 `.sh` 1:1。

## Depends on

- **Requires** `07-27-ps-install-lib` completed (or at least `install-lib.ps1` usable).

## Requirements

- R1: 标志与 bash 对齐：`--dry-run`、`--link|--copy`、`--replace`、`--prune-legacy`、`--prune-other-root`（skills）、`--target`、`--backup-dir`、agents 的 `--apply` / `--agents-home` 等。
- R2: conflict 无 `--replace` → 非零 + 保留原文件；`--link` 失败 → rollback + 非零。
- R3: manifest 驱动 skills；legacy prune 需备份；default targets 使用 `$HOME/.agents/...`。
- R4: source/target overlap 拒绝。

## Acceptance Criteria

- [ ] 四个组件脚本可通过 `install.ps1 <component>` 或直接 `pwsh -File install-<component>.ps1` 调用（与 bash 双入口习惯一致）。
- [ ] dry-run 不写盘；copy/replace/prune 行为匹配 bash 测试意图（由 ci-docs 或本 child 针对性测试覆盖关键路径）。

## Out of Scope

- codex/cursor merge；交互向导；CI。
