# Implementation Plan

1. 更新安装器测试，覆盖统一 `.timestamp.bak` 命名、唯一性和宿主目录安全；运行目标测试确认 RED。
2. 在 `install-lib.sh` 实现统一备份 helper，并迁移 agents、skills、config、Codex/Cursor merge 调用方。
3. 收窄 Codex hooks 替换范围；让 Cursor hooks 做完整替换；运行目标测试确认 GREEN。
4. 更新 README、Trellis 迁移说明和 installer contract。
5. 运行 Skill 校验、完整 unittest、`bash -n`、`git diff --check` 与范围检查。

## Rollback Points

- helper 迁移后若组件测试未全绿，优先恢复该组件调用方式，不扩大修改范围。
- 不触碰现有 `trellis/AGENTS.global.md` 或其他 active task 内容。

## TDD Evidence

- RED：更新备份命名与宿主目录安全测试后，35 个目标测试中出现 9 failures + 1 error；命中旧目录式备份、同秒冲突、Codex 删除无关内容和 Cursor 残留旧 hook。
- RED（审计补充）：断链 MCP 备份、项目失败后的 MCP 回滚、统一默认备份根、并发备份、不可写备份目录、源码/目标重叠、目标内嵌备份目录和 Cursor fragment 自覆盖测试均先失败；不可写目录用例还复现了锁预留死循环。
- GREEN：统一 helper 并迁移五个组件后，全部目标测试通过；备份改为锁目录预留、staging copy 和原子发布，MCP 后续失败按精确备份回滚，危险的源码/目标重叠被拒绝。
- Full regression：`python3 -m unittest discover -s tests -v`，80 tests passed。
- Stability：并发备份唯一性测试额外连续运行 10 次，全部通过。
- Package validation：`python3 scripts/validate-all-skills.py`，6 Skills 全部 OK。
- Task validation：`python3 ./.trellis/scripts/task.py validate 07-15-installer-timestamp-bak` 通过。
- Static checks：安装脚本 `bash -n`、`python3 -m compileall -q scripts tests` 与 `git diff --check` 通过；`shellcheck` 未安装，已明确跳过。
