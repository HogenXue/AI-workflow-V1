# Design

## Verified host contracts

MiniMax source was inspected at `564e9166d81f87b0b767b005e4779d4697b512be`:
`packages/local-runtime/src/skills/roots.ts` discovers `<dataDir>/skills`;
`packages/local-runtime-v2/src/service/turn-system/persistence/global-instructions.ts`
reads `<dataDir>/AGENTS.md`; `service/mcp/runtime/config-file.ts` recognizes
`mcp.json` and `mcp/mcp.json`, and `runtime/config.ts` uses `type` for transports.
The official README documents `MINIMAX_DATA_DIR` / `MAVIS_DATA_DIR` overrides.

WorkBuddy's official documentation describes compatibility with CodeBuddy user
configuration. Current MCP documentation takes precedence over its older directory
overview: USER reads/writes the first existing `.mcp.json`, `mcp.json`, or
`~/.codebuddy.json`, creating `.mcp.json` if absent. `CODEBUDDY.md` supplies user
instructions; `skills/` supplies user Skills. `CODEBUDDY_CONFIG_DIR` is documented.

Sources:
- https://github.com/MiniMax-AI/minimax-code
- https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting
- https://www.codebuddy.cn/docs/cli/mcp
- https://www.codebuddy.cn/docs/cli/codebuddy-dir
- https://www.codebuddy.cn/docs/cli/env-vars

## Implementation seams

Extend the existing JSON MCP merger with explicit host labels. New native fragments
remain host-specific; Cursor/Claude templates and existing LAN URL changes are
preserved. Share a new JSON-MCP component driver between the two new hosts, with
thin public Bash/PowerShell wrappers. Reuse existing backup helpers.

Share existing Claude-style full-profile steps through a document-host helper:
Skills, paired skill defaults, canonical global document, then host MCP. Preserve
Claude's paths, document name, prompts and component. MiniMax/WorkBuddy supply
their roots/documents/components, receiving no Graphify Skill or Codex hooks.
Full-install dependency bootstrap remains unchanged.

MCP discovery honors legacy locations without migration. Preview only reads.
Validate target kind and packaged-fragment identity before backup/write. Existing
JSON keys and unrelated servers are retained by the shared merger.

## Risk and validation

Follow-up: all five host templates now set both Mem0 and Recallium to the
user-confirmed `https://www.59005046.xyz:8102/mcp`. The TOML and JSON merger retain
explicit Mem0 URL overrides even when a template contains a literal default.
Existing URL prompts show the resolved default/override and keep on Enter.
Missing packaged Mem0 uses its default without requesting another URL.

L2 installer change with global-write capability. Tests use temporary homes,
harmless wizard fixtures and no network installs. Verify transports, path
precedence, URL choices, backup exactness, preview nonmutation, invalid files and
failure propagation. Adjacent wizard/MCP tests cover existing hosts. Preserve a
pre-edit snapshot outside the repository.
