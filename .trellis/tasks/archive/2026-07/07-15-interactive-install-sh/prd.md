# Interactive multi-agent installer

## Goal

无参数运行 `scripts/install.sh` 进入交互向导：多选 **Codex / Cursor**，再「推荐全装」或「单组件」。按宿主职责安装 skills、配对 config、宿主 MCP、项目 hooks，以及规则落点（Codex→`~/.codex/AGENTS.md`；Cursor→`.cursor/rules/*.mdc`）。原则：职责映射、禁止目录照抄、不删另一宿主目录（[参考文](https://www.fanyamin.com/cong-cursor-qian-dao-codexbie-ji-zhao-chao-pei-zhi-xian-ba-nao-hui-lu-qian-guo-qu.html)）。

## Background

- 无参现状：Usage + exit 2。
- Codex≈AGENTS+skills+hooks 运行时；Cursor≈IDE 内 agent；Rules/Commands 同名不同义。
- Skill 读 `../../config/defaults.yaml` → config 必须与 skills 根配对。
- 本地两边 MCP 已有 recallium/gitnexus；Codex 缺 `hooks` 键；仓库已有 `.cursor/hooks*`。

## Requirements

1. TTY 无参：选 agent（Codex/Cursor 可多选）→ 推荐全装或单组件；非 TTY 无参 → Usage + exit 2。
2. **Codex 全装**：skills→`~/.agents/skills`；config→`~/.agents/config`；agents→`~/.codex`+`hooks=true`；MCP 合并进 `config.toml`；项目 `.codex/hooks.json`(+脚本)。
3. **Cursor 全装**：skills→`~/.cursor/skills`；config→`~/.cursor/config`；MCP 合并进 `~/.cursor/mcp.json`；确保/更新项目 `.cursor/hooks`；`.cursor/rules/ai-workflow-global.mdc` **在安装时从** `trellis/AGENTS.global.md` **动态生成**（frontmatter + 正文）；**不改**仓库根 Trellis `AGENTS.md`。
4. 冲突（skills/config/MCP/hooks/rules）：TTY 询问；非交互有 flag。
5. 不整文件覆盖宿主配置；不装全局 `~/.codex/hooks.json`；不删除 `.cursor/` 或 Codex 树；不把 Cursor rules 写入 Codex sandbox `rules`。
6. 有参 CLI 兼容；新能力可用新组件/flag（如 `codex-merge` / `cursor-merge`）。
7. mem0 无权威 URL 时：TTY 问或 `--mem0-url`。
8. **项目根必须显式选择**（Cursor rules/hooks、Codex 项目 hooks）：
   - **禁止**静默默认 `git rev-parse --show-toplevel`。
   - TTY：列出候选（可将当前 Git 根作为**可选项**），要求用户显式选择；允许粘贴路径；允许取消/跳过项目级安装。
   - 非交互：项目级写入必须 `--project-root PATH`；缺省则跳过项目级并打印明确提示（全局 skills/MCP/config/agents 仍可装）。

## Out of scope

- Claude 等其他宿主
- Commands↔slash 一对一
- 删除任一宿主旧配置
- 默认改 sandbox/approval_policy
- 覆盖项目根 `AGENTS.md`

## Acceptance Criteria

- [ ] TTY 可多选 Codex/Cursor 并完成全装/单组件
- [ ] 单选只写对应宿主；多选两边都写；互不删除
- [ ] Codex：`hooks=true`、MCP、项目 `.codex/hooks`（仅在显式 project-root 下）、skills/config 配对在 `~/.agents`
- [ ] Cursor：skills/config 配对在 `~/.cursor`、`mcp.json`、项目 hooks；rules `.mdc` 正文与 `trellis/AGENTS.global.md` 一致（动态生成）；根 `AGENTS.md` 未被安装器改写
- [ ] 无显式 project-root 时不写项目级文件，并有清晰提示
- [ ] 非 TTY 无参 Usage + exit 2
- [ ] `python -m unittest` 相关安装测试通过，并覆盖 merge/冲突 flag 路径

## Decisions (locked)

| # | Topic | Choice |
| --- | --- | --- |
| 1 | 交互深度 | 推荐全装 + 单组件 |
| 2 | Codex 配置 | hooks + 项目 hooks + MCP |
| 3 | Codex hooks 位置 | 全局 feature+MCP；项目 hooks 文件 |
| 4 | MCP/skills/config 冲突 | TTY 询问 |
| 5 | 非 TTY 无参 | Usage + exit 2 |
| 6 | Agent 选择器 | Codex/Cursor 可多选 |
| 7 | Cursor 配置面 | skills + mcp + 项目 hooks + rules mdc |
| 8 | Cursor「AGENTS」 | `.cursor/rules/*.mdc`，**安装时从** `AGENTS.global.md` **动态生成** |
| 9 | config 配对 | 随 skills 根：`~/.agents` vs `~/.cursor` |
| 10 | 映射原则 | 职责映射，禁止照抄 |
| 11 | 项目根 | **显式选择**；Git 根仅作候选；非交互需 `--project-root` 否则跳过项目级 |

## Open questions

无阻塞项。
