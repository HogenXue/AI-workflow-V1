# Timestamped Installer Backup Design

## Boundary

将备份命名与复制逻辑集中在 `scripts/install-lib.sh`。组件仍负责决定哪些目标即将被覆盖，以及失败后的局部回滚。

## Backup Contract

- 文件：`<backup-dir>/<basename>.<UTC timestamp>.bak`
- 目录：`<backup-dir>/<basename>.<UTC timestamp>.bak/`
- 时间戳使用 UTC 秒级格式；同秒冲突追加递增序号。
- 通过锁目录原子预留名称，先复制到锁内 staging payload，再 rename 为最终 `.bak`。
- helper 输出实际备份路径，供组件记录并在失败时恢复。
- backup helper 只复制，不移动原目标；组件在备份成功后再替换目标。
- 若备份目录等于目标或位于目标内部，helper 在创建目录前拒绝执行，避免递归自复制。

## Host Replacement

- Codex：分别备份并替换 `hooks.json` 和 `hooks/`，保留 `.codex` 其余内容。
- Cursor：分别备份 rules、hooks.json、hooks/；备份后删除旧 hooks/ 再复制模板。
- MCP：wrapper 在调用原子合并 helper 前备份现有目标。
- MCP 已更新但后续项目级步骤失败时，wrapper 恢复原目标或移除本次新建目标。

## Compatibility

保留现有 CLI flags 和 `--backup-dir` 语义。默认备份根统一为宿主配对根下的 `.ai-workflow-backups`；旧备份目录保留。`trellis/install.sh` 继续委托统一 agents 组件。

## Rollback

组件写入失败时使用本次返回的备份路径恢复；若目标原先不存在，则移除本次新建目标。历史 `.bak` 不参与自动清理。

回滚边界是单组件：完整安装的后续组件失败时，不撤销已经成功的前序组件。备份名称发布支持并发不覆盖，但目标写入不做跨安装器串行化，因此不支持同时运行多个安装器。
