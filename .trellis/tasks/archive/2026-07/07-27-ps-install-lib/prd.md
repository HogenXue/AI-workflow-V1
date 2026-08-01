# PS install shared lib

## Goal

提供与 `scripts/install-lib.sh` 1:1 的 `scripts/install-lib.ps1`，供其余 PS 安装器 dot-source。

## Depends on

- None（首个 child）。Parent: `07-27-windows-ps-installers`。

## Requirements

- R1: 实现 prompt Y/N、candidate git root、`Resolve-ProjectRoot`（显式 path / skip / TTY 菜单；禁止静默应用 git root）。
- R2: 备份：UTC stamp、`.bak`、lock 目录预留、staging→publish、冲突后缀、失败不留下半成品 `.bak`。
- R3: restore / rollback-target；path normalize、overlap、within 检查。
- R4: 稳定 `ERROR:` / `SKIP:` / `BACKUP:` / `PROJECT-ROOT:` 消息与 bash 语义对齐。
- R5: 仅在 pwsh 7+ 下可用（或由调用方保证）；函数可被组件脚本复用。

## Acceptance Criteria

- [ ] `install-lib.ps1` 存在且导出与 bash 对等的能力面。
- [ ] 有针对并行备份唯一性、不可写 backup dir、nested backup reject、失败不发布 partial bak 的可自动验证（本 child 测试或为 ci-docs 预留的可调用 harness）。
- [ ] 不修改 bash `install-lib.sh` 行为（除非发现共享契约 bug 并同步两边——本 child 默认不改 bash）。

## Out of Scope

- 各组件安装逻辑、交互主菜单、CI 矩阵。
