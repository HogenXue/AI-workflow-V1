# Publication scope and candidate validation — 2026-10-04

The user explicitly requested a push after approving MiniMax Code / WorkBuddy
support and the shared default MCP URLs. Target: GitHub `origin/main`.

## Scoped candidate

Base: `af1c6f658707ea467821aa4bf2ba8c51b1ae63b6`.
An external temporary Git index and exported snapshot contain only the approved
host support, default endpoints, tests, specs and this task's records.

Excluded pre-existing work remains in the user's checkout:

- `AGENTS.md` deletion.
- LAN/private-IP HTTP validation in `merge_host_mcp.py`, the two corresponding
  tests, and the associated README policy change.
- `.trellis/tasks/09-18-lan-http-memory-mcp/`.

The earlier `verified-files.json` describes the historical full local tree.
`publication-source-sha256.json` identifies the isolated candidate sources; use
the latter when reusing evidence for the delivered code.

## Actual validation of the exported candidate

A Python unittest loader combined `test_mcp_defaults.py`,
`test_install_interactive.py`, `test_install_new_hosts.py`,
`test_install_merge_ps.py`, `test_install_wizard.py`, and
`test_install_entry_ps.py`: **106 discovered, 64 passed, 42 skipped, zero
failures/errors**, 5.950 seconds. The two excluded LAN tests explain the count
difference from the full local tree. Skips require unavailable `pwsh`.

Bash syntax, Python AST, native JSON parsing, task context validation and staged
diff checks passed. Native Trellis review was applied to this scoped candidate.
The only subsequent source normalization removed blank lines left by excluding
the old LAN tests; its AST was verified identical, so test evidence was reused.

No full repository suite, application-session acceptance, native PowerShell
runtime, external MCP connection or real user-profile installation was performed.
No unrelated work is part of this delivery. Remote advancement and original
index/worktree preservation are checked immediately around the Git operations.
