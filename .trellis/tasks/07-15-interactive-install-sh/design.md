# Design: Interactive multi-agent installer

## Mechanism map

| Truth | Mechanism |
| --- | --- |
| 用户要直接跑 install.sh | TTY 无参菜单；非 TTY → Usage+exit 2 |
| 两套宿主职责不同 | Agent 多选 → 按 profile 派发，禁止目录照抄 |
| Skill 读 `../../config` | config target = parent of skills root |
| MCP 最好迁 | 同源 server 列表；Codex=toml、Cursor=json |
| Hooks 绑**用户选定**项目 | 只写显式 project-root 下的 `.codex/` / `.cursor/` |
| 不能猜错项目 | **禁止**静默用 cwd git root；必须选择或 `--project-root` |
| Cursor 规则 ≠ Codex rules | Cursor：`.cursor/rules/*.mdc`；Codex：`AGENTS.md` + hooks feature |
| 不破坏 Trellis 根 AGENTS | 安装器永不写仓库根 `AGENTS.md` |
| 冲突不安全静默覆盖 | TTY 问；flag 等价 |

## Profiles

```text
codex:
  skills_target:  ~/.agents/skills
  config_target:  ~/.agents/config
  agents_home:    ~/.codex          # AGENTS.md + hooks=true
  mcp_file:       ~/.codex/config.toml
  project_hooks:  <chosen-project>/.codex/hooks.json + hooks/

cursor:
  skills_target:  ~/.cursor/skills
  config_target:  ~/.cursor/config
  rules_target:   <chosen-project>/.cursor/rules/<generated>.mdc
  mcp_file:       ~/.cursor/mcp.json
  project_hooks:  <chosen-project>/.cursor/hooks.json + hooks/
```

Multi-select runs each selected profile sequentially after one confirmation summary.

## Project root resolution

Needed for: Cursor `.cursor/rules` + `.cursor/hooks`, Codex project `.codex/hooks`.

**Never** auto-apply `git rev-parse --show-toplevel` without an explicit user choice.

| Mode | Behavior |
| --- | --- |
| `--project-root PATH` | Use that path for project-scoped writes |
| TTY interactive | Show candidates (e.g. current git root as option 1), custom path entry, and **skip project-scoped** |
| Non-interactive without `--project-root` | Skip project-scoped steps; print clear message; continue global installs |

Global installs (skills, paired config, host MCP, Codex `~/.codex/AGENTS.md` + `hooks=true`) do **not** require a project root.

## Architecture

```text
scripts/install.sh
  ├─ args → skills|agents|config|codex-merge|cursor-merge
  ├─ no args + non-TTY → usage exit 2
  └─ no args + TTY → menu
        ├─ pick agents (codex/cursor, multi)
        ├─ pick project root (explicit) or skip project steps
        ├─ recommended full | single component
        └─ dispatch per profile

scripts/install-skills.sh / install-config.sh / install-agents.sh  # existing
scripts/install-codex-merge.sh   # MCP toml + optional project .codex hooks
scripts/install-cursor-merge.sh  # MCP json + optional project hooks/rules
scripts/install-lib.sh           # shared prompts, project-root helpers (optional)

trellis/codex/   # MCP toml fragments, hooks templates
trellis/cursor/  # MCP json fragments, rules mdc template, hooks templates
```

## MCP merge contract

Servers: `gitnexus`, `recallium`, `mem0`.

| Host | Format | Notes |
| --- | --- | --- |
| Codex | `[mcp_servers.X]` sections | backup; append or overwrite on confirm |
| Cursor | `mcpServers` object in JSON | backup; merge per key |

Flags: `--mcp-keep` / `--mcp-overwrite`; `--mem0-url`; `--project-root`; `--skip-project`.

## Compatibility / rollback

- Existing CLI tests stay green; never delete other host’s files; atomic MCP write after backup.
- Parent/child: single task.
