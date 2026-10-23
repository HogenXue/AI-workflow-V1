# Host compatibility evidence and native discovery boundary

Task: `.trellis/tasks/10-23-unify-skill-host-compatibility`

Verified: 2026-10-23 (Asia/Shanghai). This note records previously fetched official sources, local CLI/schema inspection, and an isolated protocol fixture. No new browsing, repository mutation, or live HOME discovery was performed while preparing this note.

## Local executable evidence

Read-only `--version` checks returned:

| Executable | Result |
| --- | --- |
| `codex` | `codex-cli 0.154.0` |
| `cursor-agent` | `2026.04.17-787b533` |
| `claude` | `2.1.275 (Claude Code)` |
| `mcode`, `codebuddy`, `workbuddy` | Not found on PATH |

PATH absence does not establish whether a corresponding desktop app is installed. Official current documentation can describe newer behavior than these local executables. Native acceptance must name the actual tested host/version.

## Codex native skills/list probe

Probe: `/private/tmp/codex-discovery-396u6t4q/probe_skills.py`

SHA-256: `295a6a90437a3e9f43255cf9bbe055e4f4d10dab179e94629ed132b12624e408`

The probe is suitable for checking **Codex native discovery after the four-host update**. It is not a common protocol client for Cursor, MiniMax or WorkBuddy; no claim of native discovery for those three hosts follows from its result.

The locally generated protocol schema establishes:

- `v1/InitializeParams.json`: required `clientInfo.name` and `clientInfo.version`; `capabilities.experimentalApi` may be false.
- `v2/SkillsListParams.json`: `cwds` is an array of strings; `forceReload: true` bypasses the Skill cache.
- `v2/SkillsListResponse.json`: `data[]` contains `cwd`, `skills[]`, and `errors[]`. A Skill has `name`, `path`, `enabled`, `scope`, description and optional metadata.
- No `allow_implicit_invocation` or invocation-policy field is returned by this response schema.

Generation command already run successfully:

```bash
codex app-server generate-json-schema --out /private/tmp/codex-discovery-396u6t4q/schema
```

The probe starts `codex app-server --stdio` as a separate process, writes one JSON message per line, waits for initialization, lists Skills, and closes the process. The only sent methods are:

```json
{"id":1,"method":"initialize","params":{"clientInfo":{"name":"local_skill_discovery_audit","version":"1.0.0"},"capabilities":{"experimentalApi":false}}}
{"method":"initialized"}
{"id":2,"method":"skills/list","params":{"cwds":["/absolute/project/path"],"forceReload":true}}
```

It never sends `thread/start`, `turn/start`, model requests, configuration writes, hook-trust operations or credential-management requests. Like any app-server process, it may create ordinary runtime/cache/log data in its selected Codex home; it must not be described as a byte-for-byte no-write audit of that home.

Only selected response metadata is persisted: `name`, `path`, `enabled`, `scope`, `pluginId`, errors and basic server identity. Skill bodies, dependencies, unselected notifications and stderr are not persisted by this probe. The result still contains local absolute paths and possibly parser diagnostics; inspect/sanitize before publishing it.

### Completed fixture

A separate temporary HOME and CODEX_HOME were supplied using the subprocess environment, with only basic runtime environment variables retained and credential variables omitted. An isolated `~/.agents/skills/discovery-probe/SKILL.md` was created. The three-message handshake completed with 7 Skills and 0 errors; `discovery-probe` was returned as `enabled: true`, `scope: user` at the expected fixture path.

Evidence: `/private/tmp/codex-discovery-396u6t4q/fixture-result.json`.

This proves the installed CLI supports the protocol and scans the supplied fixture. It does not prove live installation results.

### Root-owned post-install invocation

Use the normal installed Codex environment when intentionally checking actual local discovery, rather than the fixture environment. Write the result to the task's private evidence location first:

```bash
python3 /private/tmp/codex-discovery-396u6t4q/probe_skills.py \
  --cwd /Users/hogenxue/Projects/CodexTamplate \
  --output /absolute/private-evidence/codex-native-skills.json
```

Compare returned paths and enabled names with the package manifest, count same-name entries by source, and inspect parser errors. The API's `enabled` property does not prove implicit-invocation policy or model selection behavior. CLI discovery does not prove the desktop app menu has refreshed, because the app may have a different bundled runtime and cache. Cursor/MiniMax/WorkBuddy native loading and UI menu checks remain `not_run` until independently exercised.

Source: [Codex App Server](https://learn.chatgpt.com/docs/app-server), corroborated by local generated JSON schema and the fixture above.

## Skill discovery and invocation contracts

### Codex

Current official local discovery uses user `~/.agents/skills` and repository `.agents/skills` from the working directory toward the repository root. Same-named Skills are not merged; both can appear in selectors. Symlinked Skill folders are supported. Explicit invocation is `$skill-name` or `/skills` in the CLI/IDE. `agents/openai.yaml` with `policy.allow_implicit_invocation: false` controls explicit-only behavior; a Claude-style frontmatter flag alone is insufficient evidence of Codex enforcement.

Source: [Build skills](https://learn.chatgpt.com/docs/build-skills).

### Cursor

Official current discovery includes user and project `.agents/skills` and `.cursor/skills`, with compatibility loading from `.claude/skills` and `.codex/skills`. Project Skill directories can be nested and recursive. Installing byte copies in separate host directories can therefore expose multiple same-named Skills to one Cursor instance. The fetched page does not specify a reliable duplicate-name winner. `disable-model-invocation: true` makes a Skill explicit-only through `/skill-name`.

Source: [Cursor Agent Skills](https://cursor.com/docs/skills).

### Claude Code

Personal Skills use `~/.claude/skills`; project and ancestor `.claude/skills` are supported. `disable-model-invocation: true` prevents autonomous invocation, whereas `user-invocable: false` hides the user command. Current documented precedence is enterprise over personal over project for identical names, so project scope cannot be assumed to override user scope. Current direct `AGENTS.md` fallback is documented for v2.1.277+, newer than the tested local v2.1.275; preserve the supported `CLAUDE.md` entry.

Sources: [Claude Skills](https://code.claude.com/docs/en/skills), [Claude project memory](https://code.claude.com/docs/en/memory).

### MiniMax Code

The official source was inspected at fixed revision `da22f11c55d4748155d7162c1030414228a00565`. It includes `<dataDir>/skills` and external user roots `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`. External workspace roots include `.minimax/skills`, `.claude/skills`, `.agents/skills`. Configured priorities choose a same-name winner. `MINIMAX_DATA_DIR` takes precedence over `MAVIS_DATA_DIR`; default data directory is `~/.minimax`. Runtime Skill commands are exposed in supported ACP sessions, with built-in names winning collisions. No sufficient inspected evidence established hard enforcement of `disable-model-invocation` in this runtime; retain explicit-only prose but label native policy enforcement unverified.

Sources:

- [Discovery roots](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/packages/local-runtime/src/skills/roots.ts)
- [External-source priorities](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/packages/config/src/skills-config.ts)
- [Data directory selection](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/packages/tui/src/runtime/data-dir.ts)
- [ACP Skill command contract](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/docs/tui-capabilities.md)

### WorkBuddy / CodeBuddy

WorkBuddy documentation explicitly supports `.codebuddy/skills`, `.codebuddy/commands`, `.codebuddy/rules` and `.codebuddy/CODEBUDDY.md` for code projects, compatible with CodeBuddy Code. Project same-name configurations take priority over user configurations. CodeBuddy Skills document `disable-model-invocation: true` and `/skill-name`. This is a documentation-supported compatibility contract, not native WorkBuddy runtime acceptance on this machine.

Sources: [WorkBuddy project configuration](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project), [CodeBuddy Skills](https://www.codebuddy.cn/docs/cli/skills).

## Instructions, MCP and hooks

| Host | Verified configuration boundary |
| --- | --- |
| Codex | Nonempty global `AGENTS.override.md` takes precedence over `AGENTS.md`. Installing a base document cannot imply it is effective when an override remains. Hooks load from active `hooks.json` or inline `[hooks]`; matching sources are additive. Native hook trust is hash-based and user-reviewed through `/hooks`; configuration installation alone does not grant trust. Hooks are enabled by default in current documentation; preserve a user override of `false`. |
| Cursor | Project rules use `.cursor/rules/*.mdc` or project/nested `AGENTS.md`. User Rules are configured through the UI; no evidence here establishes `~/.cursor/AGENTS.md` as a global source. Global MCP uses `~/.cursor/mcp.json`; project MCP uses `.cursor/mcp.json`. Project hooks run relative to project root; user hooks relative to `~/.cursor`. `sessionStart` emits `additional_context`; `preToolUse` can emit `updated_input`. Multiple hook sources are additive. |
| Claude | Global instructions use `~/.claude/CLAUDE.md`; user MCP uses `~/.claude.json` top-level `mcpServers`; project MCP uses `.mcp.json`. Hooks belong in native settings files, e.g. `~/.claude/settings.json`; copying Codex hooks.json is not an equivalent integration. |
| MiniMax | Global instructions are `<dataDir>/AGENTS.md`. Official runtime code recognizes user `mcp.json` and `mcp/mcp.json`. Plugin hooks are version-specific, so Codex hook files cannot be assumed portable. |
| WorkBuddy / CodeBuddy | Global instructions use `~/.codebuddy/CODEBUDDY.md`. User MCP selects the first existing file: `~/.codebuddy/.mcp.json`, then `~/.codebuddy/mcp.json`, then `~/.codebuddy.json`. CodeBuddy documents JSONC support. Hooks are native settings entries with additive matching behavior. |

Primary sources:

- [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex Hooks](https://learn.chatgpt.com/docs/hooks)
- [Cursor Rules](https://cursor.com/docs/rules)
- [Cursor MCP](https://cursor.com/docs/mcp)
- [Cursor Hooks](https://cursor.com/docs/hooks)
- [Claude MCP](https://code.claude.com/docs/en/mcp)
- [Claude Hooks](https://code.claude.com/docs/en/hooks)
- [MiniMax global instruction reader](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/packages/local-runtime-v2/src/service/turn-system/agent-host/preparation/static-prompt-reader.ts)
- [MiniMax MCP file names](https://github.com/MiniMax-AI/minimax-code/blob/da22f11c55d4748155d7162c1030414228a00565/packages/local-runtime-v2/src/service/mcp/runtime/config-file.ts)
- [MiniMax plugin compatibility](https://github.com/MiniMax-AI/MiniMax-Code-Plugins/blob/main/docs/plugin-compatibility.md)
- [CodeBuddy memory](https://www.codebuddy.cn/docs/cli/memory)
- [CodeBuddy MCP](https://www.codebuddy.cn/docs/cli/mcp)
- [CodeBuddy Hooks](https://www.codebuddy.cn/docs/cli/hooks)

## Acceptance wording

Distinguish: package content validation; per-host file installation; preservation fingerprints; native discovery; invocation-policy handling; actual model workflow; application UI refresh; hook trust/execution; MCP connectivity. Evidence for one layer does not establish all the others. Avoid claiming perfect compatibility across versions or model behavior; state the verified host/version and remaining `not_run` coverage.
