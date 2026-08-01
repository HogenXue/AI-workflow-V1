# Design: ps-install-merge

Port `install-codex-merge.sh` / `install-cursor-merge.sh`. Invoke `lib/merge_host_mcp.py` via resolved Python executable. Preserve project-root skip rules, MCP conflict policies, dangling symlink backup, and Cursor rules generation from `trellis/AGENTS.global.md` as bash does.
