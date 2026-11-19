# Claude connector repair evidence

## Authorized scope and baseline

The user explicitly requested removing Claude's Headroom connector, installing
Mem0, and repairing Recallium on 2026-11-05. This task changes local host
configuration, not application source or the package installer. The pre-existing
untracked `.cursor/rules/ai-workflow-global.mdc` is outside this task.

Before mutation, `claude mcp list` reproduced:

- Headroom: SSE connection reset.
- Recallium at `http://www.59005046.xyz:8102/mcp`: version negotiation timeout.
- Mem0: skipped because its URL entry had `transport: http` but no `type`.
  It also pointed at Recallium's 8102 port instead of Mem0's 8103 port.
- GitNexus: connected.

The desktop app's existing session showed Recallium's POST connection error.

## Configuration repair

Used native `claude mcp remove --scope user` and
`claude mcp add --scope user --transport http` commands to remove Headroom and
configure:

- Recallium: `https://www.59005046.xyz:8102/mcp`.
- Mem0: `https://www.59005046.xyz:8103/mcp`.

Backup:
`/Users/hogen/.claude/.ai-workflow-backups/claude.json.memory-connectors-20261105T090255292308Z.bak`.

No credentials were added, no memory facts were written, and no backend was
installed or replaced. The existing GitNexus definition was preserved.

The desktop session's Recallium Reconnect action subsequently displayed
`Connected · 28 tools`. Its server list still retained the old Headroom entry
and did not discover newly added Mem0. Reopening the session or restarting the
app after active work is the remaining UI refresh boundary; this task did not
stop the user's running session or its jobs.

## Network diagnosis and repair

Correct HTTPS entries initially connected, but repeated fresh connections
still showed handshake resets/timeouts. TLS probes with Python, curl, Node,
Bun and OpenSSL confirmed this was not only a Claude configuration warning.
OpenSSL received no peer certificate before the connection closed.

The active Clash Verge controller identified the existing
`DOMAIN-SUFFIX,59005046.xyz,DIRECT` route. An endpoint-specific controller probe
returned HTTP 504 on DIRECT and HTTP 200 with a 781 ms measurement through the
existing US automatic group. No proxy mode or global group selection was changed.

Added two persistent subscription rules, before the existing direct rule:

```yaml
- 'AND,((DOMAIN,www.59005046.xyz),(DST-PORT,8102)),🇭🇰 香港 02'
- 'AND,((DOMAIN,www.59005046.xyz),(DST-PORT,8103)),🇭🇰 香港 02'
```

Only these endpoint/port pairs use the selected proxy. The existing domain's
other ports and all original rules are retained. The initial automatic group
trial was insufficient because its selected nodes varied; independent tests of
the final Hong Kong 02 node reached 8102 in 696 ms and 8103 in 740 ms.

Persistent rule file:
`/Users/hogen/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/profiles/rHC1lAShoXKf.yaml`.

Original rule backup:
`/Users/hogen/.claude/.ai-workflow-backups/clash-rules.memory-connectors-20261105T091029040139Z.yaml.bak`.

Used Clash Verge's **重新激活订阅** action. Its runtime Rules page visibly
confirmed both exact endpoint rules selecting Hong Kong 02 ahead of DIRECT.

## Backend verification

After the final routing change, certificate-verified MCP `initialize`,
`notifications/initialized`, and `tools/list` requests passed on both endpoints:

- 8102: `minime-mcp-python` 1.23.3; 28 tools, including `get_rules` and
  `search_memories`.
- 8103: `memory-mcp` 1.28.1; exactly six tools: `memory_add`, `memory_search`,
  `memory_get`, `memory_update`, `memory_delete`, and `memory_list`.

TLS certificate verification remained enabled throughout the repair.

Default-runtime native health checks then passed twice, but a third fresh
check connected to Recallium and timed out during tool discovery. The documented
v1 compatibility runtime subsequently passed three consecutive independent
`claude mcp list` checks (11.48 s, 8.01 s and 9.46 s), with all three configured
servers fully connected in each check.

Added only `env.MCP_SDK_GENERATION = "v1"` to
`/Users/hogen/.claude/settings.json`, preserving its existing environment setting.
Backup:
`/Users/hogen/.claude/.ai-workflow-backups/settings.json.memory-connectors-20261105T091754111919Z.bak`.
An ordinary `claude mcp list` invocation with no shell environment overrides then
confirmed all three servers connected. This supports the compatibility setting
for this installation; it does not prove every default-runtime failure was
caused by the SDK version.

The compatibility runtime is picked when a Claude process starts. The existing
desktop session was kept running; reopen the session or restart after its work
finishes to pick up both the runtime setting and added/removed server list.

## Sources

- Claude configuration and runtime reference:
  https://code.claude.com/docs/en/mcp
- Clash Verge custom rule ordering, logical AND and destination ports:
  https://www.clashverge.dev/guide/rules.html

## Native quality gate

Performed the local `trellis-check` checklist inline, with `code-review` analysis
inside the same gate:

- **Spec:** all requested configuration changes match the PRD. Both services
  completed TLS-verified protocol initialization and tool discovery; three
  compatibility-runtime native checks and the final installed-setting native
  check passed. Desktop Recallium visibly connected with 28 tools. The retained
  old desktop list is explicitly documented above.
- **Standards:** native Claude formats, user scope, HTTPS verification, timestamped
  backups, minimal additive proxy rules, and unrelated configuration preservation
  checked. No installer, packaged template, hook, Codex configuration, or Git
  changes. No findings in task scope.
- **Preservation:** final deep JSON comparison matched every original value
  outside the three requested MCP entries. Native CLI serialization had omitted
  the existing `projectOnboardingSeenCount` counter for the user's milk worktree;
  restored only that missing integer using a concurrent-write guard, then
  confirmed exact equality outside the authorized MCP entries. The settings
  comparison found exactly the one compatibility environment addition. YAML
  comparison found exactly the two new endpoint rules and retained all originals.
- **Scope:** only this task's PRD/evidence/metadata were added in the repository;
  the original untracked Cursor rule was preserved. No application source code
  changed, so repository implementation tests/lint were not applicable. Live
  integration checks cover the actual configuration changes.
- **Shared-helper degradation:** `config/workflow_check.py` is absent in this
  checkout. Used native task validation, scoped configuration comparison, live
  MCP checks and this Spec/Standards review instead; no shared readiness,
  quality or completion command is claimed. No task archival or Git action.

## Remaining boundaries

- Restart/reopen the existing Claude session after its active work to refresh
  the full connector list and runtime. Its already reconnected Recallium remains
  available in the meantime.
- The two routing exceptions depend on the active subscription retaining the
  existing Hong Kong 02 node. Original direct rules are backed up and preserved.
- Package source templates were outside this host-repair scope. Reinstallation
  should preserve the verified Mem0 endpoint rather than replacing it with a
  default copied from Recallium.
