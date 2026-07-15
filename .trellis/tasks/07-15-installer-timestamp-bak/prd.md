# Unify timestamped installer backups

## Goal

确保所有一键安装入口在覆盖、删除或迁移现有目标前创建可恢复、不可覆盖的时间戳 `.bak` 备份，并修复宿主 hooks 替换过程中误删无关内容或残留旧文件的问题。

## Requirements

1. 现有文件备份名使用 `<filename>.<UTC timestamp>.bak`；现有目录使用 `<dirname>.<UTC timestamp>.bak`。
2. 时间戳必须足以避免连续执行碰撞；若目标仍存在，必须生成唯一名称，不得覆盖历史备份。
3. 任何覆盖、删除或迁移只能在备份成功后发生；备份失败必须终止当前组件且保留原目标。
4. `skills`、`agents`、`config`、`codex-merge`、`cursor-merge` 及兼容入口必须遵循同一契约。
5. Codex 项目 hooks 更新只能替换 `.codex/hooks.json` 与 `.codex/hooks/`，不得删除 `.codex` 中的无关内容。
6. Cursor hooks 更新在备份后必须完整替换旧 hooks 目录，不能保留模板中已删除的脚本。
7. dry-run 与文档必须反映新的备份命名和行为。
8. 并发备份必须原子预留唯一名称，不能暴露未完成的 `.bak`。
9. MCP 目标即使是断开的符号链接也必须先备份；后续项目级步骤失败时必须回滚已完成的 MCP 修改。
10. 默认备份根统一使用 `.ai-workflow-backups`；旧备份目录保留但不再写入。
11. 安装目标不得与包内源码目录重叠，Cursor MCP 目标不得指向包内 MCP fragment。
12. 自定义备份目录不得位于正被整体备份的目标内部，避免递归自复制和备份随目标一起被删除。

## Acceptance Criteria

- [x] 每类安装目标都有自动化测试证明原内容在写入前被备份为 `.<UTC timestamp>.bak`。
- [x] 连续备份不会覆盖已有备份。
- [x] 备份失败时原目标不变，安装返回非零。
- [x] Codex hooks 替换保留 `.codex` 下无关文件。
- [x] Cursor hooks 替换清除旧 hook 文件，同时保留 `.cursor` 下无关文件。
- [x] Skill 校验、全部单元测试和 shell 语法检查通过。
- [x] 并发备份、不可写备份目录和不完整备份发布均有自动化证据。
- [x] Codex/Cursor 的断链 MCP 目标先备份，项目冲突后 MCP 恢复原状。
- [x] 默认备份根统一，危险的源码/目标重叠被拒绝。
- [x] 目标内部的自定义备份目录在任何写入前被拒绝。

## Out of Scope

- 改变 Codex/Cursor MCP 内容或 Skill 功能。
- 重构 Trellis task 生命周期。
- 清理与本任务无关的现有工作区改动。
